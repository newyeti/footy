import asyncio
import os
import sys

import os.path
import pytest

# Add the parent directory (app) to sys.path
current_directory =  os.path.abspath(os.path.dirname(__file__))
parent_directory = os.path.abspath(os.path.join(current_directory, "../../.."))
sys.path.insert(0, parent_directory)

from app.entrypoints.cmd.main import run
from app.core.tools.hydra import load_app_config
from app.adapters.services import redis_service

@pytest.mark.asyncio
async def test_main():
    current_directory =  os.path.abspath(os.path.dirname(__file__))
    config_directory = os.path.abspath(os.path.join(current_directory, "config"))
    data_directory = os.path.abspath(os.path.join(current_directory, "data/2022"))
    services = ["teams", "fixtures", "fixture_events", "fixture_lineups", "fixture_player_stats", "top_scorers"]
    service = "all"
    season = "2022"
    
    app_config = load_app_config(config_directory, "app")
    redis_control = redis_service.RedisSingleton(
        name=app_config.control.redis.client_id,
        redis_config=app_config.control.redis)
    
    report = await run(app_config=app_config,
        services=services,
        service=service,
        season=2022,
        location=data_directory)
    
    assert report is not None
    
    try:
        for key in report.keys():
            redis_key = redis_control.get_key(prefix=season, key=key, suffix=None)
            redis_value = redis_control.get(redis_key)
            dict_key = redis_key.replace(f"{season}_", "")
            assert redis_value is not None
            assert report[dict_key] == int(redis_value)
    finally:
        for key in report.keys():
            redis_key = redis_control.get_key(prefix=season, key=key, suffix=None)
            redis_control.redis.delete(redis_key)
        
    assert "newyeti.source.teams.v1" in report and report["newyeti.source.teams.v1"] == 20
    assert "newyeti.source.fixtures.v1" in report and report["newyeti.source.fixtures.v1"] == 1
    assert "newyeti.source.fixture_events.v1" in report and report["newyeti.source.fixture_events.v1"] == 12
    assert "newyeti.source.fixture_lineups.v1" in report and report["newyeti.source.fixture_lineups.v1"] == 2
    assert "newyeti.source.fixture_player_stats.v1" in report and report["newyeti.source.fixture_player_stats.v1"] == 40
    assert "newyeti.source.top_scorers.v1" in report and report["newyeti.source.top_scorers.v1"] == 20

if __name__ == "__main__":
    asyncio.run(test_main())
