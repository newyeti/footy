from app.adapters.services.node_manager import NodeManager
from app.core.tools.linked_list import LinkedList
from app.core.model.domain import MessageHelper
import datetime
import logging
from pydantic import BaseModel

class MessageEvent(BaseModel):
    topic: str
    message: str
    
class MessageService:
    def __init__(self, message_helpers: LinkedList[MessageHelper],
                 batch_size: int = 10) -> None:
        self.message_helpers = message_helpers
        self.current = message_helpers.head
        self.batch_size=batch_size
        self.messages = []
    
    def _is_kafka_limit_reached(self):
        return False
    
    def get(self, comparator_func) -> MessageHelper:
        while self.current is not None and comparator_func(self.current.data) == False:
            self.current = self.current.next
            
        if self.current is not None:    
            return self.current.data
        return None
    
    def add_message(message: MessageEvent):
        ...
    
    def _send(self, topic:str, message: str):
        message_helper = self.get(self._is_kafka_limit_reached)
        if message_helper is None:
            logging.info(f"All available kafka are exuasterd for {datetime.datetime.now().date()}")
        
        message_helper.kafka.send(topic=topic, message=message)