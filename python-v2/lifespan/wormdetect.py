from . import mainparams as mp
from .global_vars import global_vars as gv
import numpy as np, cv2, torch
import skimage
from .algos import fill_holes, torch_bwopen

def detect_worm_2d(image):
    # thv, bw = cv2.threshold(image, 0, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    bw = (image < mp.worm_threshold)
    bw[image==0] = 0
    # image open operation
    # bw = torch_bwopen(bw, np.zeros([11,11]) + 1)
    # detect worms
    bw = bw.type(torch.uint8).cpu().numpy()
    bwl,nbwl = skimage.measure.label(bw, return_num=True)
    bwp = skimage.measure.regionprops(bwl)
    bwa = np.array([x.area for x in bwp])
    bwlm = torch.cuda.IntTensor(np.zeros(tuple(bw.shape)))
    bwl = torch.cuda.IntTensor(bwl)
    label = 0
    for i in range(nbwl):
        if bwa[i] > mp.worm_minarea and bwa[i] < mp.worm_maxarea:
            label += 1
            bwlm += ((bwl==(i+1)).type(torch.int32) * label)
    bw = (bwlm>0).type(torch.uint8)
    # # fill holes
    # from .algos import fill_holes 
    # bw = fill_holes(bw)
    return bw

class WormDetector:
    def __init__(self, images):
        self.images = images
    def step(self, index):
        if self.images[index].error:
            return False
        gpuwormbw = detect_worm_2d(self.images[index].gpuimage)
        self.images[index].gpuwormbw = gpuwormbw
        self.images[index].wormbw = gpuwormbw.cpu().numpy()
        return True
