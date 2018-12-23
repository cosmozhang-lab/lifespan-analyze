import numpy as np
import os
from torch.optim import SGD as SGDOptimizer
import torch
from torch.utils.data import DataLoader
from .dataset import Dataset
import torchvision.transforms as transforms
from .discriminator import Discriminator
from .torchutils import OneHotTransform
import time
import re

class Trainer:
    def __init__(self, datasetdir=None, generate_from=None, device="cpu", load_model=None, soft_load=True):
        self.stepid = 0
        if load_model:
            if Trainer.model_exists(load_model):
                print("load model from %s" % load_model)
                self.net, self.stepid = Trainer.load_model(load_model)
            elif soft_load:
                print("model %s doesn't exist, build a new model" % load_model)
                self.net = Discriminator()
            else:
                raise IOError("failed to load model %s" % load_model)
        else:
            print("build a new model")
            self.net = Discriminator()
        self.device = torch.device(device)
        self.net.to(self.device)
        print("Using device:", self.device)
        self.optimizer = SGDOptimizer(self.net.parameters(), lr=0.01)
        self.dataset = Dataset(datasetdir, generate_from=generate_from).shuffle_()
        self.trainset, self.testset = self.dataset.split((8,2))
        self.trainset_loader = DataLoader(self.trainset, batch_size=4, shuffle=True)
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
    def train(self, epochs=None, steps=None, with_test=False, log_steps=-1, save_steps=-1, save_model=None):
        epoch_counter = 0
        step_counter = 0
        ts = time.time()
        if save_model:
            saved_filepath = Trainer.save_model(self.net, save_model)
            print("model saved to %s" % saved_filepath)
        while True:
            print("Epoch #%d" % epoch_counter)
            for local_step, batchdata in enumerate(self.trainset_loader):
                logstep = ((step_counter % log_steps) == 0) if (log_steps > 0) else (local_step == 0)
                savestep = ((step_counter % save_steps) == 0) if (save_steps > 0) else (local_step == 0)
                if with_test and logstep:
                    batchinput, batchlabel = next(iter(self.testset_loader))
                    testloss, testacc = self.test_step(batchinput, batchlabel)
                if savestep and save_model:
                    saved_filepath = Trainer.save_params(self.net, save_model, self.stepid)
                    print("   model params saved to %s" % saved_filepath)
                    self.stepid += 1
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

    def save_model(net, save_name):
        filename = save_name + ".model.pkl"
        dirname = os.path.dirname(filename)
        if not os.path.isdir(dirname): os.makedirs(dirname)
        torch.save(net, filename)
        return filename
    def save_params(net, save_name, stepid):
        filename = save_name + ".params.%04d.pkl" % stepid
        dirname = os.path.dirname(filename)
        if not os.path.isdir(dirname): os.makedirs(dirname)
        torch.save(net.state_dict(), filename)
        return filename
    def load_model(save_name):
        filepath = save_name + ".model.pkl"
        if not os.path.isfile(filepath):
            raise IOError("model file %s does not exist")
        net = torch.load(filepath)
        dirname, filename = os.path.split(save_name)
        regexp = re.compile(r"^" + filename + r"\.params\.(\d+)\.pkl$")
        filenames = os.listdir(dirname)
        filenames = list(map(lambda item: re.match(regexp, item), filenames))
        filenames = list(filter(lambda item: not item is None, filenames))
        filenames = sorted(filenames, key = lambda item: int(item.group(1)))
        stepid = 0
        if len(filenames) > 0:
            filename = filenames[-1].group(0)
            stepid = int(filenames[-1].group(1)) + 1
            filepath = os.path.join(dirname, filename)
            net.load_state_dict(torch.load(filepath))
        return (net, stepid)
    def model_exists(save_name):
        filepath = save_name + ".model.pkl"
        if not os.path.isfile(filepath):
            return False
        return True
    def clear_model(save_name):
        dirname, filename = os.path.split(save_name)
        if not os.path.isdir(dirname):
            return
        filenames = os.listdir(dirname)
        filenames = list(filter(lambda item: item.split(".")[0] == filename, filenames))
        for filename in filenames:
            os.remove(os.path.join(dirname, filename))

