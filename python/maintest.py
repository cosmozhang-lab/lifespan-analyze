# This must be imported as the last package because it will cause lifespan modules execute immediately
import lifespan.mainparams as mp
import userparam
import time

from lifespan.main_load_files import main_load_files
# from lifespan.main_preproc import main_preproc
# from lifespan.main_analyze import main_analyze

ts = time.time()

main_load_files()
# main_preproc()
# main_analyze()

te = time.time()
