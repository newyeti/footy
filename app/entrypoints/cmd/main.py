import sys
import os
import os.path
import argparse
import logging

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
from app.core.exceptions.client_exception import ClientException
from app.entrypoints.cmd.config import CliAppConfig

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
        return messaging_service.MessageService(message_helpers=messaga_helpers, batch_size=10)
    
def main():
    parser = argparse.ArgumentParser(description="Telemetry")
    parser.add_argument("-service", choices=["teams", "fixtures", "fixture_events", "fixture_lineups", "fixture_player_stats", "top_scorers"], required=True,
                        help="Choose the service from the list: [team, fixture]")
    parser.add_argument("-loc", type=str, required=True, help="Path where files are located")
    parser.add_argument("-season", type=int, required=True, help="Year (4 digits)")

    args = parser.parse_args()
    
    location = args.loc
    season = args.season
    service = args.service
    
    if os.path.isdir(location) == False:
        raise FileNotFoundError(f"File {location} not found.")
    
    app_config = load_app_config(f"{current_directory}/config", "app")
    message_service = get_message_service(app_config=app_config)

    switch = Switch(message_service=message_service, service_config=app_config.service)
    current_time = time.time()
    switch.execute(service=service, season=season, loc=location)    
    end_time = time.time() - current_time
    logger.info(f"Total time taken: {end_time}")

if __name__ == "__main__":
    main()
    
