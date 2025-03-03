#! /usr/bin/env python3
from __future__ import annotations

import os
import shutil
import argparse
from pathlib import Path
from importlib import import_module

from ..core import GLOBAL_CONF, print_error, print_warning, __add_lib2path


def closing(dst_path: Path):
    os.remove(dst_path)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('libfile',
                        help='Path of the library file of the additional type to install')
    parser.add_argument('ext', help='File extension of the additional type.',
                        nargs='*')
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    lib_path = Path(args.libfile)
    if not lib_path.is_file():
        print_error(f'{lib_path} does not exist.')
        return
    if not lib_path.name.endswith('.py'):
        print_error(f'Incorrect extension: {lib_path.name}')
        return

    __add_lib2path()
    dst_path = GLOBAL_CONF.conf_dir/f'.lib/add_viewers/{lib_path.name}'
    type_name = lib_path.name[:-3]
    shutil.copy(lib_path, dst_path)
    lib = import_module(f'add_viewers.{type_name}')

    if not hasattr(lib, 'main'):
        print_error('main function is not found.')
        closing(dst_path)
        return
    if not hasattr(lib, 'add_args'):
        print_error('add_args function is not found.')
        closing(dst_path)
        return
    if not hasattr(lib, 'show_help'):
        print_warning('show_help function is not found.')

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
