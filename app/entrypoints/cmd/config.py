from pydantic import BaseModel
from infra.upstash_stack import Stack

class KafkaConfig(BaseModel):
    bootstrap_servers: list[str]
    client_id: str
    sasl_mechanism: str
    security_protocol: str
    sasl_plain_username: str
    sasl_plain_password: str

class RedisConfig(BaseModel):
    url: str
    token: str
    
class Stack(BaseModel):
    redis: RedisConfig
    kafka: KafkaConfig
    
class ServiceConfigDetail(BaseModel):
    filename: str
    topic: str
    
class ServiceConfig(BaseModel):
    teams: ServiceConfigDetail
    standings: ServiceConfigDetail
    fixtures: ServiceConfigDetail
    fixture_events: ServiceConfigDetail
    fixture_lineups: ServiceConfigDetail
    fixture_player_stats: ServiceConfigDetail
    top_scorers: ServiceConfigDetail
    
class CliAppConfig(BaseModel):
    stacks: list[Stack]
    service: ServiceConfig
