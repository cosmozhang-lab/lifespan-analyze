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
    def __init__(self, datasetdir=None, generate_from=None, device="cpu", load_model=None, soft_load=True, dataset_info_path=None):
        self.stepid = 0
        self.epochid = 0
        self.net = Discriminator()
        if load_model:
            if Trainer.model_param_exists(load_model):
                self.stepid, self.epochid = Trainer.load_model_params(self.net, load_model)
            elif not soft_load:
                raise IOError("model params %s does not exist" % load_model)
        self.device = torch.device(device)
        self.net.to(self.device)
        print("Using device:", self.device)
        self.optimizer = SGDOptimizer(self.net.parameters(), lr=0.01)
        if dataset_info_path is None:
            trainset_info_path = None
            testset_info_path = None
        else:
            dataset_info_dir = os.path.dirname(dataset_info_path)
            if not os.path.isdir(dataset_info_dir): os.makedirs(dataset_info_dir)
            trainset_info_path = dataset_info_path + ".train.json"
            testset_info_path = dataset_info_path + ".test.json"
        if trainset_info_path and testset_info_path and os.path.isfile(trainset_info_path) and os.path.isfile(testset_info_path):
            print("load dataset<train> from %s" % trainset_info_path)
            print("load dataset<test> from %s" % trainset_info_path)
            self.trainset = Dataset(info_file=trainset_info_path)
            self.testset = Dataset(info_file=testset_info_path)
            self.dataset = Dataset(join=[self.trainset,self.testset])
        else:
            print("load dataset from %s" % datasetdir)
            self.dataset = Dataset(datasetdir, generate_from=generate_from).shuffle_()
            self.trainset, self.testset = self.dataset.split((8,2))
            if trainset_info_path and testset_info_path:
                self.trainset.save_info(trainset_info_path)
                self.testset.save_info(testset_info_path)
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
        while True:
            print("Epoch #%d" % self.epochid)
            for local_step, batchdata in enumerate(self.trainset_loader):
                logstep = ((step_counter % log_steps) == 0) if (log_steps > 0) else (local_step == 0)
                savestep = ((step_counter % save_steps) == 0) if (save_steps > 0) else (local_step == 0)
                if with_test and logstep:
                    batchinput, batchlabel = next(iter(self.testset_loader))
                    testloss, testacc = self.test_step(batchinput, batchlabel)
                if savestep and save_model:
                    saved_filepath = Trainer.save_model_params(self.net, save_model, stepid=self.stepid, epochid=self.epochid)
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
            self.epochid += 1
            if epochs and epoch_counter >= epochs:
                break

    def save_model(net, save_name):
        filename = save_name + ".model.pkl"
        dirname = os.path.dirname(filename)
        if not os.path.isdir(dirname): os.makedirs(dirname)
        torch.save(net, filename)
        return filename
    def save_model_params(net, save_name, stepid=0, epochid=0):
        filename = save_name + ".params.%04d.pkl" % stepid
        dirname = os.path.dirname(filename)
        if not os.path.isdir(dirname): os.makedirs(dirname)
        torch.save({
            "model_state": net.state_dict(),
            "step": stepid,
            "epoch": epochid
        }, filename)
        return filename
    def load_model(save_name, log=True):
        filepath = save_name + ".model.pkl"
        if not os.path.isfile(filepath):
            raise IOError("model file %s does not exist")
        net = torch.load(filepath)
        if log: print("load model from %s" % filepath)
        Trainer.load_model_params(net, save_name, log=log)
        return net
    def load_model_params(net, save_name, log=True):
        dirname, filename = os.path.split(save_name)
        regexp = re.compile(r"^" + filename + r"\.params\.(\d+)\.pkl$")
        filenames = os.listdir(dirname)
        filenames = list(map(lambda item: re.match(regexp, item), filenames))
        filenames = list(filter(lambda item: not item is None, filenames))
        filenames = sorted(filenames, key = lambda item: int(item.group(1)))
        stepid = 0
        epochid = 0
        if len(filenames) > 0:
            filename = filenames[-1].group(0)
            filepath = os.path.join(dirname, filename)
            saveddata = torch.load(filepath)
            net.load_state_dict(saveddata["model_state"])
            epochid = saveddata["epoch"]
            stepid = saveddata["step"]
            if log: print("load model params from %s" % filepath)
        return (stepid, epochid)
    def model_exists(save_name):
        filepath = save_name + ".model.pkl"
        if not os.path.isfile(filepath):
            return False
        return True
    def model_param_exists(save_name):
        dirname, filename = os.path.split(save_name)
        if not os.path.isdir(dirname):
            return False
        regexp = re.compile(r"^" + filename + r"\.params\.(\d+)\.pkl$")
        filenames = os.listdir(dirname)
        filenames = list(map(lambda item: re.match(regexp, item), filenames))
        filenames = list(filter(lambda item: not item is None, filenames))
        if len(filenames) == 0:
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

    def check_dataset(self):
        print("checking dataset <train>...")
        summary = self.trainset.check()
        print("dataset <train> info: total %d (pos: %d / neg: %d)" % (summary.total, summary.positive, summary.negative))
        print("checking dataset <test>...")
        summary = self.testset.check()
        print("dataset <test> info: total %d (pos: %d / neg: %d)" % (summary.total, summary.positive, summary.negative))


    def run_dataset(self, dataset, batchsize=4):
        requires_grad = self.net.requires_grad
        if requires_grad: self.net.requires_grad_(False)
        loader = DataLoader(self.trainset, batch_size=batchsize)
        labels = []
        scores = []
        for i, batchdata in enumerate(loader):
            batchinput, batchlabel = batchdata
            batchscore = self.net(batchinput)
            labels += list(batchlabel.numpy().flatten())
            scores += list(batchscore.numpy().flatten())
        return RunResult(labels=labels, scores=scores)


class RunResult:
    def __init__(self, labels=None, scores=None):
        self.labels = np.array(labels, dtype=np.bool)
        self.scores = np.array(scores, dtype=np.float)
    def stats(self, score_th):
        labels = self.labels
        predicts = self.scores > score_th
        p = predicts[labels]
        n = predicts[~labels]
        tp = p[p]
        fp = n[n]
        tn = n[~n]
        fn = p[~p]
        return RunStats(tp=tp, fp=fp, tn=tn, fn=fn)

class RunStats:
    def __init__(self, tp=None, fp=None, tn=None, fn=None):
        self.accuracy = accuracy
        self.tp = tp
        self.fp = fp
        self.tn = tn
        self.fn = fn
    @property
    def total(self):
        return self.positive + self.negative
    @property
    def positive(self):
        return self.tp + self.fn
    @property
    def negative(self):
        return self.fp + self.tn
    @property
    def true(self):
        return self.tp + self.tn
    @property
    def false(self):
        return self.fp + self.fn
    @property
    def true_positive(self):
        return self.tp
    @property
    def false_positive(self):
        return self.fp
    @property
    def true_negative(self):
        return self.tn
    @property
    def false_negative(self):
        return self.fn
    @property
    def accuracy(self):
        return self._accuracy


