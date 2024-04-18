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
        ImageViewers.append(iv_name)


__collect_image_viewers()


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
        return False
    elif img_viewer in ImageViewers:
        try:
            mod = import_module(f'pyviewer.core.image_viewer.{img_viewer}')
            ret = mod.show_image_file(img_file)
        except Exception as e:
            cprint(f'failed to show an image file {img_file}.',
                   file=sys.stderr, fg='r')
            logger.error(f'load image viewer failed({type(e).__name__}: {e})')
            return False
        return ret
    else:
        if not chk_cmd(img_viewer, logger=logger):
            logger.error(f'{img_viewer} is not executable')
            return False
        cmds = __get_exec_cmds(img_viewer, img_file)
        subprocess.run(cmds)
        # wait to open file. this is for, e.g., open command on Mac OS.
        input('Press Enter to continue')
    return True


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
        try:
            mod = import_module(f'pyviewer.core.image_viewer.{img_viewer}')
            ret = mod.show_image_ndarray(data, name)
        except Exception as e:
            cprint('failed to show an image data.', file=sys.stderr, fg='r')
            cprint(f'{type(e).__name__}: {e}', file=sys.stderr, fg='r')
            return False
        return ret
    else:
        if not chk_cmd(img_viewer):
            logger.error(f'{img_viewer} is not executable')
            return False
        with tempfile.NamedTemporaryFile(suffix='.bmp') as tmp:
            make_bitmap(tmp.name, data, verbose=False, logger=logger)
            cmds = __get_exec_cmds(img_viewer, tmp.name)
            subprocess.run(cmds)
            # wait to open file. this is for, e.g., open command on Mac OS.
            input('Press Enter to continue')
    return True


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
