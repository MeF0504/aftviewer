import os
from typing import Any

import cv2

from .. import print_error


def show_image_file(img_file: str) -> bool:
    name = os.path.basename(img_file)
    try:
        img = cv2.imread(img_file)
        cv2.imshow(name, img)
        cv2.waitKey(0)
        cv2.destroyWindow(name)
    except Exception as e:
        print_error(f'failed to open image: {img_file}')
        print_error(f'{type(e).__name__}: {e}')
        return False
    else:
        return True


def show_image_ndarray(data: Any, name: str) -> bool:
    if data.shape[2] == 3:
        img = data[:, :, ::-1]  # RGB -> BGR
    elif data.shape[2] == 4:
        img = data[:, :, [2, 1, 0, 3]]  # RGBA -> BGRA
    else:
        print('invalid data shape')
        return False
    try:
        cv2.imshow(name, img)
        cv2.waitKey(0)
        cv2.destroyWindow(name)
    except Exception as e:
        print_error('failed to open image data')
        print_error(f'{type(e).__name__}: {e}')
        return False
    else:
        return True
