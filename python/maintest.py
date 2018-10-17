# This must be imported as the last package because it will cause lifespan modules execute immediately
import lifespan.mainparams as mp
import userparam
import time

from lifespan.global_vars import global_vars as gv
from lifespan.main_load_files import main_load_files
from lifespan.main_registrate import main_registrate
from lifespan.main_detect import main_detect
from lifespan.main_analyze import main_analyze

ts = time.time()

main_load_files()
main_registrate()
main_detect()
main_analyze()

te = time.time()

# from lifespan.main_load_files import get_file_list
# filelist = get_file_list(mp.plate)
# for i in range(len(filelist)):
#     print(i+1, filelist[i].subdir)

from scipy.io import savemat
savemat("/disk1/home/cosmo/downloads/out.mat", {"worms":gv["images"][0].worms_bw, "im":gv["images"][0].image})

print("Task completed, total time consume:", te - ts)