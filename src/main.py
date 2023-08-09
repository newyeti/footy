import service.team_service as team_service

if __name__ == "__main__":
    try:
        team_list = team_service.read_csv("data/raw/pl/2022/team.csv")
        print(team_list[0])
    except FileNotFoundError as e:
        print(e)
