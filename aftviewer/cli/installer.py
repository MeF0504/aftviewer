#! /usr/bin/env python3
from __future__ import annotations

import os
import sys
import shutil
import argparse
import tempfile
import subprocess
from urllib import request
from pathlib import Path
from importlib import import_module
from logging import getLogger
from types import FunctionType

from ..core import GLOBAL_CONF, print_error, print_warning, __load_lib

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


def __install_viewer(args: argparse.Namespace, lib_path: Path):
    lib_dir = GLOBAL_CONF.conf_dir/'.lib/add_viewers'
    dst_path = lib_dir/lib_path.name
    type_name = lib_path.stem
    if not lib_dir.is_dir():
        lib_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(lib_path, dst_path)
    lib = import_module(f'add_viewers.{type_name}')

    if not hasattr(lib, 'main'):
        print_error(f'main function is not found in {lib_path}.',
                    file=sys.stderr)
        closing(dst_path)
        return
    if not hasattr(lib, 'add_args'):
        print_error(f'add_args function is not found in {lib_path}.',
                    file=sys.stderr)
        closing(dst_path)
        return
    if not hasattr(lib, 'show_help'):
        print_warning(f'show_help function is not found in {lib_path}.')

    if lib.main.__code__.co_argcount != 2:
        print_warning('Number of arguments of main is not 2.')
    if lib.add_args.__code__.co_argcount != 1:
        print_warning('Number of arguments of add_args is not 1.')

    add_txt = GLOBAL_CONF.conf_dir/'.lib/add_types.txt'
    add_types = {}
    if add_txt.is_file() and os.access(add_txt, os.R_OK):
        with open(add_txt, 'r') as f:
            for line in f:
                line = line.replace('\n', '')
                add_type, exts = line.split('\t')
                add_types[add_type] = exts
    with open(add_txt, 'w') as f:
        for t, e in add_types.items():
            f.write(f'{t}\t{e}\n')
        f.write(f'{type_name}\t{" ".join(args.ext)}\n')


def install_image_viewer(args: argparse.Namespace, lib_path: Path):
    lib_dir = GLOBAL_CONF.conf_dir/'.lib/add_image_viewers'
    dst_path = lib_dir/lib_path.name
    type_name = lib_path.stem
    if not lib_dir.is_dir():
        lib_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(lib_path, dst_path)
    lib = import_module(f'add_image_viewers.{type_name}')

    if not hasattr(lib, 'show_image_file'):
        print_error(f'show_image_file function is not found in {lib_path}.',
                    file=sys.stderr)
        closing(dst_path)
        return
    if not hasattr(lib, 'show_image_ndarray'):
        print_error(f'show_image_ndarray function is not found in {lib_path}.',
                    file=sys.stderr)
        closing(dst_path)
        return

    if lib.show_image_file.__code__.co_argcount != 1:
        print_warning('Number of arguments of main is not 1.')
    if lib.show_image_ndarray.__code__.co_argcount != 2:
        print_warning('Number of arguments of add_args is not 2.')


# def get_args() -> argparse.Namespace:
#     parser = argparse.ArgumentParser()
#     parser.add_argument('libfile',
#                         help='Path or URL of the library file of'
#                         ' the additional type to install')
#     parser.add_argument('ext', help='File extension of the additional type.',
#                         nargs='*')
#     args = parser.parse_args()
#     return args


# def main():
#     args = get_args()
#     tmpdir: None | tempfile.TemporaryDirectory = None
#     if args.libfile.startswith(('http://', 'https://')):
#         libname = os.path.basename(args.libfile)
#         tmpdir = tempfile.TemporaryDirectory()
#         with request.urlopen(args.libfile) as response:
#             with open(os.path.join(tmpdir.name, libname), 'wb') as tf:
#                 tf.write(response.read())
#                 lib_path = Path(tf.name)
#                 logger.debug(f'Save downloaded file to {tf.name}.')
#     else:
#         lib_path = Path(args.libfile)

#     if not lib_path.is_file():
#         print_error(f'{lib_path} does not exist.', file=sys.stderr)
#         rmtmp(tmpdir)
#         return
#     if not lib_path.name.endswith('.py'):
#         print_error(f'Incorrect extension: {lib_path.name}', file=sys.stderr)
#         rmtmp(tmpdir)
#         return

#     __add_lib2path()
#     if args.ext == ['image-viewer']:
#         logger.debug(f'install image viewer extension "{lib_path}".')
#         install_image_viewer(args, lib_path)
#     else:
#         logger.debug(f'install viewer extension "{lib_path}".')
#         install_viewer(args, lib_path)

#     rmtmp(tmpdir)
