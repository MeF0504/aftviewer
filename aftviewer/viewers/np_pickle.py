import os
from pathlib import PurePath
from functools import partial
from logging import getLogger

import numpy as np
from numpy.lib.npyio import NpzFile

from .. import (GLOBAL_CONF, args_chk, print_key, get_config,
                interactive_view, interactive_cui, help_template,
                add_args_specification, add_args_encoding)
from .. import ReturnMessage as RM
from .numpy import show_numpy
from .pickle import show_func as show_pickle, get_contents as get_pickle
logger = getLogger(GLOBAL_CONF.logname)


def show_func(data, path, **kwargs):
    parts = PurePath(path).parts
    if len(parts) < 1:
        return RM(' something wrong, path is too short.', True)
    if len(parts) == 1:
        res = RM('{}'.format(data[parts[0]]), False)
    else:
        pdata = data[parts[0]]
        assert pdata.dtype == np.dtype('O'), f'incorrect type, {pdata.dtype}'
        res = show_pickle(pdata.item(), os.sep.join(parts[1:]))
    return res


def get_contents(data, path):
    dirs = []
    files = []
    parts = PurePath(path).parts
    if len(parts) == 0:
        for k in data.keys():
            if data[k].dtype == np.dtype('O'):
                dirs.append(k)
            else:
                files.append(k)
        dirs.sort()
        files.sort()
    else:
        pdata = data[parts[0]]
        assert pdata.dtype == np.dtype('O'), f'incorrect type, {pdata.dtype}'
        dirs, files = get_pickle(pdata.item(), os.sep.join(parts[1:]))
    return dirs, files


def show_data(data, key):
    print_key(key)
    if data[key].dtype == np.dtype('O'):
        # object
        print(data[key].item())
    else:
        print(data[key])
        show_numpy(data[key])


def add_args(parser):
    add_args_encoding(parser)
    add_args_specification(parser, verbose=True, key=True,
                           interactive=True, cui=True)


def show_help():
    helpmsg = help_template('np_pickle', 'show the contents of a pickle-allowed NumPy-compressed file.' +
                            ' Note that this type is not specified automatically.',
                            add_args)
    print(helpmsg)


def main(fpath, args):
    if args_chk(args, 'encoding'):
        logger.info('set encoding from args')
        encoding = args.encoding
    else:
        encoding = get_config('encoding', 'np_pickle')
    logger.info(f'encoding: {encoding}')
    opts = get_config('numpy_printoptions', 'np_pickle')
    np.set_printoptions(**opts)

    data = np.load(fpath, allow_pickle=True, encoding=encoding)
    if type(data) is not NpzFile:
        print('please use --type numpy')
        return
    fname = os.path.basename(fpath)
    gc = partial(get_contents, data)
    sf = partial(show_func, data)

    if args_chk(args, 'verbose'):
        for k in data.keys():
            show_data(data, k)
    elif args_chk(args, 'key'):
        if args.key:
            for k in args.key:
                show_data(data, k)
        else:
            for k in data.keys():
                print(k)
        pass
    elif args_chk(args, 'interactive'):
        interactive_view(fname, gc, sf)
    elif args_chk(args, 'cui'):
        interactive_cui(fname, 'np_pickle', gc, sf)
    else:
        for k in data.keys():
            print_key(k)
            show_numpy(data[k])
