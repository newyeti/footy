from app.adapters.services import kafka_service_impl
from app.adapters.services import data_reader_service_impl
from app.core.tools.json import convert_to_json
from typing import Any

producer = kafka_service_impl.KafkaProducerSingleton()

def process_team_data(file: str, season: int):
    team_service = data_reader_service_impl.TeamDataReader(file=file)
    teams = team_service.read()
    for team in teams:
        team.season = season
    print(teams[0])
    send("newyeti.telemetry.teams.v1", teams[0])


def send(topic: str, obj : Any):
    json_data = convert_to_json(obj)
    producer.send(topic=topic, message=json_data)

