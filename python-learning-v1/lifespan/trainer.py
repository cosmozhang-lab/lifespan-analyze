import numpy as np
import os
from torch.optim import SGD as SGDOptimizer
import torch
from torch.utils.data import DataLoader
from torchvision.datasets import MNIST
import torchvision.transforms as transforms
from .discriminator import WormDiscriminator
from .torchutils import OneHotTransform
import time

class Trainer:
    def __init__(self, datasetdir, batchsize=32, device="cpu"):
        self.net = WormDiscriminator()
        self.device = torch.device(device)
        self.net.to(self.device)
        print("Using device:", self.device)
        self.optimizer = SGDOptimizer(self.net.parameters(), lr=0.01)
        self.batchsize = batchsize
        self.trainset = MNIST(datasetdir, train=True, download=True,
            transform=transforms.Compose([transforms.ToTensor()]))
        self.trainset_loader = DataLoader(self.trainset, batch_size=32, shuffle=True)
        self.testset = MNIST(datasetdir, train=False, download=True,
            transform=transforms.Compose([transforms.ToTensor()]))
        self.testset_loader = DataLoader(self.testset, batch_size=32, shuffle=True)
    def train_step(self, batchinput, batchlabel):
        batchinput = batchinput.to(self.device)
        batchlabel = batchlabel.to(self.device)
        self.optimizer.zero_grad()
        output = self.net(batchinput)
        acc = self.net.accuracy(output, batchlabel)
        loss = self.net.loss(output, batchlabel)
        loss.backward()
        self.optimizer.step()
        return loss, acc
    def test_step(self, batchinput, batchlabel):
        batchinput = batchinput.to(self.device)
        batchlabel = batchlabel.to(self.device)
        output = self.net(batchinput)
        acc = self.net.accuracy(output, batchlabel)
        loss = self.net.loss(output, batchlabel)
        return loss, acc
    def train(self, epochs=None, steps=None, with_test=False, log_steps=-1):
        epoch_counter = 0
        step_counter = 0
        ts = time.time()
        while True:
            print("Epoch #%d" % epoch_counter)
            for local_step, batchdata in enumerate(self.trainset_loader):
                logstep = ((step_counter % log_steps) == 0) if (log_steps > 0) else (local_step == 0)
                if with_test and logstep:
                    batchinput, batchlabel = next(iter(self.testset_loader))
                    testloss, testacc = self.test_step(batchinput, batchlabel)
                batchinput, batchlabel = batchdata
                trainloss, trainacc = self.train_step(batchinput, batchlabel)
                if logstep:
                    if with_test:
                        print("   % 4d  loss = %f    acc = %.1f%% (train) / %1.f%% (test)    time = %.2fs" % (step_counter, trainloss, trainacc*100, testacc*100, time.time() - ts))
                    else:
                        print("   % 4d  loss = %f    acc = %.1f%% (train)    time = %.2fs" % (step_counter, trainloss, trainacc*100, time.time() - ts))
                    ts = time.time()
                step_counter += 1
                if steps and step_counter >= steps:
                    break
            if steps and step_counter >= steps:
                break
            epoch_counter += 1
            if epochs and epoch_counter >= epochs:
                break
