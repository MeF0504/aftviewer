#! /usr/bin/env python3
from __future__ import annotations

import os
import sys
import shutil
import argparse
from pathlib import Path
from importlib import import_module
from logging import getLogger

from ..core import GLOBAL_CONF, print_error, print_warning, __add_lib2path

logger = getLogger(GLOBAL_CONF.logname)


def closing(dst_path: Path):
    os.remove(dst_path)


def install_viewer(args: argparse.Namespace, lib_path: Path):
    dst_path = GLOBAL_CONF.conf_dir/f'.lib/add_viewers/{lib_path.name}'
    type_name = lib_path.name[:-3]
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
    dst_path = GLOBAL_CONF.conf_dir/f'.lib/add_image_viewers/{lib_path.name}'
    type_name = lib_path.name[:-3]
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


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('libfile',
                        help='Path of the library file of'
                        ' the additional type to install')
    parser.add_argument('ext', help='File extension of the additional type.',
                        nargs='*')
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    lib_path = Path(args.libfile)
    if not lib_path.is_file():
        print_error(f'{lib_path} does not exist.', file=sys.stderr)
        return
    if not lib_path.name.endswith('.py'):
        print_error(f'Incorrect extension: {lib_path.name}', file=sys.stderr)
        return

    __add_lib2path()
    if args.ext == ['image-viewer']:
        logger.debug(f'install image viewer extension "{lib_path}".')
        install_image_viewer(args, lib_path)
    else:
        logger.debug(f'install viewer extension "{lib_path}".')
        install_viewer(args, lib_path)
