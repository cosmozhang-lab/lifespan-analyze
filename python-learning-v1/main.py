import os
from lifespan.trainer import Trainer

datasetsdir = os.path.join(os.path.dirname(__file__), "datasets")
if not os.path.exist(datasetsdir): os.mkdir(datasetsdir)
datasetdir = os.path.join(datasetsdir, "MNIST")

trainer = Trainer(datasetsdir)
