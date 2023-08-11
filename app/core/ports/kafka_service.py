from abc import ABC, abstractmethod

class KafkaService(ABC):
    
    @abstractmethod
    def send(self, topic: str, message: str) -> None:
        ...
