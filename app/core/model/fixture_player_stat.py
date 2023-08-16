from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class ShotStat(BaseModel):
    total: int = Field(default=0)
    on: int = Field(default=0)

class GoalStat(BaseModel):
    total: int = Field(default=0)
    conceded: int = Field(default=0)
    assists: int = Field(default=0)
    saves: int = Field(default=0)

class PassStat(BaseModel):
    total: int = Field(default=0)
    key: int = Field(default=0)
    accuracy: int = Field(default=0)

class TackleStat(BaseModel):
    total: int  = Field(default=0)
    blocks: int = Field(default=0)
    interceptions: int = Field(default=0)

class DuelStat(BaseModel):
    total: int = Field(default=0)
    won: int = Field(default=0)

class DribbleStat(BaseModel):
    attempts: int = Field(default=0)
    success: int = Field(default=0)
    past: int = Field(default=0)

class FoulStat(BaseModel):
    drawn: int = Field(default=0)
    committed: int = Field(default=0)

class CardStat(BaseModel):
    yellow: int = Field(default=0)
    red: int = Field(default=0)

class PenaltyStat(BaseModel):
    won: int = Field(default=0)
    committed: int = Field(default=0)
    success: int = Field(default=0)
    saved: int = Field(default=0)

class FixturePlayerStat(BaseModel):
    season: int = Field(default=0, title="Season")
    league_id: int
    fixture_id: int
    event_date: str
    player_id: int
    player_name: str
    team_id: int
    team_name: str
    number: Optional[int]
    position: str
    rating: Optional[float]
    minutes_played: Optional[int]
    caption: Optional[str]
    substitute: Optional[int]
    offsides: Optional[int]
    shots: Optional[ShotStat]
    goals: Optional[GoalStat]
    passes: Optional[PassStat]
    tackles: Optional[TackleStat]
    duels: Optional[DuelStat]
    dribbles: Optional[DribbleStat]
    fouls: Optional[FoulStat]
    cards: Optional[CardStat]
    penalty: Optional[PenaltyStat]

