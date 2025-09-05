import os
from typing import Any
from logging import getLogger

import numpy as np
from PIL import Image
import plotly.graph_objects as go

from aftviewer import GLOBAL_CONF

logger = getLogger(GLOBAL_CONF.logname)


def show_image_file(img_file: str) -> bool:
    name = os.path.basename(img_file)
    img_data = Image.open(img_file)
    if 'RGB' not in img_data.mode:
        logger.info(f'convert {img_data.mode} to RGB')
        img_data = img_data.convert('RGBA')
    img_data = np.asarray(img_data)
    show_image_ndarray(img_data, name)
    return True


def show_image_ndarray(data: Any, name: str) -> bool:
    fig = go.Figure()
    fig.add_trace(go.Image(z=data))
    fig.update_layout(title=dict(text=name))
    fig.show()
    return True
