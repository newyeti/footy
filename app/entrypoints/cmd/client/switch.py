from app.adapters.services.kafka_service_impl import KafkaProducerSingleton
from app.core.exceptions.client_exception import ClientException
from app.entrypoints.cmd.config import ServiceConfig
from app.core.tools.json import convert_to_json
from app.adapters.services.readers.team_data_reader import TeamDataReader
from app.adapters.services.readers.fixture_data_reader import FixtureDataReader

class Switch:
    """Executes the date import service and sends data to kafka topic"""
    
    def __init__(self, kafka_producer: KafkaProducerSingleton, service_config: ServiceConfig) -> None:
        self.kafka_producer = kafka_producer
        self.service_config = service_config
        self._services = {
            "teams": self._teams,
            "standings": self._standings,
            "fixtures": self._fixtures,
            "fixture_events": self._fixture_events,
            "fixture_lineup": self._fixture_lineup,
            "fixture_player_stat": self._fixture_player_stat
        }
        
    def execute(self, service: str, season: int, file: str) -> None:
        if service in self._services:
            print(f"Executing service: '{service}'")
            self._services[service](season=season, file=file)    
        else:
            raise ClientException(f"Invalid service name: {service}")

    def _teams(self, season, file):
        data_reader = TeamDataReader(file=file)
        teams = data_reader.read()
        for team in teams:
            team.season = season
            self.kafka_producer.send(self.service_config.team.topic, 
                                     convert_to_json(team))
    
    def _fixtures(self, season, file):
        data_reader = FixtureDataReader(file=file)
        fixtures = data_reader.read()
        for fixture in fixtures:
            fixture.season = season
            self.kafka_producer.send(self.service_config.fixtures.topic, 
                                     convert_to_json(fixture))
    
    def _standings(self, season, file):
        pass
    
    def _fixture_events(self, season, file):
        pass
    
    def _fixture_lineup(self, season, file):
        pass
    
    def _fixture_player_stat(self, season, file):
        pass
    