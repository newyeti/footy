import service.team_service as team_service
from tools.json import Encoder
import json
from service.team_service import TeamService

if __name__ == "__main__":
    try:
        team_service = TeamService()
        team_list = team_service.read_file("data/raw/pl/2022/team.csv")
        json_string = json.dumps(team_list, indent=4, cls=Encoder)
        print(json_string)
    except FileNotFoundError as e:
        print(e)
