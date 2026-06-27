# test arguments of all file types.
import argparse
import warnings
from importlib import import_module

import pytest

from . import chk_deps
from aftviewer.core import GLOBAL_CONF
from aftviewer.cli import get_parser_arg


# image viewer, encoding, output, verbose, key 0, key 1, key 2,
# interactive, interactive_cui
args_ft = [
    ('pickle', [False, True, False, True, True, True, True, True, True]),
    ('tar', [True, False, True, True, True, True, True, True, True]),
    ('zip', [True, False, True, True, True, True, True, True, True]),
    ('jupyter', [True, True, True, True, False, False, False, False, False]),
    ]
if 'hdf5' in GLOBAL_CONF.add_viewers:
    args_ft.append(('hdf5', [False, False, False, True, True, True, True,
                             True, True]))
if 'sqlite3' in GLOBAL_CONF.add_viewers:
    args_ft.append(('sqlite3', [False, False, True, True, True, True, True,
                                True, True]))
if 'np_pickle' in GLOBAL_CONF.add_viewers:
    args_ft.append(('np_pickle', [False, True, False, True, True, True, True,
                                  True, True]))
if 'e' in GLOBAL_CONF.add_viewers:
    args_ft.append(('e-mail', [True, True, False, True, True, True, True,
                               False, True]))
if 'numpy' in GLOBAL_CONF.add_viewers:
    args_ft.append(('numpy', [False, False, False, True, True, True, True,
                              False, False]))
if 'raw_image' in GLOBAL_CONF.add_viewers:
    args_ft.append(('raw_image', [True, False, False, False, False, False,
                                  False, False, False]))
if 'xpm' in GLOBAL_CONF.add_viewers:
    args_ft.append(('xpm', [True, False, False, False, False, False, False,
                            False, False]))
if 'stl' in GLOBAL_CONF.add_viewers:
    args_ft.append(('stl', [False, False, False, False, False, False, False,
                            False, False]))
if 'fits' in GLOBAL_CONF.add_viewers:
    args_ft.append(('fits', [True, False, False, False, True, True, True,
                             False, False]))
if 'healpix' in GLOBAL_CONF.add_viewers:
    args_ft.append(('healpix', [False, False, True, False, True, True, True,
                                False, False]))
if 'excel' in GLOBAL_CONF.add_viewers:
    args_ft.append(('excel', [False, True, False, False, True, True, True,
                              False, True]))
if 'root' in GLOBAL_CONF.add_viewers:
    args_ft.append(('root', [False, False, False, True, True, True, True,
                             False, False]))
if 'plist' in GLOBAL_CONF.add_viewers:
    args_ft.append(('plist', [False, False, False, True, True, True, True,
                              True, True]))


@pytest.mark.parametrize(('filetype', 'is_args_ok'), args_ft)
def test_args_filetypes(filetype, is_args_ok):
    if not chk_deps(filetype):
        warnings.warn(f'skip cheking {filetype}')
        return
    test_args_list = [
            ['--image_viewer', 'PIL'],
            ['--encoding', 'enc'],
            ['--output', 'path/to/file'],
            ['--verbose'],
            ['--key'],
            ['--key', 'KEY'],
            ['--key', 'KEY1', 'KEY2'],
            ['--interactive'],
            ['--interactive_cui'],
            ]
    assert len(is_args_ok) == len(test_args_list)
    if filetype in GLOBAL_CONF.add_viewers:
        lib = import_module(f'viewers.{filetype}')
    else:
        lib = import_module(f'aftviewer.viewers.{filetype}')
    not_ok = []
    for i, test_args in enumerate(test_args_list):
        parser = argparse.ArgumentParser(**get_parser_arg())
        parser.add_argument('file', help='input file')
        parser.add_argument('-t', '--type')
        parser.add_argument('-', dest='subcmd', default=None)
        lib.add_args(parser)
        args, rems = parser.parse_known_args(
                ['file', '-t', filetype] + test_args)
        if len(rems) == 0:
            if is_args_ok[i] is not True:
                not_ok.append(' '.join(test_args))
        else:
            if is_args_ok[i] is not False:
                not_ok.append(' '.join(test_args))

    assert len(not_ok) == 0, f'failed arguments ({filetype}): {not_ok}'
