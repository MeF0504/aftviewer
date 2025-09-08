import os
import sys
import tempfile
from logging import getLogger

from aftviewer import GLOBAL_CONF, print_error
from libsixel.encoder import Encoder, SIXEL_OPTFLAG_WIDTH, SIXEL_OPTFLAG_COLORS
from pymeflib.color import make_bitmap

logger = getLogger(GLOBAL_CONF.logname)


def show_image_file(img_file: str) -> bool:
    if not os.path.isfile(img_file):
        print_error(f'file not found: {img_file}', file=sys.stderr)
        return False
    encoder = Encoder()
    encoder.setopt(SIXEL_OPTFLAG_WIDTH, '300')
    encoder.setopt(SIXEL_OPTFLAG_COLORS, '16')
    encoder.encode(img_file)
    return True


def show_image_ndarray(data: any, name: str) -> bool:
    if os.name == 'nt':  # Windows
        # See aftviewer/core/image_viewer/__init__.py
        tmpd = False
    else:
        tmpd = True
    with tempfile.NamedTemporaryFile(suffix='.bmp', delete=tmpd) as tmp:
        make_bitmap(tmp.name, data, verbose=False, logger=logger)
        res = show_image_file(tmp.name)
    return res
