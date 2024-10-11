from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Union


@dataclass(frozen=True)
class CONF:
    """
    Global configuration variable.
    This variable contains following attributes.

    Attributes:
    debug: bool
        debug mode is enabled or not.
    conf_dir: pathlib.Path
        configuration directory.
        default: "$XDG_CONFIG_HOME/aftviewer" or "~/.config/aftviewer"
    types: dict
        supported file types and its extensions.
        This dictionary is overridden by "additional_types" in opts.
    logname: str
        log name used in logger.
    """
    debug: bool
    conf_dir: Path
    types: dict
    logname: str


@dataclass
class ReturnMessage:
    """
    class for returned message.

    Attributes:
    message: str
        returned message.
    error: bool
        True if this message is an error.
    """
    message: str
    error: bool


@dataclass
class Args:
    """
    wrapper of argument parser. The following attributes are examples
    that are used in some of default file types.
    The actual arguments depends on the file type.
    Type 'aftviewer help -t <file type>' to see the selectable arguments.

    Attributes:
    file: str
        opened file.
    type: str
        file type.
    image_viewer: str
        Image viewer which specify the method to open an image file.
        If image viewer is specified at both command line and setting file
        (setting.json), command value has priority.
    encoding: str
        The name of the encoding used to open the file.
    verbose: bool
        Show the details if --verbose|-v is set.
    key: list of keys
        Specify the keys/pathes to show the information.
    interactive: bool
        Open the file with interactive mode if --interactive|-i is set.
    cui: bool
        Open the file with interactive-cui mode if --interactive_cui|-c is set.
    output: str
        Specify the output file.

    Note that verbose, key, interactive, and interactive_cui options
    are exclusive.
    """
    file: str
    type: str
    image_viewer: str
    encoding: str
    verbose: bool
    key: list[str]
    interactive: bool
    cui: bool
    output: str


SF = Callable[..., ReturnMessage]

COLType = Union[str, int, None]
