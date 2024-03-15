#! /usr/bin/env python3

import sys
from importlib import import_module
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
# NumPy Style -> https://numpydoc.readthedocs.io/en/latest/format.html

funcs = {
        '.core': ['GLOBAL_CONF', 'Args', 'ReturnMessage',
                  'args_chk', 'get_config', 'cprint', 'print_key',
                  'get_col', 'set_numpy_format', 'show_opts',
                  'interactive_view', 'run_system_cmd',
                  ],
        '.core.image_viewer': ['get_image_viewer', 'is_image',
                               'show_image_file', 'show_image_ndarray',
                               ],
        '.core.helpmsg': ['help_template', 'add_args_imageviewer',
                          'add_args_encoding', 'add_args_output',
                          'add_args_verbose', 'add_args_key',
                          'add_args_interactive', 'add_args_cui',
                          'add_args_specification'],
        '.core.cui': ['interactive_cui'],
        }

for mod, funcs in funcs.items():
    for func in funcs:
        ret = import_module(mod, 'pyviewerlib')
        ret2 = eval(f'ret.{func}')
        # print('## {}'.format(ret2.__name__))
        print('## {}'.format(func))
        print(ret2.__doc__)
        print()
