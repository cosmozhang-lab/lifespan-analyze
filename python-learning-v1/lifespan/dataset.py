import torch
from torch.utils.data import Dataset as TorchDataset
import os
import numpy as np
from scipy.io import loadmat, savemat
from . import mainparams as mp
import re
import random

def generate_dataset(fromdir, todir):
    def walk_and_list_files(rootdir, suffix):
        suffix = suffix.lower()
        ret = []
        files = [os.path.join(rootdir, item) for item in os.listdir(rootdir)]
        for item in files:
            if os.path.isdir(item):
                ret += walk_and_list_files(item, suffix)
            elif item.split(".")[-1].lower() == suffix:
                ret.append(item)
        return ret
    files = walk_and_list_files(fromdir, "mat")
    print("generating dataset from %s" % fromdir)
    def log(message):
        logfile = open(os.path.join(todir, "generate.log"), "a")
        logfile.write(message + "\n")
        logfile.close()
    import progressbar
    prgbar = progressbar.ProgressBar(maxval=len(files), widgets=[
                progressbar.Bar("#"),
                progressbar.Counter(" %(value)d/%(max_value)d"),
                progressbar.ETA(format             = "  %(elapsed)s (ETA: %(eta)s)",
                                format_finished    = "  %(elapsed)s",
                                format_not_started = "  --:--:-- (ETA: --:--:--)")
            ])
    counter = 0
    for file in files:
        data = loadmat(file)
        image = data["img"]
        bwlworms = data["bwlworms"]
        regions = data["regions"]
        regiontypes = data["regiontypes"].flatten()
        regionids = data["regionids"].flatten()
        name = re.match(r"(^.+\/)?([^\/]+)\.\w+$", file).group(2)
        ignored = 0
        generated = 0
        for i in range(len(regionids)):
            regiontype = int(regiontypes[i])
            if regiontype == 1:
                target = True
            elif regiontype == 2:
                target = False
            else:
                ignored += 1
                continue
            rx,ry,rw,rh = tuple(regions[i,:])
            mw,mh = mp.marksize
            imw,imh = tuple(image.shape)
            if rw < mw: rx = min(imw-mw, max(0, int(rx-(mw-rw)/2)))
            if rh < mh: ry = min(imh-mh, max(0, int(ry-(mh-rh)/2)))
            if rw > mw or rh > mh:
                ignored += 1
                log("Warning: ignored region because it is too large. @%s #%d" % (name, int(regionids[i])))
                continue
            img_piece = image[ry:ry+mh, rx:rx+mw].astype(np.uint8)
            bw_piece = (bwlworms[ry:ry+mh, rx:rx+mw] == int(regionids[i])).astype(np.uint8)
            savemat(os.path.join(todir, name + "__%03d.mat" % i), {
                    "img": img_piece,
                    "bw": bw_piece,
                    "target": np.array(target)
                })
            generated += 1
        log("Completed %s, %d samples generated, %d regions ignored" % (name, generated, ignored))
        counter += 1
        prgbar.update(counter)
        continue
    prgbar.finish()



class Dataset(TorchDataset):
    def __init__(self, root=None, generate_from=None, _empty=False):
        if _empty:
            self.root = None
            self.files = None
            return
        self.root = root
        if root is None:
            raise ValueError("root directory is not given")
        if not os.path.isdir(root) or len(os.listdir(root)) == 0:
            if generate_from is None:
                raise ValueError("root directory is empty")
            print("root directory is empty, generate from %s" % generate_from)
            if not os.path.isdir(generate_from):
                raise ValueError("directory %s does not exist" % generate_from)
            if not os.path.isdir(root):
                os.makedirs(root)
            generate_dataset(generate_from, root)
        files = os.listdir(root)
        files = list(filter(lambda filename: os.path.isfile(os.path.join(root, filename)) and filename.split(".")[-1].lower() == "mat", files))
        self.files = files
    def __len__(self):
        return len(self.files)
    def __getitem__(self, index):
        if isinstance(index, str):
            return self.get_by_name(index)
        elif isinstance(index, int):
            return self.get_by_file(self.files[index])
        elif isinstance(index, slice):
            return [self.get_by_file(file) for file in self.files[index]]
        else:
            raise ValueError("indexing is not valid")
    def get_by_name(self, name):
        for file in self.files:
            if name == re.match(r"(^.+\/)?([^\/]+)\.\w+$", file).group(2):
                return self.get_by_file(file)
    def get_by_file(self, file):
        data = loadmat(os.path.join(self.root, file))
        img = torch.FloatTensor(data["img"]) / 255.0
        bw = torch.FloatTensor(data["bw"])
        img = torch.stack([img, bw], dim=0)
        label = torch.FloatTensor(data["target"].flatten())
        return (img, label)
    def copy(self):
        dataset = Dataset(_empty=True)
        dataset.root = self.root
        dataset.files = [file for file in self.files]
    def shuffle_(self):
        random.shuffle(self.files)
        return self
    def shuffle(self):
        ret = self.copy()
        return ret.shuffle_()
    def split(self, proportions):
        sumproportions = float(np.sum(proportions))
        for p in proportions: sumproportions += float(p)
        proportions = [float(p) / sumproportions for p in proportions]
        total = len(self.files)
        lengths = [round(total*p) for p in proportions]
        ret = []
        start = 0
        for length in lengths:
            end = start + length
            if end > total: end = total
            subset = Dataset(_empty=True)
            subset.root = self.root
            subset.files = self.files[start:end]
            ret.append(subset)
            start = end
        return proportions.__class__(ret)




