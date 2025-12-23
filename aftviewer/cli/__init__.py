#! /usr/bin/env python3
from __future__ import annotations

import os
import sys
import argparse
from pathlib import Path
from types import FunctionType
from typing import Any
from logging import getLogger
import subprocess
import shutil
import textwrap

from ..core import (GLOBAL_CONF, __set_filetype, __load_lib,
                    __add_types, __get_opt_keys, __get_color_names,
                    print_key, print_error, cprint,
                    args_chk, get_config, get_col)
from ..core.__version__ import VERSION
from ..core.helpmsg import add_args_shell_cmp, add_args_update
from ..core.types import Args
from .updater import get_py_cmd, update_core

if GLOBAL_CONF.debug:
    term_width = 80-2
else:
    term_width = shutil.get_terminal_size().columns-2

logger = getLogger(GLOBAL_CONF.logname)
__subcmds = ['help', 'update', 'config_list', 'shell_completion']


class MyHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def __init__(self, prog, indent_increment=2,
                 max_help_position=24, width=term_width):
        super().__init__(prog, indent_increment, max_help_position, width)


def get_parser_arg() -> dict[str, Any]:
    supported_type = list(GLOBAL_CONF.types.keys()).copy()
    args_desc_ori = f"""displays the contents of a file.
Supported file types ... {', '.join(supported_type)}."""
    args_ep_ori = """AFTViewer has some optional subcommands;
 - aftviewer - help -t TYPE
       shows detailed help and available options for the TYPE.
 - aftviewer - update
       runs the update command of AFTViewer.
 - aftviewer - config_list [-t TYPE]
       shows the current optional configuration.
       If TYPE is specified, shows the configuration for the TYPE.
 - aftviewer - shell_completion --bash >> ~/.bashrc
   aftviewer - shell_completion --zsh >> ~/.zshrc
        sets the completion script for bash/zsh."""
    args_desc = ''
    args_ep = ''
    for ad in args_desc_ori.splitlines():
        args_desc += '\n'.join(textwrap.wrap(ad, width=term_width))+'\n'
    for ae in args_ep_ori.splitlines():
        args_ep += '\n'.join(textwrap.wrap(ae, width=term_width))+'\n'
    return dict(prog='aftviewer',
                description=args_desc,
                epilog=args_ep,
                formatter_class=MyHelpFormatter,
                allow_abbrev=False,
                )


def get_args(argv: None | list[str] = None) -> Args:
    parser = argparse.ArgumentParser(**get_parser_arg())
    if (argv is None and '-' not in sys.argv[1:]) or \
       (argv is not None and '-' not in argv):
        parser.add_argument('file', help='input file')
        parser.add_argument('--version', '-V', action='version',
                            version=f'%(prog)s {VERSION}')
    parser.add_argument('-t', '--type', dest='type',
                        help='specify the file type.'
                        ' See above for available file types.'
                        ' "aftviewer - help -t TYPE"'
                        ' will show the detailed help')
    parser.add_argument('-', help='run subcommand and exit',
                        choices=__subcmds, default=None, dest='subcmd')
    tmpargs, rems = parser.parse_known_args(argv, namespace=Args())
    if tmpargs.subcmd == 'shell_completion':
        add_args_shell_cmp(parser)
    elif tmpargs.subcmd == 'update':
        add_args_update(parser)
    __set_filetype(tmpargs)
    lib = __load_lib(tmpargs)
    if lib is not None:
        lib.add_args(parser)
    args = parser.parse_args(argv, namespace=Args())
    logger.debug(f'args: {args}')
    return args


def show_opts(filetype: str | None) -> None:
    def show_col(cname, filetype):
        try:
            fg, bg = get_col(cname, filetype)
            print(f'  {cname}: ', end='')
            cprint(f'{fg}, {bg}', '', fg=fg, bg=bg)
        except Exception as e:
            print(f'Failed to display color {cname} ({e})')

    opts = __get_opt_keys()
    if filetype is not None:
        print_key(filetype)
        print_key('config')
        keys = list(set(opts['defaults'] + opts[filetype]))
        for key in keys:
            val = get_config(key, filetype)
            print(f'  {key}: {val}')
        print_key('colors')
        cnames = list(set(__get_color_names('defaults')
                          + __get_color_names(filetype)))
        cnames.sort()
        for cname in cnames:
            show_col(cname, filetype)
        return

    # filetype is None -> show all.
    if len(__add_types.keys()) != 0:
        print_key('additional_types')
        for ft in __add_types:
            print(f'  {ft}: {__add_types[ft]}')
    print_key('config')
    print_key('defaults')
    for key in opts['defaults']:
        val = get_config(key, 'defaults')
        print(f'  {key}: {val}')
    opts.pop('defaults')
    for ft in opts:
        if len(opts[ft]) != 0:
            print_key(ft)
            for key in opts[ft]:
                val = get_config(key, ft)
                print(f'  {key}: {val}')
    print_key('colors')
    print_key('defaults')
    for cname in __get_color_names('defaults'):
        show_col(cname, 'defaults')
    for ft in opts:
        cnames = __get_color_names(ft)
        if len(cnames) != 0:
            print_key(ft)
            for cname in cnames:
                show_col(cname, ft)


