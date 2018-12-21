import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as functional
from .torchutils import Accuracy

class WormDiscriminator(nn.Module):
    def __init__(self):
        super().__init__()
        # trainable layers
        # input: 1x28x28
        self.conv1 = nn.Conv2d(1, 6, 5) # 6x24x24
        self.pool1 = nn.MaxPool2d(2) # 6x12x12
        self.conv2 = nn.Conv2d(6, 16, 5) # 16x8x8
        self.pool2 = nn.MaxPool2d(2) # 16x4x4
        self.conv3 = nn.Conv2d(16, 32, 3) # 32x2x2
        self.pool3 = nn.MaxPool2d(2) # 32x1x1
        self.num_flat_features = 32
        self.fc = nn.Linear(32, 10)
        # non-linear functions
        self.nl = functional.relu
        # loss function
        self.loss = nn.CrossEntropyLoss()
        self.accuracy = Accuracy()
    def forward(self, x):
        y = x
        y = self.conv1(y)
        y = self.pool1(y)
        y = self.nl(y)
        y = self.conv2(y)
        y = self.pool2(y)
        y = self.nl(y)
        y = self.conv3(y)
        y = self.pool3(y)
        y = self.nl(y)
        y = y.view((-1,self.num_flat_features))
        y = self.fc(y)
        return y
