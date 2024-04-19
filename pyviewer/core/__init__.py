import os
import sys
import json
import platform
import subprocess
import tarfile
from importlib import import_module
from pathlib import Path, PurePath
from typing import Union, Tuple, Any, Optional
from types import ModuleType
from logging import getLogger, StreamHandler, FileHandler, NullHandler, \
    Formatter, DEBUG as logDEBUG, INFO as logINFO

from pymeflib.color import FG, BG, FG256, BG256, END
from pymeflib.tree2 import TreeViewer, GC, PPath
from .types import CONF, Args, SF


__debug = False
if 'XDG_CONFIG_HOME' in os.environ:
    __conf_dir = Path(os.environ['XDG_CONFIG_HOME'])/'pyviewer'
else:
    __conf_dir = Path(os.path.expanduser('~/.config'))/'pyviewer'
if not __conf_dir.exists():
    os.makedirs(__conf_dir, mode=0o755)

# load config file.
with (Path(__file__).parent/'default.json').open('r') as f:
    __json_opts = json.load(f)
if (__conf_dir/'setting.json').is_file():
    with open(__conf_dir/'setting.json') as f:
        load_opts = json.load(f)
        if 'debug' in load_opts:
            __debug = bool(load_opts['debug'])
        if 'force_default' in load_opts and load_opts['force_default']:
            load_opts = {}
        if 'additional_types' in load_opts:
            __add_types = load_opts['additional_types']
            __json_opts['additional_types'] = __add_types
        else:
            __add_types = {}
        for key in list(__json_opts.keys()) + list(__add_types.keys()):
            if key == 'additional_types':
                continue
            if key in load_opts:
                if key in __json_opts:
                    # update values in default.json
                    for k2, v2 in load_opts[key].items():
                        if k2 in __json_opts[key]:
                            __json_opts[key][k2] = v2
                else:
                    # create settings for new file type
                    __json_opts[key] = load_opts[key]
    del load_opts
else:
    __add_types = {}

# set supported file types
__type_config = {
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
__type_config.update(__add_types)

# logger setting
__logname = 'PyViewerLog'
__log_file = __conf_dir/'debug.log'
__logger = getLogger(__logname)
# (NOTSET <) DEBUG < INFO < WARNING < ERROR < CRITICAL
# see https://docs.python.org/3/library/logging.html#logging-levels
# in debug mode, more than INFO is shown in stdout and
# all logs (more than DEBUG to be exact) are saved in conf_dir/debug.log.
__logger.setLevel(logDEBUG)
if __debug:
    __st_hdlr = StreamHandler()
    __st_hdlr.setLevel(logINFO)
    __st_format = '>> %(levelname)-9s %(message)s'
    __st_hdlr.setFormatter(Formatter(__st_format))
    __fy_hdlr = FileHandler(filename=__log_file, mode='w', encoding='utf-8')
    __fy_hdlr.setLevel(logDEBUG)
    __fy_format = '%(levelname)-9s %(asctime)s [%(filename)s:%(lineno)d]:' \
        + ' %(message)s'
    __fy_hdlr.setFormatter(Formatter(__fy_format))
    __logger.addHandler(__st_hdlr)
    __logger.addHandler(__fy_hdlr)
else:
    __null_hdlr = NullHandler()
    __logger.addHandler(__null_hdlr)

# global variables
GLOBAL_CONF = CONF(__debug,
                   __conf_dir,
                   __json_opts,
                   __type_config,
                   __logname)


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
    elif attr == 'bash':
        return args.bash
    elif attr == 'zsh':
        return args.zsh
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
    assert key1 in ["config", "colors"] + list(__type_config.keys()), \
        f'incorrect key name: {key1}'
    if key1 not in __json_opts:
        # type name is not set in setting.json.
        return None
    val1 = __json_opts[key1]
    if key2 not in val1:
        return None
    else:
        return val1[key2]


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
        __logger.warning(f'incorrect type for fg: {fg}')
        fg_str = ''
    if type(bg) is str and bg in BG:
        bg_str = BG[bg]
    elif type(bg) is int and 0 <= bg <= 255:
        bg_str = BG256(bg)
    elif bg is None:
        bg_str = ''
    else:
        __logger.warning(f'incorrect type for bg: {bg}')
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
        __logger.warning(f'incorrect color set name: {name}')
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
    purepath: PurePath, PurePosixPath, or PureWindowsPath
        Specify the class to treat the path-like object.
        This is because in some case, the separator shoud be '/' not '\\'
        even if the OS is Windows.

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
    tv = TreeViewer('.', get_contents, purepath=purepath, logger=__logger)
    while True:
        dirs, files = tv.get_contents(cpath)
        cprint('current path:', ' {}/{}'.format(fname, cpath), fg=fg1, bg=bg1)
        cprint('contents in this dict:', ' ', fg=fg2, bg=bg2, end='')
        for d in dirs:
            print('{}/, '.format(d), end='')
        for f in files:
            print('{}, '.format(f), end='')
        print('\n')
        key_name = input(inter_str)
        if key_name == 'q':
            __logger.info('quit')
            break
        elif key_name == '':
            __logger.info('continue')
            continue
        elif key_name == '..':
            __logger.info('go up')
            if str(cpath) != '.':
                cpath = cpath.parent
        else:
            __logger.info(f'specify key:{key_name}')
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


def get_filetype(fpath: Path) -> Optional[str]:
    if not fpath.is_file():
        __logger.debug('file does not exists')
        return None
    ext = fpath.suffix[1:].lower()
    if tarfile.is_tarfile(fpath):
        __logger.debug('set file type: tar')
        return 'tar'
    else:
        for typ, exts in __type_config.items():
            if ext in exts.split():
                __logger.debug(f'set file type: {typ}')
                return typ
    __logger.debug('file type is not set.')
    return None


def load_lib(args: Args) -> Optional[ModuleType]:
    if args.type is None:
        __logger.debug('file type is None')
        return None
    elif args.type == 'text':
        __logger.debug('file type is text.')
        return None

    # lib_path  -> python import style
    # lib_path2 -> file path
    if args.type in __add_types:
        if str(__conf_dir) not in sys.path:
            __logger.debug(f'add {str(__conf_dir)} to sys.path.')
            sys.path.insert(0, str(__conf_dir))
        lib_path = f'additional_types.{args.type}'
        lib_path2 = __conf_dir/f'additional_types/{args.type}.py'
    else:
        lib_path = f'pyviewer.viewers.{args.type}'
        lib_path2 = Path(__file__).parent.parent
        lib_path2 /= f'viewers/{args.type}.py'
    if not lib_path2.is_file():
        __logger.error(f'Library file {lib_path2} is not found.')
        return None
    try:
        lib = import_module(lib_path)
    except ImportError as e:
        __logger.error(f'Failed to load library (lib: {lib_path2}, error: {e})')
        return None
    return lib
