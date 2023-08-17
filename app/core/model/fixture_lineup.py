from pydantic import BaseModel, Field
from app.core.tools import utils
from typing import Optional

class Player(BaseModel):
    player_id : int
    player_name : str

class FixtureLineup(BaseModel):
    season: int = Field(default=0, title="Season")
    league_id : int
    fixture_id: int
    event_date: str = Field(default=utils.current_date_str(),title= "Season")
    coach_id: int
    coach_name: str
    formation: str
    team_id: int
    startingXI: list[Player]
    substitutes: Optional[list[Player]]

