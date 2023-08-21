
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
from infra.setup_kafka_cluster import kafka_connector_configs

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


async def create_clusters(session: aiohttp.ClientSession, 
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

async def create_topics(cluster_id: str, 
                        topics: list[str], 
                        topic_configs: dict, 
                        base_url: str,
                        username: str,
                        password: str) -> list[Request] : 
    topic_post_requests: list[Request] = []
    
    for topic in topics:
        data = topic_configs[topic]
        data['cluster_id'] = cluster_id
        request_data = json.dumps(data)
    
        topic_post_requests.append(Request(
            id=topic,
            url=f"{base_url}/topic", 
            method="post",
            data=request_data,
            username=username,
            password=password
        ))
    return topic_post_requests

async def process_clusters(cluster_configs: dict, 
                           session: aiohttp.ClientSession,
                           base_url: str) -> dict:
    cluster_requests: [Request] = []
    cluster_info = {}
    try:
        for cluster in cluster_configs:
            validate_cluster(cluster=cluster)
            
            cluster_map = await create_clusters(session=session, 
                                    base_url=base_url,
                                    cluster=cluster,
                                    cluster_requests=cluster_requests)
            if cluster_map is not None:
                cluster_info[cluster_map['cluster_name']] = cluster_map['cluster_id']

        if len(cluster_requests) > 0:
            logging.info("Creating clusters started")
            
            # Asynchronous API requests
            tasks = [post_request(session=session, request=request) for request in cluster_requests]
            results = await asyncio.gather(*tasks)
        
            for request, result in zip(cluster_requests, results):
                cluster_info[request.id] = result['cluster_id']
        
            logging.info("Creating clusters completed")
            
    except ClientException as e:
            logging.error(e)

    return cluster_info

async def create_connectors(cluster_id: str, 
                        connectors: list[str], 
                        connector_configs: dict, 
                        base_url: str,
                        username: str,
                        password: str) -> list[Request] : 
    connector_post_requests: list[Request] = []
    
    for connector in connectors:
        data = connector_configs[connector]
        data['cluster_id'] = cluster_id
        request_data = json.dumps(data)
    
        connector_post_requests.append(Request(
            id=connector,
            url=f"{base_url}/connector", 
            method="post",
            data=request_data,
            username=username,
            password=password
        ))
        
    return connector_post_requests

async def process_cluster_topics(cluster_configs: dict,
                                 topic_configs: dict,
                                 available_clusters: dict,
                                 base_url: str,
                                 session: aiohttp.ClientSession) -> dict:
    
    for cluster in cluster_configs:
        valid_topics = [topic for topic in cluster['topics'] if topic in topic_configs ]
        cluster_name = cluster['cluster']['name']
        username = cluster['email']
        password = cluster['api_key']
        
        if cluster_name in available_clusters:
            topic_post_requests = await create_topics(cluster_id=available_clusters[cluster_name],
                                                topics=valid_topics, 
                                                topic_configs=topic_configs,
                                                base_url=base_url,
                                                username=username,
                                                password=password)
            tasks = [post_request(session=session, request=request) for request in topic_post_requests]
            results = await asyncio.gather(*tasks)
            
            for topic, result in zip(valid_topics, results):
                logging.info(f'topic: {topic}, result: {result}')

async def process_cluster_connectors(cluster_configs: dict,
                                        connector_configs: dict,
                                        available_clusters: dict,
                                        base_url: str,
                                        session: aiohttp.ClientSession) -> dict:
    
    for cluster in cluster_configs:
        valid_connectors = [connector for connector in cluster['connectors'] if connector in connector_configs ]
        cluster_name = cluster['cluster']['name']
        username = cluster['email']
        password = cluster['api_key']
        
        if cluster_name in available_clusters:
            connectors_post_requests = await create_connectors(cluster_id=available_clusters[cluster_name],
                                                                connectors=valid_connectors, 
                                                                connector_configs=connector_configs,
                                                                base_url=base_url,
                                                                username=username,
                                                                password=password)
            tasks = [post_request(session=session, request=request) for request in connectors_post_requests]
            results = await asyncio.gather(*tasks)
            
            for connector, result in zip(valid_connectors, results):
                logging.info(f'connector: {connector}, result: {result}')
        
async def main():
    configs = load_config()
    base_url = configs['uri']
    
    topic_configs = configs['topic_configs']
    connector_configs = configs['connector_configs']
    
    async with aiohttp.ClientSession() as session:
        available_clusters = await process_clusters(cluster_configs=configs['cluster_configs'], 
                        session=session,
                        base_url=base_url)
        logging.info(f"Available clusters: {available_clusters}")
        
        await process_cluster_topics(cluster_configs=configs['cluster_configs'],
                                     topic_configs=topic_configs,
                                     available_clusters=available_clusters,
                                     base_url=base_url,
                                     session=session)

        await process_cluster_connectors(cluster_configs=configs['cluster_configs'],
                                            connector_configs=connector_configs,
                                            available_clusters=available_clusters,
                                            base_url=base_url,
                                            session=session)

if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    end = time.time()
    
    logging.info(f"Total time taken {end-start} seconds.")
