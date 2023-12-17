import argparse
from importlib import import_module
from typing import Optional

from . import type_config, debug_print


def help_template(filetype: str, description: str,
                  sup_iv: bool = False, sup_encoding: bool = False,
                  sup_password: bool = False,
                  sup_o: bool = False,
                  sup_v: bool = False, sup_k: bool = False,
                  sup_i: bool = False, sup_c: bool = False,
                  add_args: Optional[str] = None,
                  ) -> str:
    """
    offer a template for help messages.

    Parameters
    ----------
    filetype: str
        The file type of help message. This file type is required to be
        supported by the `pyviewer` command.
    description: str
        the description of the file type.
    sup_iv: bool
        set True if this file type supports --image_viewer option.
    sup_encoding: bool
        set True if this file type supports --encoding option.
    sup_o: bool
        set True if this file type supports --output option.
    sup_password: bool
        set True if this file type supports --ask_password option.
    sup_v: bool
        set True if this file type supports --verbose option.
    sup_k: bool
        set True if this file type supports --key option.
    sup_i: bool
        set True if this file type supports --interactive option.
    sup_c: bool
        set True if this file type supports --interactive_cui option.
    add_args: Optional[str]
        The name of the file adding optional arguments.
        Please see the wiki for more details.

    Returns
    -------
    str
        the help message.
    """
    if filetype not in type_config:
        return ''
    ex = type_config[filetype].split()
    if ex:
        description += ' The corresponding extensions are [{}].'.format(', '.join(ex))
    parser = argparse.ArgumentParser(description=description,
                                     prog=f'pyviewer FILE -t {filetype}',
                                     add_help=False)
    set_def_args(parser, sup_iv=sup_iv, sup_encoding=sup_encoding,
                 sup_password=sup_password,
                 sup_v=sup_v, sup_k=sup_k, sup_i=sup_i, sup_c=sup_c)
    if add_args is not None:
        try:
            # additional arguments
            lib = import_module("pyviewerlib.{}".format(add_args))
        except ImportError as e:
            debug_print(e.msg)
        else:
            lib.main(parser)

    return parser.format_help()


def set_def_args(parser: argparse.ArgumentParser,
                 sup_iv: bool = False, sup_encoding: bool = False,
                 sup_password: bool = False,
                 sup_o: bool = False,
                 sup_v: bool = False, sup_k: bool = False,
                 sup_i: bool = False, sup_c: bool = False,
                 add_args: Optional[str] = None,
                 ) -> None:
    if sup_iv:
        parser.add_argument('-iv', '--image_viewer',
                            help="set image viewer. " +
                            "Supported args are " +
                            "'matplotlib' (use matplotlib.pyplot.imshow), " +
                            "'PIL' (use PIL.Image.show), " +
                            "'cv2' (use cv2.imshow), " +
                            "and other string is treated as an external command (e.g. gosr, open).",
                            type=str,
                            )
    if sup_encoding:
        parser.add_argument('--encoding', help='specify the encoding format.',
                            dest='encoding', type=str,
                            )
    if sup_password:
        parser.add_argument('--ask_password', '-p',
                            help='ask for the password for the file if needed.',
                            action='store_true',
                            )
    if sup_o:
        parser.add_argument('-o', '--output',
                            help='specify the output file if supported.',
                            type=str)
    group = parser.add_mutually_exclusive_group()
    if sup_v:
        group.add_argument('-v', '--verbose', help='show details',
                           dest='verbose',
                           action='store_true',
                           )
    if sup_k:
        group.add_argument('-k', '--key',
                           help='specify the key name to show. ' +
                           'If no key is specified, return the list of keys.',
                           dest='key',
                           nargs='*',
                           )
    if sup_i:
        group.add_argument('-i', '--interactive',
                           help='open a file with interactive mode.',
                           dest='interactive',
                           action='store_true',
                           )
    if sup_c:
        group.add_argument('-c', '--interactive_cui',
                           help='open a file with interactive CUI mode.',
                           dest='cui',
                           action='store_true',
                           )
