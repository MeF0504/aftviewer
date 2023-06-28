from typing import Any

import matplotlib.pyplot as plt

try:
    from screeninfo import get_monitors
except ImportError:
    get_screen = False
else:
    get_screen = True


def clear_mpl_axes(axes):
    # not display axes
    axes.xaxis.set_visible(False)
    axes.yaxis.set_visible(False)
    axes.spines['top'].set_visible(False)
    axes.spines['bottom'].set_visible(False)
    axes.spines['right'].set_visible(False)
    axes.spines['left'].set_visible(False)


def show_image_file(img_file: str) -> None:
    img = plt.imread(img_file)
    fig1 = plt.figure()
    ax11 = fig1.add_axes((0, 0, 1, 1))
    ax11.imshow(img)
    clear_mpl_axes(ax11)
    plt.show()
    plt.close(fig1)


def show_image_ndarray(data: Any, name: str) -> None:
    if get_screen:
        height = get_monitors()[0].height
    else:
        height = 540
    rate = data.shape[0]/height*100
    h = int(data.shape[0]/rate)
    w = int(data.shape[1]/rate)
    fig1 = plt.figure(figsize=(w, h))
    # full display
    ax1 = fig1.add_axes((0, 0, 1, 1))
    ax1.imshow(data)
    clear_mpl_axes(ax1)
    plt.show()
    plt.close(fig1)
