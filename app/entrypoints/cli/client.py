import sys
import os
import os.path
import argparse
import hydra

# Add the parent directory (app) to sys.path
parent_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, parent_directory)

import commands

@hydra.main(config_path="conf", config_name="config.yaml", version_base="1.2")
def main(cfg):
    print(cfg)
    
    parser = argparse.ArgumentParser(description="Telemetry")
    parser.add_argument("-service", choices=["team", "fixture"], required=True,
                        help="Choose the service from the list: [team, fixture]")
    parser.add_argument("-file", type=str, required=True, help="Filepath")
    parser.add_argument("-season", type=int, required=True, help="Season")

    args = parser.parse_args()
    
    file = args.file
    season = args.season
    service = args.service
    
    if os.path.isfile(file) == False:
        raise FileNotFoundError(f"File {file} not found.")
    
    match service:
        case "team":
            print(f"processing teams data from file={file}")
            commands.process_team_data(file=file, season=season)
        case "fixture":
            print(f"processing teams file {file}")


if __name__ == "__main__":
    main()
