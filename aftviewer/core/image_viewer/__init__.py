from __future__ import annotations

import os
import tempfile
import subprocess
import mimetypes
from typing import Any
from types import ModuleType
from importlib import import_module
from pathlib import Path
from logging import getLogger

from .. import (GLOBAL_CONF, args_chk, get_config, print_error, print_warning,
                Args, __add_lib2path, __def)
from pymeflib.color import make_bitmap
from pymeflib.util import chk_cmd

logger = getLogger(GLOBAL_CONF.logname)

# image viewer
# not set, module in this package, or external command.
__ImgViewer: None | ModuleType | str = None
__set_ImgViewer = False


def __get_exec_cmds(fname) -> list[str]:
    global __ImgViewer
    assert type(__ImgViewer) is str, 'Something wrong:' \
        f' image viewer is not set yet? {__ImgViewer}'
    res = []
    for cmd in get_config('iv_cmds').get(__ImgViewer, []):
        if cmd == '%s':
            res.append(fname)
        else:
            res.append(cmd)
    logger.debug(f'executed command: {res}')
    return res


def __collect_image_viewers() -> tuple[list[str], ...]:
    viewers_none = ['None']
    viewers_module: list[str] = []
    viewers_cmd: list[str] = list(get_config('iv_cmds').keys())

    file_dir = Path(__file__).parent
    for fy in file_dir.glob('*'):
        if not fy.is_file():
            continue
        if fy.name.startswith('__'):
            continue
        iv_name = os.path.splitext(fy.name)[0]
        logger.debug(f'add {iv_name} to viewers_module')
        # arbitary setting?
        viewers_module.append(iv_name)
    if not __def:
        add_dir = GLOBAL_CONF.conf_dir/'.lib/add_image_viewers'
        for fy in add_dir.glob('*'):
            if not fy.is_file():
                continue
            if fy.name.startswith('__'):
                continue
            iv_name = os.path.splitext(fy.name)[0]
            logger.debug(f'add {iv_name} to viewers_module from add dir')
            viewers_module.append(iv_name)

    for vc in viewers_cmd:
        assert vc not in viewers_none \
            or vc not in viewers_module, \
            f'The key name {vc} in "iv_cmds" is a reserved name.' \
            ' Please change to other name.'
    return viewers_none, viewers_module, viewers_cmd


def __get_mod(img_viewer: None | str) -> None | ModuleType:
    __add_lib2path()
    try:
        add_path = GLOBAL_CONF.conf_dir/f'.lib/add_image_viewers/{img_viewer}.py'
        if (Path(__file__).parent/f'{img_viewer}.py').is_file():
            mod = import_module(f'aftviewer.core.image_viewer.{img_viewer}')
        elif add_path.is_file():
            mod = import_module(f'add_image_viewers.{img_viewer}')
        else:
            raise OSError(f'library {img_viewer} is not found.')
    except Exception as e:
        logger.error(f'load image viewer failed({type(e).__name__}: {e})')
        return None
    return mod


def __set_image_viewer(args: Args) -> None:
    global __ImgViewer, __set_ImgViewer
    none_iv, mod_iv, cmd_iv = __collect_image_viewers()
    iv_config = get_config('image_viewer')
    iv_cui_config = get_config('image_viewer_cui')

    tmp_iv = None
    if args_chk(args, 'image_viewer'):
        logger.info('set image viewer from args')
        tmp_iv = args.image_viewer
    elif args_chk(args, 'cui') and iv_cui_config is not None:
        logger.info('set image viewer from config file (CUI)')
        tmp_iv = iv_cui_config
    elif iv_config is not None:
        logger.info('set image viewer from config file')
        tmp_iv = iv_config
    else:
        logger.info('search available image viewer')
        for iv in mod_iv:
            logger.debug(f'iv: {iv}')
            mod = __get_mod(iv)
            if mod is not None:
                logger.info(f'find image_viewer: {iv}')
                __ImgViewer = mod
                break

    if tmp_iv is None:
        # image viewer is already searched.
        pass
    elif tmp_iv in none_iv:
        __ImgViewer = 'None'
    elif tmp_iv in mod_iv:
        __ImgViewer = __get_mod(tmp_iv)
    elif tmp_iv in cmd_iv:
        # external command
        if args_chk(args, 'cui'):
            logger.error('external command is not supported in CUI mode.')
            __ImgViewer = None
        else:
            cmd_list = get_config('iv_cmds').get(tmp_iv, None)
            if cmd_list is None:
                msg = f'{tmp_iv} is not found in "iv_cmds".'
                print_error(msg)
                logger.error(msg)
                __ImgViewer = None
            elif not chk_cmd(cmd_list[0], logger=logger):
                msg = f'command {cmd_list[0]} is not executable.'
                print_error(msg)
                logger.error(msg)
                __ImgViewer = None
            else:
                if '%s' not in cmd_list:
                    msg = 'Special character to specify image file path' \
                        ' "%s" is not in the specified iv commands.' \
                        ' The image file may not be shown.'
                    print_warning(msg)
                __ImgViewer = tmp_iv
    else:
        msg = f'non-supported image viewer is set: {tmp_iv}'
        print_error(msg)
        logger.error(msg)
    __set_ImgViewer = True
    logger.debug(f'image viewer: {__ImgViewer} (None?:{__ImgViewer is None})')


