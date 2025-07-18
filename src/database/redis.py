import redis
from src.conf.config import settings

redis_cache = redis.Redis(
    host=settings.REDIS_DOMAIN, port=settings.REDIS_PORT, db=settings.REDIS_DB
)
