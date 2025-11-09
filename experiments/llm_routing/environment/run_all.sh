#!/bin/bash

# Benchmark script for evaluating LLM request schedulers
# Matches the setup from the Glia paper

set -e  # Exit on error

# Configuration (matching paper's setup)
DEVICE="a100"
MODEL="meta-llama/Llama-2-7b-hf"
NUM_REPLICAS=4
TRACE_FILE="./data/processed_traces/splitwise_conv.csv"
TARGET_QPS=2.0

echo "=========================================="
echo "LLM Scheduler Benchmark"
echo "=========================================="
echo "Device: $DEVICE (4 identical GPUs)"
echo "Model: $MODEL"
echo "Replicas: $NUM_REPLICAS"
echo "Target QPS: $TARGET_QPS"
echo "Trace: $TRACE_FILE"
echo "=========================================="

# Run AI scheduler only
# (Baseline should already exist from prior runs)
echo ""
echo "Running AI scheduler..."
python -m vidur.main \
    --replica_config_device $DEVICE \
    --replica_config_model_name $MODEL \
    --cluster_config_num_replicas $NUM_REPLICAS \
    --replica_config_tensor_parallel_size 1 \
    --replica_config_num_pipeline_stages 1 \
    --global_scheduler_config_type ai \
    --request_generator_config_type synthetic \
    --synthetic_request_generator_config_duration 1000 \
    --length_generator_config_type trace \
    --trace_request_length_generator_config_trace_file $TRACE_FILE \
    --interval_generator_config_type poisson \
    --poisson_request_interval_generator_config_qps $TARGET_QPS \
    --replica_scheduler_config_type vllm \
    --metrics_config_output_dir simulator_results/splitwise_AI_${TARGET_QPS}

echo ""
echo "AI scheduler run complete!"
echo ""

# Find the latest output directory
AI_DIR=$(ls -td simulator_results/splitwise_AI_${TARGET_QPS}/*/ 2>/dev/null | head -1)

if [ -n "$AI_DIR" ]; then
    echo "=========================================="
    echo "Results"
    echo "=========================================="
    echo "AI scheduler results: $AI_DIR"
    echo ""
    echo "Key files:"
    echo "  - config.json: Experiment configuration"
    echo "  - request_metrics.csv: Per-request metrics"
    echo ""
    if [ -f "${AI_DIR}request_metrics.csv" ]; then
        AI_AVG_TIME=$(awk -F',' 'NR>1 {sum+=$2; count++} END {if(count>0) printf "%.2f", sum/count}' "${AI_DIR}request_metrics.csv")
        echo "AI scheduler average request_e2e_time: ${AI_AVG_TIME} seconds"
        echo ""
        echo "Compare to baseline (LLQ): 3.42 seconds"
        if [ -n "$AI_AVG_TIME" ]; then
            IMPROVEMENT=$(awk -v baseline=3.42 -v ai=$AI_AVG_TIME 'BEGIN {printf "%.1f", (baseline-ai)/baseline*100}')
            echo "Improvement: ${IMPROVEMENT}%"
        fi
    fi
    echo "=========================================="
else
    echo "Error: Could not find output directory"
    exit 1
fi
