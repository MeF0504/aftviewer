import os
from functools import partial

import h5py

from . import args_chk, print_key, cprint, debug_print,\
    interactive_view, interactive_cui,FG, BG, END
from libtree import show_tree
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
            except Exception as e:
                dmean = '{}: {}'.format(str(type(e)).split("'")[1], e)
            res.append('mean : {}'.format(dmean))
            try:
                dmax = np.nanmax(data)
            except Exception as e:
                dmax = '{}: {}'.format(str(type(e)).split("'")[1], e)
            res.append(' max : {}'.format(dmax))
            try:
                dmin = np.nanmin(data)
            except Exception as e:
                dmin = '{}: {}'.format(str(type(e)).split("'")[1], e)
            res.append(' min : {}'.format(dmin))
            try:
                dstd = np.nanstd(data)
            except Exception as e:
                dstd = '{}: {}'.format(str(type(e)).split("'")[1], e)
            res.append(' std : {}'.format(dstd))
            if hasattr(data, 'shape'):
                try:
                    nan_rate = np.sum(np.isnan(data))/np.prod(data.shape)
                    res.append('nan rate: {:.1f}%'.format(nan_rate*100))
                except Exception:
                    pass
    return res, None


def make_list(args, h5_file, list_tree, name, obj):
    if isinstance(obj, h5py.Dataset):
        if not (args_chk(args, 'interactive') or args_chk(args, 'cui')):
            if args_chk(args, 'verbose'):
                print_key(name)
                print("{}".format(h5_file[name][()]))
            elif args_chk(args, 'key') and len(args.key) == 0:
                print(name)

        tmp_list = list_tree
        depth = 1
        debug_print('cpath: {}'.format(name))
        for p in name.split('/'):
            if p == name.split('/')[-1] and depth == len(name.split('/')):
                tmp_list.append(p)
                debug_print('add {}'.format(p))
            elif p in tmp_list[0]:
                tmp_list = tmp_list[0][p]
                depth += 1
            else:
                tmp_list[0][p] = [{}]
                tmp_list = tmp_list[0][p]
                depth += 1


def main(fpath, args):
    list_tree = [{}]
    fname = os.path.basename(fpath)

    h5_file = h5py.File(fpath, 'r')
    # make list_tree
    h5_file.visititems(partial(make_list, args, h5_file, list_tree))

    if args_chk(args, 'interactive'):
        interactive_view(list_tree, fname, partial(show_hdf5, h5_file))
    elif args_chk(args, 'cui'):
        interactive_cui(list_tree, fpath, partial(show_hdf5, h5_file))
    elif args_chk(args, 'key'):
        for k in args.key:
            print_key(k)
            info, err = show_hdf5(h5_file, k, False)
            if err is None:
                print("\n".join(info))
                print()
            else:
                cprint(err, fg='r')
    elif not args_chk(args, 'verbose'):
        show_tree(list_tree, fname)

    h5_file.close()
