from . import mainparams as mp
from .global_vars import global_vars as gv
from .image_item import ImageItem
import numpy as np, cv2, torch
import skimage
import os

ims = gv["images"]

def torch_imopen(bw, stel):
    if not isinstance(stel, torch.Tensor):
        stel = torch.Tensor(stel).cuda()
    if len(stel.shape) != 4:
        stel = torch.reshape(stel, [1,1] + stel.shape[-2:])
    sumstel = torch.sum(stel)
    kh,kw = tuple(stel.shape[-2:])
    pdh,pdw = (kh/2,kw/2)
    bw = (torch.conv2d(bw, stel, padding=(pdh,pdw)) == sumstel).type(torch.float32)
    bw = (torch.conv2d(bw, stel, padding=(pdh,pdw)) > 0).type(torch.float32)
    return bw

def detect_worm_2d(image):
    thv, bw = cv2.threshold(image, 0, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # image open operation
    bw = torch(bw).cuda().type(torch.float32)
    bw = torch_imopen(bw, np.zeros([5,5]) + 1)
    # find max-area region
    bw = bw.type(torch.uint8).cpu().numpy().reshape(list(bw.shape[-2:]))
    bwl,nbwl = skimage.measure.label(bw, return_num=True)
    bwp = skimage.measure.regionprops(bwl)
    bwa = [x.area for x in bwp]
    maxlabel, maxarea = (0, 0)
    for i in range(nbwl):
        if bwa[i] > maxarea:
            maxarea = bwa[i]
            maxlabel = i + 1
    bw = (bwl == maxlabel)

for i in range(mp.nfiles):
    ims[i].bw = ims[i].data
