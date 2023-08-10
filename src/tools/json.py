from json import JSONEncoder

class Encoder(JSONEncoder):
    def default(self, o):
        if o is None:
            return None
        return o.__dict__

def remove_none_fields(obj):
    def empty(x):
        return x is None or x == "" or x == {} or x == []
    
    return {key: value for key, value in obj.items() if not empty(value)}

def remove_empty_elements(d):
    """recursively remove empty lists, empty dicts, or None elements from a dictionary"""

    def empty(x):
        return x is None or x == {} or x == [] or x == ""

    if not isinstance(d, (dict, list)):
        return d
    elif isinstance(d, list):
        return [v for v in (remove_empty_elements(v) for v in d) if not empty(v)]
    else:
        return {k: v for k, v in ((k, remove_empty_elements(v)) for k, v in d.items()) if not empty(v)}