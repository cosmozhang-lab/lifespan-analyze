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

class RegionType:
    UNKNOWN = None
    TARGET = None
    MISTAKE = None
    BLANK = None
    _CONSTANTS = []
    def __init__(self, num=None, name=None):
        if num is None or name is None:
            fetched = RegionType.get(num=num, name=name)
            if fetched is None:
                raise ValueError("invalid num and name")
            num = fetched.num
            name = fetched.name
        self.num = num
        self.name = name
    def get(num=None, name=None):
        if num is None and name is None:
            raise ValueError("must specify a num or a name")
        for item in RegionType._CONSTANTS:
            if not num is None and item.num != num: continue
            if not name is None and item.name != name: continue
            return item
        return None

RegionType.UNKNOWN = RegionType(0, "unknown")
RegionType.TARGET  = RegionType(1, "target")
RegionType.MISTAKE = RegionType(2, "mistake")
RegionType.BLANK   = RegionType(3, "blank")
RegionType._CONSTANTS = [RegionType.UNKNOWN, RegionType.TARGET, RegionType.MISTAKE, RegionType.BLANK]