def set_shell_comp(args: Args) -> bool:
    base_dir = Path(__file__).parent.parent
    if args_chk(args, 'bash'):
        sh_cmp_file = base_dir/'shell-completion/completion.bash'
    elif args_chk(args, 'zsh'):
        sh_cmp_file = base_dir/'shell-completion/completion.zsh'
    else:
        print('Please specify shell (--bash or --zsh).')
        return False
    with open(sh_cmp_file, 'r') as f:
        for line in f:
            print(line, end='')
    return True


def update(branch: str, test: bool) -> bool:
    py_cmd = get_py_cmd()
    if py_cmd is None:
        return False
    update_cmd = [py_cmd, '-m', 'pip', 'install', '--upgrade',
                  'aftviewer @ '
                  f'git+https://github.com/MeF0504/aftviewer@{branch}',
                  ]
    logger.debug(f'update command: {update_cmd}')
    update_core(f'{update_cmd}', test)
    return True


def update_packages(ftype: str, test: bool) -> bool:
    py_cmd = get_py_cmd()
    if py_cmd is None:
        return False
    base_dir = Path(__file__).parent.parent
    req_file = base_dir/f'requirements/{ftype}.txt'
    logger.info(f'requirement file: {req_file}')
    if not req_file.is_file():
        print('Requirement file is not found.'
              ' Requirements are already satisfied.')
        return True
    update_cmd = [py_cmd, '-m', 'pip', 'install', '--upgrade',
                  '-r', str(req_file)]
    update_core(f'{update_cmd}', test)
    return True


def main() -> None:
    args = get_args()
    if not (args.type is None or args.type in GLOBAL_CONF.types):
        supported_type = ', '.join(list(GLOBAL_CONF.types.keys()).copy())
        print(f'Please specify the type from {supported_type}.')
        print_error(f'invalid file type: {args.type}.')
        return

    if args.subcmd is not None:
        ret = False
        if args.subcmd == 'config_list':
            show_opts(args.type)
            ret = True
        elif args.subcmd == 'shell_completion':
            ret = set_shell_comp(args)
        elif args.subcmd == 'update':
            # update はversionが変わらないと作用しないっぽい。
            # branch を切り替えるにもversionの違いが必要そう
            if args.type is None:
                ret = update(args.branch, args.test)
            else:
                ret = update_packages(args.type, args.test)
        elif args.subcmd == 'help':
            if args_chk(args, 'type'):
                lib = __load_lib(args)
                if lib is None:
                    print('Failed to load the library.')
                    ret = False
                else:
                    if hasattr(lib, 'show_help') and \
                       type(lib.show_help) is FunctionType:
                        lib.show_help()
                    else:
                        print("this type does not support showing help.")
                    ret = True
            else:
                print('please set --type to see the details.')
                ret = False
        else:
            print_error(f'Invalid subcommand: {args.subcmd}.')
            ret = False
        if ret:
            sys.exit(0)
        else:
            sys.exit(1)

    fpath = Path(args.file).expanduser()
    if not fpath.exists():
        print("file doesn't exists!")
        return
    if fpath.is_dir():
        print("{} is a directory.".format(fpath))
        return

    __set_filetype(args)

    if args.type == 'text':
        if ('LANG' in os.environ) and ('ja_JP' in os.environ['LANG']):
            print('vimでも使ってろ！')
        else:
            print("Why Don't you use vim???")
        return
    elif args.type is None:
        print('This is not a supported file type.')
        return

    lib = __load_lib(args)
    if lib is None:
        print(f'Failed to load the library for "{args.type}".')
    else:
        lib.main(fpath, args)
    return
