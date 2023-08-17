from app.core.tools import utils
from pydantic import BaseModel, Field
from typing import Optional

class FixtureEvent(BaseModel):
    season: int = Field(default=0,title= "Season")
    event_date: str = Field(default=utils.current_date_str(),title= "Season")
    league_id: int
    fixture_id: int
    elapsed: int
    elapsed_plus: Optional[int]
    team_id: int
    team_name: str
    player_id: int
    player_name: str
    assist_player_id: Optional[int]
    assist_player_name: Optional[str]
    event_type: str
    detail: Optional[str]
    comments: Optional[str]


    