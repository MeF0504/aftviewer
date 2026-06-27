# test functions in aftviewer/cli/__init__.py
import argparse
from unittest.mock import patch

import pytest

from aftviewer.cli import (main, get_args, show_opts, set_shell_comp, update,
                           update_packages, get_parser_arg,
                           install_viewer, add_args_install)
from aftviewer.cli.get_types import main as get_types
from . import FTs

fts = [(None)]
for ft in FTs:
    fts.append((ft))


def test_main():
    # syntax check?
    with patch('sys.argv', ["aftviewer", "file"]):
        main()


def test_get_types():
    # syntax check?
    get_types()


def test_get_args():
    # check the function run correctly.
    get_args(['file'])


@pytest.mark.parametrize(('filetype'), fts)
def test_show_opts(filetype):
    # check the function run correctly.
    show_opts(filetype)


@pytest.mark.parametrize(('shell'), [
    ('bash'),
    ('zsh'),
    ])
def test_shell_comp(shell):
    parser = argparse.ArgumentParser(**get_parser_arg())
    parser.add_argument('file', help='input file')
    parser.add_argument('-t', '--type')
    parser.add_argument(f'--{shell}', action='store_true')
    args = parser.parse_args(['file', '-t', 'ft', f'--{shell}'])
    assert set_shell_comp(args), f'failed to get shell comp, "{shell}"'


def test_update():
    assert update('main', True)
    assert update_packages('tar', True)


def test_installer():
    parser = argparse.ArgumentParser(**get_parser_arg())
    add_args_install(parser)
    args = parser.parse_args(['https://github.com/MeF0504/aftviewer-viewer-util.git'])
    install_viewer(args)
