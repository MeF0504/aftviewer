import os
import tarfile
import tempfile
import subprocess
from functools import partial

from . import get_exec_cmds, args_chk, print_key, cprint, debug_print,\
    get_image_viewer, is_image, clear_mpl_axes,\
    interactive_view, interactive_cui
from libtree import branch_str, tree_viewer, show_tree


def show_tar(tar_file, list_tree, args, cpath, cui=False):
    img_viewer, mod = get_image_viewer(args)

    res = []
    # check cpath
    try:
        if cpath.endswith('/'):
            key_name = cpath[:-1]
        else:
            key_name = cpath
        tarinfo = tar_file.getmember(key_name)
    except KeyError:
        return [], 'Error!! Cannot open {}.'.format(cpath)

    # file
    if tarinfo.isfile():

        # image file
        if is_image(cpath):
            if img_viewer is None:
                return [], 'There are no way to show image.'
            elif img_viewer == 'PIL':
                Image = mod
                with Image.open(tar_file.extractfile(cpath)) as img:
                    img.show(title=os.path.basename(cpath))
            elif img_viewer == 'matplotlib':
                plt = mod
                with tempfile.TemporaryDirectory() as tmpdir:
                    tar_file.extractall(path=tmpdir, members=[tarinfo])
                    tmpfile = os.path.join(tmpdir, cpath)
                    img = plt.imread(tmpfile)
                fig1 = plt.figure()
                ax11 = fig1.add_axes((0, 0, 1, 1))
                ax11.imshow(img)
                clear_mpl_axes(ax11)
                plt.show()
            elif img_viewer == 'OpenCV':
                cv2 = mod
                with tempfile.TemporaryDirectory() as tmpdir:
                    tar_file.extractall(path=tmpdir, members=[tarinfo])
                    tmpfile = os.path.join(tmpdir, cpath)
                    img = cv2.imread(tmpfile)
                cv2.imshow(os.path.basename(cpath), img)
                cv2.waitKey(0)
                # cv2.destroyAllWindows()
            else:
                if cui:
                    return [], 'external command is not supported in cui mode.'
                with tempfile.TemporaryDirectory() as tmpdir:
                    tar_file.extractall(path=tmpdir, members=[tarinfo])
                    tmpfile = os.path.join(tmpdir, cpath)
                    cmds = get_exec_cmds(args, tmpfile)
                    subprocess.run(cmds)
                    # wait to open file. this is for, e.g., open command on Mac OS.
                    input('Press Enter to continue')

        # text file?
        else:
            for line in tar_file.extractfile(cpath):
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
