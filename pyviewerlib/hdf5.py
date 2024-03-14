import os
from functools import partial
from pathlib import PurePosixPath
from logging import getLogger

import h5py

from . import GLOBAL_CONF, args_chk, print_key, cprint, get_col, \
    FG, BG, FG256, BG256, END, set_numpy_format, get_config, \
    interactive_view, interactive_cui, help_template, add_args_specification
from . import ReturnMessage as RM
from pymeflib.tree2 import show_tree

try:
    import numpy as np
except ImportError:
    imp_np = False
else:
    imp_np = True
    set_numpy_format(np)
logger = getLogger(GLOBAL_CONF.logname)


def show_hdf5(h5_file, cpath, **kwargs):
    if 'cui' in kwargs and kwargs['cui']:
        fg = ''
        bg = ''
        end = ''
    else:
        fgkey, bgkey = get_config('hdf5', 'type_color')
        if fgkey in FG:
            fg = FG[fgkey]
        elif type(fgkey) is int:
            fg = FG256(fgkey)
        else:
            # debug_print(f'incorrect fg color: {fgkey}')
            logger.warning(f'incorrect fg color: {fgkey}')
            fg = ''
        if bgkey in BG:
            bg = BG[bgkey]
        elif type(bgkey) is int:
            bg = BG256(bgkey)
        else:
            # debug_print(f'incorrect bg color: {bgkey}')
            logger.warning(f'incorrect bg color: {bgkey}')
            bg = ''
        end = END
    data = h5_file[cpath]
    res = []
    res.append('{}{}attrs{}'.format(fg, bg, end))
    for attr in data.attrs:
        res.append('{}: {}'.format(attr, data.attrs[attr]))
    if isinstance(data, h5py.Group):
        res.append('{}{}contents{}'.format(fg, bg, end))
        for k in data.keys():
            res.append(k)
    elif isinstance(data, h5py.Dataset):
        res.append('{}{}value{}'.format(fg, bg, end))
        data = data[()]
        res.append('{}'.format(data))
        if hasattr(data, 'shape'):
            res.append('shape: {}'.format(data.shape))
            is_array = True
        elif hasattr(data, '__len__'):
            res.append('len: {}'.format(len(data)))
            is_array = True
        else:
            is_array = False
        if imp_np and is_array and (len(data) != 0):
            try:
                dmean = np.nanmean(data)
                res.append('mean : {}'.format(dmean))
            except Exception as e:
                # debug_print('{}: {}'.format(str(type(e)).split("'")[1], e))
                logger.debug(f'{type(e).__name__}: {e}')
            try:
                dmax = np.nanmax(data)
                res.append(' max : {}'.format(dmax))
            except Exception as e:
                # debug_print('{}: {}'.format(str(type(e)).split("'")[1], e))
                logger.debug(f'{type(e).__name__}: {e}')
            try:
                dmin = np.nanmin(data)
                res.append(' min : {}'.format(dmin))
            except Exception as e:
                # debug_print('{}: {}'.format(str(type(e)).split("'")[1], e))
                logger.debug(f'{type(e).__name__}: {e}')
            try:
                dstd = np.nanstd(data)
                res.append(' std : {}'.format(dstd))
            except Exception as e:
                # debug_print('{}: {}'.format(str(type(e)).split("'")[1], e))
                logger.debug(f'{type(e).__name__}: {e}')
            if hasattr(data, 'shape'):
                try:
                    nan_rate = np.sum(np.isnan(data))/np.prod(data.shape)
                    res.append('nan rate: {:.1f}%'.format(nan_rate*100))
                except Exception:
                    pass
    return RM('\n'.join(res), False)


def show_detail(h5_file, name, obj):
    if isinstance(obj, h5py.Dataset):
        print_key(name)
        print("{}".format(h5_file[name][()]))


def show_names(name, obj):
    if isinstance(obj, h5py.Dataset):
        print(name)


def get_contents(h5_file, path):
    dirs = []
    files = []
    data = h5_file[str(path)]
    if isinstance(data, h5py.Group):
        for k in data.keys():
            contents = '{}/{}'.format(path, k)
            if isinstance(h5_file[contents], h5py.Group):
                dirs.append(k)
            elif isinstance(h5_file[contents], h5py.Dataset):
                files.append(k)
    return dirs, files


def add_args(parser):
    add_args_specification(parser, verbose=True, key=True,
                           interactive=True, cui=True)


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
        fg, bg = get_col('msg_error')
        if args.key:
            for k in args.key:
                print_key(k)
                info = show_hdf5(h5_file, k, cui=False)
                if not info.error:
                    print(info.message)
                    print()
                else:
                    cprint(info.message, fg=fg, bg=bg)
        else:
            h5_file.visititems(show_names)
    elif args_chk(args, 'verbose'):
        h5_file.visititems(partial(show_detail, h5_file))
    else:
        show_tree(fname, gc, purepath=PurePosixPath)

    h5_file.close()
