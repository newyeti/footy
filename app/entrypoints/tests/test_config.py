
import os.path
import pytest
import os
import sys
import logging

# Add the parent directory (app) to sys.path
current_directory =  os.path.abspath(os.path.dirname(__file__))
parent_directory = os.path.abspath(os.path.join(current_directory, "../../.."))
config_directory = os.path.abspath(os.path.join(current_directory, "../cmd/config"))
sys.path.insert(0, parent_directory)

from app.core.tools import hydra
from app.adapters.services import kafka_service, redis_service

def load_config():
    return hydra.load_app_config(f"{config_directory}", "app")

def test_singleton_objects():
    app_config = load_config()
    kafka_instances = set()
    redis_instances = set()

    for stack in app_config.stacks:
        kafka_config = stack.kafka
        redis_config = stack.redis
        kafka = kafka_service.KafkaSingleton(name=kafka_config.client_id,kafka_config=kafka_config)
        redis = redis_service.RedisSingleton(name=redis_config.client_id, redis_config=redis_config)
        kafka_instances.add(kafka)
        redis_instances.add(redis)
    
    assert len(kafka_instances) == len(app_config.stacks)
    assert len(redis_instances) == len(app_config.stacks)
