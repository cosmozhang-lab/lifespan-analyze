import numpy as np
import os
from torch.optim import SGD as SGDOptimizer
from torch.utils.data import DataLoader
from torchvision.datasets import MNIST
import torchvision.transforms as transforms
from .discriminator import WormDiscriminator

class Trainer:
    def __init__(self, datasetdir, batchsize=32):
        self.net = WormDiscriminator()
        self.optimizer = SGDOptimizer(self.net.parameters())
        self.batchsize = batchsize
        self.dataset = MNIST(datasetdir, download=True,
            transform=transforms.Compose([transforms.ToTensor()]),
            target_transform=transforms.Compose([transforms.]))
        self.dataiter = iter(DataLoader(self.dataset, batch_size=32, shuffle=True))
    def train_step(self):
        # TODO
