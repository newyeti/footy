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
