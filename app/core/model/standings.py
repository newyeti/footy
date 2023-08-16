from pydantic import BaseModel
from app.core.model.common import Team
from datetime import datetime

class Goals(BaseModel):
    goals_for: int
    goals_against: int

class Stat(BaseModel):
    played: int
    win: int
    draw: int
    lose: int
    goals: Goals

class TeamStandings(BaseModel):
    rank: int
    team: Team
    points: int
    goals_diff: int
    group: str
    form: str
    status: str
    description: str
    all: Stat
    home: Stat
    away: Stat

class Standings(BaseModel):
    season: int
    league_id: int
    name: str
    country: str
    logo: str
    flag: str
    standings: TeamStandings
    update: datetime

    