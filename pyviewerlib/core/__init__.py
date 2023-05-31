import os
import json
import platform
import subprocess
from pathlib import Path, PurePath

from pymeflib.color import FG, BG, FG256, BG256, END
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
        for key, val in json_opts.items():
            if key in load_opts:
                # update
                if type(val) is dict:
                    for k2, v2 in val.items():
                        if k2 in load_opts[key]:
                            json_opts[key][k2] = load_opts[key][k2]
                else:
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
    if fg in FG:
        fg_str = FG[fg]
    elif type(fg) == int and 0 <= fg <= 255:
        fg_str = FG256(fg)
    elif fg is None:
        fg_str = ''
    else:
        debug_print(f'incorrect type for fg: {fg}')
        fg_str = ''
    if bg in BG:
        bg_str = BG[bg]
    elif type(bg) == int and 0 <= bg <= 255:
        bg_str = BG256(bg)
    elif bg is None:
        bg_str = ''
    else:
        debug_print(f'incorrect type for bg: {bg}')
        bg_str = ''
    if len(fg_str+bg_str) != 0:
        end_str = END
    else:
        end_str = ''
    print_str = f'{fg_str}{bg_str}{str1}{end_str}{str2}'
    print(print_str, **kwargs)


def get_col(name):
    col_conf = json_opts['color_config']
    if name in col_conf:
        return col_conf[name]
    else:
        debug_print(f'incorrect color set name: {name}')
        return None, None


def interactive_view(fname, get_contents, show_func):
    cpath = PurePath('.')
    inter_str = "'q':quit, '..':go to parent, key_name:select a key >> "
    fg1, bg1 = get_col('interactive_path')
    fg2, bg2 = get_col('interactive_contents')
    fg3, bg3 = get_col('interactive_output')
    fge, bge = get_col('error')
    tv = TreeViewer('.', get_contents)
    while(True):
        dirs, files = tv.get_contents(cpath)
        dirs.sort()
        files.sort()
        cprint('current path:', ' {}/{}'.format(fname, cpath), fg=fg1, bg=bg1)
        cprint('contents in this dict:', ' ', fg=fg2, bg=bg2, end='')
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
                cprint('output::', '\n', fg=fg3, bg=bg3)
                info, err = show_func(str(cpath/key_name), cui=False)
                if err is None:
                    print(info)
                else:
                    cprint(err, fg=fge, bg=bge)
            elif key_name in dirs:
                cpath /= key_name
            else:
                cprint('"{}" is not a correct name'.format(key_name),
                       '', fg=fge, bg=bge)


def print_key(key_name):
    fg, bg = get_col('key_name')
    cprint('<<< {} >>>'.format(key_name), '', fg=fg, bg=bg)


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
