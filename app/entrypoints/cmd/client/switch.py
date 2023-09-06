from app.adapters.services import messaging_service
from app.core.exceptions.client_exception import ClientException
from app.entrypoints.cmd.config import ServiceConfig
from app.core.tools.json import convert_to_json
from app.adapters.services.readers.team_data_reader import TeamDataReader
from app.adapters.services.readers.fixture_data_reader import FixtureDataReader
from app.core.model.fixture import Fixture
from app.adapters.services.readers.fixture_lineup_data_reader import FixtureLineDataReader
from app.adapters.services.readers.fixture_player_stat_data_reader import FixturePlayerStatDataReader
from app.adapters.services.readers.fixture_event_data_reader import FixtureEventDataReader
from app.adapters.services.readers.top_scorer_reader import TopScorerDataReader

import logging

logger = logging.getLogger(__name__)

class Switch:
    """Executes the date import service and sends data to kafka topic"""
    
    def __init__(self, message_service: messaging_service.MessageService, service_config: ServiceConfig) -> None:
        self._message_service = message_service
        self._service_config = service_config
        self._services = {
            "teams": self._teams,
            "fixtures": self._fixtures,
            "fixture_events": self._fixture_events,
            "fixture_lineups": self._fixture_lineup,
            "fixture_player_stats": self._fixture_player_stats,
            "top_scorers": self._top_scorers,
        }
        
    def execute(self, service: str, season: int, loc: str) -> None:
        if service in self._services:
            logger.info(f"Executing service: '{service}'")
            self._services[service](season=season, loc=loc)    
        else:
            raise ClientException(f"Invalid service name: {service}")

    def _teams(self, season, loc):
        file=loc+"/"+self._service_config.teams.filename
        data_reader = TeamDataReader(file=file)
        teams = data_reader.read()
        count = 0
        
        try:
            for team in teams:
                team.season = season
                data_dict = {
                    "topic": self._service_config.teams.topic,
                    "message": convert_to_json(team),
                }
                self._message_service.add_message(messaging_service.MessageEvent(**data_dict))
                count += 1
        except ClientException as e:
            logger.error(e)
            
        logger.info(f"Total messages sent to topic {self._service_config.teams.topic}: {count}")
    
    def _find_fixtures(self, season, loc) -> list[Fixture] :
        file=loc+"/"+self._service_config.fixtures.filename
        data_reader = FixtureDataReader(file=file)
        fixtures = data_reader.read()
        for fixture in fixtures:
            fixture.season = season
        return fixtures
    
    def _fixtures(self, season, loc):
        count = 0
        try:
            fixtures = self._find_fixtures(season, loc)
            for fixture in fixtures:
                fixture.season = season
                self._message_service.add_message(messaging_service.MessageEvent(self._service_config.fixtures.topic, 
                                        convert_to_json(fixture)))
                count += 1
        except ClientException as e:
            logger.error(e)
            
        logger.info(f"Total messages sent to topic {self._service_config.fixtures.topic}: {count}")
    
    def _fixture_events(self, season, loc):
        logger.info(f"Loading fixtures - starting")
        fixtures = self._find_fixtures(season, loc)
        if len(fixtures) == 0:
            raise ClientException(f"Fixtures are not available. " +
                                  + "Please make sure {self._service_config.fixtures.filename} is available in location {location}")
            
        logger.info(f"Loading fixtures - completed")
        
        fixture_map = self._fixture_event_date_mapper(fixtures=fixtures)
        file=loc+"/"+self._service_config.fixture_events.filename
        data_reader = FixtureEventDataReader(file=file)
        events = data_reader.read()
        count =0 
        
        try:
            for event in events:
                event.season = season
                if event.fixture_id in fixture_map:
                    event.event_date = fixture_map[event.fixture_id]
                self._message_service.add_message(messaging_service.MessageEven(self._service_config.fixture_events.topic, convert_to_json(event)))
                count += 1
        except ClientException as e:
            logger.error(e)
        
        logger.info(f"Total messages sent to topic {self._service_config.fixture_events.topic}: {count}")
    
    def _fixture_lineup(self, season, loc):
        logger.info(f"Loading fixtures - starting")
        fixtures = self._find_fixtures(season, loc)
        if len(fixtures) == 0:
            raise ClientException(f"Fixtures are not available. " +
                                  + "Please make sure {self._service_config.fixtures.filename} is available in location {location}")
            
        logger.info(f"Loading fixtures - completed")
        
        fixture_map = self._fixture_event_date_mapper(fixtures=fixtures)
        file=loc+"/"+self._service_config.fixture_lineups.filename
        data_reader = FixtureLineDataReader(file=file)
        lineups = data_reader.read()
        count = 0
        
        try:
            for lineup in lineups:
                lineup.season = season
                if lineup.fixture_id in fixture_map:
                    lineup.event_date = fixture_map[lineup.fixture_id]
                self._message_service.add_message(messaging_service.MessageEven(self._service_config.fixture_lineups.topic, convert_to_json(lineup)))
                count += 1
        except ClientException as e:
            logger.error(e)
            
        logger.info(f"Total messages sent to topic {self._service_config.fixture_lineups.topic}: {count}")
    
    def _fixture_player_stats(self, season, loc):
        file=loc+"/"+self._service_config.fixture_player_stats.filename
        data_reader = FixturePlayerStatDataReader(file=file)
        player_stats = data_reader.read()
        count = 0
        try:
            for stat in player_stats:
                stat.season = season
                self._message_service.add_message(messaging_service.MessageEven(self._service_config.fixture_player_stats.topic, convert_to_json(stat)))
                count += 1
        except ClientException as e:
            logger.error(e)
            
        logger.info(f"Total messages sent to topic {self._service_config.fixture_player_stats.topic}: {count}")
        
    def _top_scorers(self, season, loc):
        file = loc + "/" + self._service_config.top_scorers.filename
        data_reader = TopScorerDataReader(file=file)
        top_scorers = data_reader.read()
        count = 0
        try:
            for ts in top_scorers:
                ts.season = season
                self._message_service.add_message(messaging_service.MessageEven(self._service_config.top_scorers.topic, convert_to_json(ts)))
                count += 1
        except ClientException as e:
            logger.error(e)
        
        logger.info(f"Total messages sent to topic {self._service_config.top_scorers.topic}: {count}")
    
    def _fixture_event_date_mapper(self, fixtures : list[Fixture]) -> dict[Fixture]:
        fixture_event_date_map = {}
        
        for fixture in fixtures:
            if(fixture.fixture_id not in fixture_event_date_map):
                fixture_event_date_map[fixture.fixture_id] = fixture.event_date
            
        return fixture_event_date_map
