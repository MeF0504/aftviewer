# test help messages.
import argparse
import warnings
from types import FunctionType

import pytest

from aftviewer.core import __load_lib
from . import chk_deps
from aftviewer.cli import get_parser_arg


@pytest.mark.parametrize(('filetype'), [
    ('hdf5'),
    ('pickle'),
    ('sqlite3'),
    ('np_pickle'),
    ('tar'),
    ('zip'),
    ('jupyter'),
    ('e-mail'),
    ('numpy'),
    ('raw_image'),
    ('xpm'),
    ('stl'),
    ('fits'),
    ('healpix'),
    ('excel'),
    ])
def test_help_message(filetype):
    if not chk_deps(filetype):
        warnings.warn(f'skip cheking {filetype}')
        return
    parser = argparse.ArgumentParser(**get_parser_arg())
    args = parser.parse_args([])
    args.file = 'help'
    args.type = filetype
    lib = __load_lib(args)
    assert lib is not None, 'failed to load library.'
    if hasattr(lib, 'show_help') and type(lib.show_help) is FunctionType:
        lib.show_help()
    else:
        warnings.warn(f'{filetype} does not support showing help.')
