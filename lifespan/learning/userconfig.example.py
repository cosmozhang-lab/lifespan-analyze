import os
from .defaultconfig import *

# datasetdir = os.path.expanduser("~/temp")
datasetdir = "/path/to/dataset"
datamark_storage = "/path/to/datamark/storage"
dataset_info_path = os.path.expanduser("~/temp/dataset-info")
device = "cuda:0"
clear_dataset = False
clear_model = False
load_model = True
save_model = True
model_path = "/path/to/models/prefix"
run_datasets_output = os.path.expanduser("~/temp/run")
