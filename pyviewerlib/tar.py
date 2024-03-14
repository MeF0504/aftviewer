import os
import tarfile
import tempfile
from functools import partial
from pathlib import Path, PurePosixPath
from logging import getLogger

from . import GLOBAL_CONF, args_chk, print_key, cprint, get_image_viewer, \
    is_image, interactive_view, interactive_cui, \
    show_image_file, run_system_cmd, get_col, help_template, ImageViewers, \
    add_args_imageviewer, add_args_output, add_args_specification
from . import ReturnMessage as RM
from pymeflib.tree2 import branch_str, show_tree
logger = getLogger(GLOBAL_CONF.logname)


def show_tar(tar_file, tmpdir, args, get_contents, cpath, **kwargs):
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
        # debug_print(e)
        logger.error(f'failed to open [{cpath}]: {e}')
        return RM('Error!! Cannot open {}.'.format(cpath), True)

    if args_chk(args, 'output') and args_chk(args, 'key'):
        outpath = Path(args.output)
        if not outpath.parent.is_dir():
            outpath.parent.mkdir(parents=True)
        tar_file.extractall(path=outpath, members=[tarinfo])
        return RM(f'file is saved to {outpath/cpath}', False)

    if tarinfo.isfile():
        # file
        if 'system' in kwargs and kwargs['system']:
            tar_file.extractall(path=tmpdir.name, members=[tarinfo])
            tmpfile = os.path.join(tmpdir.name, cpath)
            ret = run_system_cmd(tmpfile)
            if ret:
                return RM('open {}'.format(cpath), False)
            else:
                return RM('Failed to open {}.'.format(cpath), True)
        elif is_image(key_name):
            if img_viewer == 'None':
                return RM('image viewer is None', False)
            if 'cui' in kwargs and kwargs['cui']:
                ava_iv = ImageViewers
                if img_viewer not in ava_iv:
                    return RM('Only {} are supported as an Image viewer in CUI mode. current: "{}"'.format(', '.join(ava_iv), img_viewer), True)
            tar_file.extractall(path=tmpdir.name, members=[tarinfo])
            tmpfile = os.path.join(tmpdir.name, cpath)
            ret = show_image_file(tmpfile, args)
            if not ret:
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


def add_args(parser):
    add_args_imageviewer(parser)
    add_args_output(parser)
    add_args_specification(parser, verbose=True, key=True,
                           interactive=True, cui=True)


def show_help():
    helpmsg = help_template('tar', 'show the contents of a tar file.' +
                            ' The tar file type is identified by the'
                            ' "tarfile" module, not the extension of a file.' +
                            ' NOTE: --output works only with --key.',
                            add_args)
    print(helpmsg)


def main(fpath, args):
    if not tarfile.is_tarfile(fpath):
        print('{} is not a tar file.'.format(fpath))
        return
    tar_file = tarfile.open(fpath, 'r:*')
    tmpdir = tempfile.TemporaryDirectory()
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
        fg, bg = get_col('msg_error')
        if len(args.key) == 0:
            tar_file.list(verbose=False)
        for k in args.key:
            print_key(k)
            info = show_tar(tar_file, tmpdir, args, gc, k)
            if not info.error:
                print(info.message)
                print()
            else:
                cprint(info.message, fg=fg, bg=bg)
    elif args_chk(args, 'verbose'):
        tar_file.list(verbose=True)
    else:
        show_tree(fname, gc, purepath=PurePosixPath)

    tar_file.close()
    tmpdir.cleanup()
