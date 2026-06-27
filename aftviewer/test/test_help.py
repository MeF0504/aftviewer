# test help messages.
import argparse
import warnings
from types import FunctionType

import pytest

from aftviewer.core import __load_lib
from . import chk_deps, FTs
from aftviewer.cli import get_parser_arg

fts = []
for ft in FTs:
    fts.append(ft)


@pytest.mark.parametrize(('filetype'), fts)
def test_help_message(filetype):
    if not chk_deps(filetype):
        warnings.warn(f'skip cheking {filetype}')
        return
    parser = argparse.ArgumentParser(**get_parser_arg())
    args = parser.parse_args([])
    args.file = 'help'
    args.type = filetype
    lib, err = __load_lib(args)
    assert lib is not None, f'failed to load library ({err}).'
    if hasattr(lib, 'show_help') and type(lib.show_help) is FunctionType:
        lib.show_help()
    else:
        warnings.warn(f'{filetype} does not support showing help.')
