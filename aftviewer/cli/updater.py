#! /usr/bin/env python3
from __future__ import annotations

import os
import sys
import subprocess
from logging import getLogger

from ..core import GLOBAL_CONF, print_error
logger = getLogger(GLOBAL_CONF.logname)


__py_cmd: str | None = None


def is_win_aft():
    # ref: pip._internal.utils.misc.protect_pip_from_modification_on_windows
    windows = sys.platform.startswith("win") \
        or (sys.platform == "cli" and os.name == "nt")
    return windows and os.path.basename(sys.argv[0]) == 'aftviewer'


def get_py_cmd() -> None | str:
    global __py_cmd
    if __py_cmd is not None:
        return __py_cmd

    py_cmd = sys.executable
    py_X = os.access(py_cmd, os.X_OK)
    logger.info(f'python cmd: {py_cmd}')
    if py_cmd == '' or py_cmd is None or not py_X:
        print_error('failed to find python command.')
        logger.error(f'python interpriter not found: {py_cmd}, {py_X}')
        return None
    else:
        __py_cmd = py_cmd
        return py_cmd


def update_core(cmd_list: list[str], test: bool) -> bool:
    if is_win_aft():
        new_cmd = [sys.executable, "-m", "aftviewer"] + sys.argv[1:]
        cmd_str = ' '.join(new_cmd)
        print(f'To update the aftviewer, please run "{cmd_str}".')
        return False

    if test:
        print(cmd_list)
        return True
    else:
        subprocess.run(cmd_list)
        return True
