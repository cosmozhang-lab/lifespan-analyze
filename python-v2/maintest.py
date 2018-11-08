# This must be imported as the last package because it will cause lifespan modules execute immediately
import lifespan.mainparams as mp
import userparam
import time

from lifespan.global_vars import global_vars as gv
from lifespan.main import Analyzer

from utils import format_duration

for plate in mp.plates:
    print("Task: %s" % plate)
    mp.plate = plate
    ts = time.time()
    analyzer = Analyzer(mp.plate)
    analyzer.carryout()
    te = time.time()
    print("Task %s completed, total time consume: %s\n" % (plate, format_duration(te - ts)))
