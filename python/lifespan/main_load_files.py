from . import mainparams as mp
from .global_vars import global_vars as gv
from .image_item import ImageItem
import numpy as np
import os

class FileItem:
    def __init__(self, rootdir, subdir, filename):
        self.rootdir = rootdir
        self.subdir = subdir
        self.filename = filename

    @property
    def path():
        return os.path.join(self.rootdir, self.subdir, self.filename)

def get_file_list(plate):
    filelist = os.listdir(mp.rootdir)
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
    return filelist

def load_files(filelist, callback=None):
    def parse_fileitem(index):
        fileitem = filelist[index]
        item = ImageItem(fileitem.path)
        callback(index, fileitem)
        return item
    ret = [parse_fileitem(i) for i in range(len(filelist))]
    return ret

def main_load_files():
    filelist = get_file_list(mp.plate)
    filelist = filelist[mp.ifile0:(mp.ifile0+mp.nfiles)]
    def load_callback(index, fileitem):
        if mp.verbose >= 10:
            print("loaded %d/%d   (%s/%s)" % (index + 1, mp.nfiles, fileitem.subdir, fileitem.filename))
    if mp.verbose >= 5:
        print("loading files...")
    gv["images"] = 2 # load_files(filelist, load_callback)
    if mp.verbose >= 5:
        print("loaded files. ok.")
    return gv["images"]

if mp.immediate:
    main_load_files()
