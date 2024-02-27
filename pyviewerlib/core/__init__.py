import os
import json
import platform
import subprocess
from pathlib import Path, PurePath
from typing import Callable, Union, List, Tuple, Any
from dataclasses import dataclass

from pymeflib.color import FG, BG, FG256, BG256, END
from pymeflib.tree2 import TreeViewer, GC, PPath


# global variables
debug = False
if 'XDG_CONFIG_HOME' in os.environ:
    conf_dir = Path(os.environ['XDG_CONFIG_HOME'])/'pyviewer'
else:
    conf_dir = Path(os.path.expanduser('~/.config'))/'pyviewer'
if not conf_dir.exists():
    os.makedirs(conf_dir, mode=0o755)

# load config file.
with (Path(__file__).parent/'default.json').open('r') as f:
    json_opts = json.load(f)
if (conf_dir/'setting.json').is_file():
    with open(conf_dir/'setting.json') as f:
        load_opts = json.load(f)
        if 'debug' in load_opts:
            debug = bool(load_opts['debug'])
        if 'force_default' in load_opts and load_opts['force_default']:
            load_opts = {}
        if 'additional_types' in load_opts:
            add_types = load_opts['additional_types']
            json_opts['additional_types'] = add_types
        else:
            add_types = {}
        for key in list(json_opts.keys()) + list(add_types.keys()):
            if key == 'additional_types':
                continue
            if key in load_opts:
                if key in json_opts:
                    # update values in default.json
                    for k2, v2 in load_opts[key].items():
                        if k2 in json_opts[key]:
                            json_opts[key][k2] = v2
                else:
                    # create settings for new file type
                    json_opts[key] = load_opts[key]
    del load_opts
else:
    add_types = {}

# set supported file types
type_config = {
    "hdf5": "hdf5",
    "pickle": "pkl pickle",
    "numpy": "npy npz",
    "np_pickle": "",
    "tar": "",  # tar is identified by tarfile module.
    "zip": "zip",
    "sqlite3": "db db3 sqp sqp3 sqlite sqlite3",
    "raw_image": "raw nef nrw cr3 cr2 crw tif arw",  # nikon, canon, sony
    "jupyter": "ipynb",
    "xpm": "xpm",
    "text": "py txt",
}
type_config.update(add_types)
del add_types


@dataclass
class ReturnMessage:
    """
    class for returned message.

    self.message: str
        returned message.
    self.error: bool
        True if this message is an error.
    """
    message: str
    error: bool


@dataclass
class Args:
    """
    wrapper of argument parser.
    """
    file: str
    type: str
    image_viewer: str
    encoding: str
    ask_password: bool
    verbose: bool
    key: List[str]
    interactive: bool
    cui: bool
    debug: bool
    output: str


SF = Callable[..., ReturnMessage]


def debug_print(msg: str) -> None:
    """
    print a message if PyViewer works in debug mode.

    Parameters
    ----------
    msg: str
        a message printed if in debug mode.

    Returns
    -------
    None
    """
    if debug:
        print(msg)


def args_chk(args: Args, attr: str) -> bool:
    """
    return True if a given attribute is set in args.
    NOTE: This function supports only default attributes.

    Parameters
    ----------
    args: Args
        The arguments given by the command line.
    attr: str
        The attribute to check that is set from the command line.

    Returns
    -------
    bool
        Return True if the attribute is set correctly.
    """
    if not hasattr(args, attr):
        return False
    if attr == 'type':
        return args.type is not None
    elif attr == 'verbose':
        return args.verbose
    elif attr == 'key':
        return args.key is not None
    elif attr == 'interactive':
        return args.interactive
    elif attr == 'image_viewer':
        return args.image_viewer is not None
    elif attr == 'encoding':
        return args.encoding is not None
    elif attr == 'cui':
        return args.cui
    elif attr == 'output':
        return args.output is not None
    else:
        return False


def get_config(key1: str, key2: str) -> Any:
    """
    get the current configuration value.

    Parameters
    ----------
    key1: str
        Main key name. Selected one from "config", "colors", and type names.
    key2: str
        configuration key name.

    Returns
    -------
    Any
        Return specified configuration value. If it is not set, return None.
    """
    assert key1 in ["config", "colors"] + list(type_config.keys()), \
        f'incorrect key name: {key1}'
    if key1 not in json_opts:
        # type name is not set in setting.json.
        return None
    val1 = json_opts[key1]
    if key2 not in val1:
        return None
    else:
        return val1[key2]


