import os
from pathlib import Path

import rawpy

from .. import Args, show_image_ndarray, help_template, add_args_imageviewer


def add_args(parser):
    add_args_imageviewer(parser)


def show_help():
    helpmsg = help_template('raw_image', 'show a raw image using "rawpy".',
                            add_args)
    print(helpmsg)


def main(fpath: Path, args: Args) -> int:
    with rawpy.imread(str(fpath)) as raw:
        rgb = raw.postprocess(demosaic_algorithm=rawpy.DemosaicAlgorithm.LINEAR)

    ret = show_image_ndarray(rgb, os.path.basename(fpath), args)
    if ret is None:
        return 3
    elif ret:
        return 0
    else:
        return 2
