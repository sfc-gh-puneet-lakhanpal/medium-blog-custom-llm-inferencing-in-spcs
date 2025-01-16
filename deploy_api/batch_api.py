import logging
import os
import sys
import ray
from opencv_fixer import AutoFix
from ray import serve
import torch
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer
from typing import List
import os
import torch
from fastapi import FastAPI, Request
AutoFix()
MODEL = os.getenv("HF_MODEL")
system_prompt = """You are a helpful assistant."""
ray_data_logger = logging.getLogger("ray.data")
ray_data_logger.setLevel(logging.INFO)
# disable progress bar    
context = ray.data.DataContext().get_current() 
context.execution_options.verbose_progress = False
context.enable_operator_progress_bars = False
context.enable_progress_bars = False

# disable long logging for ray in general
ray_logger = logging.getLogger("ray")
ray_logger.setLevel(logging.INFO)
# set root logger as well
logging.getLogger().setLevel(logging.INFO)  
gpu_count = 1
if torch.cuda.is_available():
    gpu_count = torch.cuda.device_count()
    print("Number of available GPUs:", gpu_count)
else:
    print("No GPUs available.")

class vLLMBatchInference:
    def __init__(self, 
        model_name: str, 
        system_prompt:str, 
        llm: LLM
    ) -> None:
        """
        Initialisation method for the deployment.
        """
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.llm = llm
        self.system_prompt = system_prompt

    def requests(self, batched_inputs: List) -> List:
        """
        Method for deployment batched requests, called once for each batch request.
        """
        max_tokens = batched_inputs[0][1]
        if max_tokens <= 0:
            max_tokens = 256
        sampling_params = SamplingParams(max_tokens=max_tokens)
        user_prompts_list = [input[0] for input in batched_inputs]
        full_prompts =  [self.tokenizer.apply_chat_template([{"role": "system", "content": self.system_prompt}, {"role": "user", "content": element}], tokenize=False, add_generation_prompt=True) for element in user_prompts_list]
        outputs = self.llm.generate(full_prompts, sampling_params)
        generated_texts: List[str] = []
        for output in outputs:
            generated_texts.append(' '.join([o.text for o in output.outputs]))
        return generated_texts
    
# Logging
def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.CRITICAL)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.CRITICAL)
    handler.setFormatter(
        logging.Formatter(
            '%(name)s [%(asctime)s] [%(levelname)s] %(message)s'))
    logger.addHandler(handler)
    return logger

logger = get_logger('snowpark-container-service')
rayserver_logger = logging.getLogger("ray.serve")
rayserver_logger.setLevel(logging.INFO)
tensor_parallel_size = 2
pg_resources = []
pg_resources.append({"CPU": 1})  # for the deployment replica
for i in range(tensor_parallel_size):
    pg_resources.append({"CPU": 1, "GPU": 1})

app = FastAPI()
@serve.deployment(num_replicas=2, placement_group_bundles=pg_resources, placement_group_strategy="STRICT_PACK", max_ongoing_requests=1000)
@serve.ingress(app)
class FastAPIWrapper:
    def __init__(self):
        llm = LLM(
            model=MODEL,  
            gpu_memory_utilization=0.9,
            trust_remote_code=True,
            device="cuda",
            dtype=torch.bfloat16,
            enable_prefix_caching=True,
            tensor_parallel_size = tensor_parallel_size
        )
        self.vllm_deployment = vLLMBatchInference(model_name=MODEL, system_prompt=system_prompt, llm=llm)
    
    
    @serve.batch(max_batch_size=100, batch_wait_timeout_s=0.1)
    async def get_batched_completion(self, batched_inputs:List):
        #start = time.time()
        #rayserver_logger.info("Got batch size: ", len(batched_inputs))
        results = self.vllm_deployment.requests(batched_inputs)
        #timediff = time.time() - start
        #rayserver_logger.info(f'Batch took: {timediff} secs')
        return results

    @app.post("/llm", tags=["Endpoints"])
    async def llm_inference(self, request: Request):
        request_body = await request.json()
        user_prompt = request_body['user_prompt']
        max_tokens = request_body['max_tokens']
        return await self.get_batched_completion((user_prompt, max_tokens))


print("Initializing Ray...")
ray.init(address="auto", log_to_driver=False)
print("Printing Ray cluster resources...")
print(ray.cluster_resources())
print("Running Ray Serve with a route prefix of / and the fastapi has an endpoint of /llm...")
serve.run(FastAPIWrapper.bind(), route_prefix="/")