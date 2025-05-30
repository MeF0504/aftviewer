import os
from logging import getLogger

from .. import (GLOBAL_CONF, show_image_ndarray, help_template,
                add_args_imageviewer)
from pymeflib.xpm_loader import XPMLoader
logger = getLogger(GLOBAL_CONF.logname)


def add_args(parser):
    add_args_imageviewer(parser)


def show_help():
    helpmsg = help_template('xpm', 'show an xpm file as an image.', add_args)
    print(helpmsg)


def main(fpath, args):
    xpm = XPMLoader(fpath, logger=logger)
    xpm.xpm_to_ndarray()
    data = xpm.ndarray

    show_image_ndarray(data, os.path.basename(fpath), args)
