from fastapi import FastAPI, Path, status, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import logging
import aiohttp
import asyncio
import os
import sys
from typing import Annotated, Optional, Any
from enum import Enum

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the parent directory (app) to sys.path
current_directory =  os.path.abspath(os.path.dirname(__file__))
logger.debug(current_directory)

parent_directory = os.path.abspath(os.path.join(current_directory, "../../../../.."))
sys.path.insert(0, parent_directory)

logger.debug(parent_directory)

from app.entrypoints.api.rest.datasync.http_helpers import get_request

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


rapid_api_hostname = "api-football-v1.p.rapidapi.com"
rapid_api_key = "U4y3LniAIdmsh1SryySGibO7k8ELp1syFPvjsnpHOQNWAvpJAk"

headers = {
            'X-RapidAPI-Key': rapid_api_key,
            'X-RapidAPI-Host': rapid_api_hostname
        }

app = FastAPI()


@app.exception_handler(ServiceException)
async def service_exception_handler(request: Request, exec: ServiceException):
    return jsonable_encoder(JSONResponse(
        status_code = status.HTTP_400_BAD_REQUEST,
        content = {"service": exec.name, "message": exec.message}
    ))
    

@app.get("/")
async def health():
    return {"status": "ok"}


@app.post("/teams/{season}/{league_id}",
          status_code=status.HTTP_200_OK,
          summary = "Synchornize teams data",
          description = "Retrive teams data from API and updates database",
          tags=[Tags.teams],
          response_model=ServiceResponse)
async def sync_teams(season: Annotated[int, Path(title= "Season", gt=0)], 
                    league_id: Annotated[int, Path(title= "The ID of league to synchornize data", gt=0)]) -> Any:
    
    logger.info(f"calling endpoint=/teams/{season}/{league_id}")
    
    
    url = f"https://{rapid_api_hostname}/v3/teams"
    params = {
        "season": season,
        "league": league_id
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            result = await asyncio.gather(get_request(session=session,
                            url=url, params=params, headers=headers))
            
            logger.info(result[0]) 
            
            api_response = result[0]
            if api_response.status_code == status.HTTP_200_OK:
                response = ServiceResponse(season=season, 
                                       league_id=league_id,
                                       service="teams",
                                       status= ServiceStatus.success)   
                return jsonable_encoder(response)
            else:
                raise ServiceException(name="teams", message = api_response.response_data)
            
        except aiohttp.ClientError as e:
            raise ServiceException(name="teams", message = str(e))
            
    