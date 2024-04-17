#! /usr/bin/env python3

import os
import argparse
from pathlib import Path
from types import FunctionType
from logging import getLogger

from .core import get_filetype, load_lib, GLOBAL_CONF, args_chk, show_opts

logger = getLogger(GLOBAL_CONF.logname)


def get_args():
    supported_type = list(GLOBAL_CONF.types.keys()).copy()
    supported_type.remove('text')
    parser = argparse.ArgumentParser(
            description="show the constitution of a file."
            + f" default support file types ... {', '.join(supported_type)}",
            epilog="To see the detailed help of each type,"
            + " type 'pyviewer help -t TYPE'. "
            + " PyViewer has other subcommands,"
            + " 'pyviewer config_list' shows"
            + " the current optional configuration,"
            + " 'pyviewer set_shell_cmp' set the completion script"
            + " for bash/zsh."
            )
    parser.add_argument('file', help='input file')
    parser.add_argument('-t', '--type', dest='type',
                        help='specify the file type.'
                        + ' "pyviewer help -t TYPE"'
                        + ' will show the detailed help.',
                        choices=supported_type)
    tmpargs, rems = parser.parse_known_args()
    if not args_chk(tmpargs, 'type'):
        tmpargs.type = get_filetype(Path(tmpargs.file))
    lib = load_lib(tmpargs)
    if lib is not None:
        lib.add_args(parser)
    args = parser.parse_args()
    logger.debug(f'args: {args}')
    return args


def main():
    args = get_args()

    if args.file == 'config_list':
        show_opts()
        return

    if args.file == 'set_shell_cmp':
        return

    if args.file == 'help':
        if not args_chk(args, 'type'):
            print('please set --type to see the details.')
            return
        lib = load_lib(args)
        if lib is None:
            print('Library file is not found.')
        else:
            if hasattr(lib, 'show_help') and type(lib.show_help) is FunctionType:
                lib.show_help()
            else:
                print("this type does not support showing help.")
        return

    fpath = Path(args.file).expanduser()
    if not fpath.exists():
        print("file doesn't exists!")
        return
    if fpath.is_dir():
        print("{} is a directory.".format(fpath))
        return

    if not args_chk(args, 'type'):
        args.type = get_filetype(fpath)

    if args.type == 'text':
        if ('LANG' in os.environ) and ('ja_JP' in os.environ['LANG']):
            print('vimでも使ってろ！')
        else:
            print("Why Don't you use vim???")
        return

    lib = load_lib(args)
    if lib is None:
        print('Library file is not found.')
    else:
        lib.main(fpath, args)
    return
