import numpy as np
from scipy.io import savemat
import os

class SummaryItem:
    def __init__(self):
        self.subdir = None
        self.shifting = None
        self.numdeaths = None
        self.centroids = None
        self.centroids_origin = None

class SummaryCollector:
    def __init__(self, images, plate):
        self.images = images
        self.plate = plate
        self.stpouts = [None for i in range(len(self.images))]
    def step(self, index):
        self.stpouts[index] = SummaryItem()
        self.stpouts[index].subdir = self.images[index].subdir
        self.stpouts[index].shifting = self.images[index].shifting
        self.stpouts[index].numdeaths = self.images[index].death.numdeaths if not self.images[index].death is None else np.nan
        self.stpouts[index].centroids = self.images[index].death.centroids if not self.images[index].death is None else []
        self.stpouts[index].centroids_origin = self.images[index].death.centroids_origin if not self.images[index].death is None else []
    def complete(self):
        outdata = {}
        outdata["nfiles"] = len(self.images)
        outdata["plate"] = self.plate
        outdata["numdeaths"] = np.array([item.numdeaths for item in self.stpouts])
        outdata["centroids"] = np.array([item.centroids for item in self.stpouts], np.object)
        outdata["oricentroids"] = np.array([item.centroids_origin for item in self.stpouts], np.object)
        outdata["dirnames"] = np.array([item.subdir for item in self.stpouts], np.object)
        outdata["imshifts"] = np.array([item.shifting for item in self.stpouts])
        # write result
        savemat(os.path.join(mp.outdir, "%s.out.mat" % self.plate), outdata)
