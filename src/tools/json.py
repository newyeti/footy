from json import JSONEncoder

class Encoder(JSONEncoder):
    def default(self, o):
        if o is None:
            return None
        return o.__dict__

def remove_none_fields(obj):
    return {key: value for key, value in obj.items() if value is not None}
