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

# These should not be rewritten
imgsuffix = ".tiff"
imagesize = (6680, 6680)
finterval = 3
tolerance_diedrate = 0.7
tolerance_havingdiedrate = 0.5
minsize = 1000
maxsize = 3500
