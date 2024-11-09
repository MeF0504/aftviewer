# test functions in aftviewer/core/__init__.py
import argparse
import warnings

import pytest

from . import chk_deps

from aftviewer.core import (args_chk, __load_lib, get_config, cprint,
                            get_col, interactive_view, print_error,
                            print_warning, print_key, run_system_cmd,
                            __set_filetype, __get_opt_keys, __get_color_names,
                            __def_opts, __user_opts)
from aftviewer.core.helpmsg import (add_args_imageviewer, add_args_encoding,
                                    add_args_output, add_args_verbose,
                                    add_args_key, add_args_interactive,
                                    add_args_cui)


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
    ('stl'),
    ('fits'),
    ])
def test_load_lib(filetype):
    if not chk_deps(filetype):
        warnings.warn(f'skip cheking {filetype}')
        return
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='input file')
    parser.add_argument('-t', '--type')
    args = parser.parse_args(['file', '-t', filetype])
    lib = __load_lib(args)
    assert lib is not None, f'failed to load library; {args.type}'
    if not hasattr(lib, 'show_help'):
        warnings.warn(f'showing help is not supported; {args.type}')
    assert hasattr(lib, 'main')


def test_def_get_config():
    __user_opts['config'] = {}
    def_opts = __def_opts['config']
    for ft in def_opts:
        if ft == 'defaults':
            ft2 = None
        else:
            ft2 = ft
        for key in def_opts[ft]:
            def1 = def_opts[ft][key]
            def2 = get_config(key, ft2)
            assert def1 == def2, f'"{ft}"-"{key}" is not much: {def1}, {def2}'


@pytest.mark.parametrize(('key', 'val', 'filetype'), [
    ('image_viewer', 'display', 'defaults'),
    ('system_cmd', 'ls', 'hdf5'),
    ('iv_exec_cmd', ['%c', '%s', '-v'], 'raw_image'),
    ('numpy_printoptions', {}, 'numpy'),
    ('encoding', 'utf-8', 'pickle'),
    ('facecolor', '#505050', 'stl'),
    ])
def test_user_get_config(key, val, filetype):
    def_opts = __def_opts['config']['defaults']
    __user_opts['config'] = {}
    __user_opts['config'][filetype] = {key: val}
    res1 = get_config(key, filetype)
    assert res1 == val, f'get config ({filetype}) is not match, {res1}, {val}'
    res2 = get_config(key)
    if filetype == 'defaults':
        def1 = val
    elif key in def_opts:
        def1 = def_opts[key]
    else:
        return
    assert res2 == def1, f'get config (def) is not match, {res2}, {def1}'


def test_cprint():
    keys = [0, 100, 200, 255]
    keys += list('wrbgcmyb')
    keys += [None]
    for fkey in keys:
        for bkey in keys:
            cprint('test1', 'test2', fg=fkey, bg=bkey)


def test_get_col():
    pass


def test_interactive_view():
    # impossible to test?
    pass


def test_print_error():
    pass


def test_print_warning():
    pass


def test_print_key():
    pass


def test_run_system_command():
    pass


def test_set_filetype():
    pass


def test_get_opt_keys():
    pass


def test_get_color_names():
    pass
