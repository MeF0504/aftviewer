import sys
import argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from viewers.core import args_chk
from viewers.core.helpmsg import add_args_imageviewer, add_args_encoding, \
    add_args_output, add_args_verbose, add_args_key, add_args_interactive, \
    add_args_cui


@pytest.mark.parametrize(('attr', 'arg_list', 'expected'), [
    ('type', ['file', '-t', 'piclke'], True),
    ('type', ['file'], False),
    ('verbose', ['file', '-t', 'piclke', '-v'], True),
    ('verbose', ['file', '-t', 'piclke'], False),
    ('key', ['file', '-t', 'piclke', '-k'], True),
    ('key', ['file', '-t', 'piclke', '-k', 'a'], True),
    ('key', ['file', '-t', 'piclke', '-k', 'a', 'b'], True),
    ('key', ['file', '-t', 'piclke'], False),
    ('interactive', ['file', '-t', 'piclke', '-i'], True),
    ('interactive', ['file', '-t', 'piclke'], False),
    ('image_viewer', ['file', '-t', 'piclke', '-iv', 'matplotlib'], True),
    ('image_viewer', ['file', '-t', 'piclke'], False),
    ('encoding', ['file', '-t', 'piclke', '--encoding', 'ASCII'], True),
    ('encoding', ['file', '-t', 'piclke'], False),
    ('cui', ['file', '-t', 'piclke', '-c'], True),
    ('cui', ['file', '-t', 'piclke'], False),
    ('output', ['file', '-t', 'piclke', '-o', 'path/to/file'], True),
    ('output', ['file', '-t', 'piclke'], False),
    ])
def test_args(attr, arg_list, expected):
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
