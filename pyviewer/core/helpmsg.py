import argparse
from typing import Callable, Optional

from . import GLOBAL_CONF


def add_args_imageviewer(parser: argparse.ArgumentParser):
    """
    add optional argument --image_viewer.

    Parameters
    ----------
    parser: ArgumentParser
        ArgumentParser which optional arguments will be added.

    Returns
    -------
    None
    """
    parser.add_argument('-iv', '--image_viewer',
                        help="set image viewer. " +
                        "Supported args are " +
                        "'None' (do not show any images), " +
                        "'matplotlib' (use matplotlib.pyplot.imshow), " +
                        "'PIL' (use PIL.Image.show), " +
                        "'cv2' (use cv2.imshow), " +
                        "and other string is treated as an external command (e.g. gosr, open).",
                        type=str,
                        )


def add_args_encoding(parser: argparse.ArgumentParser):
    """
    add optional argument --encoding.

    Parameters
    ----------
    parser: ArgumentParser
        ArgumentParser which optional arguments will be added.

    Returns
    -------
    None
    """
    parser.add_argument('--encoding', help='specify the encoding format.',
                        dest='encoding', type=str,
                        )


def add_args_output(parser: argparse.ArgumentParser):
    """
    add optional argument --output.

    Parameters
    ----------
    parser: ArgumentParser
        ArgumentParser which optional arguments will be added.

    Returns
    -------
    None
    """
    parser.add_argument('-o', '--output',
                        help='specify the output file if supported.',
                        type=str)


def add_args_verbose(parser: argparse.ArgumentParser):
    """
    add optional argument --verbose.

    Parameters
    ----------
    parser: ArgumentParser
        ArgumentParser which optional arguments will be added.

    Returns
    -------
    None
    """
    parser.add_argument('-v', '--verbose', help='show details',
                        dest='verbose',
                        action='store_true',
                        )


def add_args_key(parser: argparse.ArgumentParser):
    """
    add optional argument --key.

    Parameters
    ----------
    parser: ArgumentParser
        ArgumentParser which optional arguments will be added.

    Returns
    -------
    None
    """
    parser.add_argument('-k', '--key',
                        help='specify the key name to show. ' +
                        'If no key is specified, return the list of keys.',
                        dest='key',
                        nargs='*',
                        )


def add_args_interactive(parser: argparse.ArgumentParser):
    """
    add optional argument --interactive.

    Parameters
    ----------
    parser: ArgumentParser
        ArgumentParser which optional arguments will be added.

    Returns
    -------
    None
    """
    parser.add_argument('-i', '--interactive',
                        help='open a file with interactive mode.',
                        dest='interactive',
                        action='store_true',
                        )


def add_args_cui(parser: argparse.ArgumentParser):
    """
    add optional argument --interactive_cui.

    Parameters
    ----------
    parser: ArgumentParser
        ArgumentParser which optional arguments will be added.

    Returns
    -------
    None
    """
    parser.add_argument('-c', '--interactive_cui',
                        help='open a file with interactive CUI mode.',
                        dest='cui',
                        action='store_true',
                        )


def add_args_specification(parser: argparse.ArgumentParser,
                           verbose: bool, key: bool,
                           interactive: bool, cui: bool):
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

    Returns
    -------
    None
    """
    group = parser.add_mutually_exclusive_group()
    if verbose:
        add_args_verbose(group)
    if key:
        add_args_key(group)
    if interactive:
        add_args_interactive(group)
    if cui:
        add_args_cui(group)


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
                  add_args: Optional[Callable[[argparse.ArgumentParser], None]] = None
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
    add_args: Callable or None
        A function to add optional arguments.
        This function takes one variable which type is ArgumentParser.

    Returns
    -------
    str
        the help message.
    """
    if filetype not in GLOBAL_CONF.types:
        return ''
    ex = GLOBAL_CONF.types[filetype].split()
    if len(ex) != 0:
        exs = ', '.join(ex)
        description += f' The corresponding extensions are [{exs}].'
    parser = argparse.ArgumentParser(description=description,
                                     prog=f'pyviewer FILE -t {filetype}',
                                     add_help=False)
    if add_args is not None:
        add_args(parser)

    return parser.format_help()
