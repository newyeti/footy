import sys
import os
import os.path
import argparse

from omegaconf import OmegaConf
from hydra import compose, initialize_config_dir
from pydantic import ValidationError

# Add the parent directory (app) to sys.path
current_directory =  os.path.abspath(os.path.dirname(__file__))
parent_directory = os.path.abspath(os.path.join(current_directory, "../../.."))
sys.path.insert(0, parent_directory)

from app.entrypoints.cmd.config import CliAppConfig
from app.adapters.services import (
    kafka_service_impl, 
    redis_service_impl
)
from app.entrypoints.cmd.client.switch import Switch



def load_config(config_dir: str, config_name: str, version_base = "1.3"):
    # Initialize the config directory for Hydra
    initialize_config_dir(config_dir=config_dir, version_base=version_base)

    # Load the configuration using Hydra
    config = compose(config_name=config_name)

    # Convert the OmegaConf config to a Pydantic model
    try:
        app_config = CliAppConfig(**OmegaConf.to_container(config.app, resolve=True))
    except ValidationError as e:
        print(f"Invalid configuration: {e}")
        return None

    return app_config


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
    
    app_config = load_config(f"{current_directory}/config", "app")
    
    kafka_instances = []
    redis_instances = []

    for stack in app_config.stacks:
        redis_config = stack.redis
        kafka_config = stack.kafka
        
        redis = redis_service_impl.RedisSingleton(redis_config=redis_config)
        kafka = kafka_service_impl.KafkaSingleton(kafka_config=kafka_config, redis=redis)
        
        redis_instances.append(redis)
        kafka_instances.append(kafka)
    
    # switch = Switch(kafka_producer=kafka_producer, service_config=app_config.service)
    # switch.execute(service=service, season=season, loc=location)

if __name__ == "__main__":
    main()
