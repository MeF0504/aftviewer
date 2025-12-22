#! /usr/bin/env python3
from __future__ import annotations

import os
import sys
import subprocess
import tempfile
from logging import getLogger

from ..core import GLOBAL_CONF, print_error
logger = getLogger(GLOBAL_CONF.logname)


UPDATER = """
import time
import subprocess

time.sleep(1)

subprocess.check_call({})
"""


def get_py_cmd() -> None | str:
    py_cmd = sys.executable
    py_X = os.access(py_cmd, os.X_OK)
    logger.info(f'python cmd: {py_cmd}')
    if py_cmd == '' or py_cmd is None or not py_X:
        print_error('failed to find python command.')
        logger.error(f'python interpriter not found: {py_cmd}, {py_X}')
        return None
    else:
        return py_cmd


def update_core(cmd_str: str, test: bool):
    py_cmd = get_py_cmd()
    tfile = tempfile.NamedTemporaryFile(suffix='.py', delete=False)
    with open(tfile.name, 'w') as f:
        print(UPDATER.format(cmd_str), file=f)
    if test:
        print('----------')
        with open(tfile.name, 'r') as f:
            [print(ln, end='') for ln in f.readlines()]
        print('----------')
        tfile.close()
    else:
        if hasattr(subprocess, 'DETACHED_PROCESS'):
            cflag = subprocess.DETACHED_PROCESS
        else:
            cflag = 0
        print('run the update process...')
        subprocess.Popen([py_cmd, tfile.name],
                         creationflags=cflag, close_fds=True)