def show_image_file(img_file: str, args: Args,
                    wait: bool = True) -> None | bool:
    """
    show an image file with the image viewer.

    Parameters
    ----------
    img_file: str
        image file.
    args: Args
        The arguments given by the command line.
    wait: bool
        If true, wait to press any key after opening the image file
        by the command.
        Default: True.

    Returns
    -------
    True, False, or None
        Return True if the file opened successfully and
        False if opening file failed.
        If a module to open the image is not found, return None.
    """
    global __set_ImgViewer, __ImgViewer
    logger.debug(f'img file: {img_file}')
    if not os.path.isfile(img_file):
        logger.error(f'image file {img_file} in not found')
        return False

    if not __set_ImgViewer:
        __set_image_viewer(args)

    if __ImgViewer is None:
        logger.error("I can't find any libraries to show image.")
        ret = None
    elif __ImgViewer == 'None':
        logger.info('image viewer is None.')
        ret = True
    elif type(__ImgViewer) is ModuleType:
        if hasattr(__ImgViewer, 'show_image_file'):
            ret = __ImgViewer.show_image_file(img_file)
        else:
            logger.error('show_image_file function is not found'
                         f'({__ImgViewer}).')
            ret = None
    elif type(__ImgViewer) is str:
        cmds = __get_exec_cmds(img_file)
        out = subprocess.run(cmds)
        if wait:
            # wait to open file. this supports stable behavior
            # for, e.g., open command on Mac OS.
            input('Press Enter to continue')
        if out.returncode == 0:
            ret = True
        else:
            ret = False
    return ret


def show_image_ndarray(data: Any, name: str, args: Args,
                       wait: bool = True) -> None | bool:
    """
    show a given ndArray as an image with the image viewer.

    Parameters
    ----------
    data: array-like
        Data to be shown as an image. the shape of the data should be
        (h, w, 3) or (h, w, 4).
        Some image viewers requires numpy.ndarray data.
    name: str
        The name of the image.
    args: Args
        The arguments given by the command line.
    wait: bool
        If true, wait to press any key after opening the image file
        by the command.
        Default: True

    Returns
    -------
    bool
        Return True if the file opened successfully and
        False if opening file failed.
        If a module to open the image is not found, return None.
    """
    global __set_ImgViewer, __ImgViewer
    if hasattr(data, 'shape'):
        logger.debug(f'data shape: {data.shape}')
    else:
        logger.debug(f'data shape: {len(data)}, {len(data[0])}')

    if not __set_ImgViewer:
        __set_image_viewer(args)

    if __ImgViewer is None:
        logger.error("I can't find any libraries to show image.")
        ret = None
    elif __ImgViewer == 'None':
        logger.info('image viewer is None.')
        ret = True
    elif type(__ImgViewer) is ModuleType:
        if hasattr(__ImgViewer, 'show_image_ndarray'):
            ret = __ImgViewer.show_image_ndarray(data, name)
        else:
            logger.error('show_image_ndarray function is not found'
                         f'({__ImgViewer}).')
            ret = None
    elif type(__ImgViewer) is str:
        if os.name == 'nt':  # Windows
            # Because Windows does not allow "with" statement in temp file.
            # delete_on_close is supported in >= 3.12
            tmpd = False
        else:
            tmpd = True
        with tempfile.NamedTemporaryFile(suffix='.bmp',
                                         delete=tmpd) as tmp:
            make_bitmap(tmp.name, data, verbose=False, logger=logger)
            cmds = __get_exec_cmds(tmp.name)
            out = subprocess.run(cmds)
            if wait:
                # wait to open file. this supports stable behavior
                # for, e.g., open command on Mac OS.
                input('Press Enter to continue')
            if out.returncode == 0:
                ret = True
            else:
                ret = False
        if not tmpd and os.path.isfile(tmp.name):
            os.remove(tmp.name)
            logger.debug(f'tmp file {tmp.name} is deleted')
    return ret


def is_image(path: str | os.PathLike) -> bool:
    """
    judge whether the file of a given path is an image file.

    Parameters
    ----------
    path: str or PathLike
        a path to a file judging whether it is an image file or not.

    Returns
    -------
    bool
        return True if the file is judged as an image file.
    """
    mime = mimetypes.guess_type(path)[0]
    if mime is None:
        return False
    elif mime.split('/')[0] == 'image':
        return True
    else:
        return False
