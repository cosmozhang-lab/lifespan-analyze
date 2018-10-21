from . import mainparams as mp
from .utils import datetime_regfmt, parse_datetime
from .global_vars import global_vars as gv
from .image_item import ImageItem
import numpy as np
import os

def get_buffdir():
    if mp.buffdir:
        if not os.path.isdir(mp.buffdir):
            os.mkdir(mp.buffdir)
        buffdir = os.path.join(mp.buffdir, mp.plate)
        if not os.path.isdir(buffdir):
            os.mkdir(buffdir)
    else:
        buffdir = None
    return buffdir

class FileItem:
    def __init__(self, rootdir, subdir, filename):
        self.rootdir = rootdir
        self.subdir = subdir
        self.filename = filename
        self.datetime = parse_datetime(subdir)

    @property
    def path(self):
        return os.path.join(self.rootdir, self.subdir, self.filename)

def get_file_list(plate):
    import re
    filelist = os.listdir(mp.rootdir)
    filelist = list(filter(
                    lambda xx: not re.match(datetime_regfmt, xx) is None,
                    filelist
                ))
    filelist = list(filter(
        lambda x: not x is None,
        list(map(
            lambda xx: (lambda y: FileItem(mp.rootdir, xx, y[0]) if len(y) > 0 else None)(
                list(filter(
                    lambda xxx: xxx.split(".")[0] == mp.plate,
                    os.listdir(os.path.join(mp.rootdir, xx))
                ))
            ),
            filelist
        ))
    ))
    filelist.sort(key=(lambda x: x.datetime))
    return filelist

def load_files(filelist, buffdir=None, callback=None):
    def parse_fileitem(index):
        fileitem = filelist[index]
        item = ImageItem(filename=fileitem.path, buffdir=buffdir)
        callback and callback(index, fileitem)
        return item
    ret = [parse_fileitem(i) for i in range(len(filelist))]
    return ret

def load_shiftings(buffdir=None):
    buffdir = get_buffdir() if (buffdir is None) else buffdir
    if buffdir is None:
        return
    from scipy.io import loadmat
    filename = os.path.join(buffdir, "shiftings.mat")
    if not os.path.exists(filename):
        return
    shiftings = loadmat(filename)["shiftings"]
    maxlen = np.max([shiftings.shape[0], len(gv.images)])
    for i in range(0, maxlen):
        gv.images[i].shifting = tuple(shiftings[i,:])

def save_shiftings(buffdir=None):
    buffdir = get_buffdir() if (buffdir is None) else buffdir
    if buffdir is None:
        return
    from scipy.io import savemat
    filename = os.path.join(buffdir, "shiftings.mat")
    shiftings = np.array([item.shifting for item in gv.images])
    savemat(filename, {"shiftings": shiftings})

def main_load_files():
    buffdir = get_buffdir()
    filelist = get_file_list(mp.plate)
    filelist = filelist[mp.ifile0:(mp.ifile0+mp.nfiles)]
    gv.nfiles = len(filelist)
    mp.verbose >= 5 and print("loading files...")
    def dolog(index, fileitem):
        if mp.verbose >= 10:
            print("loaded %d/%d   (%s/%s)" % (index + 1, gv.nfiles, fileitem.subdir, fileitem.filename))
        elif mp.verbose >= 5:
            from .utils import progress
            progress(index)
    gv.images = []
    gv.images = load_files(filelist, buffdir = buffdir, callback = dolog)
    load_shiftings(buffdir)
    mp.verbose >= 5 and print("loaded files. ok.")
    return gv.images

if mp.immediate:
    main_load_files()
