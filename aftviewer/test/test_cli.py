# test functions in aftviewer/cli/__init__.py
import argparse
import warnings

import pytest

from aftviewer.cli import (main, get_types,
                           get_args, show_opts, set_shell_comp, update)


def test_main():
    # syntax check?
    main()


def test_get_types():
    pass


def test_get_args():
    pass


def test_show_opts():
    pass


def test_shell_comp():
    pass


def test_update():
    assert update('main', True)
