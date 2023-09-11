import aiohttp
import argparse
import asyncio
import base64
import copy
import json
import logging
import os
import sys
import time
from typing import Any

# Add the parent directory (app) to sys.path
current_directory =  os.path.abspath(os.path.dirname(__file__))
parent_directory = os.path.abspath(os.path.join(current_directory, ".."))
sys.path.insert(0, parent_directory)

from infra.helper import (load_config, get_request, post_request, get_auth)
from infra.upstash_stack import (Kafka, Project, Redis, Stack)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('infra')


def process_kafka_cluster(session: aiohttp.ClientSession,
                            base_url: str, 
                            username: str, 
                            password: str, 
                            kafka: Kafka,
                            existing_cluster: dict) -> list:
    cluster_url = f"{base_url}{kafka.endpoint}/cluster"
    kafka_cluster = kafka.cluster
    auth = get_auth(username=username, password=password)
    
    cluster_tasks = []
   
    if existing_cluster[kafka_cluster.name] == '':
        cluster_tasks.append(asyncio.create_task(
            post_request(session=session,
                         url=cluster_url, 
                         auth=auth, 
                         data=json.dumps(kafka_cluster.properties),
                         logging=logging)))
    
    return cluster_tasks
    
    
def process_kafka_topic_and_connector(session: aiohttp.ClientSession,
                            base_url: str, 
                            username: str, 
                            password: str, 
                            kafka: Kafka,
                            existing_cluster: dict,
                            topic_configuration: dict,
                            connector_configuration: dict) -> tuple:
    topic_tasks = []
    connector_tasks = []
    
    kafka_cluster = kafka.cluster
    auth = get_auth(username=username, password=password)
    
    for topic in kafka_cluster.topics:
        topic_properties = topic_configuration[topic]
        topic_properties['cluster_id'] = existing_cluster[kafka_cluster.name]
        payload = json.dumps(topic_configuration[topic])
        
        topic_tasks.append(asyncio.create_task(
            post_request(session=session, 
                         url=f"{base_url}{kafka.endpoint}/topic", 
                         auth=auth, 
                         data=payload,
                         logging=logging)))
    
    for connector in kafka_cluster.connectors:
        connector_config = copy.deepcopy(connector_configuration[connector])
        properties = connector_config['properties']
        connector_config['cluster_id'] = existing_cluster[kafka_cluster.name]
        
        # Decode keyfile 
        if "keyfile" in properties.keys():
            encoded_key_file = properties['keyfile']
            decoded_bytes = base64.b64decode(encoded_key_file)
            decoded_key_file = decoded_bytes.decode('utf-8')
            properties['keyfile'] = decoded_key_file
        
        payload = json.dumps(connector_config)
        connector_tasks.append(asyncio.create_task(
            post_request(session=session, 
                         url=f"{base_url}{kafka.endpoint}/connector", 
                         auth=auth, 
                         data=payload,
                         logging=logging)))
    
    return (topic_tasks, connector_tasks)


def process_redis_database(session: aiohttp.ClientSession, 
                           username: str,
                           password: str,
                           base_url: str, 
                           redis: Redis,
                           existing_database: dict) -> []:
    auth =  get_auth(username=username, password=password)
    url = f"{base_url}{redis.endpoint}/database"
    task = []
    
    if existing_database[redis.database.name] == "":
        task.append(asyncio.create_task(
            post_request(session=session,
                         url=url, 
                         auth=auth, 
                         data=json.dumps(redis.database.properties),
                         logging=logging)))
    return task

     
async def find_existing_stack(session: aiohttp.ClientSession, base_url: str, projects: list[Project]) -> dict:
    get_cluster_tasks = []
    get_database_tasks = []
    available_clusters = {}
    available_databases = {}
    
    for project in projects:
        auth = get_auth(username=project.email, password=project.api_key)
        get_cluster_tasks.append(asyncio.create_task(
            get_request(session=session, url=f"{base_url}{project.kafka.endpoint}/clusters", auth=auth))
        )
        
        get_database_tasks.append(asyncio.create_task(
            get_request(session=session, url=f"{base_url}{project.redis.endpoint}/databases", auth=auth))
        )
        
    cluster_results = await asyncio.gather(*get_cluster_tasks)
    database_results = await asyncio.gather(*get_database_tasks)
    
    logger.info(f"Cluster Response: {cluster_results}")
    logger.info(f"Redis Response: {database_results}")
    
    for project, cluster_result, database_result in zip(projects, cluster_results, database_results):
        cluster_id = ""
        database_id = ""
        
        if len(cluster_result) > 0:
            cluster_id = cluster_result[0]['cluster_id']
        available_clusters[project.kafka.cluster.name] = cluster_id
        
        if len(database_result) > 0:
            database_id = database_result[0]['database_id']
        available_databases[project.redis.database.name] = database_id
    
    return (available_clusters, available_databases)
    
    
