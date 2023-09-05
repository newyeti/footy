from kafka import KafkaProducer
from kafka.errors import KafkaError
import certifi
import ssl
from app.core.tools.decorators import singleton_with_initializer
from app.entrypoints.cmd.config import KafkaConfig
from app.adapters.services.redis_service_impl import RedisSingleton

def kafka_producer_initializer(instance, kafka_config):
    instance.producer = KafkaProducer(
        bootstrap_servers = kafka_config.bootstrap_servers,
        client_id = kafka_config.client_id,
        sasl_mechanism = kafka_config.sasl_mechanism,
        security_protocol = kafka_config.security_protocol,
        sasl_plain_username = kafka_config.sasl_plain_username,
        sasl_plain_password = kafka_config.sasl_plain_password,
        ssl_context = ssl.create_default_context(cafile=certifi.where()),
        value_serializer = lambda v : str(v).encode("utf-8")
    )

@singleton_with_initializer(kafka_producer_initializer)
class KafkaSingleton:
    def __init__(self, name: str, kafka_config: KafkaConfig):
        self.name = name
        self.kafka_config = kafka_config
        pass
    
    def send(self, topic: str, message: str) -> None:
        future = self.producer.send(topic=topic, value=message)
        
        try:
            record_metadata = future.get(timeout=10)
            print(f"Message delivered to {record_metadata.topic} [{record_metadata.partition}]")
        except KafkaError as e:
            print(f"Message delivery failed: {e}")
