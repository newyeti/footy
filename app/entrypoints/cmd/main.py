import asyncio
import sys
import os
import os.path
import argparse
import logging
from datetime import timedelta

# Add the parent directory (app) to sys.path
current_directory =  os.path.abspath(os.path.dirname(__file__))
parent_directory = os.path.abspath(os.path.join(current_directory, "../../.."))
sys.path.insert(0, parent_directory)

from app.adapters.services import (
    kafka_service, 
    redis_service,
    messaging_service
)

from app.core.tools.hydra import load_app_config
from app.core.tools.linked_list import LinkedList
from app.entrypoints.cmd.client.switch import Switch
import time
from app.entrypoints.cmd.config import CliAppConfig
from app.entrypoints.tests.test_config import config_directory
from app.core.exceptions.client_exception import ClientException

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_message_service(app_config: CliAppConfig) -> messaging_service.MessageService:
    messaga_helpers = LinkedList[messaging_service.MessageHelper]()
    
    for stack in app_config.stacks:
        redis_config = stack.redis
        kafka_config = stack.kafka
        
        redis = redis_service.RedisSingleton(name=redis_config.client_id, redis_config=redis_config)
        kafka = kafka_service.KafkaSingleton(name=kafka_config.client_id, kafka_config=kafka_config)
        data_dict = {
            "kafka": kafka,
            "redis": redis,
        }
        message_helper = messaging_service.MessageHelper(**data_dict)
        messaga_helpers.append(message_helper)
    return messaging_service.MessageService(message_helpers=messaga_helpers, 
                                            batch_size=app_config.message.batch_size,
                                            kafka_daily_limit=app_config.message.kafka_daily_limit,
                                            redis_daily_limit=app_config.message.redis_daily_limit)


async def run(app_config: CliAppConfig, services: list[str], service: str, season: int, location: str):
    """Runs the import task asynchronously"""
    
    redis_control = redis_service.RedisSingleton(
        name=app_config.control.redis.client_id,
        redis_config=app_config.control.redis)
    message_service = get_message_service(app_config=app_config)
    switch = Switch(message_service=message_service, service_config=app_config.service, db=redis_control)
    
    tasks = []
    if service not in services:
        for serv in services:
            tasks.append(asyncio.create_task(switch.execute(serv, season, location)))
    else:
        tasks.append(asyncio.create_task(switch.execute(service, season, location))) 

    try:
        # Run asynchronous tasks
        await asyncio.gather(*tasks)
        
        #Flush remaining messages
        await message_service.flush(message_service.messages)
    except ClientException as e:
        logger.error(e)
    finally:
        report = message_service.get_report()
        
        # store sent message count in redis database
        for key, value in report.items():
            redis_key = redis_control.get_key(prefix=str(season), key=key, suffix=None)
            redis_control.set(key=redis_key, value=value, expiry=timedelta(days=app_config.message.key_expiry_in_days))
    
    return report
    

async def main():
    parser = argparse.ArgumentParser(description="Telemetry")
    services = ["teams", "fixtures", "fixture_events", "fixture_lineups", "fixture_player_stats", "top_scorers"]
    parser.add_argument("-service", choices=["all"] + services, required=True,
                        help="Choose the service from the list: [team, fixture]")
    parser.add_argument("-loc", type=str, required=True, help="Path where files are located")
    parser.add_argument("-season", type=int, required=True, help="Year (4 digits)")

    args = parser.parse_args()
    
    location = args.loc
    season = args.season
    service = args.service
    
    if os.path.isdir(location) == False:
        raise FileNotFoundError(f"File {location} not found.")
    
    config_directory = f"{current_directory}/config"
    app_config = load_app_config(config_directory, "app")
    
    report = await run(app_config=app_config, 
              services=services, 
              service=service, 
              season=season, 
              location=location)
    
    logger.info(f"Message report: {report}")
    
    
if __name__ == "__main__":
    current_time = time.time()
    asyncio.run(main())
    end_time = time.time() - current_time
    logger.info(f"Total time taken: {end_time}")
    
