import pickle
import os
from pathlib import PurePath
from functools import partial
from logging import getLogger

from . import GLOBAL_CONF, args_chk, print_key, get_config, get_col, cprint, \
    interactive_view, interactive_cui, help_template, \
    add_args_specification, add_args_encoding
from . import ReturnMessage as RM

from pymeflib.tree2 import show_tree
logger = getLogger(GLOBAL_CONF.logname)


def show_keys(data, key):
    fg, bg = get_col('msg_error')
    if key:
        for k in key:
            if k in data:
                print(data[k])
            else:
                cprint(f'"{k}" not in this file.', fg=fg, bg=bg)
    else:
        for k in data:
            print(k)


def get_item(data, cpath):
    tmp_data = data
    for k in PurePath(cpath).parts:
        tmp_data_update = False
        for key in tmp_data.keys():
            if str(key) == k:
                tmp_data = tmp_data[key]
                tmp_data_update = True
                break
        if not tmp_data_update:
            logger.error(f'key not found: {cpath}, {k}')
            return None
    return tmp_data


def show_func(data, cpath, **kwargs):
    tmp_data = get_item(data, cpath)
    if tmp_data is None:
        return RM(f'Error! no key {cpath}', False)
    return RM('{}'.format(tmp_data), False)


def get_contents(data, path):
    dirs = []
    files = []
    tmp_data = get_item(data, path)
    if tmp_data is None:
        return [], []
    if isinstance(tmp_data, dict):
        for k in tmp_data.keys():
            if isinstance(tmp_data[k], dict):
                dirs.append(str(k))
            else:
                files.append(str(k))
    return dirs, files


def add_args(parser):
    add_args_encoding(parser)
    add_args_specification(parser, verbose=True, key=True,
                           interactive=True, cui=True)


def show_help():
    helpmsg = help_template('pickle', 'show the contents of the pickled file.',
                            add_args)
    print(helpmsg)


def main(fpath, args):
    if args_chk(args, 'encoding'):
        logger.info('set encoding from args')
        encoding = args.encoding
    else:
        encoding = get_config('pickle', 'encoding')
    logger.info(f'encoding: {encoding}')
    with open(fpath, 'rb') as f:
        data = pickle.load(f, encoding=encoding)
    fname = os.path.basename(fpath)
    gc = partial(get_contents, data)

    if isinstance(data, dict):
        if args_chk(args, 'key'):
            show_keys(data, args.key)
        elif args_chk(args, 'interactive'):
            interactive_view(fname, gc, partial(show_func, data))
        elif args_chk(args, 'cui'):
            interactive_cui(fname, gc, partial(show_func, data))
        else:
            if args_chk(args, 'verbose'):
                try:
                    tmp_keys = sorted(data.keys())
                except TypeError:
                    tmp_keys = data.keys()
                for key in tmp_keys:
                    print_key(key)
                    print(' >>> {}'.format(data[key]))
            else:
                show_tree(fname, gc, logger=logger)
    else:
        print(data)
