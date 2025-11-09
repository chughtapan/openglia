from typing import List, Tuple
from math import ceil

from vidur.entities import Request
from vidur.scheduler.global_scheduler.base_global_scheduler import BaseGlobalScheduler


class AIGlobalScheduler(BaseGlobalScheduler):
    """
    Memory-aware, size-aware global scheduler.

    Key ideas:
    - Avoid head-of-line blocking created by large-prefill requests by
      scheduling shorter-prefill requests first (Shortest-Prefill-First).
    - Place each request on the replica that is most likely to admit it quickly
      using a cost that considers queue depth and instantaneous memory headroom.
    - Steer large requests preferentially to replicas with empty queues and
      high free memory to prevent blocking small jobs behind them.

    Note: We never look at num_decode_tokens (unknown in practice).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Cache per-replica static params for cost computation
        self._per_replica_params = {}
        for rid, sched in self._replica_schedulers.items():
            cfg = sched._config  # vLLM scheduler config (public dataclass)
            num_blocks = cfg.num_blocks
            block_size = cfg.block_size
            watermark_blocks = int(cfg.watermark_blocks_fraction * num_blocks)
            self._per_replica_params[rid] = {
                "num_blocks": num_blocks,
                "block_size": block_size,
                "watermark": watermark_blocks,
            }

        # Heuristic weights for the cost function (configurable via env for ablations)
        import os
        self._w_pending = float(os.getenv("VIDUR_AI_WPEND", 1.0))
        self._w_used_frac = float(os.getenv("VIDUR_AI_WUSE", 0.5))
        # Strongly penalize placements that cannot be admitted immediately
        self._w_mem_shortfall = float(os.getenv("VIDUR_AI_WMEM", 4.0))

        # Define what "large" means for prefill tokens. This is a soft
        # threshold only used to steer large requests to emptier replicas.
        # We pick 1536 tokens (~1.5k) as a good tradeoff for 7B models.
        self._large_prefill_tokens = int(os.getenv("VIDUR_AI_LARGE_TOK", 1536))

        # Ablation mode switch (full | fifo_cost | spt_llq | full_no_shadow)
        self._mode = os.getenv("VIDUR_AI_MODE", "full").lower()

    def _required_blocks(self, rid: int, prefill_tokens: int) -> int:
        params = self._per_replica_params[rid]
        return ceil(prefill_tokens / params["block_size"])

    def _replica_cost(self, rid: int, req: Request) -> float:
        sched = self._replica_schedulers[rid]
        params = self._per_replica_params[rid]

        # Shadow overlay values set during a scheduling round (if present)
        shadow_pending = getattr(sched, "_ai_shadow_pending", 0)
        shadow_blocks = getattr(sched, "_ai_shadow_blocks", 0)

        pending = sched.num_pending_requests + shadow_pending
        used_blocks = sched.num_allocated_blocks + shadow_blocks
        num_blocks = params["num_blocks"]
        watermark = params["watermark"]

        free_blocks = max(num_blocks - used_blocks, 0)
        need_blocks = self._required_blocks(rid, req.num_prefill_tokens)
        headroom_after = free_blocks - need_blocks - watermark
        mem_shortfall = max(0, -headroom_after)

        used_frac = used_blocks / num_blocks if num_blocks > 0 else 1.0

        # Primary components:
        # - pending queue depth (proxy for time waiting in replica scheduler)
        # - normalized used memory (proxy for decode load and future contention)
        # - memory shortfall penalty if the request cannot be admitted immediately
        cost = (
            self._w_pending * pending
            + self._w_used_frac * used_frac
            + self._w_mem_shortfall * mem_shortfall
        )
        return cost

    def _choose_replica_for_request(self, req: Request) -> int:
        # For large prefill requests, prefer replicas with empty queues first
        # to avoid blocking smaller jobs behind them. Among empty replicas,
        # pick the one with minimal cost; otherwise fall back to global min cost.
        large = req.num_prefill_tokens >= self._large_prefill_tokens

        candidate_ids = list(self._replica_schedulers.keys())

        if large:
            empty_replicas = [
                rid
                for rid in candidate_ids
                if self._replica_schedulers[rid].num_pending_requests
                + getattr(self._replica_schedulers[rid], "_ai_shadow_pending", 0)
                == 0
            ]
            if empty_replicas:
                # Choose among empty replicas by minimizing cost (i.e., memory headroom)
                return min(empty_replicas, key=lambda r: self._replica_cost(r, req))

        # Default: global min cost
        return min(candidate_ids, key=lambda r: self._replica_cost(r, req))

    def schedule(self) -> List[Tuple[int, Request]]:
        # Keep overall FIFO fairness, but break ties among similarly-aged requests
        # by prioritizing smaller prefill first to reduce head-of-line blocking.
        # Sort key: (arrival_time bucketed, prefill_tokens, arrival_time)
        # Bucket recent requests together so very old requests stay at the head.
        self.sort_requests()

        if not self._request_queue:
            return []

        # Stable sort by prefill tokens while preserving arrival ordering groups
        # We first copy and then clear to control placement order explicitly.
        requests = list(self._request_queue)
        self._request_queue.clear()

        # Age-aware SPT: split into two bands to preserve fairness of older requests
        # Band 1: oldest half by arrival time; keep their arrival order (FIFO)
        # Band 2: newer half; order by ascending prefill to reduce blocking
        if self._mode in ("full", "full_no_shadow", "spt_llq"):
            mid = len(requests) // 2
            band1 = requests[:mid]
            band2 = sorted(requests[mid:], key=lambda r: r.num_prefill_tokens)
            ordered = band1 + band2
        else:
            ordered = requests

        request_mapping: List[Tuple[int, Request]] = []

        for req in ordered:
            if self._mode == "spt_llq":
                rid = min(
                    self._replica_schedulers.keys(),
                    key=lambda r: self._replica_schedulers[r].num_pending_requests
                    + getattr(self._replica_schedulers[r], "_ai_shadow_pending", 0),
                )
            else:
                rid = self._choose_replica_for_request(req)
            request_mapping.append((rid, req))

            # Optimistically update the replica's perceived state so that
            # subsequent placement decisions in this scheduling round are
            # consistent (reduces stampeding multiple reqs to the same replica).
            sched = self._replica_schedulers[rid]
            params = self._per_replica_params[rid]
            if self._mode != "fifo_cost":
                if not hasattr(sched, "_ai_shadow_pending"):
                    sched._ai_shadow_pending = 0
                if not hasattr(sched, "_ai_shadow_blocks"):
                    sched._ai_shadow_blocks = 0

                # Increase pending queue length by 1 since the request will be queued
                sched._ai_shadow_pending += 1

                # Tentatively account for reserved blocks if there is headroom
                if self._mode != "full_no_shadow":
                    need_blocks = ceil(req.num_prefill_tokens / params["block_size"])
                    free_blocks = (
                        params["num_blocks"]
                        - (sched.num_allocated_blocks + sched._ai_shadow_blocks)
                    )
                    if free_blocks - need_blocks - params["watermark"] >= 0:
                        sched._ai_shadow_blocks += need_blocks

        # Clean up the shadow attributes so future schedule() calls read fresh state
        for sched in self._replica_schedulers.values():
            if hasattr(sched, "_ai_shadow_pending"):
                delattr(sched, "_ai_shadow_pending")
            if hasattr(sched, "_ai_shadow_blocks"):
                delattr(sched, "_ai_shadow_blocks")

        return request_mapping
