from . import mainparams as mp
from .global_vars import global_vars as gv
import numpy as np, torch
import skimage
from .algos import fill_holes, make_coors, torch_bwcentroid

constants = {
    "coors": None
}

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
    centroid = torch_bwcentroid(tgbw, constants["coors"])
    # centroid = skimage.measure.regionprops(bw)[0].centroid
    # return
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

def main_registrate():
    ims = gv["images"]
    constants["coors"] = make_coors(ims[0].data.shape)
    c0, ims[0].bw = plate_centroid(ims[0].data)
    ims[0].image = np.array(ims[0].data)
    ims[0].image[ims[0].bw == 0] = 0
    mp.verbose >= 5 and print("registrating...")
    def dolog(index):
        if mp.verbose >= 10:
            print("registrated %d/%d" % (index + 1, mp.nfiles))
        elif mp.verbose >= 5:
            from .utils import progress
            progress(index)
    for i in range(1, mp.nfiles):
        c1, ims[i].bw = plate_centroid(ims[i].data)
        oridata = ims[i].data
        ims[i].shifting = c0 - c1
        ims[i].image = shift_image(ims[i].data, c0 - c1)
        ims[i].bw = shift_image(ims[i].bw, c0 - c1)
        ims[i].image[ims[i].bw == 0] = 0
        dolog(i)
    mp.verbose >= 5 and print("registrating. ok.")

