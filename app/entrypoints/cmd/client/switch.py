from app.adapters.services.kafka_service_impl import KafkaProducerSingleton
from app.adapters.services.data_reader_service_impl import TeamDataReader
from app.core.exceptions.client_exception import ClientException

class Switch:
    """Executes the date import service and sends data to kafka topic"""
    
    def __init__(self, kafka_producer: KafkaProducerSingleton) -> None:
        self.kafka_producer = kafka_producer
        self._services = {
            "team": self._team,
            "standings": self._standings,
            "fixture": self._fixture,
            "fixture_events": self._fixture_events,
            "fixture_lineup": self._fixture_lineup,
            "fixture_player_stat": self._fixture_player_stat
        }
        
    def execute(self, service: str, season: int, file: str) -> None:
        if service in self._services:
            print(f"Executing service {service}")
            self._services[service](season=season, file=file)    
        else:
            raise ClientException(f"Invalid service name: {service}")

    def _team(self, season, file):
        team_service = TeamDataReader(file=file)
        teams = team_service.read()
        for team in teams:
            team.season = season
        self.kafka_producer.send("newyeti.telemetry.teams.v1", teams[0])
    
    def _standings(self, season, file):
        pass
    
    def _fixture(self, season, file):
        pass
    
    def _fixture_events(self, season, file):
        pass
    
    def _fixture_lineup(self, season, file):
        pass
    
    def _fixture_player_stat(self, season, file):
        pass
    