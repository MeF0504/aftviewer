import sys
import platform
import subprocess
from pathlib import Path, PurePath

sys.path.append(str(Path(__file__).parent.parent.parent))
from pymeflib.color import FG, BG, END
from pymeflib.tree2 import TreeViewer


debug = False
json_opts = {}


def set_param(args):
    global debug
    global json_opts
    debug = args.debug
    json_opts = args.opts


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
                info, err = show_func(str(cpath/key_name), False)
                if err is None:
                    print("\n".join(info))
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
    if 'system_cmd' in json_opts:
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

    stat = subprocess.run(res)
    if stat.returncode != 0:
        return False
    else:
        return True
