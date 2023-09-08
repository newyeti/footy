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
    
    print(report)
    
    # assert report is not None
    # assert "newyeti.source.teams.v1" in report and report["newyeti.source.teams.v1"] == 20
    # assert "newyeti.source.fixtures.v1" in report and report["newyeti.source.fixtures.v1"] == 1
    # assert "newyeti.source.fixture_events.v1" in report and report["newyeti.source.fixture_events.v1"] == 12
    # assert "newyeti.source.fixture_lineups.v1" in report and report["newyeti.source.fixture_lineups.v1"] == 2
    # assert "newyeti.source.fixture_player_stats.v1" in report and report["newyeti.source.fixture_player_stats.v1"] == 40
    # assert "newyeti.source.top_scorers.v1" in report and report["newyeti.source.top_scorers.v1"] == 20

if __name__ == "__main__":
    asyncio.run(test_main())
