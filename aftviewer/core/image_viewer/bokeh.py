from typing import Any
from logging import getLogger
import tempfile

# bokeh depends on both numpy and pillow!
import numpy as np
from PIL import Image
from bokeh.plotting import figure, output_file, show

from .. import GLOBAL_CONF, print_error, get_config

logger = getLogger(GLOBAL_CONF.logname)


def show_data(data: np.ndarray):
    assert data.dtype == np.uint8, \
        f'data type should be uint8, not {data.dtype}'
    assert len(data.shape) == 3, \
        f'len of data shape should be 3 (h, w, 4), not {len(data.shape)}.'
    h, w, _ = data.shape
    logger.debug(f'Image shape: {data.shape}')
    width = get_config('image_width')
    if width is None:
        width = w
        height = h
    else:
        height = int(width*float(h)/w)
    logger.info(f'shown image size: {width}x{height}')
    # convert uint8x4 |R|G|B|A| -> uint32 |RGBA|
    shown_data = np.empty((h, w), dtype=np.uint32)
    view = shown_data.view(dtype=np.uint8).reshape((h, w, 4))
    view[:, :, :] = data
    shown_data = np.flip(shown_data, 0)
    p = figure(width=width, height=height)
    p.x_range.range_padding = p.y_range.range_padding = 0
    p.image_rgba(image=[shown_data], x=0, y=0, dw=width, dh=height)
    with tempfile.NamedTemporaryFile(suffix='.html') as tmp:
        output_file(tmp.name)
        show(p)
        input('Enter to close.')


def show_image_file(img_file: str) -> bool:
    try:
        img = Image.open(img_file)
        img_rgba = img.convert('RGBA')
    except Exception as e:
        print_error(f'failed to open image: {img_file}')
        print_error(f'{type(e).__name__}: {e}')
        return False
    data = np.asarray(img_rgba, dtype=np.uint8)
    show_data(data)
    return True


def show_image_ndarray(data: Any, name: str) -> bool:
    shown_data = np.asarray(data, dtype=np.uint8)
    dshape = shown_data.shape
    if len(dshape) != 3:
        print_error(f'data shape is incorrect: {dshape}')
        return False
    if dshape[2] == 3:
        shown_data2 = np.ones((dshape[0], dshape[1], 4), dtype=np.uint8)*255
        shown_data2[:, :, :3] = shown_data
    elif dshape[2] == 4:
        shown_data2 = shown_data
    else:
        print_error(f'data component is not 3/4?? ({dshape[2]})')
        return False
    show_data(shown_data2)
    return True
