from app.adapters.services import kafka_service, redis_service
from app.core.tools.linked_list import LinkedList
import datetime
import logging
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
    def __init__(self, message_helpers: LinkedList[MessageHelper],
                 batch_size: int = 10) -> None:
        self.message_helpers = message_helpers
        self.current = message_helpers.head
        self.batch_size=batch_size
        self.messages : list[MessageEvent] = []
    
    def _is_kafka_limit_reached(self, data: MessageHelper):
        return True
    
    def get(self, comparator_func) -> MessageHelper:
        while self.current is not None and comparator_func(self.current.data) == False:
            logger.info(f"Kafka instance {self.current.data.kafka.name} exausted. Getting next instance.")
            self.message_helpers.delete(self.current.data)
            self.current = self.message_helpers.head
            
            if self.current is None:
                raise ValueError(f"All Kafka instances are exausted for {datetime.datetime.now().date()}")
            
            logger.info(f"Using Kafka instance {self.current.data.kafka.name}")
            
        if self.current is not None:    
            return self.current.data
        return None
    
    def add_message(self, message: MessageEvent):
        self.messages.append(message)
        
        if len(self.messages) >= self.batch_size:
            for msg in self.messages:
                self._send(topic=msg.topic, message=msg.message)
    
    def _send(self, topic:str, message: str):
        try:
            message_helper = self.get(self._is_kafka_limit_reached)
            logger.debug(f"message sent to topic= {topic}")
        except ValueError as e:
            raise ClientException(f"Messages cannot be sent because {e}")
    