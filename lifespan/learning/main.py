import os
from .trainer import Trainer
from .dataset import delete_dataset
from . import userconfig

def get_trainer():
    datasetdir = userconfig.datasetdir
    if userconfig.clear_dataset:
        delete_dataset(datasetdir)
    if not os.path.exists(datasetdir): os.mkdir(datasetdir)
    model_path = userconfig.model_path
    if userconfig.clear_model:
        Trainer.clear_model(model_path)
    load_model = model_path if userconfig.load_model else None
    trainer = Trainer(datasetdir, generate_from=userconfig.datamark_storage, device=userconfig.device, load_model=load_model, dataset_info_path=userconfig.dataset_info_path)
    return trainer

def train():
    trainer = get_trainer()
    # trainer.dataset.check()
    save_model = userconfig.model_path if userconfig.save_model else None
    trainer.train(with_test=True, log_steps=200, save_model=save_model)

def run_datasets():
    outpath = userconfig.run_datasets_output
    outdir = os.path.dirname(outpath)
    if not os.path.isdir(outdir): os.makedirs(outdir)
    trainer = get_trainer()
    print("running on dataset<train>...")
    result = trainer.run_dataset(trainer.trainset, with_progressbar=True)
    print("finished dataset<train>. saving results...")
    result.save(outpath + ".train.mat")
    print("dataset<train> ok.")
    print("running on dataset<test>...")
    result = trainer.run_dataset(trainer.testset, with_progressbar=True)
    print("finished dataset<test>. saving results...")
    result.save(outpath + ".test.mat")
    print("dataset<test> ok.")
