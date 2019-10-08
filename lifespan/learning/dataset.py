import torch
from torch.utils.data import Dataset as TorchDataset
import os
import numpy as np
from scipy.io import loadmat, savemat
import lifespan.common.mainparams as mp
from lifespan.common.algos import make_coors
from lifespan.common.geo import Rect
import re
import random
import shutil

def prepare_image(image, bwlworms, regions=None, regionids=None, coors=None):
    class ImagePiece:
        def __init__(self, wid, data):
            self.wid = wid
            self.data = data
    if regions is None or regionids is None:
        if coors is None:
            coors = make_coors(image=bwlworms)
    regions_given = not regions is None and not regionids is None
    nbwl = len(regionids) if regions_given else bwlworms.max()
    if isinstance(image, np.ndarray): fimage = image.astype(np.float)
    elif isinstance(image, torch.Tensor): fimage = image.type(torch.float)
    fplatepxs = fimage[fimage>mp.plate_threshold]
    if len(fplatepxs) == 0: return []
    imgmean = fplatepxs.mean()
    imgstd = fplatepxs.std()
    piece_datas = []
    for i in range(nbwl):
        if not regions_given:
            label = i + 1
            bw = (bwlworms == label)
            if isinstance(bw, np.ndarray): fbw = bw.astype(np.float)
            elif isinstance(bw, torch.Tensor): fbw = bw.type(torch.float)
            coorx = fbw * coors[1]
            coory = fbw * coors[0]
            maxcoorx = int(coorx.max())
            maxcoory = int(coory.max())
            coorx[coorx == 0] = mp.imagesize[1]
            coory[coory == 0] = mp.imagesize[0]
            mincoorx = int(coorx.min())
            mincoory = int(coory.min())
            rx = mincoorx
            ry = mincoory
            rw = maxcoorx - mincoorx + 1
            rh = maxcoory - mincoory + 1
            rid = label
        else:
            rx,ry,rw,rh = tuple(regions[i,:])
            rid = int(regionids[i])
        mw,mh = mp.marksize
        imw,imh = mp.imagesize
        if rw < mw: rx = min(imw-mw, max(0, int(rx-(mw-rw)/2)))
        if rh < mh: ry = min(imh-mh, max(0, int(ry-(mh-rh)/2)))
        if rw > mw or rh > mh:
            piece_datas.append(ImagePiece(rid, None))
            continue
        img_piece = image[ry:ry+mh, rx:rx+mw]
        bw_piece = (bwlworms[ry:ry+mh, rx:rx+mw] == rid)
        if isinstance(image, np.ndarray):
            img_piece = img_piece.astype(np.float)
            bw_piece = bw_piece.astype(np.float)
            img_piece = (img_piece-imgmean)/imgstd
            data = np.stack([img_piece,bw_piece], axis=0)
        elif isinstance(image, torch.Tensor):
            img_piece = img_piece.type(torch.float)
            bw_piece = bw_piece.type(torch.float)
            img_piece = (img_piece-imgmean)/imgstd
            data = torch.stack([img_piece,bw_piece], dim=0)
        piece_datas.append(ImagePiece(rid, data))
    return piece_datas


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
        regionvalid = (regiontypes == 1) | (regiontypes == 2)
        regions = regions[regionvalid,:]
        regiontypes = regiontypes[regionvalid]
        regionids = regionids[regionvalid]
        name = re.match(r"(^.+\/)?([^\/]+)\.\w+$", file).group(2)
        ignored = int((~regionvalid).sum())
        generated = 0
        for i, piece in enumerate(prepare_image(image, bwlworms, regions=regions, regionids=regionids)):
            regiontype = int(regiontypes[i])
            if regiontype == 1:
                target = True
            elif regiontype == 2:
                target = False
            else:
                raise ValueError("boooooom")
            if piece.data is None:
                ignored += 1
                log("Warning: ignored region because it is too large. @%s #%d" % (name, int(regionids[i])))
                continue
            savemat(os.path.join(todir, name + "__%03d.mat" % i), {
                    "data": piece.data,
                    "target": np.array(target)
                })
            generated += 1
        log("Completed %s, %d samples generated, %d regions ignored" % (name, generated, ignored))
        counter += 1
        prgbar.update(counter)
        continue
    prgbar.finish()

def delete_dataset(datasetdir):
    shutil.rmtree(datasetdir)



class DatasetSummary:
    def __init__(self, total=None, positive=None, negative=None):
        self.total = total
        self.positive = positive
        self.negative = negative



class Dataset(TorchDataset):
    def __init__(self, root=None, generate_from=None, info_file=None, join=None, _empty=False):
        if _empty:
            self.root = None
            self.files = None
            return
        if not join is None:
            if len(join) == 0:
                raise ValueError("join list is empty")
            self.root = join[0].root
            self.files = []
            for item in join:
                if item.root != self.root:
                    raise ValueError("datasets in join list do not have the same root")
                self.files = self.files + item.files
            return
        if info_file:
            if os.path.isfile(info_file):
                self.load_info(info_file)
            else:
                raise IOError("cannot load dataset info from %s (file does not exist)" % info_file)
            return
        if root is None:
            raise ValueError("root directory is not given")
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
        label = torch.FloatTensor(data["target"].flatten())
        data = torch.FloatTensor(data["data"])
        return (data, label)
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
        grouped_files = {}
        for filename in self.files:
            platename = filename.split("__")[0]
            if not platename in grouped_files:
                grouped_files[platename] = []
            grouped_files[platename].append(filename)
        grouped_files_list = []
        for platename in grouped_files:
            grouped_files_list.append({
                "plate": platename,
                "count": len(grouped_files[platename]),
                "files": grouped_files[platename]
            })
        # random.shuffle(grouped_files_list)
        sumproportions = float(np.sum(proportions))
        proportions = [float(p) / sumproportions for p in proportions]
        total = len(grouped_files_list)
        lengths = [round(total*p) for p in proportions]
        ret = []
        start = 0
        for length in lengths:
            end = start + length
            if end > total: end = total
            subset = Dataset(_empty=True)
            subset.root = self.root
            groups = grouped_files_list[start:end]
            files = []
            for group in groups:
                files += group["files"]
            subset.files = files
            ret.append(subset)
            start = end
        return proportions.__class__(ret)
    def check(self):
        positive = 0
        negative = 0
        for i in range(len(self)):
            img,label = self[i]
            if label: positive += 1
            else: negative += 1
        return DatasetSummary(total=len(self), positive=positive, negative=negative)
    def save_info(self, filepath, indent=None):
        import json
        filecontent = json.dumps({
                "root": self.root,
                "files": self.files
            }, indent=indent)
        file = open(filepath, "wb")
        file.write(filecontent.encode("utf-8"))
        file.close()
    def load_info(self, filepath):
        import json
        file = open(filepath, "rb")
        filecontent = file.read().decode("utf-8")
        file.close()
        jsondict = json.loads(filecontent)
        self.root = jsondict["root"]
        self.files = jsondict["files"]




