from .image_manager import ImageManager
import lifespan.common.mainparams as mp

from .registrate import Registrator
from .wormdetect import WormDetector
from .deathdetect import DeathDetector
from .output import SummaryCollector

from lifespan.common.utils import ProgressBar

class Analyzer:
    def __init__(self, rootdir=None, outdir=None, plate=None, ifile0=0, nfiles=None, save_jpeg=False, save_buff=False, save_step=None, buffdir=None):
        self.plate = plate
        self.images = ImageManager(root=rootdir, plate=plate, ifile0=ifile0, nfiles=nfiles, backward=mp.finterval-1, save_jpeg=save_jpeg, save_buff=save_buff, save_step=save_step, buffdir=buffdir)
        self.nextstep = 0
        self.registrator = Registrator(self.images)
        self.wormdetector = WormDetector(self.images)
        self.deathdetector = DeathDetector(self.images)
        self.summary = SummaryCollector(self.images, self.plate, outdir=outdir)
        self.prgbar = None
    def prepare(self):
        self.images.init(-1)
        self.nextstep = 0
        self.prgbar = ProgressBar(maxval=len(self.images))
    def step(self):
        index = self.nextstep
        if self.prgbar: self.prgbar.update(index+1, "loading")
        self.summary.tic()
        self.images.next()
        self.summary.toc(index, "load")
        if self.prgbar: self.prgbar.update(index+1, "registrating")
        self.summary.tic()
        self.registrator.step(index)
        self.summary.toc(index, "registrate")
        if self.prgbar: self.prgbar.update(index+1, "detecting worms")
        self.summary.tic()
        self.wormdetector.step(index)
        self.summary.toc(index, "wormdetect")
        if self.prgbar: self.prgbar.update(index+1, "detecting deaths")
        self.summary.tic()
        self.deathdetector.step(index)
        self.summary.toc(index, "deathdetect")
        if self.prgbar: self.prgbar.update(index+1, "collecting results")
        self.summary.step(index)
        self.images.save_step(index)
        self.nextstep += 1
    def complete(self):
        self.summary.complete()
        if self.prgbar: self.prgbar.finish()
    def carryout(self):
        self.prepare()
        while self.nextstep < len(self.images):
            self.step()
        self.complete()
