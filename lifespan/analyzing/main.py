import lifespan.common.mainparams as mp
import time

def run():
    from . import userparam
    from .global_vars import global_vars as gv
    from .analyzer import Analyzer
    from .utils import format_duration
    for plate in userparam.plates:
        print("Task: %s" % plate)
        ts = time.time()
        analyzer = Analyzer(rootdir=userparam.rootdir, outdir=userparam.outdir, plate=plate, ifile0=userparam.ifile0, nfiles=userparam.nfiles)
        analyzer.carryout()
        te = time.time()
        print("Task %s completed, total time consume: %s\n" % (plate, format_duration(te - ts)))
