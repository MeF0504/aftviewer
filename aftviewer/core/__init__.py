from __future__ import annotations

import os
import sys
import shutil
import json
import platform
import subprocess
import tarfile
import mimetypes
import pprint
import inspect
from importlib import import_module, metadata
from pathlib import Path, PurePath
from typing import Any, Literal
from types import ModuleType
from logging import (getLogger, StreamHandler, FileHandler, NullHandler,
                     Formatter, DEBUG as logDEBUG, INFO as logINFO)
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pymeflib.color import FG, BG, FG256, BG256, END
from pymeflib.tree2 import TreeViewer, GC, PPath
from .types import CONF, Args, SF, COLType


__debug = False
__def = False
__add_types = {}
__user_opts = {}
__filetype: str | None = None
if 'XDG_CONFIG_HOME' in os.environ:
    __conf_dir = Path(os.environ['XDG_CONFIG_HOME'])/'aftviewer'
else:
    __conf_dir = Path(os.path.expanduser('~/.config'))/'aftviewer'
if not __conf_dir.exists():
    (__conf_dir/'.lib').mkdir(mode=0o755, parents=True)

# load config file.
with (Path(__file__).parent/'default.json').open('r') as f:
    __def_opts = json.load(f)
if (__conf_dir/'setting.json').is_file():
    with open(__conf_dir/'setting.json') as f:
        __user_opts = json.load(f)
        if 'debug' in __user_opts:
            __debug = bool(__user_opts['debug'])
        if 'force_default' in __user_opts and __user_opts['force_default']:
            __def = True
            __user_opts = {}

# logger setting
__logname = inspect.stack()[-1].filename  # command path
if '_get_aftviewer_types' in __logname:
    __log_file = __conf_dir/'debug2.log'
elif 'aftviewer-libinstaller' in __logname:
    __log_file = __conf_dir/'debug3.log'
elif 'aftviewer' in __logname:
    __log_file = __conf_dir/'debug1.log'
else:
    __log_file = __conf_dir/'debug0.log'
__logger = getLogger(__logname)
# (NOTSET <) DEBUG < INFO < WARNING < ERROR < CRITICAL
# see https://docs.python.org/3/library/logging.html#logging-levels
# in debug mode, more than INFO is shown in stdout and
# all logs (more than DEBUG to be exact) are saved in conf_dir/debug.log.
__logger.setLevel(logDEBUG)


def __set_logger():
    global __logger, __debug, __log_file
    if __debug:
        st_hdlr = StreamHandler()
        st_hdlr.setLevel(logINFO)
        st_format = '>> %(levelname)-9s %(message)s'
        st_hdlr.setFormatter(Formatter(st_format))
        fy_hdlr = FileHandler(filename=__log_file, mode='w', encoding='utf-8')
        fy_hdlr.setLevel(logDEBUG)
        fy_format = '%(levelname)-9s %(asctime)s ' + \
            '[%(filename)s:%(funcName)s(%(lineno)d)]:' + \
            ' %(message)s'
        fy_hdlr.setFormatter(Formatter(fy_format))
        __logger.addHandler(st_hdlr)
        __logger.addHandler(fy_hdlr)
    else:
        null_hdlr = NullHandler()
        __logger.addHandler(null_hdlr)


__set_logger()
__logger.debug(f'src: {__file__}')


def __update_add_types():
    if __def:
        __logger.info('force default.')
        return
    if (__conf_dir/'.lib/add_types.txt').is_file():
        with open(__conf_dir/'.lib/add_types.txt', 'r') as f:
            for line in f:
                line = line.replace('\n', '')
                add_type, exts = line.split('\t')
                __add_types[add_type] = exts
                __logger.debug(f'add {add_type}, "{exts}" in add_types.')
    else:
        __logger.info('add_types is not found.')


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
    "e-mail": "eml",
    "xpm": "xpm",
    "stl": "stl",
    "fits": "fits fit",
}
__update_add_types()
__type_config.update(__add_types)


