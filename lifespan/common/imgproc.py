from .algos import fill_holes, torch_bwopen, make_coors
from .geo import Rect
import lifespan.common.mainparams as mp
import numpy as np, torch, skimage, cv2

def plate_bw(image):
    bw = (image >= mp.plate_threshold).astype(np.uint8)
    # find max-area region
    bwl,nbwl = skimage.measure.label(bw, return_num=True)
    if nbwl == 0: return None
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
    if not isinstance(image, torch.Tensor):
        image = torch.ByteTensor(image)
    image = image.cuda().type(torch.float32)
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
    # # fill holes
    # from .algos import fill_holes 
    # bw = fill_holes(bw)
    return bwlm

def dnn_filter_worms(image, bwlworms, discriminator, coors=None, default_adopt=None):
    import lifespan.learning.userconfig as dnnconfig
    from lifespan.learning.dataset import prepare_image
    img = image
    if not isinstance(img, torch.Tensor):
        img = torch.ByteTensor(img)
    img = img.cuda().type(torch.uint8)
    bwl = bwlworms
    if not isinstance(bwl, torch.Tensor):
        bwl = torch.IntTensor(bwl)
    bwl = bwl.cuda().type(torch.int32)
    nbwl = int(torch.max(bwl))
    if coors is None:
        coors = make_coors(image=bwl)
    mw,mh = mp.marksize
    imw,imh = mp.imagesize
    outbwl = torch.cuda.IntTensor(np.zeros(tuple(bwl.shape)))
    outnbwl = 0
    for piece in prepare_image(img, bwl, coors=coors):
        adopt = False
        if piece.data is None:
            if default_adopt is None:
                raise ValueError("region is too large for the discriminator")
            elif default_adopt:
                adopt = True
            else:
                adopt = False
        elif bool(discriminator.predict(piece.data)):
            adopt = True
        if adopt:
            outnbwl += 1
            outbwl += (bwl==piece.wid).type(torch.int) * outnbwl
    return outbwl
