import os
thisdir = os.path.realpath(os.path.split(__file__)[0])

rootdir = "/extdisk1/lifespan-20180718"
buffdir = None # os.path.join(thisdir, "buffer")
plates = ["G4"]
starttime = "2018-10-05__00-00-00"
endtime = "2018-10-30__00-00-00"
immediate = False
verbose = 5
outdir = "/disk1/home/cosmo/downloads"
savebuff = False
savejpeg = False
savestep = None # can be "registrate" | "detect"
