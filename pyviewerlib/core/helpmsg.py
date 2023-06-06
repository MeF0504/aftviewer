import argparse
from importlib import import_module

from . import type_config, debug_print

iv_help = dict(help="set image viewer. " +
                    "Supported args are " +
                    "'matplotlib' (use matplotlib.pyplot.imshow), " +
                    "'PIL' (use PIL.Image.show), " +
                    "'OpenCV' (use cv2.imshow), " +
                    "and other string is treated as an external command (e.g. gosr, open).",
               type=str,
               )
encoding_help = dict(help='specify the encoding format.',
                     dest='encoding', type=str,
                     )
pass_help = dict(help='ask for the password for the file if needed.',
                 action='store_true',
                 )
verbose_help = dict(help='show details',
                    dest='verbose',
                    action='store_true',
                    )
key_help = dict(help='specify the key name to show. ' +
                     'If no key is specified, return the list of keys.',
                dest='key',
                nargs='*',
                )
interactive_help = dict(help='open a file with interactive mode.',
                        dest='interactive',
                        action='store_true',
                        )
cui_help = dict(help='open a file with interactive CUI mode.',
                dest='cui',
                action='store_true',
                )


def help_template(filetype, description,
                  sup_iv=False, sup_encoding=False, sup_password=False,
                  sup_v=False, sup_k=False, sup_i=False, sup_c=False,
                  add_args=None,
                  ):
    if filetype not in type_config:
        return ''
    ex = type_config[filetype].split()
    if ex:
        description += ' The corresponding extensions are [{}].'.format(', '.join(ex))
    parser = argparse.ArgumentParser(description=description,
                                     prog=f'pyviewer FILE -t {filetype}',
                                     add_help=False)
    if sup_iv:
        parser.add_argument('-iv', '--image_viewer', **iv_help)
    if sup_encoding:
        parser.add_argument('--encoding', **encoding_help)
    if sup_password:
        parser.add_argument('--ask_password', '-p', **pass_help)
    if int(sup_v) + int(sup_k) + int(sup_i) + int(sup_c) > 1:
        group = parser.add_mutually_exclusive_group()
    else:
        group = parser
    if sup_v:
        group.add_argument('-v', '--verbose', **verbose_help)
    if sup_k:
        group.add_argument('-k', '--key', **key_help)
    if sup_i:
        group.add_argument('-i', '--interactive', **interactive_help)
    if sup_c:
        group.add_argument('-c', '--interactive_cui', **cui_help)
    if add_args is not None:
        try:
            # additional arguments
            lib = import_module("pyviewerlib.{}".format(add_args))
        except ImportError as e:
            debug_print(e)
        else:
            lib.main(parser)

    return parser.format_help()