def __set_user_opts(config: None | dict[str, Any],
                    colors: None | dict[str, tuple[COLType, COLType]]) -> None:
    if __def:
        __logger.info('force default.')
        return
    if config is not None:
        __user_opts['config'] = config
    if colors is not None:
        __user_opts['colors'] = colors


def __get_packs() -> list[str]:
    pack_list = []
    for dst in metadata.distributions():
        pack_list.append(dst.metadata['Name'])
    __logger.debug('installed packages:\n'
                   f'{pprint.pformat(pack_list, compact=True)}')
    return pack_list


# global variables
GLOBAL_CONF = CONF(__debug,
                   __conf_dir,
                   __type_config,
                   __logname,
                   __get_packs(),
                   )


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


def get_config(key: str, filetype: str | None = None) -> Any:
    """
    get the current configuration value.

    Parameters
    ----------
    key: str
        configuration key name.
    filetype: str or None
        set file type name of the script calling this function
        to return proper value.
        if None, use the file type set from command arguments or
        got from the file extension.

    Returns
    -------
    Any
        Return specified configuration value. If it is not set, return None.
    """
    if filetype is None:
        filetype = __filetype
    if filetype is None:
        __logger.warning(f'filetype is not set? (get_config, {key})')
    if 'config' in __user_opts:
        user_opts = __user_opts['config']
    else:
        user_opts = {}
    def_opts = __def_opts['config']

    if filetype in user_opts and key in user_opts[filetype]:
        __logger.debug(f'"{key}" in user ft "{filetype}".')
        return user_opts[filetype][key]
    elif 'defaults' in user_opts and \
         key in def_opts['defaults'] and \
         key in user_opts['defaults']:
        # check that key is in "defaults" of both default file and user file.
        __logger.debug(f'"{key}" in user settings.')
        return user_opts['defaults'][key]
    elif filetype in def_opts and key in def_opts[filetype]:
        __logger.debug(f'"{key}" in default ft "{filetype}".')
        return def_opts[filetype][key]
    elif 'defaults' in def_opts:
        if key in def_opts['defaults']:
            __logger.debug(f'"{key}" in default settings.')
            return def_opts['defaults'][key]
        else:
            __logger.error(f'"{key}" not found in settings.')
            return None
    else:
        __logger.error('something wrong; no "defaults" key in default file.')
    return None


def cprint(str1: str, str2: str = '',
           fg: COLType = None,
           bg: COLType = None,
           **kwargs) -> None:
    """
    print message in color.

    Parameters
    ----------
    str1: str
        The message to be printed in color.
    str2: str
        The message to be printed after str1 without color.
    fg: str, int, or None
        The key of the foreground color. Possible values are
            'k': black, 'r': red, 'g': green, 'y': yellow,
            'b': blue, 'c': cyan, 'm': magenta, 'w': white,
            0-255: The color id corresponding to the 256 terminal colors.
    bg: str, int, or None
        The key of the background color. Possible values are the same as fg.
    **kwargs:
        Keyword arguments to be passed to the print function.

    Returns
    -------
    None
    """
    def get_str(key: COLType, fgbg: Literal["fg", "bg"]) -> str:
        if fgbg == "fg":
            XG = FG
            XG256 = FG256
        elif fgbg == 'bg':
            XG = BG
            XG256 = BG256
        else:
            __logger.error(f'something wrong: get_str({fgbg})')
            return ''

        if type(key) is str and key in XG:
            ret_str = XG[key]
        elif type(key) is int and 0 <= key <= 255:
            ret_str = XG256(key)
        elif key is None:
            ret_str = ''
        else:
            __logger.warning(f'incorrect type for {fgbg} key: {key}')
            ret_str = ''
        return ret_str

    fg_str = get_str(fg, 'fg')
    bg_str = get_str(bg, 'bg')
    if len(fg_str+bg_str) != 0:
        end_str = END
    else:
        end_str = ''
    print_str = f'{fg_str}{bg_str}{str1}{end_str}{str2}'
    print(print_str, **kwargs)


