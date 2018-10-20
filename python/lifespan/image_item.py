import numpy as np
from .utils import parse_datetime, stringify_datetime
import cv2
from . import mainparams as mp
import re, os, shutil

class ImageItem:
    def __init__(self, init=None, filename=None, buffdir=None, time=None, plate=None, data=None):
        if not init is None:
            self.data = np.copy(init.data)
            self.time = init.time
            self.plate = init.plate
        elif not filename is None:
            nameparts = re.compile(r"[\\\/]").split(filename)
            self.time = parse_datetime(nameparts[-2])
            self.plate = nameparts[-1].split(".")[0]
            if buffdir is None:
                self.data = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
            else:
                bufffilename = os.path.join(buffdir, nameparts[-2] + mp.bufffmt)
                if not os.path.isfile(bufffilename):
                    self.data = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
                    cv2.imwrite(bufffilename, self.data, mp.buffopt)
                    # shutil.copyfile(filename, bufffilename)
                else:
                    self.data = cv2.imread(bufffilename, cv2.IMREAD_UNCHANGED)
        else:
            self.time = parse_datetime(time)
            self.plate = plate
            self.data = data
        self.image = None
        self.bw = None
        self.worms_bw = None
        self.shifting = (0,0)

    @property
    def subdirname(self):
        return stringify_datetime(self.time)
    
