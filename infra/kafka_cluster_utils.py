import aiohttp
import asyncio
import os
from typing import Awaitable, Any
import yaml
from app.core.exceptions.client_exception import ClientException
from dataclasses import dataclass

@dataclass
class Request:
    id: str
    method: str
    url: str
    data: str
    username: str
    password: str

async def run_sequence(*functions: Awaitable[Any]) -> None:
    for function in functions:
        await function

async def run_parallel(*functions: Awaitable[Any]) -> None:
    await asyncio.gather(*functions)

def load_config(file: str) -> dict[str, dict]:
    # Load YAML data from a file
    with open(file, 'r') as yaml_file:
        yaml_data = yaml_file.read()

    env_data = os.path.expandvars(yaml_data)
    
    # Parse YAML data
    return yaml.safe_load(env_data)

def validate_cluster(cluster: dict):
    cluster_api_key = cluster['api_key']
    cluster_api_email = cluster['email']
    if cluster_api_key == None or cluster_api_key == "":
        raise ClientException("ApiKey is required to access the kafka api.")
    if cluster_api_email == None or cluster_api_email == "":
        raise ClientException("Email is required to access the kafka api.")
    
async def get_request(session: aiohttp.ClientSession, url: str, username: str, password: str) -> Any:
    auth = aiohttp.BasicAuth(login=username, password=password, encoding="utf-8")
    
    try:
        async with session.get(url=url, auth=auth, ssl=False) as response:
            response_content_type = response.headers.get('Content-Type')
            if 'json' in response_content_type:
                response_data = await response.json()
            else:
                response_data = await response.text()
            return response_data
    except aiohttp.ClientError as e:
        return {"error": f"Error getting data from {url}: {e}"}
    
async def post_request(session: aiohttp.ClientSession, request: Request):
    headers = {
        'Content-Type': 'application/json'
    }
    
    auth = aiohttp.BasicAuth(login=request.username, password=request.password, encoding="utf-8")
    
    try:
        async with session.post(url=request.url,
                                data=request.data,
                                headers=headers,
                                auth=auth, 
                                ssl=False) as response:
            response_content_type = response.content_type
            
            if 'json' in response_content_type:
                response_data = await response.json()
            else:
                response_data = await response.text()
                
            return response_data
        
    except aiohttp.ClientError as e:
        return {"error": f"Error posting data to {request.base_url}: {e}"}
