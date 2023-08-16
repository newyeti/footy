from pydantic import BaseModel, Field
from typing import Optional

class Team(BaseModel):
    team_id: int = Field(..., title="TeamId", description="Team ID")
    team_name: str = Field(..., title="TeamName", description="Team Name")
    team_logo: Optional[str] = Field(..., title="TeamLogo", description="Team Logo")

