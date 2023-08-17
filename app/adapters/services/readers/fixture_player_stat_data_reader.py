from app.core.model.team import Team
from app.adapters.services.csv_data_service import CsvDataService
from app.core.ports.data_reader_service import DataReader
from app.core.model.fixture_event import FixtureEvent
from app.core.model.fixture_player_stat import FixturePlayerStat
from datetime import datetime
from app.core.tools.utils import current_date_str

class FixturePlayerStatDataReader(DataReader):
    
    def __init__(self, file: str) -> None:
        
        self.file = file
        self.dtype = {
            "league_id": "int32",
            "fixture_id": "int32",
            "updated_at": "int32",
            "player_id": "int32",
            "player_name": "string[pyarrow]",
            "team_id": "int32",
            "team_name": "string[pyarrow]",
            "number": "int32",
            "position": "string[pyarrow]",
            "rating:": "float",
            "minutes_played": "int32",
            "caption": "string[pyarrow]",
            "substitute": "int32",
            "offsides": "int32",
            "shots_total": "int32",
            "shots_on": "int32",
            "goals_total": "int32",
            "goals_conceded": "int32",
            "goals_assists": "int32",
            "goals_saves": "int32",
            "passes_total": "int32",
            "passes_key": "int32",
            "passes_accuracy": "int32",
            "tackles_total": "int32",
            "tackles_blocks": "int32",
            "tackles_interceptions": "int32",
            "duels_total": "int32",
            "duels_won": "int32",
            "dribbles_attempts": "int32",
            "dribbles_success": "int32",
            "dribbles_past": "int32",
            "fouls_drawn": "int32",
            "fouls_committed": "int32",
            "cards_yellow": "int32",
            "cards_red": "int32",
            "penalty_won": "int32",
            "penalty_commited": "int32",
            "penalty_success": "int32",
            "penalty_missed": "int32",
            "penalty_saved": "int32",
        }
        
        self.columns = ["league_id", "fixture_id", "updated_at", "player_id", "player_name", "team_id", "team_name", "number", 
                        "position", "rating", "minutes_played", "caption", "substitute", "offsides", "shots_total", "shots_on", 
                        "goals_total", "goals_conceded", "goals_assists", "goals_saves", "passes_total", "passes_key", "passes_accuracy", 
                        "tackles_total", "tackles_blocks", "tackles_interceptions", "duels_total", "duels_won", 
                        "dribbles_attempts", "dribbles_success", "dribbles_past", "fouls_drawn", "fouls_committed", 
                        "cards_yellow", "cards_red", "penalty_won", "penalty_commited", "penalty_success", "penalty_missed", "penalty_saved"]
    
    def read(self) -> list[FixtureEvent]:
        csv_kwargs = {
        "sep": ",",
        "dtype": self.dtype,
        "usecols": self.columns,
        }
        
        def parse_row(row):
            epoch_timestamp = row['updated_at']
            formatted_date = current_date_str()
            if epoch_timestamp > 0:
                datetime_obj = datetime.fromtimestamp(epoch_timestamp)
                formatted_date = datetime_obj.strftime('%Y-%m-%dT%H:%M:%S+00:00')
            
            fixture_player_stat_data = {
                "league_id": row['league_id'],
                "fixture_id": row['fixture_id'],
                "event_date": formatted_date,
                "player_id": row['player_id'],
                "player_name": row['player_name'],
                "team_id": row['team_id'],
                "team_name": row['team_name'],
                "number": row['number'],
                "position": row['position'],
                "rating": row['rating'],
                "minutes_played": row['minutes_played'],
                "caption": row['caption'],
                "substitute": row['substitute'],
                "offsides": row['offsides'],
                "shots": {
                    "total": row['shots_total'],
                    "on": row["shots_on"],
                },
                "goals": {
                    "total": row['goals_total'],
                    "conceded": row['goals_conceded'],     
                    "assists": row['goals_assists'],
                    "saves": row['goals_saves'],
                },
                "passes": {
                    "total": row['passes_total'],
                    "key": row['passes_key'],
                    "accuracy": row['passes_accuracy'],
                },
                "tackles": {
                    "total": row['tackles_total'],
                    "blocks": row['tackles_blocks'],
                    "interceptions": row['tackles_interceptions']
                },
                "duels": {
                    "total": row['duels_total'],
                    "won": row['duels_won'],
                },
                "dribbles": {
                    "attempts": row['dribbles_attempts'],
                    "success": row['dribbles_success'],
                    "past": row['dribbles_past']
                },
                "fouls": {
                    "drawn": row['fouls_drawn'],
                    "committed": row['fouls_committed'],
                },
                "cards": {
                    "yellow": row['cards_yellow'],
                    "red": row['cards_red'],
                },
                "penalty": {
                    "won": row['penalty_won'],
                    "commited": row['penalty_commited'],
                    "success": row['penalty_success'],
                    "missed": row['penalty_missed'],
                    "saved": row['penalty_saved'],
                },
            }
            
            return FixturePlayerStat(**fixture_player_stat_data)
        
        csv_service = CsvDataService()
        dask_dataframe =  csv_service.read_file(self.file, **csv_kwargs)
        return csv_service.process_dataframe(dask_dataframe, parse_row)
