import logging
from app.core.tools.linked_list import LinkedList
from datetime import datetime, timedelta
from kafka.errors import KafkaError
from pydantic import BaseModel
from app.core.exceptions.client_exception import ClientException
from app.adapters.services.kafka_service import KafkaSingleton
from app.adapters.services.redis_service import RedisSingleton


logger = logging.getLogger(__name__)

DEFAULT_KAFKA_DAILY_LIMIT = 10000
DEFAULT_REDIS_DAILY_LIMIT = 10000
DEFAULT_KEY_EXPIRY_IN_DAYS = 1
DAILY_KAFKA_MESSAGE_SENT_COUNT_KEY = "kafka_messages_sent"

class MessageHelper:
    def __init__(self, kafka: KafkaSingleton, 
                 redis: RedisSingleton) -> None:
        self.kafka = kafka
        self.redis = redis

class MessageEvent(BaseModel):
    topic: str
    message: str
    
class MessageService:
    _message_report = {}
    _counter = 0
    
    def __init__(self, message_helpers: LinkedList[MessageHelper],
                 batch_size: int = 10,
                 kafka_daily_limit: int = DEFAULT_KAFKA_DAILY_LIMIT,
                 redis_daily_limit: int = DEFAULT_REDIS_DAILY_LIMIT,
                 key_expiry_in_days: int = DEFAULT_KEY_EXPIRY_IN_DAYS) -> None:
        self.message_helpers = message_helpers
        self.current = message_helpers.head
        self.batch_size=batch_size
        self.kafka_daily_limit = kafka_daily_limit
        self.redis_daily_limit = redis_daily_limit
        self.key_expiry_in_days = key_expiry_in_days
        self.messages : list[MessageEvent] = []
        self._counter = self.get_kafka_message_count(self.current.data)
        
    
    async def _is_kafka_limit_reached(self, data: MessageHelper):
        if self._counter < self.kafka_daily_limit:
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
                raise ValueError(f"All Kafka instances are exausted for {datetime.now().date()}")
            
            self._counter = self.get_kafka_message_count(self.current.data)
            logger.info(f"Using Kafka instance {self.current.data.kafka.name}")
            
        if self.current is not None:    
            return self.current.data
        
        raise ValueError(f"All Kafka instances are exausted for {datetime.now().date()}")
    
    
    async def add_message(self, message: MessageEvent):
        self.messages.append(message)
        if len(self.messages) >= self.batch_size:
            logger.debug(f"sending new batch of messages")
            batch_messages = self.messages.copy()
            await self.flush(batch_messages)
            self.messages = []
            logger.debug(f"finished sending  batch of messages. Current message size: {len(self.messages)}")
    
        
    async def flush(self, messages):
       logger.info(f"Sending new batch of {len(messages)} messages.")
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
        self.set_kafka_message_count(self.current.data, self.batch_size)
    
    
    async def _send(self, topic:str, message: str):
        try:
            message_helper = await self.get(self._is_kafka_limit_reached)
            message_helper.kafka.send(topic=topic, message=message)
            logger.debug(f"message sent to topic= {topic}")
            self._counter += 1
        except (ValueError, KafkaError) as e:
            raise ClientException(f"Messages cannot be sent because {e}")
    
    
    def get_kafka_message_count(self, message_helper: MessageHelper) -> int:
        redis_key = message_helper.redis.get_key(key=DAILY_KAFKA_MESSAGE_SENT_COUNT_KEY, 
                                                 suffix=datetime.now().date())
        logger.debug(f"redis_key: {redis_key}")
        
        kafka_messages_sent = self.current.data.redis.get(redis_key)
        if kafka_messages_sent is None:
            kafka_messages_sent = 0
            message_helper.redis.set(redis_key, kafka_messages_sent, timedelta(days=self.key_expiry_in_days))
            logger.debug(f"Default value set for redis_key: {redis_key}")
            
        return int(kafka_messages_sent)
    
    
    def set_kafka_message_count(self, message_helper: MessageHelper, count: int):
        redis_key = message_helper.redis.get_key(key=DAILY_KAFKA_MESSAGE_SENT_COUNT_KEY, 
                                                 suffix=datetime.now().date())
        remote_count = self.current.data.redis.get(redis_key)
        if remote_count is None:
            remote_count = "0"
        kafka_messages_sent = count + int(remote_count)
        message_helper.redis.set(key=redis_key, value=kafka_messages_sent, expiry=timedelta(days=self.key_expiry_in_days))
        
            
    def get_report(self):
        return self._message_report