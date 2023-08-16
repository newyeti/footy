from pydantic import BaseModel, Field
from typing import Optional

class Games(BaseModel):
    appearences: int = Field(default=0)
    minutes_played: int = Field(default=0)

class Goals(BaseModel):
    total: int = Field(default=0)
    assists: int = Field(default=0)
    conceded: int = Field(default=0)
    saves: int = Field(default=0)
    
class Shots(BaseModel):
    total: int = Field(default=0)
    on: int = Field(default=0)

class Penalty(BaseModel):
    won: int = Field(default=0)
    committed: int = Field(default=0)

class Cards(BaseModel):
    yellow: int = Field(default=0)
    second_yellow: int = Field(default=0)
    red: int = Field(default=0)

class TopScorer(BaseModel):
    season: int = Field(default=0, title="Season")
    league_id: int 
    player_id: int
    player_name: str
    firstname: str
    lastname: str
    position: str
    nationality: str
    team_id: int
    team_name: str
    games: Optional[Games]
    goals: Optional[Goals]
    shots: Optional[Shots]
    penalty: Optional[Penalty]
    cards: Optional[Cards]