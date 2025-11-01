from __future__ import annotations

from typing import Any
from logging import getLogger

import matplotlib.pyplot as plt

from .. import GLOBAL_CONF, print_error, get_config

if "screeninfo" in GLOBAL_CONF.pack_list:
    from screeninfo import get_monitors
    get_screen = True
else:
    get_screen = False
logger = getLogger(GLOBAL_CONF.logname)
logger.info(f'use screeninfo: {get_screen}')


def clear_mpl_axes(axes):
    # not display axes
    axes.xaxis.set_visible(False)
    axes.yaxis.set_visible(False)
    axes.spines['top'].set_visible(False)
    axes.spines['bottom'].set_visible(False)
    axes.spines['right'].set_visible(False)
    axes.spines['left'].set_visible(False)


def get_size_dpi(shape: tuple[int, ...]) -> tuple[tuple[float, float], int]:
    assert len(shape) > 1, f'Image dimension must be >= 2, now {len(shape)}'
    width = get_config('image_width')
    if width is not None:
        rate = shape[1]/width
    elif get_screen:
        height = get_monitors()[0].height*0.7  # pixel
        rate = shape[0]/height
    else:
        height = 540.0  # pixel
        rate = shape[0]/height
    dpi = 100
    h = shape[0]/rate/dpi
    w = shape[1]/rate/dpi
    logger.info(f'width: {w:.2f}, height: {h:.2f}, dpi: {dpi}')
    return (w, h), dpi


def show_image_file(img_file: str) -> bool:
    try:
        img = plt.imread(img_file)
        size, dpi = get_size_dpi(img.shape)
        fig1 = plt.figure(figsize=size, dpi=dpi)
        ax11 = fig1.add_axes((0, 0, 1, 1))
        ax11.imshow(img)
        clear_mpl_axes(ax11)
        plt.show()
        plt.close(fig1)
    except Exception as e:
        print_error(f'failed to open image: {img_file}')
        print_error(f'{type(e).__name__}: {e}')
        return False
    else:
        return True


def show_image_ndarray(data: Any, name: str) -> bool:
    size, dpi = get_size_dpi(data.shape)
    try:
        fig1 = plt.figure(figsize=size, dpi=dpi)
        # full display
        ax1 = fig1.add_axes((0, 0, 1, 1))
        ax1.imshow(data)
        clear_mpl_axes(ax1)
        plt.show()
        plt.close(fig1)
    except Exception as e:
        print_error('failed to open image data')
        print_error(f'{type(e).__name__}: {e}')
        return False
    else:
        return True
