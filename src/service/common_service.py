from abc import ABC, abstractmethod

class Service(ABC):
    @abstractmethod
    def read_file(self, filepath: str) -> list:
        pass
    
    @abstractmethod
    def parse_row(row):
        pass
