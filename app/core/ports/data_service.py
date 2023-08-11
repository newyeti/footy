from abc import ABC, abstractmethod
from typing import Any

import dask.dataframe as ddf

class FileReader(ABC):
    
    @abstractmethod
    def read_file(self, file: str, **kwargs: dict) -> ddf.DataFrame:
        ...
    
    @abstractmethod
    def process_dataframe(self, dask_dataframe: ddf.DataFrame, parse_row) -> list[Any]:
        ...


class DataReader(ABC):
    @abstractmethod
    def read_file(self, filepath: str) -> list:
        pass
    
    @abstractmethod
    def parse_row(self, row) -> Any:
        pass
