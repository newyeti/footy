from app.core.model.team import Team
from app.adapters.services.csv_data_service import CsvDataService
from app.core.ports.data_reader_service import DataReader
from app.core.model.top_scorers import TopScorer

class TopScorerDataReader(DataReader):
    
    def __init__(self, file: str) -> None:
        
        self.file = file
        self.dtype = {
            "leagueid": "int32",
            "playerid": "int32",
            "playername": "string[pyarrow]",
            "firstname": "string[pyarrow]",
            "lastname": "string[pyarrow]",
            "position": "string[pyarrow]",
            "nationality": "string[pyarrow]",
            "teamid": "int",
            "teamname": "string[pyarrow]",
            "games.appearences": "int32",
            "games.minutesplayed": "int32",
            "goals.total": "int32",
            "goals.assists": "int32",
            "goals.conceded": "int32",
            "goals.saves": "int32",
            "shots.total": "int32",
            "shots.on": "int32",
            "penalty.won": "int32",
            "penalty.commited": "int32",
            "cards.yellow": "int32",
            "cards.secondyellow": "int32",
            "cards.red": "int32",
        }
        self.columns = ["leagueid", "playerid", "playername", "firstname", "lastname", "position", 
                        "nationality", "teamid", "teamname", "games.appearences", "games.minutesplayed", 
                        "goals.total", "goals.assists", "goals.conceded", "goals.saves", "shots.total", 
                        "shots.on", "penalty.won", "penalty.commited", "cards.yellow", "cards.secondyellow", 
                        "cards.red"]
        
    def read(self) -> list[Team]:
        csv_kwargs = {
        "sep": ",",
        "dtype": self.dtype,
        "usecols": self.columns,
        }
        
        def parse_row(row):
            top_scorer_data = {
                "league_id": row['leagueid'],
                "player_id": row['playerid'],
                "player_name": row['playername'],
                "firstname": row['firstname'],
                "lastname": row['lastname'],
                "position": row['position'],
                "nationality": row['nationality'],
                "team_id": row['teamid'],
                "team_name": row['teamname'],
                "games": {
                    "appearences": row['games.appearences'],
                    "minutesplayed": row['games.minutesplayed'],
                },
                "goals": {
                    "total": row['goals.total'],
                    "assists": row['goals.assists'],
                    "conceded": row['goals.conceded'],
                    "saves": row['goals.saves'],
                },
                "shots": {
                    "total": row['shots.total'],
                    "on": row['shots.on'],
                },
                "penalty": {
                    "won": row["penalty.won"],
                    "commited": row["penalty.commited"],
                },
                "cards": {
                    "yellow": row['cards.yellow'],
                    "secondyellow": row['cards.secondyellow'],
                    "red": row['cards.red'],
                },
            }
            return TopScorer(**top_scorer_data)
        
        csv_service = CsvDataService()
        dask_dataframe =  csv_service.read_file(self.file, **csv_kwargs)
        return csv_service.process_dataframe(dask_dataframe, parse_row)

