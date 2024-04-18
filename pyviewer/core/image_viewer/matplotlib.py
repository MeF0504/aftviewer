from typing import Any, Tuple
from logging import getLogger

import matplotlib.pyplot as plt

from .. import GLOBAL_CONF

try:
    from screeninfo import get_monitors
except ImportError:
    get_screen = False
else:
    get_screen = True
logger = getLogger(GLOBAL_CONF.logname)


def clear_mpl_axes(axes):
    # not display axes
    axes.xaxis.set_visible(False)
    axes.yaxis.set_visible(False)
    axes.spines['top'].set_visible(False)
    axes.spines['bottom'].set_visible(False)
    axes.spines['right'].set_visible(False)
    axes.spines['left'].set_visible(False)


def get_size_dpi(shape: Tuple[int, int]) -> Tuple[Tuple[float, float], int]:
    if get_screen:
        height = get_monitors()[0].height*0.7  # pixel
    else:
        height = 540.0  # pixel
    dpi = 100
    rate = shape[0]/height
    h = shape[0]/rate/dpi
    w = shape[1]/rate/dpi
    logger.info(f'width: {w:.2f}, height: {h:.2f}, dpi: {dpi}')
    return (w, h), dpi


def show_image_file(img_file: str) -> bool:
    img = plt.imread(img_file)
    size, dpi = get_size_dpi(img.shape)
    fig1 = plt.figure(figsize=size, dpi=dpi)
    ax11 = fig1.add_axes((0, 0, 1, 1))
    ax11.imshow(img)
    clear_mpl_axes(ax11)
    plt.show()
    plt.close(fig1)
    return True


def show_image_ndarray(data: Any, name: str) -> bool:
    size, dpi = get_size_dpi(data.shape)
    fig1 = plt.figure(figsize=size, dpi=dpi)
    # full display
    ax1 = fig1.add_axes((0, 0, 1, 1))
    ax1.imshow(data)
    clear_mpl_axes(ax1)
    plt.show()
    plt.close(fig1)
    return True
