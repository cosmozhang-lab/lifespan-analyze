import lifespan.mainparams as mp
import lifespan.main_load_files
import lifespan.main_preproc
import lifespan.main_analyze

# This must be imported as the last package because it will cause lifespan modules execute immediately
import userparam

try:
    reload
except Exception as e:
    from importlib import reload

def maintest():
    reload(userparam)
    reload(lifespan.main_load_files)
    reload(lifespan.main_preproc)
    reload(lifespan.main_analyze)

maintest()
