import os
from typing import Any

from PIL import Image


def show_image_file(img_file: str) -> bool:
    name = os.path.basename(img_file)
    with Image.open(img_file) as image:
        image.show(title=name)
    return True


def show_image_ndarray(data: Any, name: str) -> bool:
    with Image.fromarray(data) as image:
        image.show(title=name)
    return True
