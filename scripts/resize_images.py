import optparse
import os, signal
from lifespan.analyzing.image_manager import get_file_list
from lifespan.common.utils import ProgressBar
from threading import Semaphore
import cv2
import numpy as np

parser = optparse.OptionParser("python resize_images.py --root <origin_data_root> --dest <target_dest> --plate <plate> --prefix [prefix] --suffix [suffix] --ratio [ratio]")

parser.add_option("--root", dest="root", type="string", help="Root directory containing the original datas")
parser.add_option("--dest", dest="dest", type="string", help="Destination directory to save the resized")
parser.add_option("--plate", dest="plate", type="string", help="Which plate to resize")
parser.add_option("--ratio", dest="ratio", type="string", help="Resize ratio", default="1")
parser.add_option("--prefix", dest="prefix", type="string", help="Filename prefix", default="{plate}__")
parser.add_option("--suffix", dest="suffix", type="string", help="Filename suffix", default=".resize-{ratio}")
parser.add_option("--format", dest="format", type="string", help="Filename suffix", default="jpeg")
parser.add_option("--start", dest="starttime", type="string", help="Start time (format: YYYY-MM-DD__hh-mm-ss)")
parser.add_option("--end", dest="endtime", type="string", help="End time (format: YYYY-MM-DD__hh-mm-ss)")

args, _ = parser.parse_args()
args.root = os.path.expanduser(args.root)
args.dest = os.path.expanduser(args.dest)
args.prefix = args.prefix.format(**args.__dict__)
args.suffix = args.suffix.format(**args.__dict__)
args.ratio = float(args.ratio)
args.format = args.format.lower()

format_infos = {
    "tiff": {
        "suffix": ".tiff",
        "params": []
    },
    "jpeg": {
        "suffix": ".jpg",
        "params": [cv2.IMWRITE_JPEG_QUALITY, 80]
    }
}
format_infos["tif"] = format_infos["tiff"]
format_infos["jpg"] = format_infos["jpeg"]

sem = Semaphore()

def sigint_handler(arg1, arg2):
    sem.acquire()
    print("exit because keyboard interrupt")
    exit(1)
    sem.release()
signal.signal(signal.SIGINT, sigint_handler)

filelist = get_file_list(args.root, args.plate, starttime=args.starttime, endtime=args.endtime)
prgbar = ProgressBar(maxval=len(filelist))
for i in range(len(filelist)):
    prgbar.update(i, "reading")
    fileitem = filelist[i]
    filename = args.prefix + fileitem.subdir + args.suffix + format_infos[args.format]["suffix"]
    filepath = os.path.join(args.dest, filename)
    if os.path.exists(filepath):
        continue
    filedir, filename = os.path.split(filepath)
    if not os.path.exists(filedir):
        os.makedirs(filedir)
    tmpfilepath = os.path.join(filedir, "~" + filename)
    img = cv2.imread(fileitem.path, cv2.IMREAD_UNCHANGED)
    prgbar.update(i, "resizing")
    if args.ratio != 1:
        resized_shape = np.round(np.array(img.shape) * args.ratio).astype(np.int32)
        resized_shape = (resized_shape[1], resized_shape[0])
        img = cv2.resize(img, resized_shape)
    prgbar.update(i, "writing")
    cv2.imwrite(tmpfilepath, img, format_infos[args.format]["params"])
    prgbar.update(i, "relinking")
    sem.acquire()
    os.rename(tmpfilepath, filepath)
    sem.release()
prgbar.finish()
