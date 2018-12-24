import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as functional
from .torchutils import DiscriminatorAccuracy

class Discriminator(nn.Module):
    def __init__(self):
        super().__init__()
        # trainable layers
        # input: 2x256x256
        self.conv1 = nn.Conv2d(2, 8, 5, padding=2) # 8x256x256
        self.pool1 = nn.MaxPool2d(2) # 8x128x128
        self.conv2 = nn.Conv2d(8, 32, 5, padding=2) # 32x128x128
        self.pool2 = nn.MaxPool2d(2) # 32x64x64
        self.conv3 = nn.Conv2d(32, 96, 5, padding=2) # 96x64x64
        self.pool3 = nn.MaxPool2d(4) # 96x16x16
        self.conv4 = nn.Conv2d(96, 256, 5, padding=2) # 256x16x16
        self.pool4 = nn.MaxPool2d(4) # 256x4x4
        self.num_flat_features = 4096
        self.fc1 = nn.Linear(4096, 1024)
        self.fc2 = nn.Linear(1024, 256)
        self.fc3 = nn.Linear(256, 1)
        # loss function
        self.loss = nn.MSELoss()
        self.accuracy = DiscriminatorAccuracy()
    def forward(self, x):
        y = x
        y = self.conv1(y)
        y = self.pool1(y)
        y = functional.relu(y)
        y = self.conv2(y)
        y = self.pool2(y)
        y = functional.relu(y)
        y = self.conv3(y)
        y = self.pool3(y)
        y = functional.relu(y)
        y = self.conv4(y)
        y = self.pool4(y)
        y = functional.relu(y)
        y = y.view((-1,self.num_flat_features))
        y = self.fc1(y)
        y = functional.relu(y)
        y = self.fc2(y)
        y = functional.relu(y)
        y = self.fc3(y)
        y = torch.sigmoid(y)
        return y
    def predict(self, x, score_th=0.5):
        y = self.forward(x)
        label = (y > float(score_th))
        return label
    def requires_grad_(self, requires_grad=True):
        for parameter in self.parameters():
            parameter.requires_grad_(requires_grad)
