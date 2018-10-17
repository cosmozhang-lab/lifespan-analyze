from . import mainparams as mp
from .global_vars import global_vars as gv
import numpy as np, cv2, torch
import skimage
from .algos import make_coors, torch_bwcentroid

constants = {
    "coors": None
}

class ImageManager:
    def __init__(self, images, backward=0, forward=0):
        self.images = images
        self.image_size = images[0].shape
        self.length = len(images)
        self.backward = backward
        self.forward = forward
        self.gpu_images = [None for i in range(self.buffer_size)]
        self.current = 0

    @property
    def buffer_size(self):
        return self.backward + self.forward + 1
    
    def init(self, pos):
        for ig in range(self.buffer_size):
            ic = pos - self.backward + ig
            if ic < 0 or ic >= self.length:
                self.gpu_images[ig] = None
            else:
                self.gpu_images[ig] = torch.cuda.ByteTensor(self.images[ic])
        self.current = pos

    def prev(self):
        newitem = self.current - self.backward
        newitem = None if newitem < 0 else self.images[newitem]
        self.gpu_images = [torch.cuda.ByteTensor(newitem)] + self.gpu_images[:-1]
        self.current -= 1
    def next(self):
        newitem = self.current + self.forward
        newitem = None if newitem >= self.length else self.images[newitem]
        self.gpu_images = self.gpu_images[1:] + [torch.cuda.ByteTensor(newitem)]
        self.current += 1

    def __getitem__(self, index):
        if type(index) == int:
            if index < 0 or index >= self.length:
                raise IndexError("index out of range")
            ig = index - self.current + self.backward
            if ig < 0 or ig >= self.buffer_size:
                raise IndexError("queried index is not bufferred")
            return self.gpu_images[ig]
        else:
            raise TypeError("indices must be integers or slices, not list")

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
    bwoverlap = torch.cuda.ByteTensor(np.zeros(manager.image_size)) + 1
    img = np.zeros([6680,6680,3])
    for i in range(fcurrent - finterval + 1, fcurrent + 1):
        bwoverlap = bwoverlap * manager[i]
    bwcurrent = manager[fcurrent]
    bwoverlap = bwoverlap + bwcurrent
    bwl,nbwl = skimage.measure.label(bwcurrent.cpu().numpy(), return_num=True)
    # bwp = skimage.measure.regionprops(bwl)
    bwl = torch.cuda.ByteTensor(bwl)
    bwldeaths = torch.cuda.ByteTensor(np.zeros(manager.image_size))
    numdeaths = 0
    centroids = []
    for i in range(nbwl):
        label = i + 1
        bwregion = (bwl == label)
        area_ratio = float(torch.sum(bwregion * bwoverlap == 2)) / float(torch.sum(bwregion))
        centroid = torch_bwcentroid(bwregion, constants["coors"])
        if area_ratio > overlap_threshold:
            numdeaths += 1
            bwldeaths = bwldeaths + bwregion * numdeaths
            centroids.append(centroid)
    return DeathJudgement(numdeaths=numdeaths, bwldeaths=bwldeaths, centroids=centroids)

def death_select(bwldeaths1, bwldeaths2, overlap_threshold):
    bwunion = (bwldeaths1 > 0) + (bwldeaths2 > 0)
    numdeaths = 0
    bwldeaths = torch.cuda.ByteTensor(np.zeros(tuple(bwunion.shape)))
    nbwl2 = int(torch.max(bwldeaths2))
    centroids = []
    for i in range(nbwl2):
        bwregion = (bwldeaths2 == i + 1)
        bwregion_overlap = bwregion * bwunion
        area_ratio = float(torch.sum(bwregion_overlap == 2)) / float(torch.sum(bwregion))
        centroid = torch_bwcentroid(bwregion, constants["coors"])
        if area_ratio < overlap_threshold:
            numdeaths += 1
            bwldeaths = bwldeaths + bwregion * numdeaths
            centroids.append(centroid)
    return DeathJudgement(numdeaths=numdeaths, bwldeaths=bwldeaths, centroids=centroids)

def main_analyze():
    manager = ImageManager([item.worms_bw for item in gv["images"]], backward=mp.finterval)
    manager.init(mp.finterval-1)
    constants["coors"] = make_coors(manager.image_size)
    finterval = mp.finterval
    djs = [None for i in range(mp.nfiles)]
    mp.verbose >= 5 and print("analyzing...")
    def dolog(index):
        if mp.verbose >= 10:
            print("analyzed %d/%d" % (index + 1, mp.nfiles))
        elif mp.verbose >= 5:
            from .utils import progress
            progress(index)
    # prepare the first available frame
    dj1 = death_judge(manager, mp.finterval-1, mp.finterval, mp.death_overlap_threshold)
    djs[mp.finterval-1] = DeathResult(
            numdeaths = dj1.numdeaths,
            bwdeaths = (dj1.bwldeaths > 0).cpu().numpy(),
            bwdeaths_origin = (dj1.bwldeaths > 0).cpu().numpy(),
            centroids = dj1.centroids,
            centroids_origin = dj1.centroids
        )
    bwdeaths = dj1.bwldeaths > 1
    # iterate the next frames
    for i in range(mp.finterval, mp.nfiles):
        manager.next()
        dj2 = death_judge(manager, i, mp.finterval, mp.death_overlap_threshold)
        djr = death_select(bwdeaths, dj2.bwldeaths, mp.death_overlap_threshold_for_selecting)
        bwdeaths = bwdeaths | (dj2.bwldeaths > 0)
        djs[i] = DeathResult(
                numdeaths = djr.numdeaths,
                bwdeaths = (dj2.bwldeaths > 0).cpu().numpy(),
                bwdeaths_origin = (dj2.bwldeaths > 0).cpu().numpy(),
                centroids = djr.centroids,
                centroids_origin = dj2.centroids
            )
        dj1 = dj2
        dolog(i)
    # summarize
    summary = {}
    summary["numdeaths"] = np.array([(np.nan if item is None else item.numdeaths) for item in djs])
    summary["centroids"] = np.array([(np.array([]) if item is None else np.array(item.centroids)) for item in djs], np.object)
    summary["oricentroids"] = np.array([(np.array([]) if item is None else np.array(item.centroids_origin)) for item in djs], np.object)
    summary["nfiles"] = mp.nfiles
    summary["plate"] = mp.plate
    summary["dirnames"] = np.array([item.subdirname for item in gv["images"]], np.object)
    summary["imshifts"] = np.array([item.shifting for item in gv["images"]])
    mp.verbose >= 5 and print("analyzing. ok.")
    mp.verbose >= 5 and print("writing results...")
    # write result
    from scipy.io import savemat
    import os
    savemat(os.path.join(mp.outdir, "%s.out.mat" % mp.plate), summary)
    mp.verbose >= 5 and print("write results. ok.")
