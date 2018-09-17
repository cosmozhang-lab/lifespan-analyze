import numpy as np
from .utils import parse_datetime
import cv2
from . import mainparams as mp

class ImageItem:
    def __init__(self, init=None, filename=None, time=None, plate=None, data=None):
        if not init is None:
            self.data = np.copy(init.data)
            self.time = init.time
            self.plate = init.plate
        elif not filename is None:
            nameparts = re.compile(r"[\\\/]").split(filename)
            self.time = parse_datetime(nameparts[-2])
            self.plate = nameparts[-1].split(".")[0]
            self.data = cv2.imread(filename)[:,:,0]
        else:
            self.time = parse_datetime(time)
            self.plate = plate
            self.data = data
