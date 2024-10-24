import sys
import shutil

import numpy as np
from numpy.lib.npyio import NpzFile

from .. import args_chk, print_key, get_config, help_template, add_args_key

__detail_opts = dict(precision=None,
                     threshold=sys.maxsize,
                     edgeitems=None,
                     linewidth=shutil.get_terminal_size().columns-2,
                     suppress=True,
                     nanstr='nan',
                     infstr='inf',
                     sign=' ',
                     )


def show_summary(data: np.ndarray):
    # shape
    dtype = data.dtype
    print('type     : {}'.format(dtype))
    shape = data.shape
    print('shape    : {}'.format(shape))
    if np.prod(shape) == 0:
        print('  empty data.')
        return
    # other information
    try:
        isnan = np.any(np.isnan(data))
        try:
            if isnan:
                d_mean = np.nanmean(data)
            else:
                d_mean = np.mean(data)
        except Exception as e:
            d_mean = f'{type(e).__name__}: {e}'
        try:
            if isnan:
                d_max = np.nanmax(data)
            else:
                d_max = np.max(data)
        except Exception as e:
            d_max = f'{type(e).__name__}: {e}'
        try:
            if isnan:
                d_min = np.nanmin(data)
            else:
                d_min = np.min(data)
        except Exception as e:
            d_min = f'{type(e).__name__}: {e}'
        try:
            if isnan:
                nan_rate = np.sum(np.isnan(data))/np.prod(data.shape)
                nan_rate = f'{100*nan_rate:.1f}%'
            else:
                nan_rate = ''
        except Exception as e:
            nan_rate = f'{type(e).__name__}: {e}'
        if isnan:
            prt_str = f'''mean     : {d_mean}
max      : {d_max}
min      : {d_min}
nan rate : {nan_rate}'''
        else:
            prt_str = f'''mean     : {d_mean}
max      : {d_max}
min      : {d_min}'''
    except TypeError:
        # string list or something
        prt_str = 'not a array of number'
    print(prt_str)


def add_args(parser):
    ex_group = parser.add_mutually_exclusive_group()
    add_args_key(ex_group)
    ex_group.add_argument('-v', '--verbose',
                          help='show details. -v just print the value'
                          ' in this file/key.'
                          ' -vv show details (mean, std, etc.) and'
                          ' all numbers in this file/key.',
                          action='count', default=0)


def show_help():
    helpmsg = help_template('numpy',
                            'show the contents of a NumPy-compressed file.'
                            ' If the file is "npz",'
                            ' you can specify the key name.',
                            add_args)
    print(helpmsg)


def main_npy(data, args):
    if hasattr(args, 'verbose') and args.verbose > 0:
        if args.verbose == 1:
            print(data)
        elif args.verbose == 2:
            with np.printoptions(**__detail_opts):
                print(data)
            show_summary(data)
    elif args_chk(args, 'key'):
        print("'-k' option is not supported in 'npy' file.")
    else:
        show_summary(data)


def main_npz(data, args):
    if hasattr(args, 'verbose') and args.verbose > 0:
        if args.verbose == 1:
            for k in data:
                print_key(k)
                print(data[k])
        elif args.verbose == 2:
            for k in data:
                print_key(k)
                with np.printoptions(**__detail_opts):
                    print(data[k])
                show_summary(data[k])
    elif args_chk(args, 'key'):
        if len(args.key) == 0:
            for k in data:
                print(k)
        for k in args.key:
            print_key(k)
            print(data[k])
            show_summary(data[k])
            print()
    else:
        for k in data:
            print()
            print_key(k)
            show_summary(data[k])


def main(fpath, args):
    opts = get_config('numpy_printoptions')
    np.set_printoptions(**opts)
    data = np.load(fpath, allow_pickle=False)
    if type(data) is NpzFile:
        main_npz(data, args)
    else:
        main_npy(data, args)
