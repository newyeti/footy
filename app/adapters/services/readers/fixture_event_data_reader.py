from app.core.model.team import Team
from app.adapters.services.csv_data_service import CsvDataService
from app.core.ports.data_reader_service import DataReader
from app.core.model.fixture_event import FixtureEvent

class FixtureEventDataReader(DataReader):
    
    def __init__(self, file: str) -> None:
        
        self.file = file
        self.dtype = {
            "league_id": "int32",
            "fixture_id": "int32",
            "elapsed": "int32",
            "elapsed_plus": "int32",
            "team_id": "int32",
            "team_name": "string[pyarrow]",
            "player_id": "int32",
            "player_name": "string[pyarrow]",
            "assist_player_id": "string[pyarrow]",
            "assisted_by": "string[pyarrow]",
            "type": "string[pyarrow]",
            "detail": "string[pyarrow]",
            "comments": "string[pyarrow]",
        }
        
        self.columns = [ "league_id", "fixture_id", "elapsed", "elapsed_plus", "team_id", "team_name", "player_id",
                        "player", "assist_player_id", "assisted_by", "type", "detail", "comments"]
    
    def read(self) -> list[FixtureEvent]:
        csv_kwargs = {
        "sep": ",",
        "dtype": self.dtype,
        "usecols": self.columns,
        }
        
        def parse_row(row):
            fixture_event_data = {
                "league_id": row['league_id'],
                "fixture_id": row['fixture_id'],
                "elapsed": row['elapsed'],
                "elapsed_plus": row['elapsed_plus'],
                "team_id": row['team_id'],
                "team_name": row['team_name'],
                "player_id": row['player_id'],
                "player_name":row['player'],
                "assist_player_id": row['assist_player_id'],
                "assist_player_name": row['assisted_by'],
                "event_type": row['type'],
                "detail": row['detail'],
                "comments":row['comments'],
            }
            
            return FixtureEvent(**fixture_event_data)
        
        csv_service = CsvDataService()
        dask_dataframe =  csv_service.read_file(self.file, **csv_kwargs)
        return csv_service.process_dataframe(dask_dataframe, parse_row)
