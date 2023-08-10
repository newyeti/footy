import argparse
import os.path
from service.team_service import TeamService
from infra.kafka import KafkaProducerSingleton

producer = KafkaProducerSingleton()

def main(args):
    filepath = args.file
    season = args.season
    service = args.service
    
    
    if os.path.isfile(filepath) == False:
        raise FileNotFoundError(f"File {filepath} not found.")
    
    match service:
        case "team":
            print(f"processing teams data from file={filepath}")
            process_team_data(filepath, season)
        case "fixture":
            print(f"processing teams file {filepath}")

def process_team_data(filepath: str, season: int):
    team_service = TeamService()
    teams = team_service.read_file(filepath)
    for team in teams:
        team.season = season
    team_service.send(producer=producer, team=teams[0])
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Telemetry")
    parser.add_argument("-service", choices=["team", "fixture"], required=True,
                        help="Choose the service from the list: [team, fixture]")
    parser.add_argument("-file", type=str, required=True, help="Filepath")
    parser.add_argument("-season", type=int, required=True, help="Season")

    args = parser.parse_args()
    main(args)
