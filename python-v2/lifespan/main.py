from .image_manager import ImageManager
from . import mainparams as mp

from .registrate import Registrator
from .wormdetect import WormDetector
from .deathdetect import DeathDetector
from .output import SummaryCollector

from .utils import ProgressBar

class Analyzer:
    def __init__(self, plate):
        self.plate = plate
        self.images = ImageManager(plate, backward=mp.finterval-1)
        self.nextstep = 0
        self.registrator = Registrator(self.images)
        self.wormdetector = WormDetector(self.images)
        self.deathdetector = DeathDetector(self.images)
        self.summary = SummaryCollector(self.images, self.plate)
        self.prgbar = None
    def prepare(self):
        self.images.init(-1)
        self.nextstep = 0
        # self.prgbar = ProgressBar(maxval=len(self.images))
    def step(self):
        index = self.nextstep
        if self.prgbar: self.prgbar.update(index+1, "loading")
        self.images.next()
        if self.prgbar: self.prgbar.update(index+1, "registrating")
        self.registrator.step(index)
        if self.prgbar: self.prgbar.update(index+1, "detecting worms")
        self.wormdetector.step(index)
        if self.prgbar: self.prgbar.update(index+1, "detecting deaths")
        self.deathdetector.step(index)
        if self.prgbar: self.prgbar.update(index+1, "collecting results")
        self.summary.step(index)
        self.nextstep += 1
    def complete(self):
        self.summary.complete()
        if self.prgbar: self.prgbar.finish()
    def carryout(self):
        self.prepare()
        while self.nextstep < len(self.images):
            self.step()
        self.complete()
        