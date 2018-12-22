from torch.utils.data import Dataset as TorchDataset
import os

class FileInfo:
    def __init__(self, words=None):
        self.path = None
        self.num_target = 0
        self.num_mistake = 0
        self.num_unknown = 0
        self.num_blank = 0
        if not words is None:
            self.from_words(words)
    def from_words(self, words):
        if len(words) != 5: return
        self.path = words[0]
        self.num_target = int(words[1])
        self.num_mistake = int(words[2])
        self.num_unknown = int(words[3])
        self.num_blank = int(words[4])
    def to_words(self):
        return [
            self.path,
            str(self.num_target),
            str(self.num_mistake),
            str(self.num_unknown),
            str(self.num_blank)
        ]

class Dataset(TorchDataset):
    def __init__(self, root=None, infopath=None):
        if infopath and os.path.exists(infopath):
            self.init_with_info(infopath)
        else:
            self.init_without_info(root)
            if infopath:
                self.save_info(infopath)
    def init_without_info(self, rootdir):
        if root is None:
            raise ValueError("root directory is not given")
        elif not os.path.isdir(root):
            raise ValueError("root directory \"%s\" does not exist" % root)
        self.rootdir = root
    def init_with_info(self, infopath):
        if infopath is None:
            raise ValueError("info file is not given")
        elif not os.path.isfile(infopath):
            raise ValueError("info file \"%s\" does not exist" % infopath)
        file = open(infopath, "rb")
        content = file.read().decode("utf-8")
        file.close()
        content = [line.strip() for line in content.split("\n")]
        # read header infos
        for line in content:
            if line.find(",") >= 0: break
            words = [word.strip() for word in line.split("=")]
            if len(words) < 2: continue
            if words[0] == "root":
                self.rootdir = words[1]
        # read records
        fileinfos = []
        for line in content:
            words = [word.strip() for word in line.split(",")]
            item = FileInfo(words)
            if item.path is None: continue
            fileinfos.append(item)

    def save_info(self, infopath):
        pass