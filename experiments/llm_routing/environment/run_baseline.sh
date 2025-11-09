#!/bin/bash

# Script to generate baseline results with LLQ (LOR) scheduler
# This should be run ONCE to create the baseline that agents compare against

set -e

# Configuration
DEVICE="a100"
MODEL="meta-llama/Llama-2-7b-hf"
NUM_REPLICAS=4
TRACE_FILE="./data/processed_traces/splitwise_conv.csv"
TARGET_QPS=2.0

echo "=========================================="
echo "Running Baseline (LLQ/LOR Scheduler)"
echo "=========================================="
echo "This creates the baseline results for comparison"
echo ""

python -m vidur.main \
    --replica_config_device $DEVICE \
    --replica_config_model_name $MODEL \
    --cluster_config_num_replicas $NUM_REPLICAS \
    --replica_config_tensor_parallel_size 1 \
    --replica_config_num_pipeline_stages 1 \
    --global_scheduler_config_type lor \
    --request_generator_config_type synthetic \
    --synthetic_request_generator_config_duration 1000 \
    --length_generator_config_type trace \
    --trace_request_length_generator_config_trace_file $TRACE_FILE \
    --interval_generator_config_type poisson \
    --poisson_request_interval_generator_config_qps $TARGET_QPS \
    --replica_scheduler_config_type vllm \
    --metrics_config_output_dir simulator_results/splitwise_llq_${TARGET_QPS}

echo ""
echo "Baseline complete!"

# Find the output directory
BASELINE_DIR=$(ls -td simulator_results/splitwise_llq_${TARGET_QPS}/*/ 2>/dev/null | head -1)

if [ -n "$BASELINE_DIR" ]; then
    echo ""
    echo "Baseline results saved to: $BASELINE_DIR"
    echo ""
    echo "Extracting average request_e2e_time..."
    if [ -f "${BASELINE_DIR}request_metrics.csv" ]; then
        AVG_TIME=$(awk -F',' 'NR>1 {sum+=$2; count++} END {if(count>0) printf "%.2f", sum/count}' "${BASELINE_DIR}request_metrics.csv")
        echo "LLQ average request_e2e_time: ${AVG_TIME} seconds"
    fi
    echo ""
    echo "This baseline will be referenced by the AI agent."
fi
