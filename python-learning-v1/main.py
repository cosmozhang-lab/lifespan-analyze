import os
from lifespan.trainer import Trainer
import userconfig

datasetdir = userconfig.datasetdir
if not os.path.exists(datasetdir): os.mkdir(datasetdir)

trainer = Trainer(datasetdir, device=userconfig.device)

trainer.train(with_test=True)
