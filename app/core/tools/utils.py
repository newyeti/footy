from datetime import datetime
import time

def current_date_str():
    datetime_obj = datetime.fromtimestamp(time.time())
    formatted_date = datetime_obj.strftime('%Y-%m-%dT%H:%M:%S+00:00')
    return formatted_date