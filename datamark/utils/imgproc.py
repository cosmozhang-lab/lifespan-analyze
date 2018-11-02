from . import mainparams as mp
import numpy as np, torch, skimage, cv2
from .algos import fill_holes, make_coors, torch_bwcentroid, torch_bwopen
from .common import RegionType
from scipy.io import loadmat, savemat
import os, shutil

constants = {
    "coors": make_coors(mp.imagesize)
}

def plate_bw(image):
    bw = (image >= mp.plate_threshold).astype(np.uint8)
    # find max-area region
    bwl,nbwl = skimage.measure.label(bw, return_num=True)
    bwp = skimage.measure.regionprops(bwl)
    bwa = [x.area for x in bwp]
    maxlabel, maxarea = (0, 0)
    for i in range(nbwl):
        if bwa[i] > maxarea:
            maxarea = bwa[i]
            maxlabel = i + 1
    bw = (bwl == maxlabel)
    # fill holes in region
    bwfilled = fill_holes(bw)
    return bwfilled

def detect_worm_2d(image):
    image = torch.cuda.ByteTensor(image)
    # platebw = image > 0
    # nvalid = int(torch.sum(platebw))
    # hist = torch.histc(image.cpu().type(torch.float32), bins=256, min=0, max=255)
    # hist[0] = 0
    # cshist = torch.cumsum(hist, dim=0).numpy()
    # seppos = int(cshist[-1]) * 0.5
    # sepvalue = 0
    # while sepvalue < len(cshist) and cshist[sepvalue] < seppos:
    #     sepvalue += 1
    # bw = image > sepvalue
    platearea = float(torch.sum(image > 0))
    if platearea <= 0: return np.zeros(tuple(image.shape))
    meanv = float(torch.sum(image)) / float(torch.sum(image > 0))
    bw = image > (meanv * mp.worm_threshold)
    # image open operation
    bw = bw.reshape([1,1] + list(bw.shape[-2:])).type(torch.float32)
    bw = torch_bwopen(bw, np.zeros([5,5]) + 1)
    bw = 1 - bw
    # detect worms
    bw = bw.type(torch.uint8).cpu().numpy().reshape(list(bw.shape[-2:]))
    bwl,nbwl = skimage.measure.label(bw, return_num=True)
    bwp = skimage.measure.regionprops(bwl)
    bwa = np.array([x.area for x in bwp])
    bw = np.zeros(tuple(bw.shape), np.uint8)
    for i in range(nbwl):
        if bwa[i] > mp.worm_minarea and bwa[i] < mp.worm_maxarea:
            bw += (bwl == (i + 1))
    # # fill holes
    # from .algos import fill_holes 
    # bw = fill_holes(bw)
    bwl,nbwl = skimage.measure.label(bw, return_num=True)
    return bwl

class Rect:
    def __init__(self, left, top, width, height):
        self.left = left
        self.top = top
        self.width = width
        self.height = height
    @property
    def x(self):
        return self.left
    @property
    def y(self):
        return self.top
    @property
    def w(self):
        return self.width
    @property
    def h(self):
        return self.height

def mark_regions(bwl):
    bwl = torch.cuda.IntTensor(bwl)
    nbwl = int(torch.max(bwl))
    coors = constants["coors"]
    regions = [None for i in range(nbwl)]
    for i in range(nbwl):
        bw = (bwl == (i + 1)).type(torch.float32)
        coorx = bw * coors[1]
        coory = bw * coors[0]
        maxcoorx = int(torch.max(coorx))
        maxcoory = int(torch.max(coory))
        coorx[coorx == 0] = mp.imagesize[1]
        coory[coory == 0] = mp.imagesize[0]
        mincoorx = int(torch.min(coorx))
        mincoory = int(torch.min(coory))
        regions[i] = Rect(mincoorx, mincoory, maxcoorx - mincoorx + 1, maxcoory - mincoory + 1)
    return regions

class PreparedSample:
    def __init__(self, regions=None, regiontypes=None, regionids=None):
        self.regions = regions
        self.regiontypes = regiontypes
        self.regionids = regionids

def prepare_sample(filepath=None, cachename=None, storename=None):
    if storename and os.path.exists(storename + ".mat"):
        loaddata = loadmat(storename + ".mat")
        img = loaddata["img"]
        regions = [Rect(int(x[0]),int(x[1]),int(x[2]),int(x[3])) for x in loaddata["regions"]]
        regionids = [int(i) for i in np.squeeze(loaddata["regionids"])]
        regiontypes = [RegionType.get(num=int(x)) for x in np.squeeze(loaddata["regiontypes"])]
        cv2.imwrite(cachename + ".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 20])
        savemat(cachename + ".mat", loaddata)
        shutil.copy(storename + ".mat", cachename + ".mat")
        return PreparedSample(regions=regions, regiontypes=regiontypes, regionids=regionids)
    elif filepath:
        img = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)
        im = img.copy()
        bw = plate_bw(im)
        im[bw==0] = 0
        bwlworms = detect_worm_2d(im)
        regions = mark_regions(bwlworms)
        regiontypes = [RegionType.UNKNOWN for i in range(len(regions))]
        regionids = [(i+1) for i in range(len(regions))]
        npregiontypes = np.array([item.num for item in regiontypes]).astype(np.uint8)
        npregionids = np.array(regionids).astype(np.int32)
        npregions = np.array([[item.x, item.y, item.width, item.height] for item in regions]).astype(np.int32)
        savemat(cachename + ".mat", {
                "img": img,
                "bwlworms": bwlworms,
                "regiontypes": npregiontypes,
                "regionids": npregionids,
                "regions": npregions
            })
        cv2.imwrite(cachename + ".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 20])
        if storename:
            shutil.copy(cachename + ".mat", storename + ".mat")
        return PreparedSample(regions=regions, regiontypes=regiontypes, regionids=regionids)
    else:
        return None

def complete_sample(sample, cachename=None, storename=None):
    regiontypes = sample.regiontypes
    regionids = sample.regionids
    regions = sample.regions
    npregiontypes = np.array([item.num for item in regiontypes]).astype(np.uint8)
    npregionids = np.array([i for i in regionids]).astype(np.int32)
    npregions = np.array([[item.x, item.y, item.width, item.height] for item in regions]).astype(np.int32)
    thedata = loadmat(cachename + ".mat")
    thedata["regiontypes"] = npregiontypes
    thedata["regionids"] = npregionids
    thedata["regions"] = npregions
    savemat(storename + ".mat", thedata)
    os.remove(cachename + ".jpg")
    os.remove(cachename + ".mat")
