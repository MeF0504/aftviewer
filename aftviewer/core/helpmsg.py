from __future__ import annotations

import argparse
from typing import Callable
from logging import getLogger

from . import GLOBAL_CONF

logger = getLogger(GLOBAL_CONF.logname)


def add_args_imageviewer(parser: argparse.ArgumentParser,
                         msg: str | None = None) -> None:
    """
    add optional argument --image_viewer.

    Parameters
    ----------
    parser: ArgumentParser
        ArgumentParser which optional arguments will be added.
    msg: str or None
        help message. If None, default message will be used.

    Returns
    -------
    None
    """
    if msg is None:
        msg = "set image viewer. Supported args are " \
            "'None' (do not show any images), " \
            "'matplotlib' (use matplotlib.pyplot.imshow), " \
            "'PIL' (use PIL.Image.show), " \
            "'cv2' (use cv2.imshow), " \
            "and other string is treated as an external command " \
            "(e.g. display, eog, open)."
    parser.add_argument('-iv', '--image_viewer', help=msg, type=str)


def add_args_encoding(parser: argparse.ArgumentParser,
                      msg: str | None = None) -> None:
    """
    add optional argument --encoding.

    Parameters
    ----------
    parser: ArgumentParser
        ArgumentParser which optional arguments will be added.
    msg: str or None
        help message. If None, default message will be used.

    Returns
    -------
    None
    """
    if msg is None:
        msg = 'specify the encoding format.'
    parser.add_argument('--encoding', help=msg, dest='encoding', type=str)


def add_args_output(parser: argparse.ArgumentParser,
                    msg: str | None = None) -> None:
    """
    add optional argument --output.

    Parameters
    ----------
    parser: ArgumentParser
        ArgumentParser which optional arguments will be added.
    msg: str or None
        help message. If None, default message will be used.

    Returns
    -------
    None
    """
    if msg is None:
        msg = 'specify the output file if supported.'
    parser.add_argument('-o', '--output', help=msg, type=str)


def add_args_verbose(parser: argparse.ArgumentParser |
                     argparse._MutuallyExclusiveGroup,
                     msg: str | None = None) -> None:
    """
    add optional argument --verbose.

    Parameters
    ----------
    parser: ArgumentParser
        ArgumentParser which optional arguments will be added.
    msg: str or None
        help message. If None, default message will be used.

    Returns
    -------
    None
    """
    if msg is None:
        msg = 'show details'
    parser.add_argument('-v', '--verbose', help=msg, dest='verbose',
                        action='store_true')


def add_args_key(parser: argparse.ArgumentParser |
                 argparse._MutuallyExclusiveGroup,
                 msg: str | None = None) -> None:
    """
    add optional argument --key.

    Parameters
    ----------
    parser: ArgumentParser
        ArgumentParser which optional arguments will be added.
    msg: str or None
        help message. If None, default message will be used.

    Returns
    -------
    None
    """
    if msg is None:
        msg = 'specify the key name to show. ' \
            'If no key is specified, return the list of keys.'
    parser.add_argument('-k', '--key', help=msg, dest='key', nargs='*')


def add_args_interactive(parser: argparse.ArgumentParser |
                         argparse._MutuallyExclusiveGroup,
                         msg: str | None = None) -> None:
    """
    add optional argument --interactive.

    Parameters
    ----------
    parser: ArgumentParser
        ArgumentParser which optional arguments will be added.
    msg: str or None
        help message. If None, default message will be used.

    Returns
    -------
    None
    """
    if msg is None:
        msg = 'open a file with interactive mode.'
    parser.add_argument('-i', '--interactive', help=msg, dest='interactive',
                        action='store_true')


def add_args_cui(parser: argparse.ArgumentParser |
                 argparse._MutuallyExclusiveGroup,
                 msg: str | None = None) -> None:
    """
    add optional argument --interactive_cui.

    Parameters
    ----------
    parser: ArgumentParser
        ArgumentParser which optional arguments will be added.
    msg: str or None
        help message. If None, default message will be used.

    Returns
    -------
    None
    """
    if msg is None:
        msg = 'open a file with interactive CUI mode.'
    parser.add_argument('-c', '--interactive_cui', help=msg, dest='cui',
                        action='store_true')


def add_args_specification(parser: argparse.ArgumentParser,
                           verbose: bool, key: bool,
                           interactive: bool, cui: bool,
                           msg_v: str | None = None, msg_k: str | None = None,
                           msg_i: str | None = None, msg_c: str | None = None,
                           ):
    """
    add optional arguments that are used to specify items.

    Parameters
    ----------
    parser: ArgumentParser
        ArgumentParser which optional arguments will be added.
    verbose: bool
        add optional argument --verbose
    key: bool
        add optional argument --key
    interactive: bool
        add optional argument --interactive
    cui: bool
        add optional argument --interactive_cui
    msg_v: str | None
        help message for verbose option.
    msg_k: str | None
        help message for key option.
    msg_i: str | None
        help message for interactive option.
    msg_c: str | None
        help message for interactive_cui option.

    Returns
    -------
    None
    """
    group = parser.add_mutually_exclusive_group()
    if verbose:
        add_args_verbose(group, msg_v)
    if key:
        add_args_key(group, msg_k)
    if interactive:
        add_args_interactive(group, msg_i)
    if cui:
        add_args_cui(group, msg_c)


def add_args_shell_cmp(parser: argparse.ArgumentParser) -> None:
    """
    add optional argument for shell completion.

    Parameters
    ----------
    parser: ArgumentParser
        ArgumentParser which optional arguments will be added.

    Returns
    -------
    None
    """
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--bash', action='store_true',
                       help='set bash completion')
    group.add_argument('--zsh', action='store_true',
                       help='set zsh completion')


def add_args_update(parser: argparse.ArgumentParser) -> None:
    """
    add optional argument for update subcommand.

    Parameters
    ----------
    parser: ArgumentParser
        ArgumentParser which optional arguments will be added.

    Returns
    -------
    None
    """
    parser.add_argument('--branch', help='set branch name',
                        default='main')


def help_template(filetype: str, description: str,
                  add_args: None | Callable[[argparse.ArgumentParser],
                                            None] = None
                  ) -> str:
    """
    offer a template for help messages.

    Parameters
    ----------
    filetype: str
        The file type of help message. This file type is required to be
        supported by the `aftviewer` command.
    description: str
        the description of the file type.
    add_args: Callable or None
        A function to add optional arguments.
        This function takes one variable which type is ArgumentParser.

    Returns
    -------
    str
        the help message.
    """
    if filetype not in GLOBAL_CONF.types:
        logger.warning(f'not a valid type: {filetype}')
        return ''
    ex = GLOBAL_CONF.types[filetype].split()
    if len(ex) != 0:
        exs = ', '.join(ex)
        description += f' The corresponding extensions are [{exs}].'
    parser = argparse.ArgumentParser(description=description,
                                     prog=f'aftviewer FILE -t {filetype}',
                                     add_help=False)
    if add_args is not None:
        add_args(parser)

    return parser.format_help()
