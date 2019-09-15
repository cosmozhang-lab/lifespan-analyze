import lifespan.common.mainparams as mp
import numpy as np, torch, skimage, cv2
from lifespan.common.algos import make_coors
from lifespan.common.geo import Rect
from .common import RegionType
from scipy.io import loadmat, savemat
import os, shutil
from lifespan.common.imgproc import plate_bw, detect_worm_2d

constants = {}
constants["coors"] = make_coors(size=mp.imagesize, engine=torch, device="cuda")
constants["discriminator"] = None

def dnn_filter_worms(image, bwlworms, regions, regionids):
    from lifespan.learning.dataset import prepare_image
    from lifespan.learning.trainer import Trainer
    from lifespan.learning.discriminator import Discriminator
    import lifespan.learning.userconfig as dnnconfig
    if constants["discriminator"] is None:
        discriminator = Discriminator()
        Trainer.load_model_params(discriminator, dnnconfig.model_path)
        discriminator.to(torch.device("cuda"))
        discriminator.requires_grad_(False)
        constants["discriminator"] = discriminator
    else:
        discriminator = constants["discriminator"]
    if isinstance(image, np.ndarray): image = torch.cuda.ByteTensor(image)
    if isinstance(bwlworms, np.ndarray): bwlworms = torch.cuda.IntTensor(bwlworms)
    image = image.type(torch.uint8).to(torch.device("cuda"))
    bwlworms = bwlworms.type(torch.int32).to(torch.device("cuda"))
    regions = np.array([[rect.x, rect.y, rect.w, rect.h] for rect in regions], dtype=np.int32)
    regionids = np.array(regionids)
    regiontypes = []
    for i, piece in enumerate(prepare_image(image, bwlworms, regions=regions, regionids=regionids, coors=constants["coors"])):
        if piece.data is None:
            regiontypes.append(RegionType.UNKNOWN)
            continue
        label, _ = discriminator.predict(piece.data)
        if bool(label):
            regiontypes.append(RegionType.TARGET)
        else:
            regiontypes.append(RegionType.MISTAKE)
    return regiontypes

def mark_regions(bwl):
    bwl = bwl.cuda().type(torch.int)
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
    def __init__(self, regions=None, regiontypes=None, regionids=None, airegiontypes=None):
        self.regions = regions
        self.regiontypes = regiontypes
        self.regionids = regionids
        self.airegiontypes = airegiontypes

def prepare_sample(filepath=None, cachename=None, storename=None, use_dnn=False):
    if storename and os.path.exists(storename + ".mat"):
        loaddata = loadmat(storename + ".mat")
        img = loaddata["img"]
        bwlworms = loaddata["bwlworms"]
        regions = [Rect(int(x[0]),int(x[1]),int(x[2]),int(x[3])) for x in loaddata["regions"]]
        regionids = [int(i) for i in np.squeeze(loaddata["regionids"])]
        regiontypes = [RegionType.get(num=int(x)) for x in np.squeeze(loaddata["regiontypes"])]
        cv2.imwrite(cachename + ".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 20])
        savemat(cachename + ".mat", loaddata)
        shutil.copy(storename + ".mat", cachename + ".mat")
        if use_dnn:
            airegiontypes = dnn_filter_worms(img, bwlworms, regions, regionids)
        else:
            airegiontypes = None
        return PreparedSample(regions=regions, regiontypes=regiontypes, regionids=regionids, airegiontypes=airegiontypes)
    elif filepath:
        img = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)
        im = img.copy()
        bw = plate_bw(im)
        if bw is None:
            im[:] = 0
        else:
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
                "bwlworms": bwlworms.cpu().numpy(),
                "regiontypes": npregiontypes,
                "regionids": npregionids,
                "regions": npregions
            })
        cv2.imwrite(cachename + ".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 20])
        if storename:
            shutil.copy(cachename + ".mat", storename + ".mat")
        if use_dnn:
            airegiontypes = dnn_filter_worms(img, bwlworms, regions, regionids)
        else:
            airegiontypes = None
        return PreparedSample(regions=regions, regiontypes=regiontypes, regionids=regionids, airegiontypes=airegiontypes)
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
