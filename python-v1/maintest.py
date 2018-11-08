# This must be imported as the last package because it will cause lifespan modules execute immediately
import lifespan.mainparams as mp
import userparam
import time

from lifespan.global_vars import global_vars as gv
from lifespan.main_load_files import main_load_files
from lifespan.main_registrate import main_registrate
from lifespan.main_detect import main_detect
from lifespan.main_analyze import main_analyze

from utils import format_duration

for plate in mp.plates:
    print("Task: %s" % plate)
    mp.plate = plate
    ts = time.time()
    main_load_files()
    startflag = False
    if startflag or mp.startstep == mp.steps.registrate:
        main_registrate()
        startflag = True
    if startflag or mp.startstep == mp.steps.detect:
        main_detect()
        startflag = True
    if startflag or mp.startstep == mp.steps.analyze:
        main_analyze()
        startflag = True
    te = time.time()
    print("Task %s completed, total time consume: %s\n" % (plate, format_duration(te - ts)))
