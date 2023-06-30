import os
from typing import Any

import cv2


def show_image_file(img_file: str) -> None:
    name = os.path.basename(img_file)
    img = cv2.imread(img_file)
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyWindow(name)


def show_image_ndarray(data: Any, name: str) -> None:
    if data.shape[2] == 3:
        img = data[:, :, ::-1]  # RGB -> BGR
    elif data.shape[2] == 4:
        img = data[:, :, [2, 1, 0, 3]]  # RGBA -> BGRA
    else:
        print('invalid data shape')
        return False
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyWindow(name)
