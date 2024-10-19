#! /usr/bin/env python3

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
# NumPy Style -> https://numpydoc.readthedocs.io/en/latest/format.html

varis = {
        '.core': ['GLOBAL_CONF'
                  ],
        }
types = {
        '.core.types': ['Args', 'ReturnMessage',
                        ],
        }

funcs = {
        '.core': ['args_chk', 'get_config', 'get_col',
                  'cprint', 'print_key', 'print_error', 'print_warning',
                  'interactive_view', 'run_system_cmd',
                  ],
        '.core.image_viewer': ['is_image',
                               'show_image_file', 'show_image_ndarray',
                               ],
        '.core.helpmsg': ['help_template', 'add_args_imageviewer',
                          'add_args_encoding', 'add_args_output',
                          'add_args_verbose', 'add_args_key',
                          'add_args_interactive', 'add_args_cui',
                          'add_args_specification'],
        '.core.cui': ['interactive_cui'],
        }


def show_items(item_dict: dict[str, list[str]]):
    for mod, items in item_dict.items():
        for item in items:
            ret = import_module(mod, 'aftviewer')
            ret2 = eval(f'ret.{item}')
            # print('## {}'.format(ret2.__name__))
            print(f'## {item}')
            print(ret2.__doc__)
            print()


print('')
print('# Introduction')
print('This page explain the API references to extend the AFTViewer.')
print('Also see [[Extension page|Extension]].')
print('')
print('# Variables')
show_items(varis)

print('# Types')
show_items(types)

print('# Functions')
show_items(funcs)
