
import json
import os
import requests
import sys
import logging
import time
import yaml
import asyncio
import aiohttp
from dataclasses import dataclass
from typing import re, Awaitable, Any

# Add the parent directory (app) to sys.path
current_directory =  os.path.abspath(os.path.dirname(__file__))
parent_directory = os.path.abspath(os.path.join(current_directory, ".."))
sys.path.insert(0, parent_directory)

from app.core.exceptions.client_exception import ClientException

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('infra')

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
        
def load_config() -> dict[str, dict]:
    # Load YAML data from a file
    with open('infra/kaka_cluster_config.yaml', 'r') as yaml_file:
        yaml_data = yaml_file.read()

    env_data = os.path.expandvars(yaml_data)
    # Parse YAML data
    parsed_yaml = yaml.safe_load(env_data)
    return parsed_yaml['kafka_api']

def validate_cluster(cluster: dict):
    cluster_api_key = cluster['api_key']
    cluster_api_email = cluster['email']
    if cluster_api_key == None or cluster_api_key == "":
        raise ClientException("ApiKey is required to access the kafka api.")
    if cluster_api_email == None or cluster_api_email == "":
        raise ClientException("Email is required to access the kafka api.")

def handle_error(response: requests.Response) -> str:
    if response.status_code == 400:
        return response.content.decode("utf-8")
    elif response.status_code == 401:
        return json.loads(response.content)

def getAuthKey(cluster: dict) -> tuple:
    cluster_api_key = cluster['api_key']
    cluster_api_email = cluster['email']
    return (cluster_api_email, cluster_api_key)

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


async def create_cluster_request(session: aiohttp.ClientSession, 
                                 base_url: str, 
                                 cluster: dict, 
                                 cluster_requests: [Request]):
    username = cluster['email']
    password = cluster['api_key']
    
    try:
        response_data = await get_request(session=session, 
                                               url=f"{base_url}/clusters", 
                                               username=username, 
                                               password=password)
        if response_data is not None and len(response_data) > 0:
            cluster_data = response_data[0]
            cluster_id = cluster_data['cluster_id']
            cluster_name = cluster_data['name']
            logging.info(f"Cluster {cluster_id} already exists with cluster id : {cluster_name}")
            return {
                "cluster_name": cluster_name,
                "cluster_id": cluster_id
            }
        else:
            cluster_requests.append(
                Request(id=cluster['cluster']['name'],
                        method = "post",
                        url = f"{base_url}/cluster", 
                        data = json.dumps(cluster['cluster']),
                        username=username,
                        password=password))
    except aiohttp.ClientError as e:
        logging.error(e)

async def main():
    configs = load_config()
    base_url = configs['uri']
    cluster_endpoint = f"{base_url}/cluster"
    
    cluster_requests: [Request] = []
    topics: [Request] = []
    connectors: [Request] = []
    cluster_info = {}
    
    async with aiohttp.ClientSession() as session:
        try:
            for cluster in configs['clusters']:
                validate_cluster(cluster=cluster)
                
                cluster_map = await create_cluster_request(session=session, 
                                        base_url=base_url,
                                        cluster=cluster,
                                        cluster_requests=cluster_requests)
                if cluster_map is not None:
                    cluster_info[cluster_map['cluster_name']] = cluster_map['cluster_id']
        
            
            if len(cluster_requests) > 0:
                logging.info("Creating clusters started")
                tasks = [post_request(session=session, request=request) for request in cluster_requests]
                results = await asyncio.gather(*tasks)
           
                for request, result in zip(cluster_requests, results):
                    cluster_info[cluster_map[request.id]] = result['cluster_id']
            
                logging.info("Creating clusters completed")
                
            logging.info(cluster_info)
            
        except ClientException as e:
            logging.error(e)
        

if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    end = time.time()
    
    logging.info(f"Total time taken {end-start} seconds.")
