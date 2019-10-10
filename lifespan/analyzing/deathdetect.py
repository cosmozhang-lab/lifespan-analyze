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
    # for i in range(fcurrent - finterval + 1, fcurrent + 1):
    #     bwoverlap = bwoverlap & (manager[i].gpuwormbwl > 0)
    # bwl = manager[fcurrent].gpuwormbwl
    # nbwl = min(manager[fcurrent].wormcentroids.shape[0], 255)
    # for i in range(nbwl):
    #     label = i + 1
    #     bwregion = (bwl==label)
    #     bwregion_overlap = bwregion & bwoverlap
    #     area_ratio = float(torch.sum(bwregion_overlap)) / float(torch.sum(bwregion))
    #     manager[fcurrent].score_deathdetect[i] = area_ratio
    #     if area_ratio > overlap_threshold:
    #         manager[fcurrent].wormdead[i] = True
    bwshapehf = np.array(mp.marksize)
    bwshape = bwshape*2 - 1
    bwoverlap = torch.zeros(tuple(bwshape), dtype=torch.bool, device="cuda")
    nbwl = min(manager[fcurrent].wormcentroids.shape[0], 255)
    for i in range(nbwl):
        labelcur = i + 1
        centroidcur = np.round(manager[fcurrent].wormcentroids[i,:])
        rectcur = np.concatenate(centroidcur - bwshapehf + 1, centroidcur + bwshapehf)
        rectoff = -np.min((rectcur[0:2], (0,0)), axis=0)
        rectcur[0:2] += rectoff
        piececur = manager[fcurrent].gpuwormbwl[rectcur[0]:rectcur[2], rectcur[1]:rectcur[3]] == labelcur
        bwoverlap[:,:] = False
        bwoverlap[rectoff[0]:rectoff[0]+piececur.shape[0], rectoff[1]:rectoff[1]+piececur.shape[1]] = piececur
        areacur = torch.sum(bwoverlap.type(torch.uint8))
        area_ratio = np.nan
        for j in range(fcurrent - finterval + 1, fcurrent):
            if manager[j].wormcentroids is None or manager[j].wormcentroids.shape[0] == 0:
                bwoverlap[:,:] = False
                break
            dists = np.sqrt(np.sum((centroidcur - manager[j].wormcentroids)**2, axis=1))
            ihis = np.argmin(dists)
            if dists[ihis] > mp.distthre:
                bwoverlap[:,:] = False
                break
            labelhis = ihis + 1
            centroidhis = np.round(manager[j].wormcentroids[ihis,:])
            rectcur = np.concatenate(centroidhis - bwshapehf + 1, centroidhis + bwshapehf)
            rectoff = -np.min((rectcur[0:2], (0,0)), axis=0)
            rectcur[0:2] += rectoff
            piecehis = manager[j].gpuwormbwl[rectcur[0]:rectcur[2], rectcur[1]:rectcur[3]] == labelhis
            bwoverlap[rectoff[0]:rectoff[0]+piecehis.shape[0], rectoff[1]:rectoff[1]+piecehis.shape[1]] &= piecehis
            areao = torch.sum(bwoverlap.type(torch.uint8))
            area_ratio = float(areao) / float(areacur)
        manager[fcurrent].score_deathdetect[i] = area_ratio
        if area_ratio > overlap_threshold:
            manager[fcurrent].wormdead[i] = True



def death_select(manager, fcurrent, bwdeaths, overlap_threshold):
    # bwdeathscur = torch.cuda.BoolTensor(np.ones(mp.imagesize))
    # bwunion = bwdeaths & manager[fcurrent].gpuwormbwl[manager.fcurrent]
    # bwldeaths = torch.cuda.IntTensor(np.zeros(tuple(bwunion.shape)))
    for i in range(min(manager[fcurrent].wormdead.shape[0], 255)):
        if not manager[fcurrent].wormdead[i]:
            continue
        label = i + 1
        bwregion = (manager[fcurrent].gpuwormbwl == label)
        bwregion_overlap = bwregion & bwdeaths
        area_ratio = float(torch.sum(bwregion_overlap)) / float(torch.sum(bwregion))
        manager[fcurrent].score_deathselect[i] = area_ratio
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
            self.images[index].gpuwormbwl = torch.cuda.ByteTensor(self.images[index].wormbwl)
        if index < mp.finterval-1:
            return False
        death_judge(self.images, index, mp.finterval, mp.death_overlap_threshold)
        death_select(self.images, index, self.bwdeaths, mp.death_overlap_threshold_for_selecting)
        for i in range(self.images[index].wormdies.shape[0]):
            if not self.images[index].wormdies[i]: continue
            self.bwdeaths = self.bwdeaths | (self.images[index].gpuwormbwl == i + 1)
        self.images[index].step = StepAnalyze
        return True
