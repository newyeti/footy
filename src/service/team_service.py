from model.team import Team
import service.read_csv as csv_service

dtype = {
    "league_id": "int32",
    "team_id": "int32",
    "name": "string[pyarrow]",
    "code": "string[pyarrow]",
    "country": "string[pyarrow]",
    "is_national": "bool",
    "founded": "int32",
    "venuename": "string[pyarrow]",
    "venuesurface": "string[pyarrow]",
    "venueaddress": "string[pyarrow]",
    "venuecity": "string[pyarrow]",
    "venuecapacity": "int32",
}

# Use column definition
rows = ["league_id", "team_id", "name", "country", "is_national", "founded", 
        "venuename", "venuesurface", "venuecity", "venuecapacity"]

def parse_rows(row):
    """
    Parse the row and create Team object

    Args:
        row (pandas.core.series.Series): Row from a csv file

    Returns:
       Team : A team object
    """
    return Team(row['league_id'], row['team_id'], row['name'])

def read_csv(filepath: str) -> list[Team]:
    csv_kwargs = {
        "sep": ",",
        "dtype": dtype,
        "usecols": rows,
    }
    dask_dataframe =  csv_service.read_csv_with_dask(filepath, **csv_kwargs)
    return csv_service.process_dask_dataframe(dask_dataframe, parse_rows)
