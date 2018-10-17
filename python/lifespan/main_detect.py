from . import mainparams as mp
from .global_vars import global_vars as gv
import numpy as np, cv2, torch
import skimage
from .algos import fill_holes, torch_bwopen

def detect_worm_2d(image):
    thv, bw = cv2.threshold(image, 0, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # image open operation
    bw = torch.Tensor(bw).cuda().reshape([1,1] + list(bw.shape[-2:])).type(torch.float32)
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
    return bw

def main_detect():
    ims = gv["images"]
    mp.verbose >= 5 and print("detecting worms...")
    def dolog(index):
        if mp.verbose >= 10:
            print("detected %d/%d" % (index + 1, mp.nfiles))
        elif mp.verbose >= 5:
            from .utils import progress
            progress(index)
    for i in range(mp.nfiles):
        ims[i].worms_bw = detect_worm_2d(ims[i].image)
        dolog(i)
    mp.verbose >= 5 and print("detect worms. ok.")
