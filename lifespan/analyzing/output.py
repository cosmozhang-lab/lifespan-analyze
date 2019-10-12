import numpy as np
from scipy.io import savemat
import os
import time

class SummaryItem:
    def __init__(self):
        self.subdir = None
        self.shifting = None
        self.centroids = None
        self.wormdies = None
        self.wormdead = None
        self.score_deathdetect = None
        self.score_deathselect = None

class SummaryCollector:
    def __init__(self, images=None, plate=None, outdir=None):
        self.images = images
        self.plate = plate
        self.outdir = outdir
        self.stpouts = [None for i in range(len(self.images))]
        self.tictime = 0
        self.timing = {}
    def step(self, index):
        self.stpouts[index] = SummaryItem()
        self.stpouts[index].subdir = self.images[index].subdir
        self.stpouts[index].shifting = self.images[index].shifting if not self.images[index].shifting is None else np.array((np.nan, np.nan))
        self.stpouts[index].wormcentroids = self.images[index].wormcentroids if not self.images[index].wormcentroids is None else np.array([])
        self.stpouts[index].wormdies = self.images[index].wormdies if not self.images[index].wormdies is None else np.array([])
        self.stpouts[index].wormdead = self.images[index].wormdead if not self.images[index].wormdead is None else np.array([])
        self.stpouts[index].score_deathdetect = self.images[index].score_deathdetect if not self.images[index].score_deathdetect is None else np.array([])
        self.stpouts[index].score_deathselect = self.images[index].score_deathselect if not self.images[index].score_deathselect is None else np.array([])
        return True
    def tic(self):
        self.tictime = time.time()
    def toc(self, index, group, ticnext=True):
        timed = time.time() - self.tictime
        if not group in self.timing:
            self.timing[group] = [np.nan for i in range(len(self.images))]
        self.timing[group][index] = timed
        if ticnext:
            self.tic()
    def complete(self, deathdetector=None):
        outdata = {}
        outdata["nfiles"] = len(self.images)
        outdata["plate"] = self.plate
        outdata["centroids"] = np.array([item.wormcentroids for item in self.stpouts], np.object)
        outdata["fdies"] = np.array([item.wormdies for item in self.stpouts], np.object)
        outdata["fdead"] = np.array([item.wormdead for item in self.stpouts], np.object)
        outdata["rddetect"] = np.array([item.score_deathdetect for item in self.stpouts], np.object)
        outdata["rdselect"] = np.array([item.score_deathselect for item in self.stpouts], np.object)
        outdata["dirnames"] = np.array([item.subdir for item in self.stpouts], np.object)
        outdata["imshifts"] = np.array([item.shifting for item in self.stpouts])
        for group in self.timing:
            outdata["timing_" + group] = np.array(self.timing[group])
        if deathdetector is not None:
            outdata["globalids"] = deathdetector.globalids if deathdetector.globalids is not None else np.array([])
            outdata["globalcentroids"] = deathdetector.globalcentroids if deathdetector.globalcentroids is not None else np.array([])
        # write result
        savemat(os.path.join(self.outdir, "%s.out.mat" % self.plate), outdata)
