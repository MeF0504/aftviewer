import os
from typing import Any

from PIL import Image


def show_image_file(img_file: str) -> None:
    name = os.path.basename(img_file)
    with Image.open(img_file) as image:
        image.show(title=name)


def show_image_ndarray(data: Any, name: str) -> None:
    with Image.fromarray(data) as image:
        image.show(title=name)
