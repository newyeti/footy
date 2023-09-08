from datetime import datetime, timedelta
from redis import Redis
from app.core.tools.decorators import singleton_with_initializer
from app.entrypoints.cmd.config import RedisConfig

def redis_initializer(instance, redis_config: RedisConfig):
    instance.redis = Redis(host=redis_config.host,
                           port=redis_config.port,
                           password=redis_config.password,
                           ssl=True,
                            ssl_cert_reqs="none")

@singleton_with_initializer(redis_initializer)
class RedisSingleton:
    def __init__(self, name: str, redis_config: RedisConfig):
        self.name = name
        self.redis_config = redis_config
        self.redis : Redis = None
        pass
    
    def get(self, key: str):
        return self.redis.get(key)

    def set(self, key: str, value: str, expiryDays: int):
        self.redis.set(name=key, value=value, ex=timedelta(days=expiryDays))