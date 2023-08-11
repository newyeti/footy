import sys
import os
import os.path
import argparse

# Add the parent directory (app) to sys.path
parent_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, parent_directory)

import commands

def main(args):
    filepath = args.file
    season = args.season
    service = args.service
    
    if os.path.isfile(filepath) == False:
        raise FileNotFoundError(f"File {filepath} not found.")
    
    match service:
        case "team":
            print(f"processing teams data from file={filepath}")
            commands.process_team_data(filepath=filepath, season=season)
        case "fixture":
            print(f"processing teams file {filepath}")


if __name__ == "__main__":
    project_root = os.path.dirname(os.path.abspath("telemetry"))
    print(project_root)
    
    parser = argparse.ArgumentParser(description="Telemetry")
    parser.add_argument("-service", choices=["team", "fixture"], required=True,
                        help="Choose the service from the list: [team, fixture]")
    parser.add_argument("-file", type=str, required=True, help="Filepath")
    parser.add_argument("-season", type=int, required=True, help="Season")

    args = parser.parse_args()
    main(args)
