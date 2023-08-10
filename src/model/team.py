from dataclasses import dataclass, field, asdict
import json
from tools.json import Encoder
from tools.json import remove_none_fields

@dataclass
class Team:
    league_id: int
    team_id: int
    name: str = None
    code: str = None
    founded: int = None
    stadium_name: str = None
    stadium_capacity: int = None
    stadium_surface: str = None
    street: str = None
    city: str = None
    country: str = None
    is_national: bool = None
    season: int = field(default=0)
    
    def to_json(self):
        return json.dumps(asdict(self), indent=4, cls=Encoder)
