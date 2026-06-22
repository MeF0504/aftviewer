#! /usr/bin/env python3
from __future__ import annotations

import os
import shutil
import argparse
import tempfile
import subprocess
from pathlib import Path
from importlib import import_module
from logging import getLogger
from types import FunctionType

from ..core import GLOBAL_CONF, print_error, print_warning

logger = getLogger(GLOBAL_CONF.logname)


def closing(dst_path: Path):
    os.remove(dst_path)


def rmtmp(tmpdir: None | tempfile.TemporaryDirectory):
    if tmpdir is not None:
        tmpdir.cleanup()


def install_viewer(args: argparse.Namespace) -> int:
    url = args.url
    name = os.path.basename(url)
    name = os.path.splitext(name)[0]
    libdir = GLOBAL_CONF.conf_dir/'.lib/exlibs'/name
    if libdir.is_dir():
        print(f'{name} already exists. Update the library.')
        retcode = update_viewer(libdir)
        if retcode != 0:
            print_error(f'Failed to update {name}.')
            return retcode
    else:
        logger.info(f'make dir: {libdir}')
        libdir.mkdir(parents=True)
        cmds = ['git', 'clone', url, libdir]
        res = subprocess.run(cmds)
        if res.returncode != 0:
            print_error(f'failed to clone. remove {name}.')
            logger.error(f'remove {libdir}')
            shutil.rmtree(libdir)
            return res.returncode

    res = 0
    for fy in libdir.glob('viewers/*.py'):
        res += check_viewer(fy.name[:-3])  # remove ".py"
    for fy in libdir.glob('image_viewers/*.py'):
        res += check_image_viewer(fy.name[:-3])  # remove ".py"
    if res == 0:
        return 0
    else:
        return 3


def update_viewer(libdir: Path) -> int:
    os.chdir(libdir)
    cmds = ['git', 'pull']
    res = subprocess.run(cmds)
    if res.returncode != 0:
        print_error(f'failed to pull {libdir.name}.')
        return res.returncode
    return 0


def check_viewer(typename: str) -> int:
    libstr = f'viewers.{typename}'
    logger.info(f'checking {libstr}')
    try:
        lib = import_module(libstr)
    except ImportError as e:
        print_warning(f'Failed to import {typename}: {e}')
        return 1

    res = 0
    if not (hasattr(lib, 'main') and type(lib.main) is FunctionType):
        print_warning(f'main function is not in {typename}')
        res += 1
    if not (hasattr(lib, 'add_args') and type(lib.add_args) is FunctionType):
        print_warning(f'add_args function is not in {typename}')
        res += 1
    if not (hasattr(lib, 'show_help') and type(lib.show_help) is FunctionType):
        print_warning(f'show_help function is not in {typename}')
        res += 1
    return res


def check_image_viewer(typename: str) -> int:
    libstr = f'image_viewers.{typename}'
    logger.info(f'checking {libstr}')
    try:
        lib = import_module(libstr)
    except ImportError as e:
        print_warning(f'Failed to import {typename}: {e}')
        return 1

    res = 0
    if not (hasattr(lib, 'show_image_file') and
            type(lib.show_image_file) is FunctionType):
        print_warning(f'show_image_file function is not in {typename}')
        res += 1
    if not (hasattr(lib, 'show_image_ndarray') and
            type(lib.show_image_ndarray) is FunctionType):
        print_warning(f'show_image_ndarray function is not in {typename}')
        res += 1
    return res
