# test functions in aftviewer/cli/__init__.py
import argparse

import pytest

from aftviewer.cli import (main, get_types,
                           get_args, show_opts, set_shell_comp, update)


def test_main():
    # syntax check?
    main()


def test_get_types():
    # syntax check?
    get_types()


def test_get_args():
    # check the function run correctly.
    get_args()


@pytest.mark.parametrize(('filetype'), [
    (None),
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
    ])
def test_show_opts(filetype):
    # check the function run correctly.
    show_opts(filetype)


@pytest.mark.parametrize(('shell'), [
    ('bash'),
    ('zsh'),
    ])
def test_shell_comp(shell):
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='input file')
    parser.add_argument('-t', '--type')
    parser.add_argument(f'--{shell}', action='store_true')
    args = parser.parse_args(['file', '-t', 'ft', f'--{shell}'])
    assert set_shell_comp(args), f'failed to get shell comp, "{shell}"'


def test_update():
    assert update('main', True)
