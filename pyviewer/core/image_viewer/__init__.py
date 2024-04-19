import os
import sys
import tempfile
import subprocess
import mimetypes
from typing import Any, Union, Optional
from importlib import import_module
from pathlib import Path
from logging import getLogger

from .. import GLOBAL_CONF, args_chk, get_config, Args, cprint
from pymeflib.color import make_bitmap
from pymeflib.util import chk_cmd

logger = getLogger(GLOBAL_CONF.logname)

# image viewer
__ImgViewer = None
__set_ImgViewer = False
ImageViewers = ['None']


def get_image_viewer(args: Args) -> Optional[str]:
    """
    get the image viewer following the arguments from the command line and
    configuration options.

    Parameters
    ----------
    args: Args
        The arguments given by the command line.

    Returns
    -------
    Optional[str]
        the name of image viewer.
    """
    global __ImgViewer, __set_ImgViewer
    if __set_ImgViewer:
        # already set
        return __ImgViewer

    iv_config = get_config('config', 'image_viewer')
    iv_cui_config = get_config('config', 'image_viewer_cui')
    if args_chk(args, 'image_viewer'):
        logger.info('set image viewer from args')
        __ImgViewer = args.image_viewer
    elif args_chk(args, 'cui') and iv_cui_config is not None:
        logger.info('set image viewer from config file (CUI)')
        __ImgViewer = iv_cui_config
    elif iv_config is not None:
        logger.info('set image viewer from config file')
        __ImgViewer = iv_config
    else:
        logger.info('search available image_viewer')
        for iv in ImageViewers:
            if iv == 'None':
                continue
            for p in sys.path:
                if (Path(p)/iv).exists():
                    __ImgViewer = iv
                    logger.info(f' => image_viewer: {iv}')
                    break
            if __ImgViewer is not None:
                # image viewer is set.
                break
        if __ImgViewer is None:
            logger.warning("can't find image_viewer")
    __set_ImgViewer = True
    return __ImgViewer


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


def __collect_image_viewers():
    global ImageViewers
    file_dir = Path(__file__).parent
    for fy in file_dir.glob('*'):
        if not fy.is_file():
            continue
        if fy.name.startswith('__'):
            continue
        iv_name = os.path.splitext(fy.name)[0]
        logger.debug(f'add {iv_name} to ImageViewers')
        # arbitary setting?
        ImageViewers.insert(0, iv_name)
    add_dir = Path(GLOBAL_CONF.conf_dir/'additional_ivs')
    for fy in add_dir.glob('*'):
        if not fy.is_file():
            continue
        if fy.name.startswith('__'):
            continue
        iv_name = os.path.splitext(fy.name)[0]
        logger.debug(f'add {iv_name} to ImageViewers from additional dir')
        ImageViewers.insert(0, iv_name)


__collect_image_viewers()


def __get_mod(img_viewer: Optional[str]):
    try:
        add_path = GLOBAL_CONF.conf_dir/f'additional_ivs/{img_viewer}.py'
        if (Path(__file__).parent/f'{img_viewer}.py').is_file():
            mod = import_module(f'pyviewer.core.image_viewer.{img_viewer}')
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


def show_image_file(img_file: str, args: Args) -> bool:
    """
    show an image file with the image viewer.

    Parameters
    ----------
    img_file: str
        image file.
    args: Args
        The arguments given by the command line.

    Returns
    -------
    bool
        Return True if the file opened successfully, otherwise False.
    """
    img_viewer = get_image_viewer(args)
    logger.debug(f'img file:{img_file}, use {img_viewer}')
    if img_viewer == 'None':
        return True
    if not os.path.isfile(img_file):
        logger.error(f'image file {img_file} in not found')
        return False
    if img_viewer is None:
        logger.error("I can't find any libraries to show image.")
        ret = False
    elif img_viewer in ImageViewers:
        mod = __get_mod(img_viewer)
        if mod is not None:
            ret = mod.show_image_file(img_file)
        else:
            cprint(f'failed to show an image file {img_file}.',
                   file=sys.stderr, fg='r')
            ret = False
    else:
        if not chk_cmd(img_viewer, logger=logger):
            logger.error(f'{img_viewer} is not executable')
            return False
        cmds = __get_exec_cmds(img_viewer, img_file)
        out = subprocess.run(cmds)
        # wait to open file. this is for, e.g., open command on Mac OS.
        input('Press Enter to continue')
        if out.returncode == 0:
            ret = True
        else:
            ret = False
    return ret


def show_image_ndarray(data: Any, name: str, args: Args) -> bool:
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

    Returns
    -------
    bool
        Return True if the image is shown successfully, otherwise False.
    """
    img_viewer = get_image_viewer(args)
    logger.debug(f'data shape: {data.shape}, use {img_viewer}')
    if img_viewer == 'None':
        return True
    if img_viewer is None:
        logger.error("I can't find any libraries to show image.")
        return False
    elif img_viewer in ImageViewers:
        mod = __get_mod(img_viewer)
        if mod is not None:
            ret = mod.show_image_ndarray(data, name)
        else:
            cprint('failed to show an image data.', file=sys.stderr, fg='r')
            ret = False
    else:
        if not chk_cmd(img_viewer):
            logger.error(f'{img_viewer} is not executable')
            return False
        with tempfile.NamedTemporaryFile(suffix='.bmp') as tmp:
            make_bitmap(tmp.name, data, verbose=False, logger=logger)
            cmds = __get_exec_cmds(img_viewer, tmp.name)
            out = subprocess.run(cmds)
            # wait to open file. this is for, e.g., open command on Mac OS.
            input('Press Enter to continue')
            if out.returncode == 0:
                ret = True
            else:
                ret = False
    return ret


def is_image(path: Union[str, os.PathLike]) -> bool:
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
