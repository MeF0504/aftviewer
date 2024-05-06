# test image viewer related functions.
import argparse

import pytest

from aftviewer.core import image_viewer, __json_opts
from aftviewer.core.helpmsg import add_args_imageviewer, add_args_cui

ivs = [('None'), ('matplotlib'), ('PIL'), ('cv2'), ('open')]


@pytest.mark.parametrize(('iv'), ivs)
def test_get_image_viewer_args(iv):
    # args specified case
    image_viewer.__set_ImgViewer = False
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='input file')
    parser.add_argument('--type')
    add_args_imageviewer(parser)
    args = parser.parse_args(['test', '-iv', iv])
    get_iv = image_viewer.get_image_viewer(args)
    assert iv == get_iv, f'{iv}, {get_iv}'


@pytest.mark.parametrize(('iv'), ivs)
def test_get_image_viewer_cui(iv):
    # cui config case
    image_viewer.__set_ImgViewer = False
    __json_opts['config']['image_viewer_cui'] = iv
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='input file')
    parser.add_argument('--type')
    add_args_imageviewer(parser)
    add_args_cui(parser)
    args = parser.parse_args(['test', '-c'])
    get_iv = image_viewer.get_image_viewer(args)
    assert iv == get_iv, f'{iv}, {get_iv}'


@pytest.mark.parametrize(('iv'), ivs)
def test_get_image_viewer_conf(iv):
    # config case
    image_viewer.__set_ImgViewer = False
    __json_opts['config']['image_viewer'] = iv
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='input file')
    parser.add_argument('--type')
    add_args_imageviewer(parser)
    args = parser.parse_args(['test'])
    get_iv = image_viewer.get_image_viewer(args)
    assert iv == get_iv, f'{iv}, {get_iv}'


def test_get_image_viewer_search():
    # not set case
    image_viewer.__set_ImgViewer = False
    __json_opts['config']['image_viewer'] = None
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='input file')
    parser.add_argument('--type')
    add_args_imageviewer(parser)
    args = parser.parse_args(['test'])
    get_iv = image_viewer.get_image_viewer(args)
    assert get_iv is not None
