import aiohttp
import asyncio
import logging
import os
from typing import Awaitable, Any
import yaml


async def run_sequence(*functions: Awaitable[Any]) -> None:
    for function in functions:
        await function

async def run_parallel(*functions: Awaitable[Any]) -> None:
    await asyncio.gather(*functions)

def get_auth(username: str, password: str) -> aiohttp.BasicAuth:
    return aiohttp.BasicAuth(login=username, 
                                    password=password, 
                                    encoding="utf-8")
    
def load_config(file: str) -> dict[str, dict]:
    # Load YAML data from a file
    with open(file, 'r') as yaml_file:
        yaml_data = yaml_file.read()

    env_data = os.path.expandvars(yaml_data)
    
    # Parse YAML data
    return yaml.safe_load(env_data)

async def get_request(session: aiohttp.ClientSession, url: str, auth: aiohttp.BasicAuth) -> Any:
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
    
async def post_request(session: aiohttp.ClientSession, 
                       url: str, 
                       auth: aiohttp.BasicAuth, 
                       data: dict,
                       logging: logging):
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        async with session.post(url=url,
                                data=data,
                                headers=headers,
                                auth=auth, 
                                ssl=False) as response:
            response_content_type = response.content_type
            
            if 'json' in response_content_type:
                response_data = await response.json()
            else:
                response_data = await response.text()
            logging.info(f"status={response.status}, message={response_data}")
            return response_data
        
    except aiohttp.ClientError as e:
        return {"error": f"Error posting data to {url}: {e}"}
