from app.adapters.services.kafka_service_impl import KafkaProducerSingleton
from app.core.exceptions.client_exception import ClientException
from app.entrypoints.cmd.config import ServiceConfig
from app.core.tools.json import convert_to_json
from app.adapters.services.readers.team_data_reader import TeamDataReader
from app.adapters.services.readers.fixture_data_reader import FixtureDataReader
from app.core.model.fixture import Fixture
from app.adapters.services.readers.fixture_lineup_data_reader import FixtureLineDataReader
from app.adapters.services.readers.fixture_player_stat_data_reader import FixturePlayerStatDataReader
from app.adapters.services.readers.fixture_event_data_reader import FixtureEventDataReader

class Switch:
    """Executes the date import service and sends data to kafka topic"""
    
    def __init__(self, kafka_producer: KafkaProducerSingleton, service_config: ServiceConfig) -> None:
        self.kafka_producer = kafka_producer
        self.service_config = service_config
        self._services = {
            "teams": self._teams,
            # "standings": self._standings,
            "fixtures": self._fixtures,
            "fixture_events": self._fixture_events,
            "fixture_lineups": self._fixture_lineup,
            "fixture_player_stats": self._fixture_player_stats
        }
        
    def execute(self, service: str, season: int, loc: str) -> None:
        if service in self._services:
            print(f"Executing service: '{service}'")
            self._services[service](season=season, loc=loc)    
        else:
            raise ClientException(f"Invalid service name: {service}")

    def _teams(self, season, loc):
        file=loc+"/"+self.service_config.teams.filename
        data_reader = TeamDataReader(file=file)
        teams = data_reader.read()
        for team in teams:
            team.season = season
            self.kafka_producer.send(self.service_config.teams.topic, 
                                     convert_to_json(team))
    
    def _find_fixtures(self, season, loc) -> list[Fixture] :
        file=loc+"/"+self.service_config.fixtures.filename
        data_reader = FixtureDataReader(file=file)
        fixtures = data_reader.read()
        for fixture in fixtures:
            fixture.season = season
        return fixtures
    
    def _fixtures(self, season, loc):
        fixtures = self._find_fixtures(self, season, loc)
        for fixture in fixtures:
            fixture.season = season
            self.kafka_producer.send(self.service_config.fixtures.topic, 
                                     convert_to_json(fixture))
    
    def _standings(self, season, file):
        pass
    
    def _fixture_events(self, season, loc):
        print(f"Loading fixtures - starting")
        fixtures = self._find_fixtures(season, loc)
        if len(fixtures) == 0:
            raise ClientException(f"Fixtures are not available. " +
                                  + "Please make sure {self.service_config.fixtures.filename} is available in location {location}")
            
        print(f"Loading fixtures - completed")
        
        fixture_map = self._fixture_event_date_mapper(fixtures=fixtures)
        file=loc+"/"+self.service_config.fixture_events.filename
        data_reader = FixtureEventDataReader(file=file)
        events = data_reader.read()
        for event in events:
            event.season = season
            if event.fixture_id in fixture_map:
                event.event_date = fixture_map[event.fixture_id]
        print(convert_to_json(events))
    
    def _fixture_lineup(self, season, loc):
        print(f"Loading fixtures - starting")
        fixtures = self._find_fixtures(season, loc)
        if len(fixtures) == 0:
            raise ClientException(f"Fixtures are not available. " +
                                  + "Please make sure {self.service_config.fixtures.filename} is available in location {location}")
            
        print(f"Loading fixtures - completed")
        
        fixture_map = self._fixture_event_date_mapper(fixtures=fixtures)
        file=loc+"/"+self.service_config.fixture_lineups.filename
        data_reader = FixtureLineDataReader(file=file)
        lineups = data_reader.read()
        for lineup in lineups:
            lineup.season = season
            if lineup.fixture_id in fixture_map:
                lineup.event_date = fixture_map[lineup.fixture_id]
        print(convert_to_json(lineups[0]))
    
    def _fixture_player_stats(self, season, loc):
        file=loc+"/"+self.service_config.fixture_player_stats.filename
        data_reader = FixturePlayerStatDataReader(file=file)
        player_stats = data_reader.read()
        for stat in player_stats:
            stat.season = season
        print(convert_to_json(player_stats[0]))
    
    def _fixture_event_date_mapper(self, fixtures : list[Fixture]) -> dict[Fixture]:
        fixture_event_date_map = {}
        
        for fixture in fixtures:
            if(fixture.fixture_id not in fixture_event_date_map):
                fixture_event_date_map[fixture.fixture_id] = fixture.event_date
            
        return fixture_event_date_map
