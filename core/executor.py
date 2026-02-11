from taskiq_redis import ListQueueBroker
from core.settings import settings

# Initialize the broker with Redis
broker = ListQueueBroker(
    url=settings.REDIS_URL,
)
