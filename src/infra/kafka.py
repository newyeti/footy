from kafka import KafkaProducer
import certifi
import ssl

def delivery_report(err, msg):
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

# Configure Kafka connection parameters
conf = {
    'bootstrap.servers': 'flying-ghoul-13808-us1-kafka.upstash.io:9092',
    'client.id': 'newyeti-telemetry-producer',
    'sasl_mechanism': 'SCRAM-SHA-256',
    'security_protocol': 'SASL_SSL',
    'sasl_plain_username' :'Zmx5aW5nLWdob3VsLTEzODA4JK8Ko_8y0QKzRZOlFK6CSN1hNX6uJeoFsgqms64',
    'sasl_plain_password' : '3d9f1534b0e847afa95090cc9d7d7d7e'
}

@staticmethod
def send_message(topic: str, message: str):
    # Create a Kafka producer instance
    producer = KafkaProducer(
        bootstrap_servers=['flying-ghoul-13808-us1-kafka.upstash.io:9092'],
        client_id='newyeti-telemetry-producer',
        sasl_mechanism='SCRAM-SHA-256',
        security_protocol='SASL_SSL',
        sasl_plain_username='Zmx5aW5nLWdob3VsLTEzODA4JK8Ko_8y0QKzRZOlFK6CSN1hNX6uJeoFsgqms64',
        sasl_plain_password = '3d9f1534b0e847afa95090cc9d7d7d7e',
        ssl_context=ssl.create_default_context(cafile=certifi.where())
        )
    future=producer.send(topic, value=message.encode("utf-8"))
    result = future.get(timeout=60)
    print(f"kafka send result={result}")
    # Wait for any outstanding messages to be delivered and delivery reports to be received
    producer.flush()
    producer.close()