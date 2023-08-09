from dataclasses import dataclass, field
import json
from tools.json import Encoder

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
    season: int = field(default=0)
    
    def to_json(self):
        return json.dumps(self, indent=4, cls=Encoder)
        
