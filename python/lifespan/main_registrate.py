from . import mainparams as mp
from .global_vars import global_vars as gv
from .image_item import ImageItem
import numpy as np, cv2, torch
import skimage
import os

constants = {
    "coorx": None,
    "coory": None
}

def fill_holes(bw):
    bbw = (bw == 0).astype(np.uint8)
     # find max-area region
    bbwl,nbbwl = skimage.measure.label(bbw, return_num=True)
    bbwp = skimage.measure.regionprops(bbwl)
    bbwa = [x.area for x in bbwp]
    maxlabel, maxarea = (0, 0)
    for i in range(nbbwl):
        if bbwa[i] > maxarea:
            maxarea = bbwa[i]
            maxlabel = i + 1
    return (bbwl != maxlabel).astype(np.uint8)

def plate_centroid(bw):
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
    area = torch.sum(tgbw)
    cx = float(torch.sum(tgbw*constants["coorx"]) / area)
    cy = float(torch.sum(tgbw*constants["coory"]) / area)
    centroid = (cy,cx)
    # centroid = skimage.measure.regionprops(bw)[0].centroid
    # return
    return centroid

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

def plate_bw_and_centroid(image):
    bw = (image >= mp.plate_threshold).astype(np.uint8)
    return bw, np.array(plate_centroid(bw)).astype(np.int32)

def main_registrate():
    ims = gv["images"]
    imsize = ims[0].data.shape
    constants["coorx"] = torch.Tensor(np.repeat(np.arange(imsize[1]).reshape([1,imsize[1]]), imsize[0], 0)).cuda()
    constants["coory"] = torch.Tensor(np.repeat(np.arange(imsize[0]).reshape([imsize[0],1]), imsize[1], 1)).cuda()
    ims[0].bw, c0 = plate_bw_and_centroid(ims[0].data)
    mp.verbose >= 5 and print("registrating...")
    def dolog(index):
        if mp.verbose >= 10:
            print("registrated %d/%d" % (index + 1, mp.nfiles))
        elif mp.verbose >= 5:
            from .utils import progress
            progress(index)
    for i in range(1, mp.nfiles):
        ims[i].bw, c1 = plate_bw_and_centroid(ims[i].data)
        oridata = ims[i].data
        ims[i].data = shift_image(ims[i].data, c0 - c1)
        ims[i].bw = shift_image(ims[i].bw, c0 - c1)
        dolog(i)
    mp.verbose >= 5 and print("registrating. ok.")

