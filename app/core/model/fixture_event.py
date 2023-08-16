from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

# league_id,fixture_id,elapsed,elapsed_plus,team_id,team_name,player_id,player,assist_player_id,assisted_by,type,detail,comments

class FixtureEvent(BaseModel):
    season: int = Field(default=0,title= "Season")
    event_date: str = Field(default=datetime.now(),title= "Season")
    league_id: int
    fixture_id: int
    elapsed: int
    elapsed_plus: Optional[int]
    team_id: int
    team_name: str
    player_id: int
    player_name: str
    assist_player_id: Optional[str]
    assist_player_name: Optional[str]
    event_type: str
    detail: Optional[str]
    comments: Optional[str]


    