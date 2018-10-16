from datetime import datetime
from time import time
import progressbar
from . import mainparams as mp

datetime_regfmt = r"\d+\-\d+\-\d+__\d+\-\d+\-\d+"
datetime_format = "%Y-%m-%d__%H-%M-%S"

def parse_datetime(init):
    if isinstance(init, str):
        return datetime.strptime(init, datetime_format)
    elif isinstance(init, datetime):
        return init
    else:
        return None

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

_progress_bar = {"bar":None}
def progress(idx):
    if _progress_bar["bar"] is None:
        _progress_bar["bar"] = progressbar.ProgressBar(maxval=mp.nfiles, widgets=[
            progressbar.Bar("#"), progressbar.Counter(" %(value)d/%(max_value)d"), progressbar.ETA(format="  %(elapsed)s (ETA: %(eta)s)", format_finished="  %(elapsed)s")])
    _progress_bar["bar"].update(idx + 1)
    if idx + 1 == mp.nfiles:
        _progress_bar["bar"].finish()
        _progress_bar["bar"] = None
