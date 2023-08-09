from model.team import Team
import service.read_csv as csv_service
from service.common_service import Service

class TeamService(Service):
    
    def __init__(self) -> None:
        self.dtype = {
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
    
        self.columns = ["league_id", "team_id", "name", "code", "country", "is_national", "founded", 
                    "venuename", "venuesurface", "venueaddress", "venuecity", "venuecapacity"]
       
    def read_file(self, filepath: str) -> list:
        csv_kwargs = {
        "sep": ",",
        "dtype": self.dtype,
        "usecols": self.columns,
        }
        
        dask_dataframe =  csv_service.read_csv_with_dask(filepath, **csv_kwargs)
        return csv_service.process_dask_dataframe(dask_dataframe, self.parse_row)

    @staticmethod
    def parse_row(row):
        return Team(row['league_id'], 
                    row['team_id'], 
                    row['name'],
                    row['code'],
                    row['founded'],
                    row['venuename'],
                    row['venuecapacity'],
                    row['venuesurface'],
                    row['venueaddress'],
                    row['venuecity'],
                    row['country'],
                    row['is_national']
                    )
