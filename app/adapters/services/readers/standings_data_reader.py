from app.core.model.team import Team
from app.adapters.services.csv_data_service import CsvDataService
from app.core.ports.data_reader_service import DataReader
from app.core.model.standings import Standings

# league_id,rank,team_id,team_name,logo,group,status,from,description,all_stat_matchs_played,
# all_stat_win,all_stat_draw,all_stat_lose,all_stat_goals_for,all_stat_goals_against,
# home_stat_matchs_played,home_stat_win,home_stat_draw,home_stat_lose,home_stat_goals_for,
# home_stat_goals_against,away_stat_matchs_played,away_stat_win,away_stat_draw,away_stat_lose,
# away_stat_goals_for,away_stat_goals_against


class StandingsDataReader(DataReader):
    
    def __init__(self, file: str) -> None:
        
        self.file = file
        self.dtype = {
            "league_id": "int32",
            "rank": "int32",
            "team_id": "int32",
            "team_name": "string[pyarrow]",
            "logo": "string[pyarrow]",
            "group": "string[pyarrow]",
            "status": "string[pyarrow]",
            "from": "string[pyarrow]",
            "description": "string[pyarrow]",
            "all_stat_matchs_played": "string[pyarrow]",
            "all_stat_win": "int",
            "all_stat_draw": "string[pyarrow]",
            "all_stat_lose": "string[pyarrow]",
            "all_stat_goals_for": "int32",
            "all_stat_goals_against": "int32",
            "home_stat_matchs_played": "int32",
            "home_stat_win": "int32",
            "home_stat_draw": "int32",
            "home_stat_lose": "int32",
            "home_stat_goals_for": "int32",
            "home_stat_goals_against": "int32",
            "away_stat_matchs_played": "int32",
            "away_stat_win": "int32",
            "away_stat_draw": "int32",
            "away_stat_lose": "int32",
            "away_stat_goals_for": "int32",
            "away_stat_goals_against": "int32",
        }
        self.columns = ["league_id", "rank", "team_id", "team_name", "logo", "group", "status", "from", "description", 
                        "all_stat_matchs_played", "all_stat_win", "all_stat_draw", "all_stat_lose", "all_stat_goals_for", "all_stat_goals_against",
                        "home_stat_matchs_played", "home_stat_win", "home_stat_draw", "home_stat_lose", "home_stat_goals_for", "home_stat_goals_against",
                        "away_stat_matchs_played", "away_stat_win", "away_stat_draw", "away_stat_lose", "away_stat_goals_for", "away_stat_goals_against"]
        
    def read(self) -> list[Team]:
        csv_kwargs = {
        "sep": ",",
        "dtype": self.dtype,
        "usecols": self.columns,
        }
        
        def parse_row(row):
            standings_data = {
                "league_id": row['league_id'],
                "standings": {
                    "rank": row['rank'],
                    "team": {
                        "team_id": row['team_id'],
                        "team_name": row['team_name'],
                        "team_logo": row['team_logo'],
                    },
                    "form": row['group'],
                    "status": row['status'],
                    "description": row['description'],
                    "all": {
                        "played": row['all_stat_matchs_played'],
                        "win": row['all_stat_win'],
                        "draw": row['all_stat_draw'],
                        "lose": row['all_stat_lose'],
                        "goals": {
                            "goals_for": row['all_stat_goals_for'],
                            "goals_against": row['all_stat_goals_against'],
                        },
                    },
                    "home": {
                        "played": row['home_stat_matchs_played'],
                        "win": row['home_stat_win'],
                        "draw": row['home_stat_draw'],
                        "lose": row['home_stat_lose'],
                        "goals": {
                            "goals_for": row['home_stat_goals_for'],
                            "goals_against": row['home_stat_goals_against'],
                        },
                    },
                    "away": {
                        "played": row['away_stat_matchs_played'],
                        "win": row['away_stat_win'],
                        "draw": row['away_stat_draw'],
                        "lose": row['away_stat_lose'],
                        "goals": {
                            "goals_for": row['away_stat_goals_for'],
                            "goals_against": row['away_stat_goals_against'],
                        },
                    }
                }
            }
            return Standings(**standings_data)
        
        csv_service = CsvDataService()
        dask_dataframe =  csv_service.read_file(self.file, **csv_kwargs)
        return csv_service.process_dataframe(dask_dataframe, parse_row)

