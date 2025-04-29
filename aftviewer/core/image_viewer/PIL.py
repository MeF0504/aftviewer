import os
from typing import Any

from PIL import Image

from .. import print_error


def show_image_file(img_file: str) -> bool:
    name = os.path.basename(img_file)
    try:
        with Image.open(img_file) as image:
            image.show(title=name)
    except Exception as e:
        print_error(f'failed to open image: {img_file}')
        print_error(f'{type(e).__name__}: {e}')
        return False
    else:
        return True


def show_image_ndarray(data: Any, name: str) -> bool:
    try:
        with Image.fromarray(data) as image:
            image.show(title=name)
    except Exception as e:
        print_error('failed to open image data')
        print_error(f'{type(e).__name__}: {e}')
        return False
    else:
        return True
