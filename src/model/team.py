from dataclasses import dataclass, field, asdict
import json
from tools.json import Encoder
from tools.json import remove_empty_elements

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
        data_dict = asdict(self)
        filtered_data = remove_empty_elements(data_dict)
        return json.dumps(filtered_data, indent=4, cls=Encoder)
