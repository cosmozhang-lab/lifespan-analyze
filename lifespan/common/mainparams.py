import os
thisdir = os.path.realpath(os.path.dirname(__file__))

imgsuffix = ".tiff"
imagesize = (6680, 6680)
marksize = (256, 256)
distthre = 64
worm_minarea = 500
worm_maxarea = 3500
plate_threshold = 35
worm_threratio = 0.65
worm_threshold = 90
localthreshold_size = (257, 257)
death_overlap_threshold = 0.7
death_overlap_threshold_for_selecting = 0.35
finterval = 24
dnn_discriminate = True
