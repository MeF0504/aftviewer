import os
import pprint
from functools import partial
from pathlib import PurePosixPath
from logging import getLogger

import h5py

from .. import (GLOBAL_CONF, args_chk, print_key, print_error,
                FG, BG, FG256, BG256, END, get_config, get_col,
                interactive_view, interactive_cui,
                help_template, add_args_specification
                )
from .. import ReturnMessage as RM
from pymeflib.tree2 import show_tree

try:
    import numpy as np
except ImportError:
    imp_np = False
else:
    imp_np = True
    opts = get_config('numpy_printoptions')
    np.set_printoptions(**opts)
logger = getLogger(GLOBAL_CONF.logname)
pargs = get_config('pp_kwargs')


def show_hdf5(h5_file, cpath, **kwargs):
    if 'cui' in kwargs and kwargs['cui']:
        fg = ''
        bg = ''
        end = ''
    else:
        fgkey, bgkey = get_col('type_color')
        if fgkey in FG:
            fg = FG[fgkey]
        elif type(fgkey) is int and 0 <= fgkey <= 255:
            fg = FG256(fgkey)
        else:
            logger.warning(f'incorrect fg color: {fgkey}')
            fg = ''
        if bgkey in BG:
            bg = BG[bgkey]
        elif type(bgkey) is int and 0 <= bgkey <= 255:
            bg = BG256(bgkey)
        else:
            logger.warning(f'incorrect bg color: {bgkey}')
            bg = ''
        end = END
    if cpath not in h5_file:
        return RM(f'incorrect path: {cpath}', True)
    data = h5_file[cpath]
    res = []
    res.append(f'{fg}{bg}attrs{end}')
    for attr in data.attrs:
        res.append(f'{attr}: {data.attrs[attr]}')
    if isinstance(data, h5py.Group):
        res.append(f'{fg}{bg}contents{end}')
        for k in data.keys():
            res.append(k)
    elif isinstance(data, h5py.Dataset):
        res.append(f'{fg}{bg}value{end}')
        data = data[()]
        res.append(pprint.pformat(data, **pargs))
        if hasattr(data, 'shape'):
            res.append(f'shape: {data.shape}')
            is_array = True
        elif hasattr(data, '__len__'):
            res.append(f'len: {len(data)}')
            is_array = True
        else:
            is_array = False
        if imp_np and is_array and (len(data) != 0):
            try:
                res.append(f'mean : {np.nanmean(data)}')
            except Exception as e:
                logger.debug(f'{type(e).__name__}: {e}')
            try:
                res.append(f' max : {np.nanmax(data)}')
            except Exception as e:
                logger.debug(f'{type(e).__name__}: {e}')
            try:
                res.append(f' min : {np.nanmin(data)}')
            except Exception as e:
                logger.debug(f'{type(e).__name__}: {e}')
            try:
                res.append(f' std : {np.nanstd(data)}')
            except Exception as e:
                logger.debug(f'{type(e).__name__}: {e}')
            if hasattr(data, 'shape'):
                try:
                    nan_rate = np.sum(np.isnan(data))/np.prod(data.shape)
                    res.append(f'nan rate: {nan_rate*100:.1f}%')
                except Exception:
                    pass
    return RM('\n'.join(res), False)


def show_detail(h5_file, name, obj):
    if isinstance(obj, h5py.Dataset):
        print_key(name)
        pprint.pprint(h5_file[name][()], **pargs)


def show_names(name, obj):
    if isinstance(obj, h5py.Dataset):
        print(name)


def get_contents(h5_file, path):
    dirs = []
    files = []
    data = h5_file[str(path)]
    if isinstance(data, h5py.Group):
        for k in data.keys():
            contents = f'{path}/{k}'
            if isinstance(h5_file[contents], h5py.Group):
                dirs.append(k)
            elif isinstance(h5_file[contents], h5py.Dataset):
                files.append(k)
    dirs.sort()
    files.sort()
    return dirs, files


def add_args(parser):
    kwargs_k = dict(help='Specify the path to the data to show.'
                    ' If no key is provided, return the list of datasets.')
    add_args_specification(parser, verbose=True, key=True,
                           interactive=True, cui=True,
                           kwargs_k=kwargs_k)


def show_help():
    helpmsg = help_template('hdf5', 'show an contents in the hdf5 file.',
                            add_args)
    print(helpmsg)


def main(fpath, args):
    fname = os.path.basename(fpath)

    h5_file = h5py.File(fpath, 'r')
    gc = partial(get_contents, h5_file)
    sf = partial(show_hdf5, h5_file)

    if args_chk(args, 'interactive'):
        interactive_view(fname, gc, sf, PurePosixPath)
    elif args_chk(args, 'cui'):
        interactive_cui(fpath, gc, sf, PurePosixPath)
    elif args_chk(args, 'key'):
        if args.key:
            for k in args.key:
                print_key(k)
                info = show_hdf5(h5_file, k, cui=False)
                if not info.error:
                    print(info.message)
                    print()
                else:
                    print_error(info.message)
        else:
            h5_file.visititems(show_names)
    elif args_chk(args, 'verbose'):
        h5_file.visititems(partial(show_detail, h5_file))
    else:
        show_tree(fname, gc, logger=logger, purepath=PurePosixPath)

    h5_file.close()
