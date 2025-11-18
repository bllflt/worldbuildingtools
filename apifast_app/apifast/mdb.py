import redis.asyncio as redis

from apifast.config import config


def get_redis():
    r = redis.from_url(config.redis_uri)
    return r
