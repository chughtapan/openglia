# LLM Request Routing Optimization

Design an efficient request scheduler for a distributed LLM serving cluster. Use the simulator (the current working directory) to evaluate your ideas.

## System Overview

The system has a number of LLM serving instances (replicas) that can process the requests. Incoming requests are first processed by a 'global scheduler'. The global scheduler maintains a queue of requests. It decides when and which replica to send each request.

The base class for the global scheduler "BaseGlobalScheduler" can be found at: `environment/vidur/vidur/scheduler/global_scheduler/base_global_scheduler.py`

A simple implementation of the global scheduler is LLQGlobalScheduler which dispatches requests to the replica with least loaded queue, and can be found here: `environment/vidur/vidur/scheduler/global_scheduler/lor_global_scheduler.py`

The entry point for the global scheduler is the `schedule()` function. This is called by the simulator after each request arrival and request completion event.

Each serving instance schedules its incoming requests via a 'replica scheduler'. The replica scheduler creates batches of work to be processed on GPUs.

The base class for replica scheduler "BaseReplicaScheduler" can be found at: `environment/vidur/vidur/scheduler/replica_scheduler/base_replica_scheduler.py`

For this design task, we will use the vLLM replica scheduler provided here: `environment/vidur/vidur/scheduler/replica_scheduler/vllm_replica_scheduler.py`

**Request Lifecycle:**
```
incoming request → global scheduler → replica scheduler → Batch processing by GPU (prefill / decode)
```

Every request is first processed in prefill stage to compute the kv-cache of the input tokens. Once prefill is complete, the request enters the decode stage where its output tokens are computed incrementally. The total number of decode tokens is not known until a request finishes. Only the number of prefill tokens is known when a request arrives.

## Objective

Your task is to optimize the global scheduler. The primary performance metric is the average response time of requests.

## Evaluation

A benchmark is provided to evaluate your designs. It consists of a 1000-second simulation of a workload running on a cluster with 4 identical a100 GPUs. The workload generates 2.0 queries-per-second (qps). The benchmark workload can be found in `environment/vidur/data/processed_traces/splitwise_conv.csv`.

To run the benchmark, use the following command from the current directory:
```bash
cd environment/vidur && ./run_all.sh
```

As a baseline, I ran the benchmark for the LLQ algorithm. The simulation outputs artifacts in a directory like `environment/vidur/simulator_results/splitwise_AI_2.0/<folder_time_stamp>/`. This directory contains the following files:
1. `config.json` that specifies the experiment configs
2. `request_metrics.csv` provides per-request information with columns including: request_id, request_e2e_time, prefill_time, decode_time, num_prefill_tokens, num_decode_tokens, ttft (time-to-first-token), and tpot (time-per-output-token).

## Constraints

- Modify only the global scheduler. Do not change the behavior of replica scheduler.
- The global scheduler may not use the `num_decode_token` property of request objects, since the number of decode tokens of a request is not known in a real system.
- Implement your ideas in `environment/vidur/vidur/scheduler/global_scheduler/ai_global_scheduler.py`, which is prepopulated with a random scheduler.

## Your Task

Experiment by running `cd environment/vidur && ./run_all.sh` from the current directory and looking at the output found in `environment/vidur/simulator_results/splitwise_AI_2.0/[YYYY-MM-DD_HH-MM-SS-microseconds]`.

Iterate on your design to reduce the average request completion time (`request_e2e_time` in `request_metrics.csv`).

Do not interrupt me until you have found a solution that is at least better than LLQ's average request time (around 3.42 seconds on this benchmark). It should be possible to perform much better than LLQ (at least a 20% improvement is expected).
