from typing import Optional
from pydantic import BaseModel, Field

class Team(BaseModel):
    league_id: int = Field(..., title="LeagueId")
    team_id: int= Field(..., title="TeamId")
    name: str = Field(..., title="Name")
    code: str = Field(..., title="Code")
    founded: int = Field(..., title="Founded")
    stadium_name: Optional[str] = Field(title="StadiumName")
    stadium_capacity: Optional[int] = Field(title="StadiumCapacity")
    stadium_surface: Optional[str] = Field(title="StadiumSurface")
    street: str = Field(..., title="Street")
    city: str = Field(..., title="City")
    country: str = Field(..., title="Country")
    is_national: bool = Field(..., title="IsNational")
    season: int = Field(default=0, title="Season")

    