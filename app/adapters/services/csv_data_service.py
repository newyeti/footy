from app.core.ports import data_service
from typing import Any

import dask.dataframe as ddf

class CsvDataService(data_service.FileReader):
    """Csv data processing service"""
    
    def __init__(self) -> None:
        super().__init__()
    
    def read_file(self, file: str, **kwargs: dict) -> ddf.DataFrame:
        """
        Read a CSV file using Dask and return a Dask DataFrame.
        Parameters:
            file(str): Path to the CSV file.
            **kwargs: Additional keyword arguments to pass to Dask's `read_csv` function
        Returns:
            dask.dataframe.DataFrame: A Dask DataFrame representing the CSV data.
        """
        
        dask_dataframe = ddf.read_csv(file, **kwargs)
        filtered_dff = dask_dataframe.fillna("")
        return filtered_dff
    
    def process_dataframe(self, dask_dataframe: ddf.DataFrame, parse_row) -> list[Any]:
        """
        Process the dask dataframe and create list containing objects
        Args:
            dask_dataframe (dd.DataFrame): A dask dataframe
        Returns:
            list: A list of objects
        """
        
        parsed_objects = []
        
        for _, row in dask_dataframe.iterrows():
            parsed_objects.append(parse_row(row))
        return parsed_objects
