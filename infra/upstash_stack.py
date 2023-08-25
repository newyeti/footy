from pydantic import BaseModel, Field
from infra.kafka_cluster_utils import Request

class KafkaCluster(BaseModel):
    name: str
    properties: dict
    topics: list[str]
    connectors: list[str]

class Kafka(BaseModel):
    endpoint: str
    cluster: KafkaCluster
 
class RedisDatabase(BaseModel):
    name: str
    properties: dict
    
class Redis(BaseModel):
    endpoint: str
    database: RedisDatabase

class Project(BaseModel):
    name: str
    email: str
    api_key: str
    kafka: Kafka
    redis: Redis
    
class Stack(BaseModel):
    base_url: str
    projects: list[Project]
