import numpy as np
from numpy.lib.npyio import NpzFile

from .. import args_chk, print_key, get_config, help_template, \
    add_args_specification


def show_numpy(data):
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
        if np.any(np.isnan(data)):
            # including np.nan
            try:
                d_mean = np.nanmean(data)
            except Exception as e:
                d_mean = '{}: {}'.format(str(type(e)).split("'")[1], e)
            try:
                d_max = np.nanmax(data)
            except Exception as e:
                d_max = '{}: {}'.format(str(type(e)).split("'")[1], e)
            try:
                d_min = np.nanmin(data)
            except Exception as e:
                d_min = '{}: {}'.format(str(type(e)).split("'")[1], e)
            try:
                nan_rate = np.sum(np.isnan(data))/np.prod(data.shape)
            except Exception as e:
                nan_rate = '{}: {}'.format(str(type(e)).split("'")[1], e)
            prt_str = '''mean     : {}
max      : {}
min      : {}
nan rate : {:.1f}%'''.format(d_mean, d_max, d_min, 100*nan_rate)
        else:
            # normal data
            try:
                d_mean = np.mean(data)
            except Exception as e:
                d_mean = '{}: {}'.format(str(type(e)).split("'")[1], e)
            try:
                d_max = np.max(data)
            except Exception as e:
                d_max = '{}: {}'.format(str(type(e)).split("'")[1], e)
            try:
                d_min = np.min(data)
            except Exception as e:
                d_min = '{}: {}'.format(str(type(e)).split("'")[1], e)
            prt_str = '''mean     : {}
max      : {}
min      : {}'''.format(d_mean, d_max, d_min)
    except TypeError:
        # string list or something
        prt_str = 'not a array of number'
    print(prt_str)


def add_args(parser):
    add_args_specification(parser, verbose=True, key=True,
                           interactive=False, cui=False)


def show_help():
    helpmsg = help_template('numpy', 'show the contents of a NumPy-compressed file.' +
                            ' If the file is "npz", you can specify the key name.',
                            add_args)
    print(helpmsg)


def main(fpath, args):
    opts = get_config('numpy_printoptions')
    np.set_printoptions(**opts)
    data = np.load(fpath, allow_pickle=False)
    if args_chk(args, 'verbose'):
        if type(data) is NpzFile:
            for k in data:
                print_key(k)
                print(data[k])
        else:
            print(data)
    elif args_chk(args, 'key'):
        if type(data) is NpzFile:
            if len(args.key) == 0:
                for k in data:
                    print(k)
            for k in args.key:
                print_key(k)
                print(data[k])
                show_numpy(data[k])
                print()
    else:
        if type(data) is NpzFile:
            for k in data:
                print('\n{}'.format(k))
                show_numpy(data[k])
        else:
            show_numpy(data)
