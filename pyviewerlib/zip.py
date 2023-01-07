import os
import zipfile
import tempfile
import platform
from functools import partial

from . import args_chk, is_image, print_key, json_opts, cprint, debug_print,\
    interactive_view, interactive_cui, show_image_file, get_image_viewer
from pymeflib.tree import tree_viewer, branch_str, show_tree


def show_zip(zip_file, list_tree, args, cpath, cui=False):
    res = []
    img_viewer = get_image_viewer(args)
    try:
        key_name = cpath
        if key_name+'/' in zip_file.namelist():
            key_name += '/'
        if platform.system() == "Windows":
            key_name = key_name.replace('\\', '/')
        zipinfo = zip_file.getinfo(key_name)
    except KeyError as e:
        debug_print(e)
        return [], 'Error!! cannot open {}.'.format(cpath)

    # directory
    if zipinfo.is_dir():
        tree = tree_viewer(list_tree, zip_file.filename)
        res.append('{}/'.format(key_name))
        files, dirs = tree.get_contents(key_name)
        for f in files:
            res.append('{}{}'.format(branch_str, f))
        for d in dirs:
            res.append('{}{}/'.format(branch_str, d))

    # file
    else:
        if is_image(cpath):
            cond = cui and (img_viewer not in ['PIL', 'matplotlib', 'OpenCV'])
            with tempfile.TemporaryDirectory() as tmpdir:
                zip_file.extract(zipinfo, path=tmpdir)
                tmpfile = os.path.join(tmpdir, cpath)
                ret = show_image_file(tmpfile, args, cond)
            if not ret:
                return [], 'Failed to show image.'

        # text file?
        else:
            for line in zip_file.open(cpath, 'r'):
                try:
                    res.append(line.decode().replace("\n", ''))
                except UnicodeDecodeError as e:
                    return [], 'Error!! {}'.format(e)

    return res, None


def main(fpath, args):
    if not zipfile.is_zipfile(fpath):
        print('{} is not a zip file.'.format(fpath))
        return
    zip_file = zipfile.ZipFile(fpath, 'r')
    list_tree = [{}]
    fname = os.path.basename(fpath)

    # make list_tree
    if args_chk(args, 'encoding'):
        debug_print('set encoding from args')
        zip_codec = args.encoding
    elif 'zip_encoding' in json_opts:
        debug_print('set encoding from args')
        zip_codec = json_opts['zip_encoding']
    else:
        zip_codec = 'cp437'  # test codec.
    debug_print('encoding: {}'.format(zip_codec))
    for z in zip_file.infolist():
        tmp_list = list_tree
        depth = 1
        znames = z.filename.split('/')
        debug_print('cpath: {}'.format(z.filename))
        for p in znames:
            try:
                # try to decode
                p = p.encode(zip_codec, 'replace').decode()
            except Exception as e:
                debug_print(e)
            if p == '':
                continue
            if (not z.is_dir()) and depth == len(znames):
                # file
                tmp_list.append(p)
                debug_print('add {}'.format(p))
            elif p in tmp_list[0]:
                # existing directory
                tmp_list = tmp_list[0][p]
                depth += 1
            else:
                tmp_list[0][p] = [{}]
                tmp_list = tmp_list[0][p]
                depth += 1

    if args_chk(args, 'interactive'):
        interactive_view(list_tree, fname,
                         partial(show_zip, zip_file, list_tree, args))
    elif args_chk(args, 'cui'):
        interactive_cui(list_tree, fpath,
                        partial(show_zip, zip_file, list_tree, args))
    elif args_chk(args, 'key'):
        if len(args.key) == 0:
            for fy in zip_file.namelist():
                print(fy)
        for k in args.key:
            print_key(k)
            info, err = show_zip(zip_file, list_tree, args, k)
            if err is None:
                print("\n".join(info))
                print()
            else:
                cprint(err, fg='r')
    elif args_chk(args, 'verbose'):
        zip_file.printdir()
    else:
        show_tree(list_tree, fname)

    zip_file.close()
