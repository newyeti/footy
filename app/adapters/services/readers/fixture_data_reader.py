from app.core.model.team import Team
from app.adapters.services.csv_data_service import CsvDataService
from app.core.ports.data_reader_service import DataReader
from app.core.model.fixture import Fixture
import dask.dataframe as ddf

class FixtureDataReader(DataReader):
    
    def __init__(self, file: str) -> None:
        
        self.file = file
        self.dtype = {
            "league_id": "int32",
            "fixture_id": "int32",
            "league_name": "string[pyarrow]",
            "event_date": "string[pyarrow]",
            "event_timestamp": "string[pyarrow]",
            "first_half_start": "string[pyarrow]",
            "second_half_start": "string[pyarrow]",
            "round": "string[pyarrow]",
            "status_short": "string[pyarrow]",
            "elapsed": "int32",
            "venue": "string[pyarrow]",
            "referee": "string[pyarrow]",
            "home_team_team_id": "int32",
            "home_team_team_name" : "string[pyarrow]",
            "home_team_logo" : "string[pyarrow]",
            "away_team_team_id" : "int32",
            "away_team_team_name" : "string[pyarrow]",
            "away_team_logo" : "string[pyarrow]",
            "goals_home_team" : "int32",
            "goals_away_team" : "int32",
            "score_half_time" : "string[pyarrow]",
            "score_full_time" : "string[pyarrow]",
            "score_extra_time" : "string[pyarrow]",
            "score_penalty" : "string[pyarrow]",
        }
        self.columns = [ "league_id", "fixture_id", "league_name", "event_date", "event_timestamp", 
                        "first_half_start", "second_half_start", "round", "status_short", "elapsed",
                        "venue", "referee", "home_team_team_id", "home_team_team_name", "home_team_logo",
                        "away_team_team_id","away_team_team_name", "away_team_logo", 
                        "goals_home_team", "goals_away_team", 
                        "score_half_time", "score_full_time", "score_extra_time", "score_penalty"
                        ]
    
    def read(self) -> list[Fixture]:
        csv_kwargs = {
        "sep": ",",
        "dtype": self.dtype,
        "usecols": self.columns,
        }
        
        def parse_row(row):
            fixture_data = {
                "league_id" : row['league_id'],
                "fixture_id": row['fixture_id'],
                "league_name":  row['league_name'],
                "event_date": row['event_date'],
                "first_half_start": row['first_half_start'],
                "second_half_start": row['second_half_start'],
                "round": row['round'],
                "status": row['status_short'],
                "elapsed": row['elapsed'],
                "stadium": row['venue'],
                "referee": row['referee'],
                "home_team": {
                    "team_id": row['home_team_team_id'],
                    "team_name": row['home_team_team_name'],
                    "team_logo": row['home_team_logo'],
                },
                "away_team": {
                    "team_id": row['away_team_team_id'],
                    "team_name": row['away_team_team_name'],
                    "team_logo": row['away_team_logo'],
                },
                "goals": {
                    "home_team": row['goals_home_team'],
                    "away_team": row['goals_away_team'],
                },
                "score": {
                    "half_time" : row['score_half_time'],
                    "full_time" : row['score_full_time'],
                    "extra_time" : row['score_extra_time'],
                    "penalty" : row['score_penalty'],
                },
            }
            
            return Fixture(**fixture_data)
        
        csv_service = CsvDataService()
        dask_dataframe =  csv_service.read_file(self.file, **csv_kwargs)
        return csv_service.process_dataframe(dask_dataframe, parse_row)
