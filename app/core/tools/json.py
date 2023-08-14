from json import JSONEncoder
from typing import Any
import json

class Encoder(JSONEncoder):
    def default(self, o):
        if o is None:
            return None
        return o.__dict__


def convert_to_dict(obj):
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return {k: convert_to_dict(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [convert_to_dict(item) for item in obj]
    if hasattr(obj, "__dict__"):
        return convert_to_dict(obj.__dict__)
    return obj

def remove_empty_elements(d):
    """recursively remove empty lists, empty dicts, or None elements from a dictionary"""

    def empty(x):
        return x is None or x == {} or x == [] or x == ""

    if not isinstance(d, (dict, list)):
        return d
    elif isinstance(d, list):
        return [v for v in (remove_empty_elements(v) for v in d) if not empty(v)]
    else:
        return {k: v for k, v in ((k, remove_empty_elements(v))  for k, v in d.items()) if not empty(v)}

def convert_to_json(obj: Any) -> str:
    data_dict = convert_to_dict(obj)
    print(data_dict)
    filtered_data = remove_empty_elements(data_dict)
    print(filtered_data)
    return json.dumps(filtered_data, indent=4, cls=Encoder)

