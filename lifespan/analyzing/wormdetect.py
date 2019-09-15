import lifespan.common.mainparams as mp
import numpy as np, cv2, torch
import skimage
from lifespan.common.algos import fill_holes, torch_bwopen, torch_bwcentroid
from lifespan.common.imgproc import detect_worm_2d, dnn_filter_worms
from .image_manager import StepDetect

def calculate_worm_centroids(bwlworms, coors=None):
    nbwl = torch.max(bwlworms)
    centroids = []
    for i in range(nbwl):
        label = i + 1
        centroid = torch_bwcentroid(bwlworms==label, coors)
        centroids.append(centroid)
    centroids = np.array(centroids)
    return centroids

class WormDetector:
    discriminator = None
    def __init__(self, images):
        self.images = images
        if mp.dnn_discriminate and WormDetector.discriminator is None:
            from lifespan.learning.discriminator import Discriminator
            from lifespan.learning.trainer import Trainer
            import lifespan.learning.userconfig as dnnconfig
            WormDetector.discriminator = Discriminator()
            Trainer.load_model_params(WormDetector.discriminator, dnnconfig.model_path)
            WormDetector.discriminator.requires_grad_(False)
            WormDetector.discriminator.to(torch.device("cuda"))
    def step(self, index):
        if self.images[index].step >= StepDetect:
            return True
        if self.images[index].error:
            return False
        if self.images[index].gpuimage is None:
            self.images[index].gpuimage = torch.cuda.ByteTensor(self.images[index].image)
        gpuwormbwl = detect_worm_2d(self.images[index].gpuimage)
        if mp.dnn_discriminate:
            gpuwormbwl, scores = dnn_filter_worms(self.images[index].gpuimage, gpuwormbwl, WormDetector.discriminator, coors=self.images.coors, default_adopt=True)
            if scores.size > 255:
                # too many worms detected, kick out worms with low scores
                iscores = np.argsort(scores)[-255:]
                scores = scores[iscores]
                nlabel = 0
                newgpuwormbwl = np.cuda.ByteTensor(np.zeros(mp.imagesize))
                for i in list(iscores):
                    nlabel += 1
                    newgpuwormbwl += (gpuwormbwl == i + 1).to(torch.uint8) * nlabel
                gpuwormbwl = newgpuwormbwl
        else:
            # TODO: we should kick out some worms to make sure there are no more than 255 worms detected.
            pass
        self.images[index].gpuwormbwl = gpuwormbwl.to(torch.uint8)
        self.images[index].wormbwl = gpuwormbwl.cpu().numpy()
        self.images[index].wormcentroids = calculate_worm_centroids(gpuwormbwl, self.images.coors)
        nworms = self.images[index].wormcentroids.shape[0]
        self.images[index].wormdies = np.array([0 for i in range(nworms)], dtype=np.bool)
        self.images[index].wormdead = np.array([0 for i in range(nworms)], dtype=np.bool)
        self.images[index].score_deathdetect = np.array([np.nan for i in range(nworms)], dtype=np.float)
        self.images[index].score_deathselect = np.array([np.nan for i in range(nworms)], dtype=np.float)
        self.images[index].step = StepDetect
        return True
