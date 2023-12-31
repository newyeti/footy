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
from app.adapters.services.redis_service import RedisSingleton

import asyncio
import logging

logger = logging.getLogger(__name__)
LEAGUE_ID_CONVERSION_HASH_NAME = "LEAGUE_ID_CONVERSION_HASH"

class Switch:
    """Executes the date import service and sends data to kafka topic"""
    
    def __init__(self, message_service: messaging_service.MessageService, 
                 service_config: ServiceConfig,
                 db: RedisSingleton) -> None:
        self._message_service = message_service
        self._service_config = service_config
        self._db = db
        self._services = {
            "teams": self._teams,
            "fixtures": self._fixtures,
            "fixture_events": self._fixture_events,
            "fixture_lineups": self._fixture_lineup,
            "fixture_player_stats": self._fixture_player_stats,
            "top_scorers": self._top_scorers,
        }
        hash_data = db.redis_client.hgetall(name=LEAGUE_ID_CONVERSION_HASH_NAME)
        self._league_id_conversion = {}
        for field, value in hash_data.items():
            key = int(field.decode('utf-8'))
            val = int(value.decode('utf-8'))
            self._league_id_conversion[key] = val
        logger.info(f"League ID conversion hash: {self._league_id_conversion}")
            

    async def execute(self, service: str, season: int, loc: str) -> None:
        if service in self._services:
            logger.info(f"Executing service: '{service}'")
            await self._services[service](season=season, loc=loc)    
        else:
            raise ClientException(f"Invalid service name: {service}")

    async def _teams(self, season, loc):
        logger.debug(f"Loading teams - starting")
        file=loc+"/"+self._service_config.teams.filename
        topic = self._service_config.teams.topic
        data_reader = TeamDataReader(file=file)
        
        try:
            teams = data_reader.read()
        except (ValueError, FileNotFoundError) as e:
            logger.error(f"Unable to read file {file} because {e}")
            return
        
        message_sent = self._message_sent_already(season=season, key=topic)
        if message_sent > len(teams):
            logger.info(f"All messages already sent to topic {topic} for season {season}")
            logger.debug("Skipping sending repeated messages")
            return
        
        logger.debug(f"Loading teams - starting")    
        
        count = 0
        for index in range(message_sent, len(teams)):
            if 0 <= index < len(teams):
                team = teams[index]
                team.season = season
                team.league_id = self._get_league_id(team.league_id)
                data_dict = {
                    "topic": topic,
                    "message": convert_to_json(team),
                }
                await self._message_service.add_message(messaging_service.MessageEvent(**data_dict))
                count += 1
        
        logger.info(f"Total messages sent to topic {topic}: {count}")
    
    def _find_fixtures(self, season, loc) -> list[Fixture]:
        logger.debug(f"Loading find_fixtures - starting")
        file=loc+"/"+self._service_config.fixtures.filename
        data_reader = FixtureDataReader(file=file)
        try:
            fixtures = data_reader.read()
        except (ValueError, FileNotFoundError) as e:
            logger.error(f"Unable to read file {file} because {e}")
            return []
    
        logger.debug(f"Loading find_fixtures - completed")
        
        for fixture in fixtures:
            fixture.season = season
        return fixtures
    
    
    async def _fixtures(self, season, loc):
        count = 0
        fixtures = self._find_fixtures(season, loc)
        topic = self._service_config.fixtures.topic
        message_sent = self._message_sent_already(season=season, 
                                                    key=topic)
        if message_sent > len(fixtures):
            logger.info(f"All messages already sent to topic {topic} for season {season}")
            logger.debug("Skipping sending repeated messages")
            return
        
        for index in range(message_sent, len(fixtures)):
            if 0 <= index < len(fixtures):
                fixture = fixtures[index]
                fixture.season = season
                fixture.league_id = self._get_league_id(fixture.league_id)
                data_dict = {
                    "topic": topic,
                    "message": convert_to_json(fixture),
                }
                await self._message_service.add_message(messaging_service.MessageEvent(**data_dict))
                count += 1
    
        logger.info(f"Total messages sent to topic {topic}: {count}")
    
    
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
        try:
            events = data_reader.read()
        except (ValueError, FileNotFoundError) as e:
            logger.error(f"Unable to read file {file} because {e}")
            return
    
        topic = self._service_config.fixture_events.topic
        message_sent = self._message_sent_already(season=season, 
                                                    key=topic)
        if message_sent > len(events):
            logger.info(f"All messages already sent to topic {topic} for season {season}")
            logger.debug("Skipping sending repeated messages")
            return
        
        count =0
        for index in range(message_sent, len(events)):
            if 0 <= index < len(events):
                event = events[index]
                event.season = season
                event.league_id = self._get_league_id(event.league_id)
                if event.fixture_id in fixture_map:
                    event.event_date = fixture_map[event.fixture_id]
                
                data_dict = {
                    "topic": topic,
                    "message": convert_to_json(event),
                }
                
                await self._message_service.add_message(messaging_service.MessageEvent(**data_dict))
                count += 1
                
        logger.info(f"Total messages sent to topic {topic}: {count}")
    
    async def _fixture_lineup(self, season, loc):
        logger.debug(f"Loading fixture_lineup - starting")
        fixtures = self._find_fixtures(season, loc)
        if len(fixtures) == 0:
            raise ClientException(f"Fixtures are not available. " +
                                  + "Please make sure {self._service_config.fixtures.filename} is available in location {location}")
            
        logger.debug(f"Loading fixture_lineup  - completed")
        
        fixture_map = self._fixture_event_date_mapper(fixtures=fixtures)
        file=loc+"/"+self._service_config.fixture_lineups.filename
        topic = self._service_config.fixture_lineups.topic
        data_reader = FixtureLineDataReader(file=file)
        
        try:
            lineups = data_reader.read()
        except (ValueError, FileNotFoundError) as e:
            logger.error(f"Unable to read file {file} because {e}")
            return
         
        message_sent = self._message_sent_already(season=season, 
                                                    key=topic)
        if message_sent > len(lineups):
            logger.info(f"All messages already sent to topic {topic} for season {season}")
            logger.debug("Skipping sending repeated messages")
            return
        
        count = 0
        for index in range(message_sent, len(lineups)):
            if 0 <= index < len(lineups):
                lineup = lineups[index]
                lineup.season = season
                lineup.league_id = self._get_league_id(lineup.league_id)
                if lineup.fixture_id in fixture_map:
                    lineup.event_date = fixture_map[lineup.fixture_id]
                    
                data_dict = {
                    "topic": topic,
                    "message": convert_to_json(lineup),
                }    
                    
                await self._message_service.add_message(messaging_service.MessageEvent(**data_dict))
                count += 1
            
        logger.info(f"Total messages sent to topic {topic}: {count}")
    
    
    async def _fixture_player_stats(self, season, loc):
        logger.debug(f"Loading fixture_player_stats - starting")
        file=loc+"/"+self._service_config.fixture_player_stats.filename
        topic = self._service_config.fixture_player_stats.topic
        data_reader = FixturePlayerStatDataReader(file=file)
        
        try:
            player_stats = data_reader.read()
        except (ValueError, FileNotFoundError) as e:
            logger.error(f"Unable to read file {file} because {e}")
            return
        
        logger.debug(f"Loading fixture_player_stats - completed")
        
        message_sent = self._message_sent_already(season=season, 
                                                    key=topic)
        if message_sent > len(player_stats):
            logger.info(f"All messages already sent to topic {topic} for season {season}")
            logger.debug("Skipping sending repeated messages")
            return
        
        count = 0
        for index in range(message_sent, len(player_stats)):
            if 0 <= index < len(player_stats):
                stat = player_stats[index]
                stat.season = season
                stat.league_id = self._get_league_id(stat.league_id)
                data_dict = {
                    "topic": topic,
                    "message": convert_to_json(stat),
                }  
                await self._message_service.add_message(messaging_service.MessageEvent(**data_dict))
                count += 1
            
        logger.info(f"Total messages sent to topic {self._service_config.fixture_player_stats.topic}: {count}")
        
    async def _top_scorers(self, season, loc):
        logger.debug(f"Loading top_scorers - starting")
        file = loc + "/" + self._service_config.top_scorers.filename
        topic = self._service_config.top_scorers.topic
        data_reader = TopScorerDataReader(file=file)
        
        try:    
            top_scorers = data_reader.read()
        except (ValueError, FileNotFoundError) as e:
            logger.error(f"Unable to read file {file} because {e}")
            return
        
        logger.debug(f"Loading top_scorers - completed")
        
        message_sent = self._message_sent_already(season=season, 
                                                    key=topic)
        if message_sent > len(top_scorers):
            logger.info(f"All messages already sent to topic {topic} for season {season}")
            logger.debug("Skipping sending repeated messages")
            return
        
        count = 0
        for index in range(message_sent, len(top_scorers)):
            if 0 <= index < len(top_scorers):
                ts = top_scorers[index]
                ts.season = season
                ts.league_id = self._get_league_id(ts.league_id)
                data_dict = {
                    "topic": topic,
                    "message": convert_to_json(ts),
                } 
                await self._message_service.add_message(messaging_service.MessageEvent(**data_dict))
                count += 1
       
        logger.info(f"Total messages sent to topic {topic}: {count}")
    
    def _fixture_event_date_mapper(self, fixtures : list[Fixture]) -> dict[Fixture]:
        fixture_event_date_map = {}
        
        for fixture in fixtures:
            if(fixture.fixture_id not in fixture_event_date_map):
                fixture_event_date_map[fixture.fixture_id] = fixture.event_date
            
        return fixture_event_date_map

    def _message_sent_already(self, season: int, key: str) -> int:
        message_sent = self._db.get(self._db.get_key(key=key, 
                                                     prefix=str(season)))
        if message_sent is not None:
            message_sent = int(message_sent)
        else:
            message_sent = 0
            
        return message_sent
    
    
    def _get_league_id(self, league_id: int):
        if league_id in self._league_id_conversion:
            return self._league_id_conversion[league_id]
        return league_id