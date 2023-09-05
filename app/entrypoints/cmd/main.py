import sys
import os
import os.path
import argparse

# Add the parent directory (app) to sys.path
current_directory =  os.path.abspath(os.path.dirname(__file__))
parent_directory = os.path.abspath(os.path.join(current_directory, "../../.."))
sys.path.insert(0, parent_directory)

from app.adapters.services import (
    kafka_service_impl, 
    redis_service_impl
)
# from app.entrypoints.cmd.client.switch import Switch
from app.core.tools.hydra import load_app_config
from app.core.tools.linked_list import LinkedList
from app.core.model.domain import MessageHelper

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
    messaga_helper_instances = LinkedList[MessageHelper]()

    for stack in app_config.stacks:
        redis_config = stack.redis
        kafka_config = stack.kafka
        
        redis = redis_service_impl.RedisSingleton(name=redis_config.client_id, redis_config=redis_config)
        kafka = kafka_service_impl.KafkaSingleton(name=kafka_config.client_id, kafka_config=kafka_config)
        messaga_helper_instances.append(MessageHelper(kafka=kafka, redis=redis))
    
    # switch = Switch(kafka_producer=kafka_producer, service_config=app_config.service)
    # switch.execute(service=service, season=season, loc=location)

if __name__ == "__main__":
    main()
