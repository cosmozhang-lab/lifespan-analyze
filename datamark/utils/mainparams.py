import os
thisdir = os.path.realpath(os.path.split(__file__)[0])

imgsuffix = ".tiff"
imagesize = (6680, 6680)
marksize = (256, 256)
worm_minarea = 500
worm_maxarea = 8500
plate_threshold = 35
worm_threshold = 0.65