def show_opts() -> None:
    """
    show the current configuration options.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    for key, val in json_opts.items():
        if type(val) is dict:
            print_key(key)
            for k2, v2 in val.items():
                print(f'  {k2}: {v2}')
        else:
            print_key(key)
            print(val)


def cprint(str1: str, str2: str = '',
           fg: Union[str, int, None] = None,
           bg: Union[str, int, None] = None,
           **kwargs) -> None:
    """
    print message in color.

    Parameters
    ----------
    str1: str
        The message to be printed in color.
    str2: str
        The message to be printed after str1 without color.
    fg: Union[str, int, None]
        The key of the foreground color. Possible values are
            'k': black, 'r': red, 'g': green, 'y': yellow,
            'b': blue, 'c': cyan, 'm': magenta, 'w': white,
            0-255: The color id corresponding to the 256 terminal colors.
    bg: Union[str, int, None]
        The key of the background color. Possible values are the same as fg.
    **kwargs:
        Keyword arguments passed to the print function.

    Returns
    -------
    None
    """
    if type(fg) is str and fg in FG:
        fg_str = FG[fg]
    elif type(fg) is int and 0 <= fg <= 255:
        fg_str = FG256(fg)
    elif fg is None:
        fg_str = ''
    else:
        debug_print(f'incorrect type for fg: {fg}')
        fg_str = ''
    if type(bg) is str and bg in BG:
        bg_str = BG[bg]
    elif type(bg) is int and 0 <= bg <= 255:
        bg_str = BG256(bg)
    elif bg is None:
        bg_str = ''
    else:
        debug_print(f'incorrect type for bg: {bg}')
        bg_str = ''
    if len(fg_str+bg_str) != 0:
        end_str = END
    else:
        end_str = ''
    print_str = f'{fg_str}{bg_str}{str1}{end_str}{str2}'
    print(print_str, **kwargs)


def get_col(name: str) -> Tuple[Union[str, int, None],
                                Union[str, int, None]]:
    """
    get the color id of a given name.

    Parameters
    ----------
    name: str
        A name of the option. This name should be included in
        "color_config" in configuration options.

    Returns
    -------
    Union[str, int, None]
        foreground color id. If the name is incorrect, return None.
    Union[str, int, None]
        foreground color id. If the name is incorrect, return None.
    """
    col_conf = get_config('colors', name)
    if name is None:
        debug_print(f'incorrect color set name: {name}')
        return None, None
    else:
        return col_conf


def interactive_view(fname: str, get_contents: GC, show_func: SF,
                     purepath: PPath = PurePath) -> None:
    """
    provide the interactive UI to show the contents.

    Parameters
    ----------
    fname: str
        An opened file name.
    get_contents: Callable[[PurePath], Tuple[List[str], List[str]]]
        A function to get lists of directories and files.
        The argument is the path to an item.
        The first return value is a list of directory names,
        and the second return value is a list of file names.
        In this context, a directory means something that includes
        files and directories, and a file means something that includes data.
    show_func: Callable[[str, **kwargs], ReturnMessage]
        A function to show the contents.
        The first argument is the path to a file.
        Other arguments are treated as keyword arguments.
        Please see the wiki for possible keywords.
        The return value is the ReturnMessage. It is treated as
        an error message if ReturnMessage.error is True. Otherwise, it is
        treated as a standard message.

    Returns
    -------
    None
    """
    cpath = purepath('.')
    inter_str = "'q':quit, '..':go to parent, key_name:select a key >> "
    fg1, bg1 = get_col('interactive_path')
    fg2, bg2 = get_col('interactive_contents')
    fg3, bg3 = get_col('interactive_output')
    fge, bge = get_col('msg_error')
    tv = TreeViewer('.', get_contents)
    while True:
        dirs, files = tv.get_contents(cpath)
        dirs.sort()
        files.sort()
        cprint('current path:', ' {}/{}'.format(fname, cpath), fg=fg1, bg=bg1)
        cprint('contents in this dict:', ' ', fg=fg2, bg=bg2, end='')
        for d in dirs:
            print('{}/, '.format(d), end='')
        for f in files:
            print('{}, '.format(f), end='')
        print('\n')
        key_name = input(inter_str)
        if key_name == 'q':
            debug_print('quit')
            break
        elif key_name == '':
            debug_print('continue')
            continue
        elif key_name == '..':
            debug_print('go up')
            if str(cpath) != '.':
                cpath = cpath.parent
        else:
            debug_print('specify key:{}'.format(key_name))
            if key_name.endswith('/'):
                key_name = key_name[:-1]
            if key_name in files:
                cprint('output::', '\n', fg=fg3, bg=bg3)
                info = show_func(str(cpath/key_name), cui=False)
                if not info.error:
                    print(info.message)
                else:
                    cprint(info.message, fg=fge, bg=bge)
            elif key_name in dirs:
                cpath /= key_name
            else:
                cprint('"{}" is not a correct name'.format(key_name),
                       '', fg=fge, bg=bge)


def print_key(key_name: str) -> None:
    """
    print the key name with emphasis.

    Parameters
    ----------
    key_name: str
        the key name.

    Returns
    -------
    None
    """
    fg, bg = get_col('msg_key_name')
    cprint('<<< {} >>>'.format(key_name), '', fg=fg, bg=bg)


def run_system_cmd(fname: str) -> bool:
    """
    open the file using the system command.

    Parameters
    ----------
    fname: str
        a file name to be opened.

    Returns
    -------
    bool
        Return True if the command succeeded, otherwise False.
    """
    cmd = get_config('config', 'system_cmd')
    if cmd is None:
        if platform.system() == 'Windows':
            cmd = 'start'
        elif platform.uname()[0] == 'Darwin':
            cmd = 'open'
        elif platform.uname()[0] == 'Linux':
            cmd = 'xdg-open'
        else:
            print('Unsupported platform')
            return False
    res = []
    for arg in get_config('config', 'system_cmd_args'):
        if arg == '%s':
            res.append(fname)
        elif arg == '%c':
            res.append(cmd)
        else:
            res.append(arg)

    if platform.system() == 'Windows':
        shell = True
    else:
        shell = False
    stat = subprocess.run(res, shell=shell)
    if stat.returncode != 0:
        return False
    else:
        return True


def set_numpy_format(numpy: Any) -> None:
    """
    set NumPy format following the given configuration option.

    Parameters
    ----------
    numpy: module
        NumPy module. (This file is designed not to call anything other than
        standard modules, so the NumPy module is used as an argument.)

    Returns
    -------
    None
    """
    opts = get_config('numpy', 'print_option')
    numpy.set_printoptions(**opts)
