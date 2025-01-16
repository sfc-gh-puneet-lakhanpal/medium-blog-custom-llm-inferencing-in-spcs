FROM nvcr.io/nvidia/pytorch:23.06-py3
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    apt-utils \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN pip3 install --upgrade pip
COPY requirements.txt ./
RUN pip3 install -r requirements.txt
COPY download_model.py ./
COPY entrypointwithmodeldownload.sh ./
RUN chmod +x ./entrypointwithmodeldownload.sh
ENV HUGGING_FACE_MODEL=ibm-granite/granite-3.1-8b-instruct
ENTRYPOINT ["./entrypointwithmodeldownload.sh"]