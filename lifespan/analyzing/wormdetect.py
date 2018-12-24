import lifespan.common.mainparams as mp
import numpy as np, cv2, torch
import skimage
from lifespan.common.algos import fill_holes, torch_bwopen, torch_bwcentroid
from lifespan.common.imgproc import detect_worm_2d, dnn_filter_worms

def calculate_worm_centroids(bwlworms, coors=None):
    nbwl = torch.max(bwlworms)
    centroids = []
    for i in range(nbwl):
        label = i + 1
        centroid = torch_bwcentroid(bwlworms==label, coors)
        centroids.append(centroid)
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
            WormDetector.discriminator.to(torch.device("cuda"))
            WormDetector.discriminator.requires_grad_(False)
    def step(self, index):
        if self.images[index].error:
            return False
        gpuwormbwl = detect_worm_2d(self.images[index].gpuimage)
        if mp.dnn_discriminate:
            gpuwormbwl = dnn_filter_worms(self.images[index].gpuimage, gpuwormbwl, WormDetector.discriminator, coors=self.images.coors, default_adopt=True)
        gpuwormbw = gpuwormbwl > 0
        self.images[index].gpuwormbw = gpuwormbw
        self.images[index].wormbw = gpuwormbw.cpu().numpy()
        self.images[index].wormcentroids = calculate_worm_centroids(gpuwormbwl, self.images.coors)
        return True
