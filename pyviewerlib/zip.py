import os
import zipfile
import tempfile
from functools import partial
from getpass import getpass
from pathlib import PurePosixPath

from . import args_chk, is_image, print_key, cprint, debug_print, get_col,\
    interactive_view, interactive_cui, show_image_file, get_image_viewer,\
    run_system_cmd, help_template
from . import ReturnMessage as RM
from pymeflib.tree2 import branch_str, show_tree
import pyviewerlib.core.cui
import pyviewerlib.core
import pymeflib.tree2
pyviewerlib.core.cui.PurePath = PurePosixPath
pyviewerlib.core.PurePath = PurePosixPath
pymeflib.tree2.PurePath = PurePosixPath


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


def show_zip(zip_file, pwd, args, get_contents, cpath, **kwargs):
    res = []
    img_viewer = get_image_viewer(args)
    try:
        key_name = str(cpath)
        if key_name+'/' in zip_file.namelist():
            key_name += '/'
        zipinfo = zip_file.getinfo(key_name)
    except KeyError as e:
        debug_print(e)
        return RM('Error!! cannot open {}.'.format(cpath), True)

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
        if 'system' in kwargs and kwargs['system']:
            stdscr = kwargs['stdscr']
            with tempfile.TemporaryDirectory() as tmpdir:
                zip_file.extract(zipinfo, path=tmpdir, pwd=pwd)
                tmpfile = os.path.join(tmpdir, cpath)
                ret = run_system_cmd(tmpfile)
                stdscr.getkey()
            if ret:
                return RM('open {}'.format(cpath), False)
            else:
                return RM('Failed to open {}.'.format(cpath), True)
        elif is_image(key_name):
            if 'cui' in kwargs and kwargs['cui']:
                ava_iv = ['PIL', 'matplotlib', 'OpenCV']
                if img_viewer not in ava_iv:
                    return RM('Only {} are supported as an Image viewer in CUI mode. current: "{}"'.format(', '.join(ava_iv), img_viewer), True)
            with tempfile.TemporaryDirectory() as tmpdir:
                zip_file.extract(zipinfo, path=tmpdir, pwd=pwd)
                tmpfile = os.path.join(tmpdir, cpath)
                ret = show_image_file(tmpfile, args)
            if not ret:
                return RM('Failed to show image.', True)

        # text file?
        else:
            for line in zip_file.open(key_name, 'r', pwd=pwd):
                try:
                    res.append(line.decode().replace("\n", ''))
                except UnicodeDecodeError as e:
                    return RM('Error!! {}'.format(e), True)

    return RM('\n'.join(res), False)


def show_help():
    helpmsg = help_template('zip', 'show the contents of a zip file.',
                            sup_iv=True, sup_encoding=True, sup_password=True,
                            sup_v=True, sup_k=True, sup_i=True, sup_c=True)
    print(helpmsg)


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
        fg, bg = get_col('error')
        for k in args.key:
            print_key(k)
            info = show_zip(zip_file, pwd, args, gc, k)
            if not info.error:
                print(info.message)
                print()
            else:
                cprint(info.message, fg=fg, bg=bg)
    elif args_chk(args, 'verbose'):
        zip_file.printdir()
    else:
        show_tree(fname, gc)

    zip_file.close()
