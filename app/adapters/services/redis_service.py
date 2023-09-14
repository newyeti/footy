from datetime import datetime, timedelta
from redis import Redis
import datetime
from app.core.tools.decorators import singleton_with_initializer
from app.entrypoints.cmd.config import RedisConfig

def redis_initializer(instance, redis_config: RedisConfig):
    instance.redis_client = Redis(host=redis_config.host,
                           port=redis_config.port,
                           password=redis_config.password,
                           ssl=True,
                            ssl_cert_reqs="none")

@singleton_with_initializer(redis_initializer)
class RedisSingleton:
    def __init__(self, name: str, redis_config: RedisConfig):
        self.name = name
        self.redis_config = redis_config
        self.redis_client : Redis = None
        pass
    
    def get(self, key: str):
        return self.redis_client.get(key)

    def set(self, key: str, value: str, expiry: timedelta):
        self.redis_client.set(name=key, value=value, ex=expiry)
        
    def get_key(self, key: str, prefix: str = "", suffix: str = ""):
        if prefix is None:
            prefix = ""
        elif prefix != "":
            prefix = f"{prefix}_"
        
        if suffix is None:
            suffix = ""
        elif suffix != "":
            suffix = f"_{suffix}"
            
        return f"{prefix}{key}{suffix}"