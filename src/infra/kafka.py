from kafka import KafkaProducer
from kafka.errors import KafkaError
import certifi
import ssl
from tools.decorators import singleton_with_initializer

def kafka_producer_initializer(instance):
    bootstrap_servers = ['flying-ghoul-13808-us1-kafka.upstash.io:9092']
    client_id='newyeti-telemetry-producer'
    sasl_mechanism='SCRAM-SHA-256'
    security_protocol='SASL_SSL'
    sasl_plain_username='Zmx5aW5nLWdob3VsLTEzODA4JK8Ko_8y0QKzRZOlFK6CSN1hNX6uJeoFsgqms64'
    sasl_plain_password = '3d9f1534b0e847afa95090cc9d7d7d7e'
    ssl_context=ssl.create_default_context(cafile=certifi.where())
    
    instance.producer = KafkaProducer(
        bootstrap_servers = bootstrap_servers,
        client_id=client_id,
        sasl_mechanism=sasl_mechanism,
        security_protocol=security_protocol,
        sasl_plain_username=sasl_plain_username,
        sasl_plain_password=sasl_plain_password,
        ssl_context=ssl_context,
        value_serializer = lambda v : str(v).encode("utf-8")
    ) 

@singleton_with_initializer(kafka_producer_initializer)
class KafkaProducerSingleton:
    def __init__(self):
        pass
    
    def send(self, topic: str, message: str):
        future = self.producer.send(topic=topic, value=message)
        
        try:
            record_metadata = future.get(timeout=10)
            print(f"Message delivered to {record_metadata.topic} [{record_metadata.partition}]")
        except KafkaError as e:
            print(f"Message delivery failed: {e}")
