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
    bwoverlap = torch.cuda.ByteTensor(np.ones(mp.imagesize))
    for i in range(fcurrent - finterval + 1, fcurrent + 1):
        if manager[i].error:
            return DeathJudgement(numdeaths=0, bwldeaths=torch.cuda.IntTensor(np.zeros(mp.imagesize)), centroids=[])
    for i in range(fcurrent - finterval + 1, fcurrent + 1):
        bwoverlap = bwoverlap & manager[i].gpuwormbw
    bwl,nbwl = skimage.measure.label(manager[fcurrent].wormbw, return_num=True)
    # bwp = skimage.measure.regionprops(bwl)
    bwl = torch.cuda.IntTensor(bwl)
    bwldeaths = torch.cuda.IntTensor(np.zeros(mp.imagesize))
    numdeaths = 0
    centroids = []
    for i in range(nbwl):
        label = i + 1
        bwregion = (bwl==label)
        bwregion_overlap = bwregion & bwoverlap
        area_ratio = float(torch.sum(bwregion_overlap)) / float(torch.sum(bwregion))
        if area_ratio > overlap_threshold:
            numdeaths += 1
            bwldeaths = bwldeaths + bwregion.type(torch.int32) * numdeaths
            centroid = torch_bwcentroid(bwregion, manager.coors)
            centroids.append(centroid)
    return DeathJudgement(numdeaths=numdeaths, bwldeaths=bwldeaths, centroids=centroids)

def death_select(manager, bwldeaths1, bwldeaths2, overlap_threshold):
    bwunion = (bwldeaths1>0)&(bwldeaths2>0)
    numdeaths = 0
    bwldeaths = torch.cuda.IntTensor(np.zeros(tuple(bwunion.shape)))
    nbwl2 = int(torch.max(bwldeaths2))
    centroids = []
    for i in range(nbwl2):
        bwregion = (bwldeaths2 == i + 1)
        bwregion_overlap = bwregion & bwunion
        area_ratio = float(torch.sum(bwregion_overlap)) / float(torch.sum(bwregion))
        if area_ratio < overlap_threshold:
            numdeaths += 1
            bwldeaths = bwldeaths + bwregion.type(torch.int32) * numdeaths
            centroid = torch_bwcentroid(bwregion, manager.coors)
            centroids.append(centroid)
    return DeathJudgement(numdeaths=numdeaths, bwldeaths=bwldeaths, centroids=centroids)

class DeathDetector:
    def __init__(self, images):
        self.images = images
        self.bwdeaths = torch.cuda.ByteTensor(np.zeros(mp.imagesize))
    def step(self, index):
        if self.images[index].step >= StepAnalyze:
            return True
        if self.images[index].error:
            return False
        if self.images[index].gpuwormbw is None:
            self.images[index].gpuwormbw = torch.cuda.ByteTensor(self.images[index].wormbw)
        if index < mp.finterval-1:
            return False
        dji = death_judge(self.images, index, mp.finterval, mp.death_overlap_threshold)
        if index > mp.finterval-1: djr = death_select(self.images, self.bwdeaths, dji.bwldeaths, mp.death_overlap_threshold_for_selecting)
        else: djr = dji
        self.bwdeaths = self.bwdeaths | (dji.bwldeaths>0)
        self.images[index].death = DeathResult(
                numdeaths = djr.numdeaths,
                bwdeaths = None, # (djr.bwldeaths > 0).cpu().numpy(),
                bwdeaths_origin = None, # (dji.bwldeaths > 0).cpu().numpy(),
                centroids = djr.centroids,
                centroids_origin = dji.centroids
            )
        self.images[index].step = StepAnalyze
        return True
