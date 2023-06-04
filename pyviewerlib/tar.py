import os
import tarfile
import tempfile
from functools import partial
from pathlib import PurePosixPath

from . import args_chk, print_key, cprint, debug_print, get_image_viewer,\
    is_image, interactive_view, interactive_cui,\
    show_image_file, run_system_cmd, get_col
from pymeflib.tree2 import branch_str, show_tree
import pyviewerlib.core.cui
import pyviewerlib.core
import pymeflib.tree2
pyviewerlib.core.cui.PurePath = PurePosixPath
pyviewerlib.core.PurePath = PurePosixPath
pymeflib.tree2.PurePath = PurePosixPath


def show_tar(tar_file, args, get_contents, cpath, **kwargs):
    res = []
    img_viewer = get_image_viewer(args)
    # check cpath
    try:
        if cpath.endswith('/'):
            key_name = cpath[:-1]
        else:
            key_name = cpath
        tarinfo = tar_file.getmember(key_name)
    except KeyError as e:
        debug_print(e)
        return '', 'Error!! Cannot open {}.'.format(cpath)

    if tarinfo.isfile():
        # file
        if 'system' in kwargs and kwargs['system']:
            stdscr = kwargs['stdscr']
            with tempfile.TemporaryDirectory() as tmpdir:
                tar_file.extractall(path=tmpdir, members=[tarinfo])
                tmpfile = os.path.join(tmpdir, cpath)
                ret = run_system_cmd(tmpfile)
                stdscr.getkey()
            if ret:
                return 'open {}'.format(cpath), None
            else:
                return '', 'Failed to open {}.'.format(cpath)
        elif is_image(key_name):
            if 'cui' in kwargs and kwargs['cui']:
                ava_iv = ['PIL', 'matplotlib', 'OpenCV']
                if img_viewer not in ava_iv:
                    return '', 'Only {} are supported as an Image viewer in CUI mode. current: "{}"'.format(', '.join(ava_iv), img_viewer)
            with tempfile.TemporaryDirectory() as tmpdir:
                tar_file.extractall(path=tmpdir, members=[tarinfo])
                tmpfile = os.path.join(tmpdir, cpath)
                ret = show_image_file(tmpfile, args)
            if not ret:
                return '', 'Failed to show image.'

        else:
            # text file?
            for line in tar_file.extractfile(key_name):
                try:
                    res.append(line.decode().replace("\n", ''))
                except UnicodeDecodeError as e:
                    return '', 'Error!! {}'.format(e)
        res.append('')

    # directory
    elif tarinfo.isdir():
        res.append('{}/'.format(key_name))
        dirs, files = get_contents(key_name)
        for f in files:
            res.append('{}{}'.format(branch_str, f))
        for d in dirs:
            res.append('{}{}/'.format(branch_str, d))
    else:
        res.append('sorry, I can\'t show information.\n')

    return '\n'.join(res), None


def get_contents(tar_file, path):
    path = str(path)
    if path == '.':
        lenpath = 0
    else:
        lenpath = len(path)+1
    files = []
    dirs = []
    for t in tar_file.getmembers():
        if lenpath != 0:
            if t.name == path:
                continue
            if not t.name.startswith(path):
                continue
        tname = t.name[lenpath:]
        if '/' in tname:
            # in some case, directories are not listed?
            tmp_dir = tname.split('/')[0]
            if tmp_dir not in dirs:
                dirs.append(tmp_dir)
        elif t.isfile():
            files.append(tname)
        elif t.isdir():
            dirs.append(tname)
    return dirs, files


def main(fpath, args):
    if not tarfile.is_tarfile(fpath):
        print('{} is not a tar file.'.format(fpath))
        return
    tar_file = tarfile.open(fpath, 'r:*')
    fname = os.path.basename(fpath)
    gc = partial(get_contents, tar_file)
    sf = partial(show_tar, tar_file, args, gc)

    if args_chk(args, 'interactive'):
        interactive_view(fname, gc, sf)
    elif args_chk(args, 'cui'):
        interactive_cui(fpath, gc, sf)
    elif args_chk(args, 'key'):
        fg, bg = get_col('error')
        if len(args.key) == 0:
            tar_file.list(verbose=False)
        for k in args.key:
            print_key(k)
            info, err = show_tar(tar_file, args, gc, k)
            if err is None:
                print(info)
                print()
            else:
                cprint(err, fg=fg, bg=bg)
    elif args_chk(args, 'verbose'):
        tar_file.list(verbose=True)
    else:
        show_tree(fname, gc)

    tar_file.close()
