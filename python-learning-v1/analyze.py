import sys, os
import torch
from learning.trainer import Trainer
import userconfig

sys.path.append(os.path.realpath(os.path.dirname(__file__)))

discriminator = Trainer.load_model(userconfig.model_path)[0]
