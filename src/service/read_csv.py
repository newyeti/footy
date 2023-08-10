import dask.dataframe as dd
import pandas as pd

def process_dask_dataframe(dask_dataframe: dd.DataFrame, parse_row) -> list:
    """
    Process the dask dataframe and create list containing objects

    Args:
        dask_df (dd.DataFrame): A dask dataframe

    Returns:
        list: A list of objects
    """
    
    parsed_objects = []
    
    for _, row in dask_dataframe.iterrows():
        parsed_objects.append(parse_row(row))
    return parsed_objects


def remove_na_from_field(field_value):
    if isinstance(field_value, str):
        return field_value.replace('<NA>', '')
    return field_value

def read_csv_with_dask(file_path: str, **kwargs: dict) -> dd.DataFrame:
    """
    Read a CSV file using Dask and return a Dask DataFrame.

    Parameters:
        file_path (str): Path to the CSV file.
        **kwargs: Additional keyword arguments to pass to Dask's `read_csv` function.

    Returns:
        dask.dataframe.DataFrame: A Dask DataFrame representing the CSV data.
    """
    ddf = dd.read_csv(file_path, **kwargs)
    return ddf

