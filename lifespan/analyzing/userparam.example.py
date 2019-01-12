import os
thisdir = os.path.realpath(os.path.split(__file__)[0])
from datetime import datetime

rootdir = "/extdisk1/lifespan-20180718"
buffdir = None # os.path.join(thisdir, "buffer")
plate = 'G10'
plates = ["G7"]
ifile0 = 403
nfiles = 105
fromtime = None # datetime(2018,8,25,0,0,0)
totime = None # datetime(2018,10,15,23,59,59)
immediate = False
verbose = 5
outdir = "/disk1/home/cosmo/downloads"
savebuff = False
savejpeg = False
savestep = None # can be "registrate" | "detect"
