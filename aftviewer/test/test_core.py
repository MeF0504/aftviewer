# test functions in aftviewer/core/__init__.py
import argparse
import warnings
import json
from pathlib import Path
from importlib import reload

import pytest

from . import chk_deps

import aftviewer.core
from aftviewer.core import (args_chk, __load_lib, get_config, cprint,
                            get_col, print_error, print_warning, print_key,
                            __set_filetype, __get_opt_keys, __get_color_names,
                            __set_user_opts, __def_opts)
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
    __set_user_opts({}, None)
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
    __set_user_opts({filetype: {key: val}}, None)
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


def test_def_get_col():
    __set_user_opts(None, {})
    def_colors = __def_opts['colors']
    col_type = (int, str, type(None))
    for ft in def_colors:
        if ft == 'defaults':
            ft2 = None
        else:
            ft2 = ft
        for key in def_colors[ft]:
            def1 = def_colors[ft][key]
            def2 = get_col(key, ft2)
            assert len(def2) == 2, 'len(color) is not 2'
            assert type(def2[0]) in col_type, 'incorrect type (fg)'
            assert type(def2[1]) in col_type, 'incorrect type (bg)'
            assert def1 == def2, f'"{ft}"-"{key}" is not much: {def1}, {def2}'


@pytest.mark.parametrize(('key', 'val', 'filetype'), [
    ('msg_error', [0, None], 'defaults'),
    ('cui_main', [255, 'k'], 'defaults'),
    ('input_color', ['r', 150], 'jupyter'),
    ('interactive_path', [None, 'm'], 'tar'),
    ])
def test_user_get_col(key, val, filetype):
    def_colors = __def_opts['colors']['defaults']
    __set_user_opts(None, {filetype: {key: val}})
    col_type = (int, str, type(None))
    res1 = get_col(key, filetype)
    assert len(res1) == 2, 'len(color) is not 2 @ 1'
    assert type(res1[0]) in col_type, 'incorrect type (fg) @ 1'
    assert type(res1[1]) in col_type, 'incorrect type (bg) @ 1'
    assert res1 == val, f'get colors ({filetype}) is not match, {res1}, {val}'
    res2 = get_col(key)
    if filetype == 'defaults':
        def1 = val
    elif key in def_colors:
        def1 = def_colors[key]
    else:
        return
    assert len(res2) == 2, 'len(color) is not 2 @ 2'
    assert type(res2[0]) in col_type, 'incorrect type (fg) @ 2'
    assert type(res2[1]) in col_type, 'incorrect type (bg) @ 2'
    assert res2 == def1, f'get colors (def) is not match, {res2}, {def1}'


def test_print_error():
    # syntax check?
    print_error('error')


def test_print_warning():
    # syntax check?
    print_warning('warning')


def test_print_key():
    # syntax check?
    print_key('key')


def test_set_filetype():
    aftviewer.core.__filetype = None
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='input file')
    parser.add_argument('-t', '--type')
    args = parser.parse_args(['.', '-t', 'pickle'])
    __set_filetype(args)
    assert aftviewer.core.__filetype == 'pickle', \
        f'file type is incorrect @ 1, {aftviewer.core.__filetype}'

    aftviewer.core.__filetype = None
    args = parser.parse_args(['config_list'])
    __set_filetype(args)
    assert aftviewer.core.__filetype == 'defaults', \
        f'file type is incorrect @ 2, {aftviewer.core.__filetype}'

    aftviewer.core.__filetype = None
    args = parser.parse_args([__file__])
    __set_filetype(args)
    assert aftviewer.core.__filetype is not None, 'failed to set filetype'


def test_get_opt_keys():
    reload(aftviewer.core)
    with open(Path(__file__).parent.parent/'core/default.json') as f:
        opts = json.load(f)
    opt_keys = __get_opt_keys()
    for ft in opts['config']:
        for opt in opts['config'][ft]:
            assert opt in opt_keys[ft], f'def opt {ft}-{opt} not found.'

    user_optfile = Path('~/.config/aftviewer/setting.json').expanduser()
    if user_optfile.is_file():
        with open(user_optfile) as f:
            user_opts = json.load(f)
        for ft in user_opts['config']:
            if ft not in aftviewer.core.__type_config:
                continue
            for opt in user_opts['config'][ft]:
                if opt in opts['config']['defaults']:
                    assert opt in opt_keys[ft], \
                        f'user opt (def) {ft}-{opt} not found.'
                elif ft in opts['config'] and opt in opts['config'][ft]:
                    assert opt in opt_keys[ft], \
                        f'user opt ({ft}) {ft}-{opt} not found.'


def test_get_color_names():
    pass
