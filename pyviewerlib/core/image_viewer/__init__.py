import os
import tempfile
import subprocess
import mimetypes
from typing import Any, Union, Optional
from importlib import import_module

from .. import args_chk, debug_print, debug, json_opts, Args
from pymeflib.color import make_bitmap
from pymeflib.util import chk_cmd

# image viewer
__ImgViewer = None
__mods = ['PIL', 'matplotlib', 'OpenCV']


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
    global __ImgViewer
    if __ImgViewer is not None:
        return __ImgViewer
    if args_chk(args, 'image_viewer'):
        debug_print('set image viewer from args')
        __ImgViewer = args.image_viewer
    else:
        debug_print('search available image_viewer')
        try:
            from PIL import Image
            debug_print(' => image_viewer: PIL')
        except ImportError:
            pass
        else:
            __ImgViewer = 'PIL'

        if __ImgViewer is None:
            try:
                import matplotlib.pyplot as plt
                debug_print(' => image_viewer: matplotlib')
            except ImportError:
                pass
            else:
                __ImgViewer = 'matplotlib'

        if __ImgViewer is None:
            try:
                import cv2
                debug_print(' => image_viewer: OpenCV')
            except ImportError:
                pass
            else:
                __ImgViewer = 'OpenCV'

        if __ImgViewer is None:
            debug_print("can't find image_viewer")
    return __ImgViewer


def get_exec_cmds(args, fname):
    res = []
    for cmd in json_opts['iv_exec_cmd']:
        if cmd == '%s':
            res.append(fname)
        elif cmd == '%c':
            res.append(args.image_viewer)
        else:
            res.append(cmd)
    debug_print('executed command: {}'.format(res))
    return res


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
    debug_print('  use {}'.format(img_viewer))
    if not os.path.isfile(img_file):
        debug_print('image file {} in not found'.format(img_file))
        return False
    if img_viewer is None:
        print("I can't find any libraries to show image.")
        return False
    elif img_viewer in __mods:
        mod = import_module(f'pyviewerlib.core.image_viewer.{img_viewer}')
        mod.show_image_file(img_file)
    else:
        if not chk_cmd(img_viewer):
            print(f'{img_viewer} is not executable')
            return False
        cmds = get_exec_cmds(args, img_file)
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
    debug_print('{}\n  use {}'.format(data.shape, img_viewer))
    if img_viewer is None:
        print("I can't find any libraries to show image. Please install Pillow or matplotlib.")
        return False
    elif img_viewer in __mods:
        mod = import_module(f'pyviewerlib.core.image_viewer.{img_viewer}')
        mod.show_image_ndarray(data, name)
    else:
        if not chk_cmd(img_viewer):
            print(f'{img_viewer} is not executable')
            return False
        with tempfile.NamedTemporaryFile(suffix='.bmp') as tmp:
            make_bitmap(tmp.name, data, verbose=debug)
            cmds = get_exec_cmds(args, tmp.name)
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
