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

def make_coors(image_size):
    coory = torch.cuda.FloatTensor(np.repeat(np.arange(image_size[0]).reshape([image_size[0],1]), image_size[1], 1))
    coorx = torch.cuda.FloatTensor(np.repeat(np.arange(image_size[1]).reshape([1,image_size[1]]), image_size[0], 0))
    return (coory, coorx)

def torch_bwcentroid(bw, coors=None):
    if coors is None:
        coors = make_coors(tuple(bw.shape))
    bw = bw > 0
    numelems = torch.sum(bw)
    bw = bw.type(torch.float32)
    return tuple([(float(torch.sum(bw * cooritem)) / numelems) for cooritem in coors])

# def make_localthreshold_kernel(ksize):
#     return torch.cuda.FloatTensor(np.ones(ksize)) / np.prod(ksize)

# def torch_localthreshold(im, kernel=None, ksize=None):
#     if kernel is None:
#         kernel = make_localthreshold_kernel(ksize)
#     ksize = tuple(kernel.shape)
#     kh,kw = tuple(kernel.shape[-2:])
#     pdh,pdw = (int(kh/2),int(kw/2))
#     blurred = torch.conv2d(im, kernel, padding=(pdh,pdw))

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
