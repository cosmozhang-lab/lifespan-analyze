from . import mainparams as mp
from .global_vars import global_vars as gv
import numpy as np, torch
import skimage
from .algos import fill_holes, make_coors, torch_bwcentroid

def plate_centroid(image):
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
    bw = fill_holes(bw)
    # determine the centroid
    tgbw = torch.Tensor(bw).cuda()
    centroid = torch_bwcentroid(tgbw, gv.coors)
    return np.array(centroid).astype(np.int32), bw

# shifting: (y, x)
def shift_image(image, shifting):
    orisize = np.array(image.shape)
    shifting = np.array(shifting)
    absshift = np.abs(shifting)
    out = np.zeros(orisize + absshift * 2, dtype=image.dtype)
    out[absshift[0]:absshift[0]+orisize[0], absshift[1]:absshift[1]+orisize[1]] = image
    outstart = -shifting + absshift
    out = out[outstart[0]:outstart[0]+orisize[0], outstart[1]:outstart[1]+orisize[1]]
    return out

class Registrator:
    def __init__(self, images):
        self.images = images
        self.c0 = None
    def step(self, index):
        ci, bw = plate_centroid(self.images[index].image)
        if index == 0: self.c0 = ci
        self.images[index].shifting = self.c0 - ci
        self.images[index].image[bw==0] = 0
        self.images[index].image = shift_image(self.images[index].image, self.images[index].shifting)
        self.images[index].gpuimage = torch.cuda.ByteTensor(self.images[index].image)
