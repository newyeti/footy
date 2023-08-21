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

from infra.kafka_cluster_utils import(
    load_config,
    get_request
)

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('infra')

async def main():
    configs = load_config('infra/kaka_cluster_config.yaml')
    base_url = configs['uri']
    get_cluster_tasks = []
    delete_cluster_tasks = []
    
    async with aiohttp.ClientSession() as session:
        clusters = configs['cluster_configs']
        
        for cluster in clusters:
            username = cluster['email']
            password = cluster['api_key']
            get_cluster_tasks.append(
                asyncio.create_task(get_request(session=session, url=f"{base_url}/clusters", username=username, password=password))
            )
        
        results = await asyncio.gather(*get_cluster_tasks)
        
        for cluster, result in zip(clusters, results):
            if len(result) > 0:
                cluster_id = result[0]['cluster_id']
                username = cluster['email']
                password = cluster['api_key']
                delete_cluster_tasks.append(
                    asyncio.create_task(session.delete(url=f"{base_url}/cluster/{cluster_id}",
                                auth=aiohttp.BasicAuth(login=username, password=password, encoding="utf-8"), 
                                ssl=False))
                )
                logging.info(f"Cluster {cluster_id} added for deletion")
        
        logging.info(f"Cluster delete started...")
        await asyncio.gather(*delete_cluster_tasks)
        logging.info(f"Cluster delete completed")

if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    end = time.time()
    
    logging.info(f"Total time taken {end-start} seconds.")