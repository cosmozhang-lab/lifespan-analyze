import os
thisdir = os.path.realpath(os.path.split(__file__)[0])

# These needs to be rewritten
rootdir = "/store/Data/lifespan-20180718"
buffdir = os.path.join(thisdir, "buffer")
plate = "G10"
ifile0 = 403
nfiles = 105
immediate = False
verbose = 5
outdir = "/disk1/home/cosmo/downloads"

# These should not be rewritten
imgsuffix = ".tiff"
imagesize = (6680, 6680)
finterval = 3
death_overlap_threshold = 0.7
death_overlap_threshold_for_selecting = 0.5
worm_minarea = 1000
worm_maxarea = 3500
plate_threshold = 35
