from __future__ import annotations

import os
import sys
import tempfile
import subprocess
import mimetypes
from typing import Any
from types import ModuleType
from importlib import import_module
from pathlib import Path
from logging import getLogger

from .. import GLOBAL_CONF, args_chk, get_config, Args
from pymeflib.color import make_bitmap
from pymeflib.util import chk_cmd

logger = getLogger(GLOBAL_CONF.logname)

# image viewer
# not set, module in this package, or external command.
__ImgViewer: None | ModuleType | str = None
__set_ImgViewer = False


def __get_exec_cmds(image_viewer, fname):
    res = []
    for cmd in get_config('config', 'iv_exec_cmd'):
        if cmd == '%s':
            res.append(fname)
        elif cmd == '%c':
            res.append(image_viewer)
        else:
            res.append(cmd)
    logger.debug(f'executed command: {res}')
    return res


def __collect_image_viewers() -> list[str]:
    img_viewers = ['None']
    file_dir = Path(__file__).parent
    for fy in file_dir.glob('*'):
        if not fy.is_file():
            continue
        if fy.name.startswith('__'):
            continue
        iv_name = os.path.splitext(fy.name)[0]
        logger.debug(f'add {iv_name} to img_viewers')
        # arbitary setting?
        img_viewers.insert(0, iv_name)
    add_dir = Path(GLOBAL_CONF.conf_dir/'additional_ivs')
    for fy in add_dir.glob('*'):
        if not fy.is_file():
            continue
        if fy.name.startswith('__'):
            continue
        iv_name = os.path.splitext(fy.name)[0]
        logger.debug(f'add {iv_name} to img_viewers from additional dir')
        img_viewers.insert(0, iv_name)

    return img_viewers


def __get_mod(img_viewer: None | str) -> None | ModuleType:
    try:
        add_path = GLOBAL_CONF.conf_dir/f'additional_ivs/{img_viewer}.py'
        if (Path(__file__).parent/f'{img_viewer}.py').is_file():
            mod = import_module(f'aftviewer.core.image_viewer.{img_viewer}')
        elif add_path.is_file():
            if str(GLOBAL_CONF.conf_dir) not in sys.path:
                logger.debug(f'add {str(GLOBAL_CONF.conf_dir)}'
                             ' to sys.path (iv).')
                sys.path.insert(0, str(GLOBAL_CONF.conf_dir))
            mod = import_module(f'additional_ivs.{img_viewer}')
        else:
            raise OSError(f'library {img_viewer} is not found.')
    except Exception as e:
        logger.error(f'load image viewer failed({type(e).__name__}: {e})')
        return None
    return mod


def __set_image_viewer(args: Args) -> None:
    global __ImgViewer, __set_ImgViewer
    img_viewers = __collect_image_viewers()
    iv_config = get_config('config', 'image_viewer')
    iv_cui_config = get_config('config', 'image_viewer_cui')

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
        logger.info('search available image_viewer')
        for iv in img_viewers:
            logger.debug(f'iv: {iv}')
            if iv == 'None':
                __ImgViewer = iv
                break
            else:
                mod = __get_mod(iv)
                if mod is not None:
                    logger.info(f'find image_viewer: {iv}')
                    __ImgViewer = mod
                    break
    if tmp_iv is None:
        # image viewer is already searched.
        pass
    elif tmp_iv in img_viewers:
        if tmp_iv == 'None':
            __ImgViewer = 'None'
        else:
            __ImgViewer = __get_mod(tmp_iv)
    else:
        # external command
        if args_chk(args, 'cui'):
            logger.error('external command is not supported in CUI mode.')
            __ImgViewer = None
        elif not chk_cmd(tmp_iv, logger=logger):
            logger.error(f'command {tmp_iv} is not executable')
            __ImgViewer = None
        else:
            __ImgViewer = tmp_iv
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
        if chk_cmd(__ImgViewer, logger=logger):
            cmds = __get_exec_cmds(__ImgViewer, img_file)
            out = subprocess.run(cmds)
            if wait:
                # wait to open file. this supports stable behavior
                # for, e.g., open command on Mac OS.
                input('Press Enter to continue')
            if out.returncode == 0:
                ret = True
            else:
                ret = False
        else:
            logger.error(f'{__ImgViewer} is not executable')
            ret = False
    return ret


def show_image_ndarray(data: Any, name: str, args: Args,
                       wait: bool = True) -> None | bool:
    """
    show a given ndArray as an image with the image viewer.

    Parameters
    ----------
    data: numpy.ndarray
        Data to be shown as an image. the shape of the data should be
        (h, w, 3) or (h, w, 4).
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
    logger.debug(f'data shape: {data.shape}')

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
        if chk_cmd(__ImgViewer, logger=logger):
            with tempfile.NamedTemporaryFile(suffix='.bmp') as tmp:
                make_bitmap(tmp.name, data, verbose=False, logger=logger)
                cmds = __get_exec_cmds(__ImgViewer, tmp.name)
                out = subprocess.run(cmds)
                if wait:
                    # wait to open file. this supports stable behavior
                    # for, e.g., open command on Mac OS.
                    input('Press Enter to continue')
                if out.returncode == 0:
                    ret = True
                else:
                    ret = False
        else:
            logger.error(f'{__ImgViewer} is not executable')
            ret = False
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
