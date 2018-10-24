from datetime import datetime
from time import time

datetime_regfmt = r"\d+\-\d+\-\d+__\d+\-\d+\-\d+"
datetime_format = "%Y-%m-%d__%H-%M-%S"

def parse_datetime(init):
    if isinstance(init, str):
        return datetime.strptime(init, datetime_format)
    elif isinstance(init, datetime):
        return init
    else:
        return None

def stringify_datetime(datetime_item):
    return datetime_item.strftime(datetime_format)