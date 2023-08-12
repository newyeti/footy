from pydantic import BaseModel

class KafkaConfig(BaseModel):
    bootstrap_servers: list[str]
    client_id: str
    sasl_mechanism: str
    security_protocol: str
    sasl_plain_username: str
    sasl_plain_password: str


class ServiceConfigDetail(BaseModel):
    filename: str
    topic: str
    
class ServiceConfig(BaseModel):
    team: ServiceConfigDetail
    
class CliAppConfig(BaseModel):
    kafka: KafkaConfig
    service: ServiceConfig
