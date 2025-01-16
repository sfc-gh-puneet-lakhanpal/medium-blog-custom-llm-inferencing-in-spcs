#!/bin/bash
set -e  # Exit on command errors
set -x  # Print each command before execution, useful for debugging
eth0Ip=$(ifconfig eth0 | sed -En -e 's/.*inet ([0-9.]+).*/\1/p')
export log_dir="/raylogs/ray/$eth0Ip"
echo "Log directory name: $log_dir..."
mkdir -p $log_dir
export RAY_ENABLE_RECORD_ACTOR_TASK_LOGGING=1
export RAY_BACKEND_LOG_LEVEL=debug
export HOST_IP="$eth0Ip"
export NCCL_DEBUG=INFO
export NCCL_SOCKET_IFNAME=eth0
export RAY_ROTATION_MAX_BYTES=1024
export RAY_ROTATION_BACKUP_COUNT=1
ray start --node-ip-address="$eth0Ip" --head --resources='{"custom_llm_serving_label": 1}' --disable-usage-stats --port=6379 --dashboard-host=0.0.0.0 --object-manager-port=8076 --node-manager-port=8077 --runtime-env-agent-port=8078 --dashboard-agent-grpc-port=8079 --dashboard-grpc-port=8080 --dashboard-agent-listen-port=8081 --metrics-export-port=8082 --ray-client-server-port=10001 --dashboard-port=8265 --temp-dir=$log_dir
python batch_api.py &
tail -f /dev/null