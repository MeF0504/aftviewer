# test functions in viewers/core/__init__.py
import sys
import argparse
import warnings
from pathlib import Path

import pytest

from . import chk_deps

sys.path.insert(0, str(Path(__file__).parent.parent))
from viewers.core import args_chk, load_lib
from viewers.core.helpmsg import add_args_imageviewer, add_args_encoding, \
    add_args_output, add_args_verbose, add_args_key, add_args_interactive, \
    add_args_cui


@pytest.mark.parametrize(('attr', 'arg_list', 'expected'), [
    ('type', ['file', '-t', 'pickle'], True),
    ('type', ['file'], False),
    ('verbose', ['file', '-t', 'pickle', '-v'], True),
    ('verbose', ['file', '-t', 'pickle'], False),
    ('key', ['file', '-t', 'pickle', '-k'], True),
    ('key', ['file', '-t', 'pickle', '-k', 'a'], True),
    ('key', ['file', '-t', 'pickle', '-k', 'a', 'b'], True),
    ('key', ['file', '-t', 'pickle'], False),
    ('interactive', ['file', '-t', 'pickle', '-i'], True),
    ('interactive', ['file', '-t', 'pickle'], False),
    ('image_viewer', ['file', '-t', 'pickle', '-iv', 'matplotlib'], True),
    ('image_viewer', ['file', '-t', 'pickle'], False),
    ('encoding', ['file', '-t', 'pickle', '--encoding', 'ASCII'], True),
    ('encoding', ['file', '-t', 'pickle'], False),
    ('cui', ['file', '-t', 'pickle', '-c'], True),
    ('cui', ['file', '-t', 'pickle'], False),
    ('output', ['file', '-t', 'pickle', '-o', 'path/to/file'], True),
    ('output', ['file', '-t', 'pickle'], False),
    ])
def test_args_chk(attr, arg_list, expected):
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='input file')
    parser.add_argument('-t', '--type')
    add_args_imageviewer(parser)
    add_args_encoding(parser)
    add_args_output(parser)
    add_args_verbose(parser)
    add_args_key(parser)
    add_args_interactive(parser)
    add_args_cui(parser)
    args = parser.parse_args(arg_list)
    assert args_chk(args, attr) is expected


@pytest.mark.parametrize(('filetype'), [
    ('hdf5'),
    ('pickle'),
    ('sqlite3'),
    ('np_pickle'),
    ('tar'),
    ('zip'),
    ('jupyter'),
    ('numpy'),
    ('raw_image'),
    ('xpm'),
    ])
def test_loadlib(filetype):
    if not chk_deps(filetype):
        warnings.warn(f'skip cheking {filetype}')
        return
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='input file')
    parser.add_argument('-t', '--type')
    args = parser.parse_args(['file', '-t', filetype])
    lib = load_lib(args)
    assert lib is not None, f'failed to load library; {args.type}'
    if not hasattr(lib, 'show_help'):
        warnings.warn(f'showing help is not supported; {args.type}')
    assert hasattr(lib, 'main')
