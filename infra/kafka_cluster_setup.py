
import json
import os
import ssl
import sys
import logging
import time
import asyncio
import aiohttp
from typing import Any

# Add the parent directory (app) to sys.path
current_directory =  os.path.abspath(os.path.dirname(__file__))
parent_directory = os.path.abspath(os.path.join(current_directory, ".."))
sys.path.insert(0, parent_directory)

from app.core.exceptions.client_exception import ClientException
from infra.kafka_cluster_utils import (
    Request,
    load_config,  
    validate_cluster, 
    get_request, 
    post_request
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('infra')
  

async def get_clusters(cluster_configs: dict, session: aiohttp.ClientSession, base_url: str) -> dict[str, str]:
    get_cluster_tasks = []
    available_clusters = {}
    
    for cluster in cluster_configs:
        validate_cluster(cluster=cluster)
        username = cluster['email']
        password = cluster['api_key']
        
        get_cluster_tasks.append(
            asyncio.create_task(session.get(f"{base_url}/clusters", auth=aiohttp.BasicAuth(login=username, password=password, encoding="utf-8"), ssl=False))
        )

    results = await asyncio.gather(*get_cluster_tasks)
    
    for cluster, result in zip(cluster_configs, results):
        cluster_name = cluster['cluster']['name']
        response_data = await result.json()
        cluster_id = ""
        
        if len(response_data) > 0:
            cluster_id = response_data[0]['cluster_id']
        
        available_clusters[cluster_name] = cluster_id
    
    return available_clusters


async def create_cluster_requests(cluster_configs: dict, available_clusters: dict, base_url: str) -> list[Request]:
    cluster_requests: [Request] = []
            
    for cluster in cluster_configs:
        cluster_name = cluster['cluster']['name']
        
        if cluster_name in available_clusters and available_clusters[cluster_name] == "":
            username = cluster['email']
            password = cluster['api_key']
            
            cluster_requests.append(
                Request(id=cluster_name,
                        method = "post",
                        url = f"{base_url}/cluster", 
                        data = json.dumps(cluster['cluster']),
                        username=username,
                        password=password))
    
    return cluster_requests


async def create_topic_requests(cluster_id: str, 
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


async def create_connector_requests(cluster_id: str, 
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


async def process_cluster(cluster_configs: dict, 
                           session: aiohttp.ClientSession,
                           base_url: str) -> dict:
    try:
        logging.info("Creating clusters started")
        current_clusters = await get_clusters(cluster_configs=cluster_configs, session=session, base_url=base_url)
        cluster_requests = await create_cluster_requests(cluster_configs=cluster_configs, available_clusters=current_clusters, base_url= base_url)
            
        if len(cluster_requests) > 0:
            # Asynchronous API requests
            tasks = [post_request(session=session, request=request) for request in cluster_requests]
            results = await asyncio.gather(*tasks)
        
            for cluster_requests , result in zip(cluster_requests, results):
                current_clusters[cluster_requests.id] = result['cluster_id']
                logging.info(f'cluster: {cluster_requests.id}, result: {result}')
        
        logging.info(f"Available clusters: {current_clusters}")
        logging.info("Creating clusters completed")
        return current_clusters
    
    except ClientException as e:
        logging.error(e)
    except aiohttp.ClientError as e:
        logging.error(e)


async def process_cluster_topics(cluster_configs: dict,
                                    topic_configs: dict,
                                    available_clusters: dict,
                                    base_url: str,
                                    session: aiohttp.ClientSession) -> dict: 
    try:
        logging.info("Creating topics started")
        for cluster in cluster_configs:
            valid_topics = [topic for topic in cluster['topics'] if topic in topic_configs ]
            cluster_name = cluster['cluster']['name']
            username = cluster['email']
            password = cluster['api_key']
            
            if cluster_name in available_clusters:
                topic_post_requests = await create_topic_requests(cluster_id=available_clusters[cluster_name],
                                                            topics=valid_topics, 
                                                            topic_configs=topic_configs,
                                                            base_url=base_url,
                                                            username=username,
                                                            password=password)
                tasks = [post_request(session=session, request=request) for request in topic_post_requests]
                results = await asyncio.gather(*tasks)
                
                for topic, result in zip(valid_topics, results):
                    logging.info(f'topic: {topic}, result: {result}')
                    
        logging.info("Creating topics completed")
    except aiohttp.ClientError as e:
        logging.error(e)
    


async def process_cluster_connectors(cluster_configs: dict,
                                        connector_configs: dict,
                                        available_clusters: dict,
                                        base_url: str,
                                        session: aiohttp.ClientSession) -> dict:
    
    try:
        logging.info("Creating connectors started")
        
        for cluster in cluster_configs:
            valid_connectors = [connector for connector in cluster['connectors'] if connector in connector_configs ]
            cluster_name = cluster['cluster']['name']
            username = cluster['email']
            password = cluster['api_key']
            
            if cluster_name in available_clusters:
                connectors_post_requests = await create_connector_requests(cluster_id=available_clusters[cluster_name],
                                                                    connectors=valid_connectors, 
                                                                    connector_configs=connector_configs,
                                                                    base_url=base_url,
                                                                    username=username,
                                                                    password=password)
                tasks = [post_request(session=session, request=request) for request in connectors_post_requests]
                results = await asyncio.gather(*tasks)
                
                for connector, result in zip(valid_connectors, results):
                    logging.info(f'connector: {connector}, result: {result}')
                
        logging.info("Creating connectors completed")
        
    except aiohttp.ClientError as e:
        logging.error(e)


async def main():
    configs = load_config('infra/kaka_cluster_config.yaml')
    base_url = configs['uri']
    
    topic_configs = configs['topic_configs']
    connector_configs = configs['connector_configs']
    
    async with aiohttp.ClientSession() as session:
        available_clusters = await process_cluster(cluster_configs=configs['cluster_configs'], 
                        session=session,
                        base_url=base_url)
 
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
