import pickle
import os

from . import args_chk, print_key, cprint, debug_print, json_opts
try:
    import numpy as np
except ImportError:
    imp_np = False
else:
    imp_np = True


# It is difficult to rebuild a recursive dictionary by any means...
def main(fpath, args):
    inter_str = "'q':quit, '..':go to parent, key_name:select a key >> "
    if args_chk(args, 'encoding'):
        debug_print('set encoding from args')
        encoding = args.encoding
    elif 'pickle_encoding' in json_opts:
        debug_print('set encoding from json')
        encoding = json_opts['pickle_encoding']
    else:
        encoding = 'ASCII'
    debug_print('encoding: {}'.format(encoding))
    try:
        with open(fpath, 'rb') as f:
            data = pickle.load(f, encoding=encoding)
    except UnicodeDecodeError:
        debug_print('decode error: encoding={}'.format(encoding))
        with open(fpath, 'rb') as f:
            data = pickle.load(f, encoding='latin1')

    if isinstance(data, dict):
        if args_chk(args, 'key'):
            if len(args.key) == 0:
                for k in data:
                    print(k)
            else:
                for k in data:
                    if str(k) in args.key:
                        print_key(str(k))
                        print(data[k])
                        print()
        elif hasattr(args, 'interactive') and args.interactive:
            selected_keys = []
            tmp_data = data
            while(True):
                key_strs = [str(k) for k in selected_keys]
                cpath = '{}/{}'.format(os.path.basename(fpath),
                                       '/'.join(key_strs))
                cprint('current path:', ' {}'.format(cpath), bg='c')
                cprint('contents in this dict:', ' ', bg='g', end='')
                try:
                    tmp_keys = sorted(tmp_data.keys())
                except TypeError:
                    tmp_keys = tmp_data.keys()
                for i, k in enumerate(tmp_keys):
                    print('{},'.format(k), end='  ')
                print('\n')
                key_name = input(inter_str)
                if key_name == 'q':
                    break
                elif key_name == '':
                    continue
                elif key_name == '..':
                    if len(selected_keys) >= 1:
                        selected_keys = selected_keys[:-1]
                        tmp_data = data
                        for sk in selected_keys:
                            tmp_data = tmp_data[sk]
                    else:
                        cprint('you are in root.\n', '', fg='r')
                else:
                    find_key = False
                    for k in tmp_data:
                        if str(k) == key_name:
                            find_key = True
                            if type(tmp_data[k]) == dict:
                                tmp_data = tmp_data[k]
                                selected_keys.append(k)
                            else:
                                cprint('output::', '\n{}'.format(tmp_data[k]),
                                       bg='r')
                                if imp_np:
                                    if (type(tmp_data[k]) == np.ndarray) and (len(tmp_data[k]) != 0):
                                        try:
                                            dmean = np.nanmean(tmp_data[k])
                                        except Exception as e:
                                            dmean = '{}: {}'.format(str(type(e)).split("'")[1], e)
                                        try:
                                            dmedian = np.nanmedian(tmp_data[k])
                                        except Exception as e:
                                            dmedian = '{}: {}'.format(str(type(e)).split("'")[1], e)
                                        try:
                                            dstd = np.nanstd(tmp_data[k])
                                        except Exception as e:
                                            dstd = '{}: {}'.format(str(type(e)).split("'")[1], e)
                                        print('>> shape: {}, mean: {:.2e}, median: {:.2e}, std: {:.2e}'.format(tmp_data[k].shape, dmean, dmedian, dstd))
                                print('')
                    if not find_key:
                        cprint('"{}" is not a correct name'.format(key_name),
                               '', fg='r')
        else:
            try:
                tmp_keys = sorted(data.keys())
            except TypeError:
                tmp_keys = data.keys()
            for key in tmp_keys:
                print(key)
                if args.verbose:
                    print(' >>> {}'.format(data[key]))
                else:
                    print('  type   : {}'.format(type(data[key]).__name__))
                    if hasattr(data[key], '__len__'):
                        print('  length : {}'.format(len(data[key])))
    else:
        print(data)