def get_col(name: str, filetype: str | None = None) -> tuple[COLType, COLType]:
    """
    get the color id of a given name.

    Parameters
    ----------
    name: str
        A name of the color. Please see wiki
        (https://github.com/MeF0504/aftviewer/wiki/Customization#colors)
        for details.
    filetype: str or None
        set file type name of the script calling this function
        to return proper value.
        if None, use the file type set from command arguments or
        got from the file extension.

    Returns
    -------
    str, int, or None
        foreground color id. If the name is incorrect, return None.
    str, int, or None
        foreground color id. If the name is incorrect, return None.
    """
    if filetype is None:
        filetype = __filetype
    if filetype is None:
        __logger.warning(f'filetype is not set? (get_col, {name})')
    if 'colors' in __user_opts:
        user_cols = __user_opts['colors']
    else:
        user_cols = {}
    def_cols = __def_opts['colors']

    if filetype in user_cols and name in user_cols[filetype]:
        return user_cols[filetype][name]
    elif 'defaults' in user_cols and \
         name in def_cols['defaults'] and \
         name in user_cols['defaults']:
        return user_cols['defaults'][name]
    elif filetype in def_cols and name in def_cols[filetype]:
        return def_cols[filetype][name]
    elif name in def_cols['defaults']:
        return def_cols['defaults'][name]
    else:
        __logger.error(f'color name "{name}" not found in default file.')
        return None, None


def get_timezone() -> None | ZoneInfo:
    """
    Return the timezone variable based on the option "timezone".

    Parameters
    ----------
    None

    Returns
    -------
    None | zoneinfo.ZoneInfo
        Return ZoneInfo if the "timezone" option is not None and acceptable
        for the ZoneInfo function.
        Otherwise, return None.
    """
    tz = get_config('timezone')
    if tz is None:
        ret = None
    else:
        try:
            ret = ZoneInfo(tz)
        except ZoneInfoNotFoundError as e:
            __logger.warning(f'timezone "{tz}" is not found; {e}')
            ret = None
    return ret


