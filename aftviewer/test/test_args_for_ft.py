# test arguments of all file types.
import argparse
import warnings
from importlib import import_module

import pytest

from . import chk_deps


# image viewer, encoding, output, verbose, key 0, key 1, key 2,
# interactive, interactive_cui
@pytest.mark.parametrize(('filetype', 'is_args_ok'), [
    ('hdf5', [False, False, False, True, True, True, True, True, True]),
    ('pickle', [False, True, False, True, True, True, True, True, True]),
    ('sqlite3', [False, False, True, True, True, True, True, True, True]),
    ('np_pickle', [False, True, False, True, True, True, True, True, True]),
    ('tar', [True, False, True, True, True, True, True, True, True]),
    ('zip', [True, False, True, True, True, True, True, True, True]),
    ('jupyter', [True, False, True, True, False, False, False, False, False]),
    ('numpy', [False, False, False, True, True, True, True, False, False]),
    ('raw_image',
     [True, False, False, False, False, False, False, False, False]),
    ('xpm', [True, False, False, False, False, False, False, False, False]),
    ('stl', [False, False, False, False, False, False, False, False, False]),
    ])
def test_args_filetypes(filetype, is_args_ok):
    if not chk_deps(filetype):
        warnings.warn(f'skip cheking {filetype}')
        return
    test_args_list = [
            ['--image_viewer', 'matplotlib'],
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
    lib = import_module(f'aftviewer.viewers.{filetype}')
    not_ok = []
    for i, test_args in enumerate(test_args_list):
        parser = argparse.ArgumentParser()
        parser.add_argument('file', help='input file')
        parser.add_argument('-t', '--type')
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