async def create_kafka_clusters(tasks: list, availabe_clusters: dict) -> None:
    try:
        logging.info("---------------------------------------")
        logging.info("Creating Kafka Clusters - started")
        cluster_task_results = await asyncio.gather(*tasks)
        
        if len(tasks) == 0:
            logging.info("Kafka clusters are already available.")
        else:
            for result in cluster_task_results:
                logging.info(result)
                cluster_id = result['cluster_id']
                cluster_name = result['name']
                availabe_clusters[cluster_name] = cluster_id
        logging.info("Creating Kafka Clusters - completed")
        logging.info("---------------------------------------")
        
    except aiohttp.ClientError as e:
        logging.error(e)


async def create_kafka_topics(tasks: list):
    try:
        logging.info("---------------------------------------")
        logging.info("Creating Kafka Topics - started")
        
        await asyncio.gather(*tasks)
        
        logging.info("Creating Kafka Topics - completed")
        logging.info("---------------------------------------")
        
    except aiohttp.ClientError as e:
        logging.error(e)
 
    
async def create_kafka_connectors(tasks: list):
    try:
        logging.info("---------------------------------------")
        logging.info("Creating Kafka Connectors - started")
        
        await asyncio.gather(*tasks)
        
        logging.info("Creating Kafka Connectors - completed")
        logging.info("---------------------------------------")
        
    except aiohttp.ClientError as e:
        logging.error(e)


async def create_redis_databases(tasks: list, availabe_databases: dict):
    try:
        logging.info("---------------------------------------")
        logging.info("Creating Redis Database - started")
        
        if len(tasks) == 0:
            logging.info("Redis databases are already available.")
        else:
            database_task_results = await asyncio.gather(*tasks)
            for result in database_task_results:
                response_data = await result.json()
                logging.info(response_data)
                database_id = response_data['database_id']
                database_name = response_data['database_name']
                availabe_databases[database_name] = database_id
        logging.info("Creating Redis Database - completed")
    except aiohttp.ClientError as e:
        logging.error(e)


async def main():
    parsed_yaml = load_config('infra/upstash_stack.yaml')
    configuration = parsed_yaml['stack']
    topic_configuration = configuration['topic_configuration']
    connector_configuration = configuration['connector_configuration'] 
    stack = Stack(**configuration)
    base_url = stack.base_url
    
    # get_kafka_clusters = []
    create_kafka_cluster_tasks = []
    create_kafka_topic_tasks = []
    create_kafka_connector_tasks = []
    create_redis_database_tasks = []
    
    try:
        # Find kafka cluster and redis database in the project
        async with aiohttp.ClientSession() as session:
            current_stack = await find_existing_stack(session=session, 
                                                base_url=base_url, 
                                                projects=stack.projects)
            
            available_clusters = current_stack[0]
            availabe_databases = current_stack[1]

            # Create kafka cluster and redis database
            for project in stack.projects:
                kafka_cluster_tasks = process_kafka_cluster(session=session,
                                                        base_url=base_url, 
                                                        username=project.email,
                                                        password=project.api_key,
                                                        kafka=project.kafka,
                                                        existing_cluster=available_clusters)
                database_tasks = process_redis_database(session=session,
                                                base_url=base_url,
                                                username=project.email,
                                                password=project.api_key,
                                                redis=project.redis,
                                                existing_database=availabe_databases)
            
            create_kafka_cluster_tasks.extend(kafka_cluster_tasks)
            create_redis_database_tasks.extend(database_tasks)
            
            await create_kafka_clusters(tasks=create_kafka_cluster_tasks, availabe_clusters=available_clusters)
            await create_redis_databases(tasks=create_redis_database_tasks, availabe_databases=availabe_databases)
                
            logging.info("---------------------------------------")
            logging.info(f'"clusters":{available_clusters}, "database": {availabe_databases}')
            logging.info("---------------------------------------")
            
            # Create Kafka topic and connectors after kafka cluster has been created
            for project in stack.projects:
                tasks = process_kafka_topic_and_connector(
                    session=session, base_url=base_url, username=project.email, password=project.api_key,
                    kafka= project.kafka, existing_cluster=available_clusters, 
                    topic_configuration=topic_configuration,
                    connector_configuration=connector_configuration
                )
            
                create_kafka_topic_tasks.extend(tasks[0])
                create_kafka_connector_tasks.extend(tasks[1])
            
            await create_kafka_topics(tasks=create_kafka_topic_tasks)
            await create_kafka_connectors(tasks=create_kafka_connector_tasks)
            
            logging.info("Finishing creating stack")    
    except Exception as e:
        logging.error(e)
        
        
if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    end = time.time()
    
    logging.info(f"Total time taken {end-start} seconds.")
