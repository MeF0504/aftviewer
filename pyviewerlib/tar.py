import os
import tarfile
import tempfile
import platform
from functools import partial

from . import args_chk, print_key, cprint, debug_print, get_image_viewer,\
    is_image, interactive_view, interactive_cui, show_image_file
from pymeflib.tree import branch_str, tree_viewer, show_tree


def show_tar(tar_file, list_tree, args, cpath, cui=False):
    res = []
    img_viewer = get_image_viewer(args)
    # check cpath
    try:
        if cpath.endswith('/'):
            key_name = cpath[:-1]
        else:
            key_name = cpath
        if platform.system() == "Windows":
            key_name = key_name.replace('\\', '/')
        tarinfo = tar_file.getmember(key_name)
    except KeyError as e:
        debug_print(e)
        return [], 'Error!! Cannot open {}.'.format(cpath)

    # file
    if tarinfo.isfile():

        # image file
        if is_image(key_name):
            cond = cui and (img_viewer not in ['PIL', 'matplotlib', 'OpenCV'])
            with tempfile.TemporaryDirectory() as tmpdir:
                tar_file.extractall(path=tmpdir, members=[tarinfo])
                tmpfile = os.path.join(tmpdir, cpath)
                ret = show_image_file(tmpfile, args, cond)
            if not ret:
                return [], 'Failed to show image.'

        # text file?
        else:
            for line in tar_file.extractfile(key_name):
                try:
                    res.append(line.decode().replace("\n", ''))
                except UnicodeDecodeError as e:
                    return [], 'Error!! {}'.format(e)
        res.append('')

    # directory
    elif tarinfo.isdir():
        tree = tree_viewer(list_tree, tar_file.name)
        res.append('{}/'.format(key_name))
        files, dirs = tree.get_contents(key_name)
        for f in files:
            res.append('{}{}'.format(branch_str, f))
        for d in dirs:
            res.append('{}{}/'.format(branch_str, d))
    else:
        res.append('sorry, I can\'t show information.\n')

    return res, None


def main(fpath, args):
    if not tarfile.is_tarfile(fpath):
        print('{} is not a tar file.'.format(fpath))
        return
    tar_file = tarfile.open(fpath, 'r:*')
    list_tree = [{}]
    fname = os.path.basename(fpath)

    # make list_tree
    for t in tar_file:
        tmp_list = list_tree
        depth = 1
        tnames = t.name.split('/')
        debug_print('cpath: {}'.format(t.name))
        for p in tnames:
            if p == '':
                continue
            if t.isfile() and depth == len(tnames):
                # file
                tmp_list.append(p)
                debug_print('add {}'.format(p))
            elif p in tmp_list[0]:
                # existing directory
                tmp_list = tmp_list[0][p]
                depth += 1
            else:
                # new directory
                tmp_list[0][p] = [{}]
                tmp_list = tmp_list[0][p]
                depth += 1

    if args_chk(args, 'interactive'):
        interactive_view(list_tree, fname,
                         partial(show_tar, tar_file, list_tree, args))
    elif args_chk(args, 'cui'):
        interactive_cui(list_tree, fpath,
                        partial(show_tar, tar_file, list_tree, args))
    elif args_chk(args, 'key'):
        if len(args.key) == 0:
            tar_file.list(verbose=False)
        for k in args.key:
            print_key(k)
            info, err = show_tar(tar_file, list_tree, args, k)
            if err is None:
                print("\n".join(info))
                print()
            else:
                cprint(err, fg='r')
    elif args_chk(args, 'verbose'):
        tar_file.list(verbose=True)
    else:
        show_tree(list_tree, fname)

    tar_file.close()
