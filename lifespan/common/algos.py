import numpy as np, cv2, skimage, torch

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

def torch_bwopen(bw, stel):
    if not isinstance(stel, torch.Tensor):
        stel = torch.Tensor(stel).cuda()
    if len(stel.shape) != 4:
        stel = torch.reshape(stel, [1,1] + list(stel.shape[-2:]))
    sumstel = torch.sum(stel)
    kh,kw = tuple(stel.shape[-2:])
    pdh,pdw = (int(kh/2),int(kw/2))
    bw = bw.reshape([1,1] + list(bw.shape[-2:])).type(torch.float32)
    bw = (torch.conv2d(bw, stel, padding=(pdh,pdw)) == sumstel).type(torch.float32)
    bw = (torch.conv2d(bw, stel, padding=(pdh,pdw)) > 0).type(torch.float32)
    bw = bw.reshape(list(bw.shape[-2:])).type(torch.uint8)
    return bw

def make_coors(size=None, engine=np, device="cpu", image=None):
    if not image is None:
        if isinstance(image, np.ndarray): engine = np
        elif isinstance(image, torch.Tensor): engine = torch
        else: raise ValueError("unrecoginized image")
        if engine == torch: device = image.device
        size = tuple(image.shape)
    else:
        if size is None:
            raise ValueError("image size is not specified")
    coory = np.repeat(np.arange(size[0]).reshape([size[0],1]), size[1], 1).astype(np.float)
    coorx = np.repeat(np.arange(size[1]).reshape([1,size[1]]), size[0], 0).astype(np.float)
    if engine == torch:
        device = torch.device(device)
        coorx = torch.FloatTensor(coorx).to(device)
        coory = torch.FloatTensor(coory).to(device)
    return (coory, coorx)

def torch_bwcentroid(bw, coors=None):
    if coors is None:
        coors = make_coors(image=bw)
    bw = bw > 0
    numelems = torch.sum(bw)
    bw = bw.type(torch.float32)
    return tuple([(float(torch.sum(bw * cooritem)) / float(numelems)) for cooritem in coors])

def torch_localmean(im, ksize=None):
    imsize = tuple(im.shape)
    im = im.type(torch.float32).reshape([1,1]+list(imsize))
    kernel = torch.cuda.FloatTensor(np.ones(ksize)).reshape([1,1]+list(ksize))
    kh,kw = tuple(kernel.shape[-2:])
    pdh,pdw = (int(kh/2),int(kw/2))
    ones = torch.cuda.FloatTensor(np.ones(im.shape))
    summing = torch.conv2d(im, kernel, padding=(pdh,pdw))
    frac = torch.conv2d(ones, kernel, padding=(pdh,pdw))
    blurred = summing / frac
    blurred = blurred.reshape(imsize)
    return blurred
