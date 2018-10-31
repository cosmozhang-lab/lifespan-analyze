from . import mainparams as mp
import numpy as np, torch, skimage, cv2
from .algos import fill_holes, make_coors, torch_bwcentroid, torch_bwopen
from .common import RegionType
from scipy.io import loadmat, savemat
import os

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
    def __init__(self, regions=None, regiontypes=None):
        self.regions = regions
        self.regiontypes = regiontypes

def prepare_sample(filepath, outname):
    img = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)
    im = img.copy()
    bw = plate_bw(im)
    im[bw==0] = 0
    bwlworms = detect_worm_2d(im)
    regions = mark_regions(bwlworms)
    regiontypes = [RegionType.UNKNOWN for i in range(len(regions))]
    npregiontypes = np.array([item.num for item in regiontypes]).astype(np.uint8)
    npregions = np.array([[item.x, item.y, item.width, item.height] for item in regions]).astype(np.int32)
    savemat(outname + ".mat", {
            "img": img,
            "bwlworms": bwlworms,
            "regiontypes": npregiontypes,
            "regions": npregions
        })
    cv2.imwrite(outname + ".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 20])
    return PreparedSample(regions=regions, regiontypes=regiontypes)

def complete_sample(sample, inname, outname):
    regiontypes = sample.regiontypes
    regions = sample.regions
    npregiontypes = np.array([item.num for item in regiontypes]).astype(np.uint8)
    npregions = np.array([[item.x, item.y, item.width, item.height] for item in regions]).astype(np.int32)
    thedata = loadmat(inname + ".mat")
    thedata["regiontypes"] = npregiontypes
    thedata["regions"] = npregions
    savemat(outname + ".mat", thedata)
    os.remove(inname + ".jpg")
    os.remove(inname + ".mat")

def review_sample(storedname, outname):
    loaddata = loadmat(storedname + ".mat")
    img = loaddata["img"]
    regions = [Rect(int(x[0]),int(x[1]),int(x[2]),int(x[3])) for x in loaddata["regions"]]
    regiontypes = [RegionType.get(num=int(x)) for x in np.squeeze(loaddata["regiontypes"])]
    cv2.imwrite(outname + ".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 20])
    savemat(outname + ".mat", loaddata)
    return PreparedSample(regions=regions, regiontypes=regiontypes)
