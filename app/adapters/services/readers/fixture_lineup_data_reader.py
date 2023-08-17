from app.adapters.services.csv_data_service import CsvDataService
from app.core.ports.data_reader_service import DataReader
from app.core.model.fixture_lineup import FixtureLineup, Player

class FixtureLineDataReader(DataReader):
    
    def __init__(self, file: str) -> None:
        
        self.file = file
        self.dtype = {
            "league_id": "int32",
            "fixture_id": "int32",
            "coach_id": "int32",
            "coach_name": "string[pyarrow]",
            "formation": "string[pyarrow]",
            "team_id": "int32",
            "startingXI": "string[pyarrow]",
            "substitutes": "string[pyarrow]",
        }
        self.columns = [ "league_id", "fixture_id", "coach_id", "coach_name", "team_id", "formation", "startingXI", "substitutes"]
    
    def read(self) -> list[FixtureLineup]:
        csv_kwargs = {
        "sep": ",",
        "dtype": self.dtype,
        "usecols": self.columns,
        }
        
        def parse_row(row):
            
            def _get_player(player: str) -> Player:
                if player == None or len(player) == 0:
                    return None
                result = player.split("-")
                if result is None or len(result) < 2:
                    return None
                return Player(player_id=result[0], player_name=result[1])
            
            def _get_players(players: str) -> list[Player]:
                parsed_players = []
                
                if players == None or len(players) == 0:
                    return parsed_players

                split_players = players.split("|")
                if split_players is None or len(split_players) == 0:
                    return parsed_players
                
                for player in split_players:
                    if player is not None and len(player) >= 2:
                        parsed_players.append(_get_player(player=player))
                return parsed_players
            
            starting_players = _get_players(row['startingXI'])
            substitute_players = _get_players(row['substitutes'])
            
            fixture_lineup_data = {
                "league_id": row['league_id'],
                "fixture_id": row['fixture_id'],
                "coach_id": row['coach_id'],
                "coach_name": row['coach_name'],
                "formation": row['formation'],
                "team_id": row['team_id'],
                "startingXI": starting_players,
                "substitutes": substitute_players,
            }
            
            return FixtureLineup(**fixture_lineup_data)
        
        csv_service = CsvDataService()
        dask_dataframe =  csv_service.read_file(self.file, **csv_kwargs)
        return csv_service.process_dataframe(dask_dataframe, parse_row)
