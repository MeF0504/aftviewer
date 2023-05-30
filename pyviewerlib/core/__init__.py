import os
import json
import platform
import subprocess
from pathlib import Path, PurePath

from pymeflib.color import FG, BG, END
from pymeflib.tree2 import TreeViewer


# global variables
debug = False
if 'XDG_CONFIG_HOME' in os.environ:
    conf_dir = Path(os.environ['XDG_CONFIG_HOME'])/'pyviewer'
else:
    conf_dir = Path(os.path.expanduser('~/.config'))/'pyviewer'
if not conf_dir.exists():
    os.makedirs(conf_dir, mode=0o755)

# load config file.
with (Path(__file__).parent/'default.json').open('r') as f:
    json_opts = json.load(f)
if (conf_dir/'setting.json').is_file():
    with open(conf_dir/'setting.json') as f:
        load_opts = json.load(f)
        if 'force_default' in load_opts and load_opts['force_default']:
            load_opts = {}
        for key in json_opts:
            if key in load_opts:
                json_opts[key] = load_opts[key]
    if 'debug' in load_opts:
        debug = bool(load_opts['debug'])
    del load_opts

# set supported file types
type_config = {
    "hdf5": "hdf5",
    "pickle": "pkl pickle",
    "numpy": "npy npz",
    "np_pickle": "",
    "tar": "",  # tar is identified by tarfile module.
    "zip": "zip",
    "sqlite3": "db db3 sqp sqp3 sqlite sqlite3",
    "raw_image": "raw nef nrw cr3 cr2 crw tif arw",  # nikon, canon, sony
    "jupyter": "ipynb",
    "xpm": "xpm",
    "text": "py txt",
}
type_config.update(json_opts['type'])


def debug_print(msg):
    if debug:
        print(msg)


def args_chk(args, attr):
    if not hasattr(args, attr):
        return False
    if attr == 'type':
        return args.type is not None
    elif attr == 'verbose':
        return args.verbose
    elif attr == 'key':
        return args.key is not None
    elif attr == 'interactive':
        return args.interactive
    elif attr == 'image_viewer':
        return args.image_viewer is not None
    elif attr == 'encoding':
        return args.encoding is not None
    elif attr == 'cui':
        return args.cui
    else:
        return False


def show_opts():
    for key, val in json_opts.items():
        if type(val) == dict:
            print_key(key)
            for k2, v2 in val.items():
                print(f'  {k2}: {v2}')
        else:
            print_key(key)
            print(val)


def cprint(str1, str2='', fg=None, bg=None, **kwargs):
    print_str = str1
    if fg is not None:
        print_str = FG[fg]+print_str
    if bg is not None:
        print_str = BG[bg]+print_str
    if (fg is not None) or (bg is not None):
        print_str += END
    print_str += str2
    print(print_str, **kwargs)


def interactive_view(fname, get_contents, show_func):
    cpath = PurePath('.')
    inter_str = "'q':quit, '..':go to parent, key_name:select a key >> "
    tv = TreeViewer('.', get_contents)
    while(True):
        dirs, files = tv.get_contents(cpath)
        dirs.sort()
        files.sort()
        cprint('current path:', ' {}/{}'.format(fname, cpath), bg='c')
        cprint('contents in this dict:', ' ', bg='g', end='')
        for d in dirs:
            print('{}/, '.format(d), end='')
        for f in files:
            print('{}, '.format(f), end='')
        print('\n')
        key_name = input(inter_str)
        if key_name == 'q':
            debug_print('quit')
            break
        elif key_name == '':
            debug_print('continue')
            continue
        elif key_name == '..':
            debug_print('go up')
            if str(cpath) != '.':
                cpath = cpath.parent
        else:
            debug_print('specify key:{}'.format(key_name))
            if key_name.endswith('/'):
                key_name = key_name[:-1]
            if key_name in files:
                cprint('output::', '\n', bg='r')
                info, err = show_func(str(cpath/key_name), cui=False)
                if err is None:
                    print(info)
                else:
                    cprint(err, fg='r')
            elif key_name in dirs:
                cpath /= key_name
            else:
                cprint('"{}" is not a correct name'.format(key_name),
                       '', fg='r')


def print_key(key_name):
    cprint('<<< {} >>>'.format(key_name), '', fg='k', bg='y')


def run_system_cmd(fname):
    if json_opts['system_cmd'] is not None:
        res = []
        for cmd in json_opts['system_cmd']['args']:
            if cmd == '%s':
                res.append(fname)
            elif cmd == '%c':
                res.append(json_opts['system_cmd']['cmd'])
            else:
                res.append(cmd)
    else:
        if platform.system() == 'Windows':
            res = ['start', fname]
        elif platform.uname()[0] == 'Darwin':
            res = ['open', fname]
        elif platform.uname()[0] == 'Linux':
            res = ['xdg-open', fname]
        else:
            print('Unsupported platform')
            return False

    if platform.system() == 'Windows':
        shell = True
    else:
        shell = False
    stat = subprocess.run(res, shell=shell)
    if stat.returncode != 0:
        return False
    else:
        return True


def set_numpy_format(numpy):
    opts = json_opts['numpy_format']
    numpy.set_printoptions(**opts)
