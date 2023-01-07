import os
import sys
from pathlib import Path

import rawpy

sys.path.append(str(Path(__file__).parent.parent))
from . import show_image_ndarray


def main(fpath, args):
    with rawpy.imread(str(fpath)) as raw:
        rgb = raw.postprocess(demosaic_algorithm=rawpy.DemosaicAlgorithm.LINEAR)

    show_image_ndarray(rgb, os.path.basename(fpath), args)