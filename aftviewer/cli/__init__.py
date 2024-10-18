#! /usr/bin/env python3
from __future__ import annotations

import os
import sys
import argparse
from pathlib import Path
from types import FunctionType
from logging import getLogger
import subprocess

from ..core import (GLOBAL_CONF, set_filetype, load_lib, args_chk,
                    print_key, print_error, cprint, get_config, get_col,
                    get_opt_keys, get_color_names)
from ..core.__version__ import VERSION
from ..core.image_viewer import __collect_image_viewers
from ..core.helpmsg import add_args_shell_cmp, add_args_update
from ..core.types import Args

logger = getLogger(GLOBAL_CONF.logname)


def get_args() -> Args:
    supported_type = list(GLOBAL_CONF.types.keys()).copy()
    parser = argparse.ArgumentParser(
            prog='aftviewer',
            description="show the constitution of a file."
            f" Supported file types ... {', '.join(supported_type)}."
            " To see the detailed help of each type, "
            " type 'aftviewer help -t TYPE'.",
            epilog=" AFTViewer has some subcommands,"
            " 'aftviewer help -t TYPE' shows detailed help,"
            " 'aftviewer update' run the update command of AFTViewer,"
            " 'aftviewer config_list' shows the current optional configuration,"
            " 'aftviewer shell_completion --bash >> ~/.bashrc' or"
            " 'aftviewer shell_completion --zsh >> ~/.zshrc'"
            " set the completion script for bash/zsh."
            )
    parser.add_argument('file', help='input file')
    parser.add_argument('--version', '-V', action='version',
                        version=f'%(prog)s {VERSION}')
    parser.add_argument('-t', '--type', dest='type',
                        help='specify the file type.'
                        f' Available types are {", ".join(supported_type)}.'
                        ' "aftviewer help -t TYPE"'
                        ' will show the detailed help.')
    tmpargs, rems = parser.parse_known_args()
    if tmpargs.file == 'shell_completion':
        add_args_shell_cmp(parser)
    elif tmpargs.file == 'update':
        add_args_update(parser)
    set_filetype(tmpargs)
    lib = load_lib(tmpargs)
    if lib is not None:
        lib.add_args(parser)
    args = parser.parse_args()
    logger.debug(f'args: {args}')
    return args


def show_opts(filetype: str | None) -> None:
    def show_key(key, val, filetype):
        if key == 'colors':
            print('  colors:')
            for cname in val:
                try:
                    fg, bg = get_col(cname, filetype)
                    print(f'    {cname}: ', end='')
                    cprint(f'{fg}, {bg}', '', fg=fg, bg=bg)
                except Exception as e:
                    print(f'Failed to display color {cname} ({e})')
        else:
            print(f'  {key}: {val}')
    opts = get_opt_keys()
    if filetype is not None:
        print_key(filetype)
        keys = list(set(opts['defaults'] + opts[filetype]))
        for key in keys:
            if key == 'colors':
                val = list(set(get_color_names(None)
                               + get_color_names(filetype)))
                val.sort()
            else:
                val = get_config(key, filetype)
            show_key(key, val, filetype)
        return

    # filetype is None -> show all.
    at = 'additional_types'
    if at in opts:
        print_key(at)
        for ft in opts[at]:
            print(f'  {ft}: {opts[at][ft]}')
        opts.pop(at)
    print_key('defaults')
    for key in opts['defaults']:
        if key == 'colors':
            val = get_color_names(None)
        else:
            val = get_config(key, 'defaults')
        show_key(key, val, 'defaults')
    opts.pop('defaults')
    for ft in opts:
        print_key(ft)
        for key in opts[ft]:
            if key == 'colors':
                val = get_color_names(ft)
            else:
                val = get_config(key, ft)
            show_key(key, val, ft)


def set_shell_comp(args: Args) -> None:
    base_dir = Path(__file__).parent.parent
    if args_chk(args, 'bash'):
        sh_cmp_file = base_dir/'shell-completion/completion.bash'
    elif args_chk(args, 'zsh'):
        sh_cmp_file = base_dir/'shell-completion/completion.zsh'
    else:
        print('Please specify shell (--bash or --zsh).')
        return
    with open(sh_cmp_file, 'r') as f:
        for line in f:
            print(line, end='')


def update(branch: str) -> None:
    py_cmd = None
    py_version = f'{sys.version_info.major}.{sys.version_info.minor}'
    for rel_path in [f'bin/python{py_version}',
                     f'bin/python{sys.version_info.major}',
                     'bin/python',
                     f'python{py_version}.exe',
                     f'python{sys.version_info.major}.exe',
                     'python.exe',
                     ]:
        py_path = Path(sys.base_prefix)/rel_path
        if py_path.is_file() and os.access(py_path, os.X_OK):
            py_cmd = str(py_path)
            logger.info(f'find python; {py_cmd}')
            break
    if py_cmd is None:
        print_error('failed to find python command.')
        logger.error(f'python not found in {sys.base_prefix}')
        return
    update_cmd = [py_cmd, '-m', 'pip', 'install', '--upgrade',
                  'aftviewer @ '
                  f'git+https://github.com/MeF0504/aftviewer@{branch}'
                  ]
    logger.debug(f'update command: {update_cmd}')
    out = subprocess.run(update_cmd, capture_output=False)
    logger.debug(f'update command results; return code {out.returncode}')


def main() -> None:
    args = get_args()
    if not (args.type is None or args.type in GLOBAL_CONF.types):
        supported_type = ', '.join(list(GLOBAL_CONF.types.keys()).copy())
        print(f'Please specify the type from {supported_type}.')
        print_error(f'invalid file type: {args.type}.')
        return

    if args.file == 'config_list':
        show_opts(args.type)
        return

    if args.file == 'shell_completion':
        set_shell_comp(args)
        return

    if args.file == 'update':
        update(args.branch)
        return

    if args.file == 'help':
        if not args_chk(args, 'type'):
            print('please set --type to see the details.')
            return
        lib = load_lib(args)
        if lib is None:
            print('Library file is not found.')
        else:
            if hasattr(lib, 'show_help') and \
               type(lib.show_help) is FunctionType:
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

    set_filetype(args)

    if args.type == 'text':
        if ('LANG' in os.environ) and ('ja_JP' in os.environ['LANG']):
            print('vimでも使ってろ！')
        else:
            print("Why Don't you use vim???")
        return
    elif args.type is None:
        print('This is not a supported file type.')
        return

    lib = load_lib(args)
    if lib is None:
        print(f'The library file for "{args.type}" is not found.')
    else:
        lib.main(fpath, args)
    return


def get_types():
    if len(sys.argv) < 2:
        return ""
    elif sys.argv[1] == 'type':
        supported_type = list(GLOBAL_CONF.types.keys()).copy()
        print(' '.join(supported_type))
    elif sys.argv[1] == 'image_viewer':
        print(' '.join(__collect_image_viewers()))
