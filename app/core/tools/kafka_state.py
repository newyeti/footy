from __future__ import annotations
from abc import ABC, abstractmethod

class KafkaContext:
    """
    The KafkaContext defines the interface of interest to clients. It also maintains
    a reference to an instance of a KafkaState subclass, which represents the current
    state of the KafkaContext.
    """

    _state = None
    
    """
    A reference to the current state of the Context.
    """
    
    def __init__(self, state: KafkaState) -> None:
        self.transition_to(state)

    def transition_to(self, state: KafkaState):
        """
        The KafkaState allows changing the State object at runtime.
        """

        print(f"Context: Transition to {type(state).__name__}")
        self._state = state
        self._state.context = self
    
    def handle(self) -> None:
        self._state.next()


class KafkaState(ABC):
     
    @property
    def context(self) -> KafkaContext:
        return self._context
    
    @context.setter
    def context(self, context: KafkaContext) -> None:
        self._context = context
    
    @abstractmethod
    def next(self):
        pass


class KafkaStateA(KafkaState):
    
    def next(self):
        self.context.transition_to(KafkaStateB())
    
class KafkaStateB(KafkaState):
    
    def next(self):
        self.context.transition_to(KafkaStateC())

class KafkaStateC(KafkaState):
    
    def next(self):
        self.context.transition_to(KafkaStateD())

class KafkaStateD(KafkaState):
    
    def next(self):
        print("This is the end of Kafka state.")
        
if __name__ == "__main__":
    
    context = KafkaContext(KafkaStateA())
    context.handle()
    context.handle()
    context.handle()
    context.handle()
