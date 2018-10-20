import numpy as np
from .utils import parse_datetime, stringify_datetime
import cv2
from . import mainparams as mp
import re, os, shutil

class ImageItem:
    def __init__(self, init=None, filename=None, buffdir=None, time=None, plate=None, data=None):
        self.shifting = (0,0)
        self.buffdir = buffdir
        if self.buffdir:
            self.jpegdir = os.path.join(self.buffdir, "jpeg")
            if not os.path.isdir(self.jpegdir):
                os.mkdir(self.jpegdir)
            self.buffdir = os.path.join(self.buffdir, "buff")
            if not os.path.isdir(self.buffdir):
                os.mkdir(self.buffdir)
        if not init is None:
            self.image = np.copy(init.image)
            self.time = init.time
            self.plate = init.plate
            self.shifting = init.shifting
            self.buffdir = init.buffdir
        elif not filename is None:
            nameparts = re.compile(r"[\\\/]").split(filename)
            self.time = parse_datetime(nameparts[-2])
            self.plate = nameparts[-1].split(".")[0]
            if self.buffdir is None:
                self.image = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
            else:
                middlefix = (("." + str(mp.startstep.before)) if mp.startstep.before else "")
                bufffilename = os.path.join(self.buffdir, nameparts[-2] + middlefix + mp.imgsuffix)
                if not os.path.isfile(bufffilename):
                    self.image = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
                    shutil.copyfile(filename, bufffilename)
                else:
                    self.image = cv2.imread(bufffilename, cv2.IMREAD_UNCHANGED)
                if mp.startstep.before is None:
                    self.save_jpeg()
        else:
            self.time = parse_datetime(time)
            self.plate = plate
            self.image = data

    @property
    def subdirname(self):
        return stringify_datetime(self.time)

    def save_jpeg(self):
        bufffilename = os.path.join(self.jpegdir, self.subdirname + ".jpg")
        if not os.path.exists(bufffilename):
            cv2.imwrite(bufffilename, self.image, [cv2.IMWRITE_JPEG_QUALITY, 20])

    def save_step(self, name="step"):
        bufffilename = os.path.join(self.buffdir, self.subdirname + "." + str(name) + mp.imgsuffix)
        cv2.imwrite(bufffilename, self.image)
    
