from app.adapters.services import kafka_service, redis_service
from app.core.tools.linked_list import LinkedList
import datetime
from kafka.errors import KafkaError
import logging
import threading
from pydantic import BaseModel
from app.core.exceptions.client_exception import ClientException


logger = logging.getLogger(__name__)

class MessageHelper:
    def __init__(self, kafka: kafka_service.KafkaSingleton, 
                 redis: redis_service.RedisSingleton) -> None:
        self.kafka = kafka
        self.redis = redis

class MessageEvent(BaseModel):
    topic: str
    message: str
    
class MessageService:
    _lock = threading.Lock()
    _message_report = {}
    _counter = 0
    
    def __init__(self, message_helpers: LinkedList[MessageHelper],
                 batch_size: int = 10) -> None:
        self.message_helpers = message_helpers
        self.current = message_helpers.head
        self.batch_size=batch_size
        self.messages : list[MessageEvent] = []
    
    async def _is_kafka_limit_reached(self, data: MessageHelper):
        if self._counter < 10000:
            return False
        else:
            self._counter = 0
            logger.error(f"Kafka limit reached.")
            return True
    
    async def get(self, comparator_func) -> MessageHelper:
        while self.current is not None and await comparator_func(self.current.data) == True:
            logger.info(f"Kafka instance {self.current.data.kafka.name} exausted. Getting next instance.")
            self.message_helpers.delete(self.current.data)
            self.current = self.message_helpers.head
            
            if self.current is None:
                raise ValueError(f"All Kafka instances are exausted for {datetime.datetime.now().date()}")
            
            logger.info(f"Using Kafka instance {self.current.data.kafka.name}")
            
        if self.current is not None:    
            return self.current.data
        return None
    
    async def add_message(self, message: MessageEvent):
        self.messages.append(message)
        if len(self.messages) >= self.batch_size:
            logger.debug(f"sending new batch of messages")
            batch_messages = self.messages.copy()
            await self.flush(batch_messages)
            self.messages = []
            logger.debug(f"finished sending  batch of messages. Current message size: {len(self.messages)}")
    
    async def flush(self, messages):
       await self.send_message_async(messages=messages)
            
    async def send_message_async(self, messages: list[MessageEvent]):
        """Send messages to Kafka topic"""
        for msg in messages:
            await self._send(topic=msg.topic, message=msg.message)
            if msg.topic in self._message_report:
                self._message_report[msg.topic] += 1
            else:
                self._message_report[msg.topic] = 1
            
        messages = []
    
    async def _send(self, topic:str, message: str):
        try:
            message_helper = await self.get(self._is_kafka_limit_reached)
            message_helper.kafka.send(topic=topic, message=message)
            logger.debug(f"message sent to topic= {topic}")
            self._counter += 1
        except (ValueError, KafkaError) as e:
            raise ClientException(f"Messages cannot be sent because {e}")
    
    def get_report(self):
        return self._message_report