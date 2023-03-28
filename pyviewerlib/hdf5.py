import os
from functools import partial

import h5py

from . import args_chk, print_key, cprint, debug_print,\
    interactive_view, interactive_cui, FG, BG, END
from pymeflib.tree2 import show_tree
try:
    import numpy as np
except ImportError:
    imp_np = False
else:
    imp_np = True


def show_hdf5(h5_file, cpath, cui=False):
    if cui:
        fg = ''
        bg = ''
        end = ''
    else:
        fg = FG['k']
        bg = BG['w']
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
                debug_print('{}: {}'.format(str(type(e)).split("'")[1], e))
            try:
                dmax = np.nanmax(data)
                res.append(' max : {}'.format(dmax))
            except Exception as e:
                debug_print('{}: {}'.format(str(type(e)).split("'")[1], e))
            try:
                dmin = np.nanmin(data)
                res.append(' min : {}'.format(dmin))
            except Exception as e:
                debug_print('{}: {}'.format(str(type(e)).split("'")[1], e))
            try:
                dstd = np.nanstd(data)
                res.append(' std : {}'.format(dstd))
            except Exception as e:
                debug_print('{}: {}'.format(str(type(e)).split("'")[1], e))
            if hasattr(data, 'shape'):
                try:
                    nan_rate = np.sum(np.isnan(data))/np.prod(data.shape)
                    res.append('nan rate: {:.1f}%'.format(nan_rate*100))
                except Exception:
                    pass
    return res, None


def show_detail(h5_file, name, obj):
    if isinstance(obj, h5py.Dataset):
        print_key(name)
        print("{}".format(h5_file[name][()]))


def show_names(name, obj):
    if isinstance(obj, h5py.Dataset):
        print(name)


def get_contents(h5_file, root, path):
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


def main(fpath, args):
    fname = os.path.basename(fpath)

    h5_file = h5py.File(fpath, 'r')
    gc = partial(get_contents, h5_file)

    if args_chk(args, 'interactive'):
        interactive_view(fname, gc, partial(show_hdf5, h5_file))
    elif args_chk(args, 'cui'):
        interactive_cui(fpath, gc, partial(show_hdf5, h5_file))
    elif args_chk(args, 'key'):
        if args.key:
            for k in args.key:
                print_key(k)
                info, err = show_hdf5(h5_file, k, False)
                if err is None:
                    print("\n".join(info))
                    print()
                else:
                    cprint(err, fg='r')
        else:
            h5_file.visititems(show_names)
    elif args_chk(args, 'verbose'):
        h5_file.visititems(partial(show_detail, h5_file))
    else:
        show_tree(fname, gc)

    h5_file.close()
