import lifespan.common.mainparams as mp
import numpy as np, cv2, torch
import skimage
from lifespan.common.algos import make_coors, torch_bwcentroid
from .image_manager import StepAnalyze

class DeathJudgement:
    def __init__(self, numdeaths=0, bwldeaths=None, centroids=None):
        self.numdeaths = numdeaths
        self.bwldeaths = bwldeaths
        self.centroids = centroids

class DeathResult:
    def __init__(self, numdeaths=0, bwdeaths=None, bwdeaths_origin=None, centroids=None, centroids_origin=None):
        self.numdeaths = numdeaths
        self.bwdeaths = bwdeaths
        self.bwdeaths_origin = bwdeaths_origin
        self.centroids = centroids
        self.centroids_origin = centroids_origin

def death_judge(manager, fcurrent, finterval, overlap_threshold):
    bwoverlap = torch.cuda.BoolTensor(np.ones(mp.imagesize))
    for i in range(fcurrent - finterval + 1, fcurrent + 1):
        if manager[i].error:
            return
    for i in range(fcurrent - finterval + 1, fcurrent + 1):
        bwoverlap = bwoverlap & (manager[i].gpuwormbwl > 0)
    bwl = manager[fcurrent].gpuwormbwl
    nbwl = manager[fcurrent].wormcentroids.shape[0]
    for i in range(nbwl):
        label = i + 1
        bwregion = (bwl==label)
        bwregion_overlap = bwregion & bwoverlap
        area_ratio = float(torch.sum(bwregion_overlap)) / float(torch.sum(bwregion))
        manager[fcurrent].score_deathdetect[i] = area_ratio
        if area_ratio > overlap_threshold:
            manager[fcurrent].wormdead[i] = True

def death_select(manager, fcurrent, bwdeaths, overlap_threshold):
    # bwdeathscur = torch.cuda.BoolTensor(np.ones(mp.imagesize))
    # bwunion = bwdeaths & manager[fcurrent].gpuwormbwl[manager.fcurrent]
    # bwldeaths = torch.cuda.IntTensor(np.zeros(tuple(bwunion.shape)))
    for i in range(manager[fcurrent].wormdead.shape[0]):
        if not manager[fcurrent].wormdead[i]:
            continue
        label = i + 1
        bwregion = (manager[fcurrent].gpuwormbwl == label)
        bwregion_overlap = bwregion & bwdeaths
        area_ratio = float(torch.sum(bwregion_overlap)) / float(torch.sum(bwregion))
        if area_ratio < overlap_threshold:
            manager[fcurrent].wormdies[i] = True

class DeathDetector:
    def __init__(self, images):
        self.images = images
        self.bwdeaths = torch.cuda.BoolTensor(np.zeros(mp.imagesize))
    def step(self, index):
        if self.images[index].step >= StepAnalyze:
            return True
        if self.images[index].error:
            return False
        if self.images[index].gpuwormbwl is None:
            self.images[index].gpuwormbwl = torch.cuda.IntTensor(self.images[index].wormbwl)
        if index < mp.finterval-1:
            return False
        death_judge(self.images, index, mp.finterval, mp.death_overlap_threshold)
        death_select(self.images, index, self.bwdeaths, mp.death_overlap_threshold_for_selecting)
        for i in range(self.images[index].wormdead.shape[0]):
            self.bwdeaths = self.bwdeaths | (self.images[index].gpuwormbwl == i + 1)
        self.images[index].step = StepAnalyze
        return True
