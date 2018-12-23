import os
from learning.trainer import Trainer
from learning.dataset import delete_dataset
import userconfig

datasetdir = userconfig.datasetdir
if userconfig.clear_dataset:
    delete_dataset(datasetdir)
if not os.path.exists(datasetdir): os.mkdir(datasetdir)

model_path = userconfig.model_path
if userconfig.clear_model:
    Trainer.clear_model(model_path)
load_model = model_path if userconfig.load_model else None
trainer = Trainer(datasetdir, generate_from=userconfig.datamark_storage, device=userconfig.device, load_model=load_model)
save_model = model_path if userconfig.save_model else None
trainer.train(with_test=True, log_steps=200, save_model=save_model)
