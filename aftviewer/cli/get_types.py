#! /usr/bin/env python3
from __future__ import annotations

import sys
from logging import getLogger

from . import __subcmds
from ..core import GLOBAL_CONF
from ..core.image_viewer import __collect_image_viewers

logger = getLogger(GLOBAL_CONF.logname)


def main():
    logger.debug(f'argv: {sys.argv}')
    if len(sys.argv) < 2:
        return ""
    elif sys.argv[1] == 'type':
        supported_type = list(GLOBAL_CONF.types.keys()).copy()
        print(' '.join(supported_type))
    elif sys.argv[1] == 'image_viewer':
        print(' '.join(__collect_image_viewers()))
    elif sys.argv[1] == 'subcmds':
        print(' '.join(__subcmds))
