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
    main_registrate()
    main_detect()
    main_analyze()
    te = time.time()
    print("Task %s completed, total time consume: %s\n" % (plate, format_duration(te - ts)))
