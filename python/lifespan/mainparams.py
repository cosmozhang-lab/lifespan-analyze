import os
thisdir = os.path.realpath(os.path.split(__file__)[0])

class steps:
    registrate = None
    detect = None
    analyze = None
    def __init__(self, name=None, before=None):
        self.name = name
        self.before = before
    def __str__(self):
        return self.name
steps.registrate = steps("registrate")
steps.detect = steps("detect", steps.registrate)
steps.analyze = steps("analyze", steps.detect)

# These needs to be rewritten
rootdir = "/store/Data/lifespan-20180718"
buffdir = os.path.join(thisdir, "buffer")
plate = "G10"
plates = ["G10"]
ifile0 = 403
nfiles = 105
immediate = False
verbose = 5
outdir = "/disk1/home/cosmo/downloads"
startstep = steps.registrate
savebuff = False
savejpeg = False
savesteps = False

# These should not be rewritten
imgsuffix = ".tiff"
imagesize = (6680, 6680)
finterval = 10
death_overlap_threshold = 0.7
death_overlap_threshold_for_selecting = 0.5
worm_minarea = 750
worm_maxarea = 3500
plate_threshold = 35
