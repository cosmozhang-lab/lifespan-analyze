def run():
    import lifespan.common.mainparams as mp
    import time
    from . import userparam
    from .analyzer import Analyzer
    from lifespan.common.utils import format_duration
    for plate in userparam.plates:
        print("Task: %s" % plate)
        ts = time.time()
        analyzer = Analyzer(rootdir=userparam.rootdir, outdir=userparam.outdir, plate=plate, ifile0=userparam.ifile0, nfiles=userparam.nfiles,
                            save_jpeg=userparam.savejpeg, save_buff=userparam.savebuff, buffdir=userparam.buffdir)
        analyzer.carryout()
        te = time.time()
        print("Task %s completed, total time consume: %s\n" % (plate, format_duration(te - ts)))
