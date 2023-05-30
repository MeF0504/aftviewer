import pickle
import os
from pathlib import PurePath
from functools import partial

from . import args_chk, print_key, debug_print, json_opts, \
    interactive_view, interactive_cui

from pymeflib.tree2 import show_tree


def show_keys(data, key):
    if key:
        for k in key:
            if k in data:
                print(data[k])
    else:
        for k in data:
            print(k)


def show_func(data, cpath, **kwargs):
    tmp_data = data
    for k in PurePath(cpath).parts:
        if k in tmp_data:
            tmp_data = tmp_data[k]
        else:
            return '', 'Error! no key {}'.format(k)
    return '{}'.format(tmp_data), None


def get_contents(data, path):
    tmp_data = data
    dirs = []
    files = []
    for k in PurePath(path).parts:
        tmp_data = tmp_data[k]
    if isinstance(tmp_data, dict):
        for k in tmp_data.keys():
            if isinstance(tmp_data[k], dict):
                dirs.append(k)
            else:
                files.append(k)
    return dirs, files


def main(fpath, args):
    if args_chk(args, 'encoding'):
        debug_print('set encoding from args')
        encoding = args.encoding
    else:
        encoding = json_opts['pickle_encoding']
    debug_print('encoding: {}'.format(encoding))
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
                show_tree(fname, gc)
    else:
        print(data)
