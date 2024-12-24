from __future__ import annotations

import os
import tarfile
import tempfile
from functools import partial
from pathlib import Path, PurePosixPath
from logging import getLogger

from .. import (GLOBAL_CONF, Args, args_chk, print_key, print_error,
                is_image, interactive_view, interactive_cui,
                show_image_file, run_system_cmd, help_template,
                add_args_imageviewer, add_args_output, add_args_specification
                )
from .. import ReturnMessage as RM
from pymeflib.tree2 import GC, branch_str, show_tree
logger = getLogger(GLOBAL_CONF.logname)


def show_tar(tar_file: tarfile.TarFile,
             tmpdir: None | tempfile.TemporaryDirectory,
             args: Args, get_contents: GC, cpath: str, **kwargs):
    res = []
    # check cpath
    try:
        if cpath.endswith('/'):
            key_name = cpath[:-1]
        else:
            key_name = cpath
        tarinfo = tar_file.getmember(key_name)
    except KeyError as e:
        logger.error(f'failed to open [{cpath}]: {e}')
        return RM(f'Error!! Cannot open {cpath}.', True)

    if args_chk(args, 'output') and args_chk(args, 'key'):
        outpath = Path(args.output)
        logger.info(f'out key: {cpath}')
        if not outpath.parent.is_dir():
            outpath.parent.mkdir(parents=True)
        for item in tar_file.getmembers():
            logger.debug(f'checking;; {item.name}')
            if cpath == item.name:
                logger.info(f'  find1; {item.name}')
                tar_file.extract(item, path=outpath)
            elif cpath in [str(x) for x in PurePosixPath(item.name).parents]:
                logger.info(f'  find2; {item.name}')
                tar_file.extract(item, path=outpath)
        return RM(f'file is saved to {outpath/cpath}', False)

    assert tmpdir is not None, "something strange; tmpdir is not set."
    if tarinfo.isfile():
        # file
        if 'system' in kwargs and kwargs['system']:
            tar_file.extract(tarinfo, path=tmpdir.name)
            tmpfile = os.path.join(tmpdir.name, cpath)
            ret = run_system_cmd(tmpfile)
            if ret:
                return RM('open {}'.format(cpath), False)
            else:
                return RM('Failed to open {}.'.format(cpath), True)
        elif is_image(key_name):
            tar_file.extract(tarinfo, path=tmpdir.name)
            tmpfile = os.path.join(tmpdir.name, cpath)
            ret = show_image_file(tmpfile, args)
            if ret is None:
                msg = 'image viewer not found.'
                if args_chk(args, 'cui'):
                    msg += '\nNOTE: external command is not supported' + \
                        ' in CUI mode.'
                return RM(msg, True)
            elif not ret:
                return RM('Failed to show image.', True)

        else:
            # text file?
            for line in tar_file.extractfile(key_name):
                try:
                    res.append(line.decode().replace("\n", ''))
                except UnicodeDecodeError as e:
                    return RM('Error!! {}'.format(e), True)
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

    return RM('\n'.join(res), False)


def get_contents(tar_file: tarfile.TarFile, path: PurePosixPath):
    cpath = str(path)
    if cpath == '.':
        lenpath = 0
    else:
        lenpath = len(cpath)+1
    files = []
    dirs = []
    for t in tar_file.getmembers():
        tpath = PurePosixPath(t.name)
        if lenpath != 0:  # not root
            if t.name == cpath:
                continue
            if path not in tpath.parents:
                continue
        tname = t.name[lenpath:]
        if '/' in tname:
            # @ root dir, count "directoly added"(?) files.
            # in some case, directories are not listed?
            tmp_dir = tname.split('/')[0]
            if tmp_dir not in dirs:
                dirs.append(tmp_dir)
        elif t.isfile():
            files.append(tname)
        elif t.isdir():
            dirs.append(tname)
    dirs.sort()
    files.sort()
    return dirs, files


def add_args(parser):
    add_args_imageviewer(parser)
    add_args_output(parser, help='Output files to the specified directory.'
                    ' NOTE: --output works only with --key.')
    kwargs_k = dict(help='Specify the file/directory path to show.'
                    ' If no key is provided, return the list of files.')
    add_args_specification(parser, verbose=True, key=True,
                           interactive=True, cui=True,
                           kwargs_k=kwargs_k)


def show_help():
    helpmsg = help_template('tar', 'show the contents of a tar file.'
                            ' The tar file type is identified by the'
                            ' "tarfile" module, not the extension of a file.',
                            add_args)
    print(helpmsg)


def main(fpath, args):
    if not tarfile.is_tarfile(fpath):
        print('{} is not a tar file.'.format(fpath))
        return
    tar_file = tarfile.open(fpath, 'r:*')
    need_tmp = (args_chk(args, 'key') and not args_chk(args, 'output')) or \
        args_chk(args, 'interactive') or args_chk(args, 'cui')
    if need_tmp:
        tmpdir = tempfile.TemporaryDirectory()
        logger.debug(f'set tmp dir: {tmpdir.name}')
    else:
        tmpdir = None
        logger.debug('do not set tmp dir')
    fname = os.path.basename(fpath)
    gc = partial(get_contents, tar_file)
    sf = partial(show_tar, tar_file, tmpdir, args, gc)

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
            tar_file.list(verbose=False)
        for k in args.key:
            print_key(k)
            info = show_tar(tar_file, tmpdir, args, gc, k)
            if not info.error:
                print(info.message)
                print()
            else:
                print_error(info.message)
    elif args_chk(args, 'verbose'):
        tar_file.list(verbose=True)
    else:
        show_tree(fname, gc, logger=logger, purepath=PurePosixPath)

    tar_file.close()
    if need_tmp:
        tmpdir.cleanup()
        logger.debug('close tmpdir')
