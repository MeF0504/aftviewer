# test image viewer related functions.
import sys
import argparse
import warnings
import platform
from pathlib import Path
from types import ModuleType

import pytest

from aftviewer.core import image_viewer, __json_opts
from aftviewer.core.helpmsg import add_args_imageviewer, add_args_cui

uname = platform.system()
if uname == 'Darwin':
    cmd = 'open'
elif uname == 'Windows':
    cmd = 'dir'
elif uname == 'Linux':
    cmd = 'display'
else:
    cmd = None

ivs = [('None'), ('matplotlib'), ('PIL'), ('cv2'), (cmd), ('not a command')]


def check_mod_installed(iv):
    if iv not in ('matplotlib', 'PIL', 'cv2'):
        return None
    for p in sys.path:
        if (Path(p)/iv).is_dir():
            return ModuleType
    return type(None)


@pytest.mark.parametrize(('iv'), ivs)
def test_get_image_viewer_args(iv):
    # args specified case
    if cmd is None:
        warnings.warn(f'not supported OS [{uname}]. skip.')
        return
    image_viewer.__set_ImgViewer = False
    image_viewers = image_viewer.__collect_image_viewers()
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='input file')
    parser.add_argument('--type')
    add_args_imageviewer(parser)
    args = parser.parse_args(['test', '-iv', iv])
    image_viewer.__set_image_viewer(args)
    msg = f'image viewer check, {iv}, {image_viewer.__ImgViewer}'
    if iv == 'None':
        assert image_viewer.__ImgViewer == 'None', msg
    elif iv in image_viewers:
        mod_type = check_mod_installed(iv)
        assert mod_type is not None, f'something strange; {iv}'
        assert type(image_viewer.__ImgViewer) is mod_type, msg
        if mod_type is ModuleType:
            assert hasattr(image_viewer.__ImgViewer, 'show_image_file')
            assert hasattr(image_viewer.__ImgViewer, 'show_image_ndarray')
        else:
            warnings.warn(f'skip checking iv: {iv}')
    elif iv == 'not a command':
        assert image_viewer.__ImgViewer is None, msg
    else:
        assert image_viewer.__ImgViewer == iv, msg


@pytest.mark.parametrize(('iv'), ivs)
def test_get_image_viewer_cui(iv):
    # cui config case
    if cmd is None:
        warnings.warn(f'not supported OS [{uname}]. skip.')
        return
    image_viewer.__set_ImgViewer = False
    image_viewers = image_viewer.__collect_image_viewers()
    __json_opts['config']['image_viewer_cui'] = iv
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='input file')
    parser.add_argument('--type')
    add_args_imageviewer(parser)
    add_args_cui(parser)
    args = parser.parse_args(['test', '-c'])
    image_viewer.__set_image_viewer(args)
    msg = f'image viewer check, {iv}, {image_viewer.__ImgViewer}'
    if iv == 'None':
        assert image_viewer.__ImgViewer == 'None', msg
    elif iv in image_viewers:
        mod_type = check_mod_installed(iv)
        assert mod_type is not None, f'something strange; {iv}'
        assert type(image_viewer.__ImgViewer) is mod_type, msg
        if mod_type is ModuleType:
            assert hasattr(image_viewer.__ImgViewer, 'show_image_file')
            assert hasattr(image_viewer.__ImgViewer, 'show_image_ndarray')
        else:
            warnings.warn(f'skip checking iv: {iv}')
    elif iv == 'not a command':
        assert image_viewer.__ImgViewer is None, msg
    else:
        assert image_viewer.__ImgViewer is None, msg


@pytest.mark.parametrize(('iv'), ivs)
def test_get_image_viewer_conf(iv):
    # config case
    if cmd is None:
        warnings.warn(f'not supported OS [{uname}]. skip.')
        return
    image_viewer.__set_ImgViewer = False
    image_viewers = image_viewer.__collect_image_viewers()
    __json_opts['config']['image_viewer'] = iv
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='input file')
    parser.add_argument('--type')
    add_args_imageviewer(parser)
    args = parser.parse_args(['test'])
    image_viewer.__set_image_viewer(args)
    msg = f'image viewer check, {iv}, {image_viewer.__ImgViewer}'
    if iv == 'None':
        assert image_viewer.__ImgViewer == 'None', msg
    elif iv in image_viewers:
        mod_type = check_mod_installed(iv)
        assert mod_type is not None, f'something strange; {iv}'
        assert type(image_viewer.__ImgViewer) is mod_type, msg
        if mod_type is ModuleType:
            assert hasattr(image_viewer.__ImgViewer, 'show_image_file')
            assert hasattr(image_viewer.__ImgViewer, 'show_image_ndarray')
        else:
            warnings.warn(f'skip checking iv: {iv}')
    elif iv == 'not a command':
        assert image_viewer.__ImgViewer is None, msg
    else:
        assert image_viewer.__ImgViewer == iv, msg


def test_get_image_viewer_search():
    # not set case
    image_viewer.__set_ImgViewer = False
    __json_opts['config']['image_viewer'] = None
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='input file')
    parser.add_argument('--type')
    add_args_imageviewer(parser)
    args = parser.parse_args(['test'])
    image_viewer.__set_image_viewer(args)
    assert image_viewer.__ImgViewer is not None, f'{image_viewer.__ImgViewer}'
