import os
import zipfile
import tempfile
import time
from functools import partial
from getpass import getpass
from pathlib import PurePosixPath

from . import args_chk, is_image, print_key, cprint, debug_print,\
    interactive_view, interactive_cui, show_image_file, get_image_viewer,\
    run_system_cmd
from pymeflib.tree2 import branch_str, show_tree
import pyviewerlib.core.cui
import pyviewerlib.core
pyviewerlib.core.cui.PurePath = PurePosixPath
pyviewerlib.core.PurePath = PurePosixPath


def get_pwd():
    pwd = getpass()
    return pwd.encode()


def get_contents(zip_file, path):
    if str(path) == '.':
        cpath = ''
        lenpath = 0
    else:
        cpath = str(path)
        if not cpath.endswith('/'):
            cpath += '/'
        lenpath = len(cpath)
    files = []
    dirs = []
    for z in zip_file.infolist():
        # dir name ends with /
        if lenpath != 0:
            if z.filename[:-1] == cpath:
                continue
            if not z.filename.startswith(cpath):
                continue
        zname = z.filename[lenpath:]
        if zname.endswith('/'):
            zname = zname[:-1]
        if z.filename == str(cpath):
            continue
        if '/' in zname:
            # in some case, directories are not listed?
            tmp_dir = zname.split('/')[0]
            if tmp_dir not in dirs:
                dirs.append(tmp_dir)
        elif z.is_dir():
            if zname not in dirs:
                dirs.append(zname)
        else:
            files.append(zname)
    return dirs, files


def show_zip(zip_file, pwd, args, get_contents, cpath, cui=False,
             system=False):
    res = []
    img_viewer = get_image_viewer(args)
    try:
        key_name = str(cpath)
        if key_name+'/' in zip_file.namelist():
            key_name += '/'
        zipinfo = zip_file.getinfo(key_name)
    except KeyError as e:
        debug_print(e)
        return '', 'Error!! cannot open {}.'.format(cpath)

    if zipinfo.is_dir():
        # directory
        res.append('{}'.format(key_name))
        dirs, files = get_contents(key_name)
        for f in files:
            res.append('{}{}'.format(branch_str, f))
        for d in dirs:
            res.append('{}{}/'.format(branch_str, d))

    else:
        # file
        if system:
            with tempfile.TemporaryDirectory() as tmpdir:
                zip_file.extract(zipinfo, path=tmpdir, pwd=pwd)
                tmpfile = os.path.join(tmpdir, cpath)
                ret = run_system_cmd(tmpfile)
                time.sleep(3)
            if ret:
                return 'open {}'.format(cpath), None
            else:
                return '', 'Failed to open {}.'.format(cpath)
        if is_image(key_name):
            cond = cui and (img_viewer not in ['PIL', 'matplotlib', 'OpenCV'])
            with tempfile.TemporaryDirectory() as tmpdir:
                zip_file.extract(zipinfo, path=tmpdir, pwd=pwd)
                tmpfile = os.path.join(tmpdir, cpath)
                ret = show_image_file(tmpfile, args, cond)
            if not ret:
                return '', 'Failed to show image.'

        # text file?
        else:
            for line in zip_file.open(key_name, 'r', pwd=pwd):
                try:
                    res.append(line.decode().replace("\n", ''))
                except UnicodeDecodeError as e:
                    return '', 'Error!! {}'.format(e)

    return '\n'.join(res), None


def main(fpath, args):
    if not zipfile.is_zipfile(fpath):
        print('{} is not a zip file.'.format(fpath))
        return
    zip_file = zipfile.ZipFile(fpath, 'r')
    fname = os.path.basename(fpath)
    gc = partial(get_contents, zip_file)

    if args_chk(args, 'interactive'):
        if args.ask_password:
            pwd = get_pwd()
        else:
            pwd = None
        interactive_view(fname, gc, partial(show_zip, zip_file, pwd, args, gc))
    elif args_chk(args, 'cui'):
        if args.ask_password:
            pwd = get_pwd()
        else:
            pwd = None
        interactive_cui(fpath, gc, partial(show_zip, zip_file, pwd, args, gc))
    elif args_chk(args, 'key'):
        if len(args.key) == 0:
            for fy in zip_file.namelist():
                print(fy)
            return
        if args.ask_password:
            pwd = get_pwd()
        else:
            pwd = None
        for k in args.key:
            print_key(k)
            info, err = show_zip(zip_file, pwd, args, gc, k)
            if err is None:
                print(info)
                print()
            else:
                cprint(err, fg='r')
    elif args_chk(args, 'verbose'):
        zip_file.printdir()
    else:
        show_tree(fname, gc)

    zip_file.close()
