import redis.asyncio as redis

from charservice.config import config


def get_redis():
    r = redis.from_url(config.redis_uri)
    return r
