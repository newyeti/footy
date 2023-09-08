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

import asyncio
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
        
    async def execute(self, service: str, season: int, loc: str) -> None:
        if service in self._services:
            logger.info(f"Executing service: '{service}'")
            await self._services[service](season=season, loc=loc)    
        else:
            raise ClientException(f"Invalid service name: {service}")

    async def _teams(self, season, loc):
        logger.debug(f"Loading teams - starting")
        file=loc+"/"+self._service_config.teams.filename
        data_reader = TeamDataReader(file=file)
        teams = data_reader.read()
        logger.debug(f"Loading teams - starting")    
        
        count = 0
        for team in teams:
            team.season = season
            data_dict = {
                "topic": self._service_config.teams.topic,
                "message": convert_to_json(team),
            }
            await self._message_service.add_message(messaging_service.MessageEvent(**data_dict))
            count += 1
        
        logger.info(f"Total messages sent to topic {self._service_config.teams.topic}: {count}")
    
    def _find_fixtures(self, season, loc) -> list[Fixture]:
        logger.debug(f"Loading find_fixtures - starting")
        file=loc+"/"+self._service_config.fixtures.filename
        data_reader = FixtureDataReader(file=file)
        fixtures = data_reader.read()
        logger.debug(f"Loading find_fixtures - completed")
        
        for fixture in fixtures:
            fixture.season = season
        return fixtures
    
    async def _fixtures(self, season, loc):
        count = 0
        fixtures = self._find_fixtures(season, loc)
        for fixture in fixtures:
            fixture.season = season
            data_dict = {
                "topic": self._service_config.fixtures.topic,
                "message": convert_to_json(fixture),
            }
            await self._message_service.add_message(messaging_service.MessageEvent(**data_dict))
            count += 1
        
            
        logger.info(f"Total messages sent to topic {self._service_config.fixtures.topic}: {count}")
    
    async def _fixture_events(self, season, loc):
        logger.debug(f"Loading fixtures - starting")
        fixtures = self._find_fixtures(season, loc)
        if len(fixtures) == 0:
            raise ClientException(f"Fixtures are not available. " +
                                  + "Please make sure {self._service_config.fixtures.filename} is available in location {location}")
            
        logger.debug(f"Loading fixtures - completed")
        
        fixture_map = self._fixture_event_date_mapper(fixtures=fixtures)
        file=loc+"/"+self._service_config.fixture_events.filename
        data_reader = FixtureEventDataReader(file=file)
        events = data_reader.read()
        count =0 
        
        for event in events:
            event.season = season
            if event.fixture_id in fixture_map:
                event.event_date = fixture_map[event.fixture_id]
            
            data_dict = {
                "topic": self._service_config.fixture_events.topic,
                "message": convert_to_json(event),
            }
            
            await self._message_service.add_message(messaging_service.MessageEvent(**data_dict))
            count += 1
        
        logger.info(f"Total messages sent to topic {self._service_config.fixture_events.topic}: {count}")
    
    async def _fixture_lineup(self, season, loc):
        logger.debug(f"Loading fixture_lineup - starting")
        fixtures = self._find_fixtures(season, loc)
        if len(fixtures) == 0:
            raise ClientException(f"Fixtures are not available. " +
                                  + "Please make sure {self._service_config.fixtures.filename} is available in location {location}")
            
        logger.debug(f"Loading fixture_lineup  - completed")
        
        fixture_map = self._fixture_event_date_mapper(fixtures=fixtures)
        file=loc+"/"+self._service_config.fixture_lineups.filename
        data_reader = FixtureLineDataReader(file=file)
        lineups = data_reader.read()
        count = 0
        
        for lineup in lineups:
            lineup.season = season
            if lineup.fixture_id in fixture_map:
                lineup.event_date = fixture_map[lineup.fixture_id]
                
            data_dict = {
                "topic": self._service_config.fixture_lineups.topic,
                "message": convert_to_json(lineup),
            }    
                
            await self._message_service.add_message(messaging_service.MessageEvent(**data_dict))
            count += 1
            
        logger.info(f"Total messages sent to topic {self._service_config.fixture_lineups.topic}: {count}")
    
    async def _fixture_player_stats(self, season, loc):
        logger.debug(f"Loading fixture_player_stats - starting")
        file=loc+"/"+self._service_config.fixture_player_stats.filename
        data_reader = FixturePlayerStatDataReader(file=file)
        player_stats = data_reader.read()
        logger.debug(f"Loading fixture_player_stats - completed")
        
        count = 0
        for stat in player_stats:
            stat.season = season
            
            data_dict = {
                "topic": self._service_config.fixture_player_stats.topic,
                "message": convert_to_json(stat),
            }  
            
            await self._message_service.add_message(messaging_service.MessageEvent(**data_dict))
            count += 1
            
        logger.info(f"Total messages sent to topic {self._service_config.fixture_player_stats.topic}: {count}")
        
    async def _top_scorers(self, season, loc):
        logger.debug(f"Loading top_scorers - starting")
        file = loc + "/" + self._service_config.top_scorers.filename
        data_reader = TopScorerDataReader(file=file)
        top_scorers = data_reader.read()
        logger.debug(f"Loading top_scorers - completed")
        
        count = 0
        for ts in top_scorers:
            ts.season = season
            
            data_dict = {
                "topic": self._service_config.top_scorers.topic,
                "message": convert_to_json(ts),
            } 
            
            await self._message_service.add_message(messaging_service.MessageEvent(**data_dict))
            count += 1
       
        logger.info(f"Total messages sent to topic {self._service_config.top_scorers.topic}: {count}")
    
    def _fixture_event_date_mapper(self, fixtures : list[Fixture]) -> dict[Fixture]:
        fixture_event_date_map = {}
        
        for fixture in fixtures:
            if(fixture.fixture_id not in fixture_event_date_map):
                fixture_event_date_map[fixture.fixture_id] = fixture.event_date
            
        return fixture_event_date_map
