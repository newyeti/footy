from pydantic import BaseModel, Field
from app.adapters.services.kafka_service_impl import KafkaSingleton
from app.adapters.services.redis_service_impl import RedisSingleton

class MessageHelper(BaseModel):
    kafka: KafkaSingleton
    redis: RedisSingleton