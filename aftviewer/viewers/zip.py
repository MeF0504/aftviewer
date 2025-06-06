from __future__ import annotations

import os
import zipfile
import tempfile
from functools import partial
from getpass import getpass
from pathlib import Path, PurePosixPath
from logging import getLogger

from .. import (GLOBAL_CONF, Args, args_chk, is_image, print_key, print_error,
                interactive_view, interactive_cui, show_image_file,
                run_system_cmd, help_template,
                add_args_imageviewer, add_args_output, add_args_specification
                )
from .. import ReturnMessage as RM
from pymeflib.tree2 import GC, branch_str, show_tree
logger = getLogger(GLOBAL_CONF.logname)


class LocalArgs(Args):
    ask_password: bool


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
            if tmp_dir not in dirs and tmp_dir != '':
                dirs.append(tmp_dir)
        elif z.is_dir():
            if zname not in dirs and zname != '':
                dirs.append(zname)
        else:
            files.append(zname)
    dirs.sort()
    files.sort()
    logger.debug(f'get_contents: {cpath}, dirs: {dirs}, files: {files}')
    return dirs, files


def show_zip(zip_file: zipfile.ZipFile, pwd: None | bytes,
             tmpdir: None | tempfile.TemporaryDirectory,
             args: LocalArgs, get_contents: GC, cpath: str, **kwargs):
    res = []
    try:
        key_name = str(cpath)
        if key_name+'/' in zip_file.namelist():
            key_name += '/'
        zipinfo = zip_file.getinfo(key_name)
    except KeyError as e:
        logger.error(f'failed to open [{cpath}]: {e}')
        return RM(f'Error!! Cannot open {cpath}.', True)

    if args_chk(args, 'output') and args_chk(args, 'key'):
        outpath = Path(args.output)
        logger.info(f'out key: {cpath}')
        if not outpath.parent.is_dir():
            outpath.parent.mkdir(parents=True)
        for item in zip_file.namelist():
            logger.debug(f'checking;; {item}')
            if cpath == item:
                logger.info(f'  find1; {item}')
                zip_file.extract(zip_file.getinfo(item), path=outpath, pwd=pwd)
            elif cpath in [str(x) for x in PurePosixPath(item).parents]:
                logger.info(f'  find2; {item}')
                zip_file.extract(zip_file.getinfo(item), path=outpath, pwd=pwd)
        return RM(f'file is saved to {outpath/cpath}', False)

    assert tmpdir is not None, "something strange; tmpdir is not set."
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
            zip_file.extract(zipinfo, path=tmpdir.name, pwd=pwd)
            tmpfile = os.path.join(tmpdir.name, cpath)
            ret1 = run_system_cmd(tmpfile)
            if ret1:
                return RM('open {}'.format(cpath), False)
            else:
                return RM('Failed to open {}.'.format(cpath), True)
        elif is_image(key_name):
            zip_file.extract(zipinfo, path=tmpdir.name, pwd=pwd)
            tmpfile = os.path.join(tmpdir.name, cpath)
            ret2 = show_image_file(tmpfile, args)
            if ret2 is None:
                msg = 'image viewer not found.'
                if args_chk(args, 'cui'):
                    msg += '\nNOTE: external command is not supported' + \
                        ' in CUI mode.'
                return RM(msg, True)
            elif not ret2:
                return RM('Failed to show image.', True)

        # text file?
        else:
            for line in zip_file.open(key_name, 'r', pwd=pwd):
                try:
                    res.append(line.decode().replace("\n", ''))
                except UnicodeDecodeError as e:
                    return RM('Error!! {}'.format(e), True)

    return RM('\n'.join(res), False)


def add_args(parser):
    add_args_imageviewer(parser)
    parser.add_argument('--ask_password', '-p',
                        help='ask for the password for the file if needed.',
                        action='store_true',
                        )
    add_args_output(parser, help='Output files to the specified directory.'
                    ' NOTE: --output works only with --key.')
    kwargs_k = dict(help='Specify the file/directory path to show.'
                    ' If no key is provided, return the list of files.')
    add_args_specification(parser, verbose=True, key=True,
                           interactive=True, cui=True,
                           kwargs_k=kwargs_k)


def show_help():
    helpmsg = help_template('zip', 'show the contents of a zip file.' +
                            ' NOTE: --output works only with --key.',
                            add_args)
    print(helpmsg)


def main(fpath: str, args: LocalArgs):
    if not zipfile.is_zipfile(fpath):
        print('{} is not a zip file.'.format(fpath))
        return
    zip_file = zipfile.ZipFile(fpath, 'r')
    need_tmp = (args_chk(args, 'key') and not args_chk(args, 'output')) or \
        args_chk(args, 'interactive') or args_chk(args, 'cui')
    if need_tmp:
        tmpdir = tempfile.TemporaryDirectory()
        logger.debug(f'set tmp dir: {tmpdir.name}')
    else:
        tmpdir = None
        logger.debug('do not set tmp dir')
    fname = os.path.basename(fpath)
    gc = partial(get_contents, zip_file)
    if args.ask_password:
        pwd = get_pwd()
    else:
        pwd = None
    sf = partial(show_zip, zip_file, pwd, tmpdir, args, gc)

    if args_chk(args, 'output'):
        if not args_chk(args, 'key') or len(args.key) == 0:
            print('output is specified but key is not specified')
            return

    if args_chk(args, 'interactive'):
        interactive_view(fname, gc, sf, PurePosixPath)
    elif args_chk(args, 'cui'):
        interactive_cui(fpath, gc, sf, PurePosixPath)
    elif args_chk(args, 'key'):
        if len(args.key) == 0:
            for fy in zip_file.namelist():
                print(fy)
            return
        for k in args.key:
            print_key(k)
            info = show_zip(zip_file, pwd, tmpdir, args, gc, k)
            if not info.error:
                print(info.message)
                print()
            else:
                print_error(info.message)
    elif args_chk(args, 'verbose'):
        zip_file.printdir()
    else:
        show_tree(fname, gc, logger=logger, purepath=PurePosixPath)

    zip_file.close()
    if need_tmp:
        tmpdir.cleanup()
        logger.debug('close tmpdir')
