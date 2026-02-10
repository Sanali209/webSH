from collections import OrderedDict
import logging
import asyncio
from typing import Any, Optional
from core.events import event_bus

logger = logging.getLogger(__name__)

class QueryCache:
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.hits = 0
        self.misses = 0
        # Auto-subscribe to invalidation events
        # Note: Subscription happens when imported/instantiated,
        # but event_bus might not be fully ready? It's fine as long as loop runs.
        event_bus.subscribe("fs:created", self.invalidate)
        event_bus.subscribe("fs:modified", self.invalidate)
        event_bus.subscribe("fs:deleted", self.invalidate)
        event_bus.subscribe("fs:moved", self.invalidate)

    async def invalidate(self, data: Any = None, correlation_id: str = None):
        """Clears the entire cache."""
        self.cache.clear()
        logger.info("Query cache invalidated due to FS change")

    def get(self, key: Any) -> Optional[Any]:
        if key in self.cache:
            self.cache.move_to_end(key)
            self.hits += 1
            logger.debug(f"Cache HIT for {key}")
            return self.cache[key]
        self.misses += 1
        return None

    def put(self, key: Any, value: Any):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
        logger.debug(f"Cache PUT for {key}")

# Global instance
query_cache = QueryCache()
