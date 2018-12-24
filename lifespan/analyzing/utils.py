from datetime import datetime
from time import time
import progressbar
import lifespan.common.mainparams as mp
from .global_vars import global_vars as gv

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

_timing = {"ts":0}
def ts():
    _timing["ts"] = time()
    return _timing["ts"]
def te(name=None, reset=True):
    if not name is None:
        prompt = "Time consume for <%s>:" % str(name)
    else:
        prompt = "Time consume:"
    _timing_new = time()
    print(prompt, _timing_new - _timing["ts"])
    if reset:
        _timing["ts"] = time()
    return _timing_new

class ProgressBar:
    def __init__(self, maxval=100):
        self.mapping = {"status":None}
        self.prgbar = progressbar.ProgressBar(maxval=maxval, widgets=[
                progressbar.Bar("#"),
                progressbar.Counter(" %(value)d/%(max_value)d"),
                progressbar.FormatCustomText('%(status)s', mapping=self.mapping),
                progressbar.ETA(format             = "  %(elapsed)s (ETA: %(eta)s)",
                                format_finished    = "  %(elapsed)s",
                                format_not_started = "  --:--:-- (ETA: --:--:--)")
            ])
        self.started = False
        self.maxstatuslen = 0
    def __del__(self):
        if self.started:
            self.finish()
    def update(self, val, status=""):
        status = "[%s]" % status
        self.started = True
        self.maxstatuslen = max(self.maxstatuslen, len(status))
        self.mapping["status"] = "%% %ds" % (self.maxstatuslen+2) % status
        return self.prgbar.update(val, force=True)
    def finish(self):
        self.started = False
        self.mapping["status"] = ""
        return self.prgbar.finish()

def format_duration(seconds):
    minutes = int(seconds / 60)
    seconds = seconds - minutes * 60
    hours = int(minutes / 60)
    minutes = minutes - hours * 60
    result = "%ds" % seconds
    if minutes > 0:
        result = ("%dm" % minutes) + " " + result
    if hours > 0:
        result = ("%dh" % hours) + " " + result
    return result
