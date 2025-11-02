from __future__ import annotations

import argparse
from typing import Callable, Any
from logging import getLogger

from . import GLOBAL_CONF

logger = getLogger(GLOBAL_CONF.logname)


def add_args_imageviewer(parser: argparse.ArgumentParser, **kwargs) -> None:
    """
    add optional argument --image_viewer.

    Parameters
    ----------
    parser: ArgumentParser
        ArgumentParser which optional arguments will be added.
    kwargs:
        keyword arguments passed to parser.add_argument function.

    Returns
    -------
    None
    """
    args = dict(help="set image viewer. Supported args are "
                "'None' (do not show any images), "
                "'matplotlib' (use matplotlib.pyplot.imshow), "
                "'PIL' (use PIL.Image.show), "
                "'cv2' (use cv2.imshow), "
                "'bokeh' (use bokeh.plotting.figure.image_rgba), "
                "and other string is treated as an external command "
                "(e.g. display, eog, open).",
                type=str
                )
    args.update(kwargs)
    parser.add_argument('-iv', '--image_viewer', **args)


def add_args_encoding(parser: argparse.ArgumentParser, **kwargs) -> None:
    """
    add optional argument --encoding.

    Parameters
    ----------
    parser: ArgumentParser
        ArgumentParser which optional arguments will be added.
    kwargs:
        keyword arguments passed to parser.add_argument function.

    Returns
    -------
    None
    """
    args = dict(help='specify the encoding format.',
                dest='encoding', type=str)
    args.update(kwargs)
    parser.add_argument('--encoding', **args)


def add_args_output(parser: argparse.ArgumentParser, **kwargs) -> None:
    """
    add optional argument --output.

    Parameters
    ----------
    parser: ArgumentParser
        ArgumentParser which optional arguments will be added.
    kwargs:
        keyword arguments passed to parser.add_argument function.

    Returns
    -------
    None
    """
    args = dict(help='specify the output file if supported.', type=str)
    args.update(kwargs)
    parser.add_argument('-o', '--output', **args)


def add_args_verbose(parser: argparse.ArgumentParser |
                     argparse._MutuallyExclusiveGroup,
                     **kwargs) -> None:
    """
    add optional argument --verbose.

    Parameters
    ----------
    parser: ArgumentParser
        ArgumentParser which optional arguments will be added.
    kwargs:
        keyword arguments passed to parser.add_argument function.

    Returns
    -------
    None
    """
    args = dict(help='show details', dest='verbose', action='store_true')
    args.update(kwargs)
    parser.add_argument('-v', '--verbose', **args)


def add_args_key(parser: argparse.ArgumentParser |
                 argparse._MutuallyExclusiveGroup,
                 **kwargs) -> None:
    """
    add optional argument --key.

    Parameters
    ----------
    parser: ArgumentParser
        ArgumentParser which optional arguments will be added.
    kwargs:
        keyword arguments passed to parser.add_argument function.

    Returns
    -------
    None
    """
    args = dict(help='specify the key name to show. '
                'If no key is specified, return the list of keys.',
                dest='key', nargs='*')
    args.update(kwargs)
    parser.add_argument('-k', '--key', **args)


def add_args_interactive(parser: argparse.ArgumentParser |
                         argparse._MutuallyExclusiveGroup,
                         **kwargs) -> None:
    """
    add optional argument --interactive.

    Parameters
    ----------
    parser: ArgumentParser
        ArgumentParser which optional arguments will be added.
    kwargs:
        keyword arguments passed to parser.add_argument function.

    Returns
    -------
    None
    """
    args = dict(help='open a file with interactive mode.',
                dest='interactive', action='store_true')
    args.update(kwargs)
    parser.add_argument('-i', '--interactive', **args)


def add_args_cui(parser: argparse.ArgumentParser |
                 argparse._MutuallyExclusiveGroup,
                 **kwargs) -> None:
    """
    add optional argument --interactive_cui.

    Parameters
    ----------
    parser: ArgumentParser
        ArgumentParser which optional arguments will be added.
    kwargs:
        keyword arguments passed to parser.add_argument function.

    Returns
    -------
    None
    """
    args = dict(help='open a file with interactive CUI mode.',
                dest='cui', action='store_true')
    args.update(kwargs)
    parser.add_argument('-c', '--interactive_cui', **args)


def add_args_specification(parser: argparse.ArgumentParser,
                           verbose: bool, key: bool,
                           interactive: bool, cui: bool,
                           kwargs_v: dict[str, Any] = {},
                           kwargs_k: dict[str, Any] = {},
                           kwargs_i: dict[str, Any] = {},
                           kwargs_c: dict[str, Any] = {},
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
    kwargs_v: dict
        keyword arguments passed to add_argument for verbose option.
    kwargs_k: dict
        keyword arguments passed to add_argument for key option.
    kwargs_i: dict
        keyword arguments passed to add_argument for interactive option.
    kwargs_c: dict
        keyword arguments passed to add_argument for interactive_cui option.

    Returns
    -------
    None
    """
    group = parser.add_mutually_exclusive_group()
    if verbose:
        add_args_verbose(group, **kwargs_v)
    if key:
        add_args_key(group, **kwargs_k)
    if interactive:
        add_args_interactive(group, **kwargs_i)
    if cui:
        add_args_cui(group, **kwargs_c)


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
