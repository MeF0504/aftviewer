import os

from . import show_image_ndarray
from pymeflib.xpm_loader import XPMLoader


def main(fpath, args):
    xpm = XPMLoader(fpath)
    xpm.xpm_to_ndarray()
    data = xpm.ndarray

    show_image_ndarray(data, os.path.basename(fpath), args)
