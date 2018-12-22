import os
from lifespan.trainer import Trainer
import userconfig

datasetdir = userconfig.datasetdir
if not os.path.exists(datasetdir): os.mkdir(datasetdir)

trainer = Trainer(datasetdir, generate_from=userconfig.datamark_storage, device=userconfig.device)

trainer.train(with_test=True, log_steps=200)
