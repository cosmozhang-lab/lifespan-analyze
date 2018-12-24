import os
import cv2, torch
import lifespan.common.mainparams as mp
from lifespan.common.utils import datetime_regfmt, parse_datetime
from lifespan.common.algos import make_coors

class FileItem:
    def __init__(self, rootdir, subdir, plate, filename):
        self.rootdir = rootdir
        self.subdir = subdir
        self.filename = filename
        self.plate = plate
        self.datetime = parse_datetime(subdir)
    @property
    def path(self):
        return os.path.join(self.rootdir, self.subdir, self.filename)

def get_file_list(rootdir, plate):
    import re
    filelist = os.listdir(rootdir)
    filelist = list(filter(
                    lambda xx: not re.match(datetime_regfmt, xx) is None,
                    filelist
                ))
    filelist = list(filter(
        lambda x: not x is None,
        list(map(
            lambda xx: (lambda y: FileItem(rootdir, xx, plate, y[0]) if len(y) > 0 else None)(
                list(filter(
                    lambda xxx: xxx.split(".")[0] == plate,
                    os.listdir(os.path.join(rootdir, xx))
                ))
            ),
            filelist
        ))
    ))
    filelist.sort(key=(lambda x: x.datetime))
    return filelist


class ImageItem:
    def __init__(self, fileitem=None, save_jpeg=False, save_buff=False, buffdir=None):
        self.plate = fileitem.plate
        self.subdir = fileitem.subdir
        self.image = cv2.imread(fileitem.path, cv2.IMREAD_UNCHANGED)
        self.gpuimage = None
        self.wormbw = None
        self.gpuwormbw = None
        self.death = None
        self.shifting = None
        self.wormcentroids = None
        self.buffdir = buffdir
        self.save_jpeg_flag = (not buffdir is None) and save_jpeg
        self.save_buff_flag = (not buffdir is None) and save_buff
        self.save_jpeg()
        self.save_buff()
        self.error = None

    def save_jpeg(self):
        if not self.save_jpeg_flag: return
        buffdir = self.buffdir
        buffdir = os.path.join(buffdir, self.plate)
        if not os.path.isdir(buffdir): os.mkdir(buffdir)
        buffdir = os.path.join(buffdir, "jpeg")
        if not os.path.isdir(buffdir): os.mkdir(buffdir)
        bufffile = os.path.join(buffdir, self.subdir + ".jpg")
        cv2.imwrite(bufffile, self.image, [cv2.IMWRITE_JPEG_QUALITY,20])

    def save_buff(self):
        if not self.save_buff_flag: return
        buffdir = self.buffdir
        buffdir = os.path.join(buffdir, self.plate)
        if not os.path.isdir(buffdir): os.mkdir(buffdir)
        buffdir = os.path.join(buffdir, "buff")
        if not os.path.isdir(buffdir): os.mkdir(buffdir)
        bufffile = os.path.join(buffdir, self.subdir + mp.imgsuffix)
        cv2.imwrite(bufffile, self.image)

class ImageManager:
    def __init__(self, root=None, plate=None, ifile0=0, nfiles=None, backward=0, forward=0, save_jpeg=False, save_buff=False):
        self.save_jpeg_flag = save_jpeg
        self.save_buff_flag = save_buff
        self.plate = plate
        self.rootdir = root
        filelistslice = slice(ifile0) if nfiles is None else slice(ifile0, ifile0+nfiles)
        self.filelist = get_file_list(self.rootdir, self.plate)[filelistslice]
        self.backward = backward
        self.forward = forward
        self.imgbuff = [None for i in range(self.buffsize)]
        self.current = 0
        self.coors = make_coors(size=mp.imagesize, engine=torch, device="cuda")

    @property
    def buffsize(self):
        return self.backward + self.forward + 1

    @property
    def length(self):
        return len(self.filelist)
    
    def init(self, pos):
        for ig in range(self.buffsize):
            ic = pos - self.backward + ig
            if ic < 0 or ic >= self.length:
                self.imgbuff[ig] = None
            else:
                self.imgbuff[ig] = torch.cuda.ByteTensor(self.images[ic])
        self.current = pos

    def prev(self):
        self.current -= 1
        newitem = self.current - self.backward
        newitem = None if newitem < 0 else ImageItem(self.filelist[newitem], save_jpeg=self.save_jpeg_flag, save_buff=self.save_buff_flag)
        self.imgbuff = [newitem] + self.imgbuff[:-1]
    def next(self):
        self.current += 1
        newitem = self.current + self.forward
        newitem = None if newitem >= self.length else ImageItem(self.filelist[newitem], save_jpeg=self.save_jpeg_flag, save_buff=self.save_buff_flag)
        self.imgbuff = self.imgbuff[1:] + [newitem]

    def __len__(self):
        return len(self.filelist)

    def __getitem__(self, index):
        if type(index) == int:
            if index < 0 or index >= self.length:
                raise IndexError("index out of range")
            ig = index - self.current + self.backward
            if ig < 0 or ig >= self.buffsize:
                raise IndexError("queried index is not bufferred")
            return self.imgbuff[ig]
        else:
            raise TypeError("indices must be integers or slices, not list")