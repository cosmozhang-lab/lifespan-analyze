import sys, os, re
from collections import Iterable
from .common import datetime_regfmt, parse_datetime

class FileItem:
    def __init__(self, rootdir=None, subdir=None, filename=None):
        self.rootdir = rootdir
        self.subdir = subdir
        self.filename = filename

    def from_json(jsondict):
        return FileItem(rootdir = jsondict["rootdir"],
                        subdir = jsondict["subdir"],
                        filename = jsondict["filename"])
    def to_json(self):
        jsondict = {}
        jsondict["rootdir"] = self.rootdir
        jsondict["subdir"] = self.subdir
        jsondict["filename"] = self.filename
        return jsondict

    @property
    def path(self):
        return os.path.join(self.rootdir, self.subdir, self.filename)
    @property
    def datetime(self):
        return parse_datetime(subdir)
        

class FileFinder:
    def __init__(self, rootdir):
        self.rootdir = rootdir
    def get_file_lists(self, plates, ifile0=None, nfiles=None):
        import re
        if not isinstance(plates, Iterable):
            plates = [plates]
        ifile0 = ifile0 or 0
        filelists = {}
        for plate in plates:
            filelists[plate] = []
        filelist = os.listdir(self.rootdir)
        filelist = list(filter(
                        lambda xx: not re.match(datetime_regfmt, xx) is None,
                        filelist
                    ))
        filelist.sort()
        # filelist.sort(key=(lambda x: x.datetime))
        for subdir in filelist:
            filenames = os.listdir(os.path.join(self.rootdir, subdir))
            for filename in filenames:
                platename = filename.split('.')[0]
                if platename in plates:
                    filelists[platename].append(FileItem(self.rootdir, subdir, filename))
        for plate in plates:
            if nfiles is None:
                filelists[plate] = filelists[plate][ifile0:]
            else:
                filelists[plate] = filelists[plate][ifile0:nfiles]
        return filelists
