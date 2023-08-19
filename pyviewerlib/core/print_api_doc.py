#! /usr/bin/env python3

import sys
from importlib import import_module
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
# NumPy Style -> https://numpydoc.readthedocs.io/en/latest/format.html

funcs = {
        '.core': ['debug_print', 'args_chk', 'get_config', 'cprint',
                  'print_key', 'get_col', 'set_numpy_format', 'show_opts',
                  'interactive_view', 'run_system_cmd',
                  ],
        '.core.image_viewer': ['get_image_viewer', 'is_image',
                               'show_image_file', 'show_image_ndarray',
                               ],
        '.core.helpmsg': ['help_template'],
        '.core.cui': ['interactive_cui'],
        }

for mod, funcs in funcs.items():
    for func in funcs:
        ret = import_module(mod, 'pyviewerlib')
        ret2 = eval(f'ret.{func}')
        print('## {}'.format(ret2.__name__))
        print(ret2.__doc__)
        print()
