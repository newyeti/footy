from dataclasses import dataclass

@dataclass
class Team:
    league_id: int
    team_id: int
    name: str
    code: str
    founded: int
    stadium_name: str
    stadium_capacity: int
    stadium_surface: str
    street: str
    city: str
    country: str
    is_national: bool
