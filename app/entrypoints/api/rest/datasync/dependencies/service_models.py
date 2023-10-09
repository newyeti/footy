from enum import Enum
from pydantic import BaseModel
from typing import Optional
from multidict import CIMultiDictProxy
from typing import Any

class ServiceStatus(Enum):
    success = "success"
    failed = "failed"

class Tags(Enum):
    teams = "teams"
    standings = "standings"
    
class ServiceResponse(BaseModel):
    season: int
    league_id: int
    service: str
    status: ServiceStatus
    message: Optional[str | None] = None
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "season": 2023,
                    "league_id": 39,
                    "service": "teams",
                    "status": "success",
                    "message": "Data sychnorized successfully."
                }
            ]
        }
    }
    
class ServiceException(Exception):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message

class CommonPathParams:
    def __init__(self, season: int, league_id: int) -> None:
        self.season = season
        self.league_id = league_id
        
class HttpResponse:
    def __init__(self, headers: CIMultiDictProxy[str], status_code: int, response_data: Any) -> None:
        self.headers = headers
        self.status_code = status_code
        self.response_data = response_data
        
    def __str__(self) -> str:
        return f"headers:{self.headers}, status_code: {self.status_code}, data: {self.response_data}"