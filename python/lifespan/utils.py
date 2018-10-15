from datetime import datetime

datetime_regfmt = r"\d+\-\d+\-\d+__\d+\-\d+\-\d+"
datetime_format = "%Y-%m-%d__%H-%M-%S"

def parse_datetime(init):
    if isinstance(init, str):
        return datetime.strptime(init, datetime_format)
    elif isinstance(init, datetime):
        return init
    else:
        return None
