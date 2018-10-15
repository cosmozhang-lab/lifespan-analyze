import lifespan.mainparams as mp
import os
thisdir = os.path.realpath(os.path.split(__file__)[0])

mp.rootdir = "/extdisk1/lifespan-20180718"
mp.buffdir = None # os.path.join(thisdir, "buffer")
mp.plate = 'G10'
mp.ifile0 = 403
mp.nfiles = 105
mp.immediate = False
mp.verbose = 10
