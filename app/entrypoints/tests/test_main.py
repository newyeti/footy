import os
from app.entrypoints.cmd.main import run
import os.path
import pytest

@pytest.mark.asyncio
async def test_main():
    current_directory =  os.path.abspath(os.path.dirname(__file__))
    config_directory = os.path.abspath(os.path.join(current_directory, "config"))
    data_directory = os.path.abspath(os.path.join(current_directory, "data/2022"))
    services = ["teams", "fixtures", "fixture_events", "fixture_lineups", "fixture_player_stats", "top_scorers"]
    service = "all"
    
    report = await run(config_directory=config_directory,
        services=services,
        service=service,
        season=2022,
        location=data_directory)
    
    assert report is not None
    assert report["newyeti.source.teams.v1"] == 20
    assert report["newyeti.source.fixtures.v1"] == 1
    assert report["newyeti.source.fixture_events.v1"] == 12
    assert report["newyeti.source.fixture_lineups.v1"] == 2
    assert report["newyeti.source.fixture_player_stats.v1"] == 40
    assert report["newyeti.source.top_scorers.v1"] == 20
    
