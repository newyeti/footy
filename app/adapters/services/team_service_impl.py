from app.core.model.team import Team
from app.adapters.services.csv_data_service import CsvDataService
from app.core.ports.data_service import DataReader

class TeamService(DataReader):
    
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
        
        
    def read_file(self, filepath: str) -> list[Team]:
        csv_kwargs = {
        "sep": ",",
        "dtype": self.dtype,
        "usecols": self.columns,
        }
        
        csv_service = CsvDataService()
        dask_dataframe =  csv_service.read_file(filepath, **csv_kwargs)
        return csv_service.process_dataframe(dask_dataframe, self.parse_row)

    def parse_row(self, row):
        team_data = {
            "league_id" : row['league_id'],
            "team_id": row['team_id'],
            "name":  row['name'],
            "code": row['code'],
            "founded": row['founded'],
            "stadium_name": row['venuename'],
            "stadium_capacity": row['venuecapacity'],
            "stadium_surface": row['venuesurface'],
            "street": row['venueaddress'],
            "city": row['venuecity'],
            "country": row['country'],
            "is_national": row['is_national'],
        }
        
        return Team(**team_data)
