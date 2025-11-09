import random

from vidur.entities import Request
from vidur.scheduler.global_scheduler.base_global_scheduler import BaseGlobalScheduler


class AIGlobalScheduler(BaseGlobalScheduler):
    """
    AI-designed global scheduler stub.

    This is the starting point for each experiment run.
    The agent will modify this file to discover better routing algorithms.
    """

    def schedule(self) -> list[tuple[int, Request]]:
        """
        Route requests to replicas.

        Returns:
            List of (replica_id, request) tuples
        """
        request_mapping = []

        # Simple random routing as starting point
        # Agent should improve this!
        for request in self._request_queue[:]:
            replica_id = random.choice(list(self._replica_schedulers.keys()))
            request_mapping.append((replica_id, request))
            self._request_queue.remove(request)

        return request_mapping
