import sys
from pathlib import Path, PurePath

sys.path.append(str(Path(__file__).parent.parent.parent))
from pymeflib.color import FG, BG, END
from pymeflib.tree import tree_viewer


debug = False
json_opts = {}


def set_param(args):
    global debug
    global json_opts
    global curses_debug
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


def interactive_view(tree, fname, show_func):
    cpath = PurePath('.')
    inter_str = "'q':quit, '..':go to parent, key_name:select a key >> "
    tv = tree_viewer(tree, '.')
    while(True):
        files, dirs = tv.get_contents(cpath)
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

