use role LLM_ROLE;
USE DATABASE LLM_DB;
USE SCHEMA VLLM_SCH;
USE WAREHOUSE XSMALL_WH;
alter compute pool if exists RAY_VLLM_CP stop all;
drop compute pool if exists RAY_VLLM_CP;
// ray compute pool
CREATE COMPUTE POOL if not exists RAY_VLLM_CP
  MIN_NODES = 1
  MAX_NODES = 1
  INSTANCE_FAMILY = GPU_NV_M
  AUTO_SUSPEND_SECS = 300;

show compute pools like 'RAY_VLLM_CP';

//create service

 drop service if exists RAY_VLLM_SERVICE force;

CREATE SERVICE RAY_VLLM_SERVICE
  IN COMPUTE POOL RAY_VLLM_CP
  FROM @YAMLSPECS
  SPEC='ray_vllm.yaml'
  MIN_INSTANCES=1
  MAX_INSTANCES=1
  EXTERNAL_ACCESS_INTEGRATIONS=(allow_all_integration);


// check compute pool status
show compute pools like 'RAY_VLLM_CP';
//check status of the service
SELECT VALUE:status::VARCHAR as SERVICESTATUS, VALUE:message::VARCHAR as SERVICEMESSAGE FROM TABLE(FLATTEN(input => parse_json(system$get_service_status('RAY_VLLM_SERVICE')), outer => true)) f;


call system$get_service_logs('RAY_VLLM_SERVICE', 0, 'vllm', 1000);

//get the api endpoint

SHOW ENDPOINTS IN SERVICE RAY_VLLM_SERVICE;