def interactive_view(fname: str, get_contents: GC, show_func: SF,
                     purepath: PPath = PurePath) -> None:
    """
    provide the interactive UI to show the contents.

    Parameters
    ----------
    fname: str
        An opened file name.
    get_contents: Callable[[PurePath], tuple[List[str], List[str]]]
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
    tv = TreeViewer('.', get_contents, purepath=purepath, logger=__logger)
    while True:
        term_size = shutil.get_terminal_size()
        print('='*(term_size.columns-5))
        dirs, files = tv.get_contents(cpath)
        cprint('current path:', ' {}/{}'.format(fname, cpath), fg=fg1, bg=bg1)
        cprint('contents in this dict:', ' ', fg=fg2, bg=bg2)
        dir_txt = pprint.pformat([f'{d}/' for d in dirs], compact=True)
        file_txt = pprint.pformat(files, compact=True)
        if len(dirs) != 0:
            # remove [], ''
            print(' '+dir_txt.replace("'", '')[1:-1], end=', ')
        print(' '+file_txt.replace("'", '')[1:-1])
        print('')
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
                    print_error(info.message)
            elif key_name in dirs:
                cpath /= key_name
            else:
                print_error(f'"{key_name}" is not a correct name')


def print_error(msg: str, **kwargs) -> None:
    """
    print error message.

    Parameters
    ----------
    msg: string
        Error message.
    **kwargs
        Keyword arguments to be passed to the print function.

    Returns
    -------
    None
    """
    fg, bg = get_col('msg_error')
    cprint(msg, fg=fg, bg=bg, **kwargs)


def print_warning(msg: str, **kwargs) -> None:
    """
    print warning message.

    Parameters
    ----------
    msg: string
        warning message.
    **kwargs
        Keyword arguments to be passed to the print function.

    Returns
    -------
    None
    """
    fg, bg = get_col('msg_warn')
    cprint(msg, fg=fg, bg=bg, **kwargs)


def print_key(key_name: str, **kwargs) -> None:
    """
    print the key name with emphasis.

    Parameters
    ----------
    key_name: str
        the key name.
    **kwargs
        Keyword arguments to be passed to the print function.

    Returns
    -------
    None
    """
    fg, bg = get_col('msg_key_name')
    cprint('<<< {} >>>'.format(key_name), '', fg=fg, bg=bg, **kwargs)


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
    cmd = get_config('system_cmd')
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
    for arg in get_config('system_cmd_args'):
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


def __set_filetype(args: Args) -> None:
    global __filetype
    if args.type is not None:
        __filetype = args.type
        __logger.debug(f'set file type from args: {args.type}')
        return
    if args.file in ['config_list']:
        __logger.debug(f'{args.file}: set defaults')
        __filetype = 'defaults'
        return
    fpath = Path(args.file)
    if not fpath.is_file():
        __logger.debug('file does not exists')
        return
    ext = fpath.suffix[1:].lower()
    if tarfile.is_tarfile(fpath):
        __logger.debug('set file type: tar')
        args.type = 'tar'
        __filetype = args.type
        return
    else:
        for typ, exts in __type_config.items():
            if ext in exts.split():
                __logger.debug(f'set file type: {typ}')
                args.type = typ
                __filetype = args.type
                return
        mt = mimetypes.guess_type(fpath)[0]
        __logger.info(f'get mimetype: {mt}')
        if mt is not None and mt.split('/')[0] == 'text':
            args.type = 'text'
            __filetype = args.type
            return
    __logger.debug('file type is not set.')


def __add_lib2path():
    add_lib_str = str(__conf_dir/'.lib')
    if add_lib_str not in sys.path:
        __logger.debug(f'add {add_lib_str} to sys.path.')
        sys.path.insert(0, add_lib_str)


def __load_lib(args: Args) -> None | ModuleType:
    if args.type is None:
        __logger.debug('file type is None')
        return None
    elif args.type == 'text':
        __logger.debug('file type is text.')
        return None

    # lib_path  -> python import style
    # lib_path2 -> file path
    if args.type in __add_types:
        __add_lib2path()
        lib_path = f'add_viewers.{args.type}'
        lib_path2 = __conf_dir/f'.lib/add_viewers/{args.type}.py'
    else:
        lib_path = f'aftviewer.viewers.{args.type}'
        lib_path2 = Path(__file__).parent.parent
        lib_path2 /= f'viewers/{args.type}.py'
    if not lib_path2.is_file():
        __logger.error(f'Library file {lib_path2} is not found.')
        return None
    try:
        lib = import_module(lib_path)
    except ImportError as e:
        __logger.error('Failed to load library '
                       f'(lib: {lib_path2}, error: {e})')
        return None
    return lib


def __get_opt_keys() -> dict[str, list[str]]:
    def_opts = __def_opts['config']
    if 'config' in __user_opts:
        user_opts = __user_opts['config']
    else:
        user_opts = {}
    res: dict[str, list[str]] = {}
    res['defaults'] = list(def_opts['defaults'].keys())
    for t in __type_config:
        if t in __add_types:
            # only user_set config
            res[t] = []
            if t in user_opts:
                res[t] += list(user_opts[t].keys())
        else:
            # def + user_set (if in 'config') config
            res[t] = []
            if t in def_opts:
                res[t] += list(def_opts[t].keys())
            if t in user_opts:
                for k in user_opts[t]:
                    if k in def_opts['defaults']:
                        res[t].append(k)
            res[t] = list(set(res[t]))
        res[t].sort()
    return res


def __get_color_names(filetype: str | None) -> list[str]:
    def_cols = __def_opts['colors']
    if 'colors' in __user_opts:
        user_cols = __user_opts['colors']
    else:
        user_cols = {}
    if filetype is None:
        return list(def_cols['defaults'].keys())
    else:
        if filetype in __add_types:
            if filetype in user_cols:
                return list(user_cols[filetype].keys())
            else:
                return []
        else:
            res = []
            if filetype in user_cols:
                for cname in user_cols[filetype].keys():
                    if cname in def_cols['defaults']:
                        res.append(cname)
            if filetype in def_cols:
                res += list(def_cols[filetype].keys())
            res = list(set(res))
            res.sort()
            return res
