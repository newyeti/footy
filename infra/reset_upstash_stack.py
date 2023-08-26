import aiohttp
import asyncio
import logging
import os
import sys
import time

# Add the parent directory (app) to sys.path
current_directory =  os.path.abspath(os.path.dirname(__file__))
parent_directory = os.path.abspath(os.path.join(current_directory, ".."))
sys.path.insert(0, parent_directory)

from infra.upstash_stack import Stack
from infra.helper import(
    load_config,
    get_request,
    get_auth
)


logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('infra')

async def main():
    parsed_yaml = load_config('infra/upstash_stack.yaml')
    configuration = parsed_yaml['stack']
    stack = Stack(**configuration)
    base_url = stack.base_url
    
    get_cluster_tasks = []
    get_database_tasks = []
    delete_cluster_tasks = []
    delete_redis_database_tasks = []
    
    async with aiohttp.ClientSession() as session:
        
        for project in stack.projects:
            auth = get_auth(username=project.email, password=project.api_key)
            get_cluster_tasks.append(
                asyncio.create_task(get_request(session=session, 
                                                url=f"{base_url}{project.kafka.endpoint}/clusters", 
                                                auth=auth)))
            get_database_tasks.append(
                asyncio.create_task(get_request(
                    session=session, url=f"{base_url}{project.redis.endpoint}/databases",
                    auth=auth
                )))
        
        kafka_cluster_responses = await asyncio.gather(*get_cluster_tasks)
        redis_database_responses = await asyncio.gather(*get_database_tasks)
        
        for project, kafka_response, redis_response in zip(stack.projects, kafka_cluster_responses, redis_database_responses):
            auth = get_auth(username=project.email, password=project.api_key)
            if len(kafka_response) > 0:
                cluster_id = kafka_response[0]['cluster_id']
                delete_cluster_tasks.append(
                asyncio.create_task(session.delete(url=f"{base_url}{project.kafka.endpoint}/cluster/{cluster_id}",
                            auth=auth, ssl=False)))
                logging.info(f"Cluster {cluster_id} added for deletion")
                
            if len(redis_response) > 0:
                database_id = redis_response[0]['database_id']
                delete_redis_database_tasks.append(
                    asyncio.create_task(session.delete(url=f"{base_url}{project.redis.endpoint}/database/{database_id}",
                                auth=auth, ssl=False)))
                logging.info(f"Database {database_id} added for deletion")
        
        logging.info(f"Cluster delete started...")
        
        await asyncio.gather(*delete_cluster_tasks)
        await asyncio.gather(*delete_redis_database_tasks)
        
        logging.info(f"Stack reset completed")

if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    end = time.time()
    
    logging.info(f"Total time taken {end-start} seconds.")