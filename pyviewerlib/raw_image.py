import os

import rawpy

from . import show_image_ndarray, help_template


def show_help():
    helpmsg = help_template('raw_image', 'show a raw image using "rawpy".')
    print(helpmsg)


def main(fpath, args):
    with rawpy.imread(str(fpath)) as raw:
        rgb = raw.postprocess(demosaic_algorithm=rawpy.DemosaicAlgorithm.LINEAR)

    show_image_ndarray(rgb, os.path.basename(fpath), args)
