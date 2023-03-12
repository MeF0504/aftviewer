import os
import sys
import re
import mimetypes
import tempfile
import subprocess
from pathlib import Path, PurePath
from functools import partial

try:
    from screeninfo import get_monitors
except ImportError:
    get_screen = False
else:
    get_screen = True

sys.path.append(str(Path(__file__).parent.parent))
from pymeflib.color import FG, BG, END, make_bitmap
from pymeflib.tree import tree_viewer, get_list
from pymeflib.util import chk_cmd


debug = False
curses_debug = False
json_opts = {}

# image viewer
Image = None
plt = None
cv2 = None
img_viewer = None
run_giv = False


def set_param(args):
    global debug
    global json_opts
    global curses_debug
    debug = args.debug
    json_opts = args.opts
    curses_debug = args.curses_debug


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


def is_image(path):
    mime = mimetypes.guess_type(path)[0]
    if mime is None:
        return False
    elif mime.split('/')[0] == 'image':
        return True
    else:
        return False


def get_image_viewer(args):
    global img_viewer
    global run_giv
    if run_giv:
        return img_viewer
    global Image
    global plt
    global cv2
    if args_chk(args, 'image_viewer'):
        debug_print('set image viewer from args')
        img_viewer = args.image_viewer
        if img_viewer == 'PIL':
            from PIL import Image
        elif img_viewer == 'matplotlib':
            import matplotlib.pyplot as plt
        elif img_viewer == 'OpenCV':
            import cv2
        else:
            # external command
            if not chk_cmd(img_viewer, debug):
                img_viewer = None
    else:
        debug_print('search available image_viewer')
        try:
            from PIL import Image
            debug_print(' => image_viewer: PIL')
        except ImportError:
            try:
                import matplotlib.pyplot as plt
                debug_print(' => image_viewer: matplotlib')
            except ImportError:
                try:
                    import cv2
                    debug_print(' => image_viewer: OpenCV')
                except ImportError:
                    debug_print("can't find image_viewer")
                    img_viewer = None
                else:
                    img_viewer = 'OpenCV'
            else:
                img_viewer = 'matplotlib'
        else:
            img_viewer = 'PIL'
    run_giv = True
    return img_viewer


def clear_mpl_axes(axes):
    # not display axes
    axes.xaxis.set_visible(False)
    axes.yaxis.set_visible(False)
    axes.spines['top'].set_visible(False)
    axes.spines['bottom'].set_visible(False)
    axes.spines['right'].set_visible(False)
    axes.spines['left'].set_visible(False)


def get_exec_cmds(args, fname):
    if 'exec_cmd' in json_opts:
        res = []
        for cmd in json_opts['exec_cmd']:
            if cmd == '%s':
                res.append(fname)
            elif cmd == '%c':
                res.append(args.image_viewer)
            else:
                res.append(cmd)
    else:
        res = [args.image_viewer, fname]
    debug_print('executed command: {}'.format(res))
    return res


def show_image_file(img_file, args, disable_cond=False):
    name = os.path.basename(img_file)
    img_viewer = get_image_viewer(args)
    debug_print('  use {}'.format(img_viewer))
    if disable_cond:
        return False
    if not os.path.isfile(img_file):
        debug_print('image file {} in not found'.format(img_file))
        return False
    if img_viewer is None:
        print("I can't find any libraries to show image. Please install Pillow or matplotlib.")
        return False
    elif img_viewer == 'PIL':
        with Image.open(img_file) as image:
            image.show(title=name)
    elif img_viewer == 'matplotlib':
        img = plt.imread(img_file)
        fig1 = plt.figure()
        ax11 = fig1.add_axes((0, 0, 1, 1))
        ax11.imshow(img)
        clear_mpl_axes(ax11)
        plt.show()
        plt.close(fig1)
    elif img_viewer == 'OpenCV':
        img = cv2.imread(img_file)
        cv2.imshow(name, img)
        cv2.waitKey(0)
        cv2.destroyWindow(name)
    else:
        cmds = get_exec_cmds(args, img_file)
        subprocess.run(cmds)
        # wait to open file. this is for, e.g., open command on Mac OS.
        input('Press Enter to continue')
    return True


def show_image_ndarray(data, name, args, disable_cond=False):
    img_viewer = get_image_viewer(args)
    debug_print('{}\n  use {}'.format(data.shape, img_viewer))
    if disable_cond:
        return False
    if img_viewer is None:
        print("I can't find any libraries to show image. Please install Pillow or matplotlib.")
        return False
    elif img_viewer == 'PIL':
        with Image.fromarray(data) as image:
            image.show(title=name)
    elif img_viewer == 'matplotlib':
        if get_screen:
            height = get_monitors()[0].height
        else:
            height = 540
        rate = data.shape[0]/height*100
        h = int(data.shape[0]/rate)
        w = int(data.shape[1]/rate)
        fig1 = plt.figure(figsize=(w, h))
        # full display
        ax1 = fig1.add_axes((0, 0, 1, 1))
        ax1.imshow(data)
        clear_mpl_axes(ax1)
        plt.show()
        plt.close(fig1)
    elif img_viewer == 'OpenCV':
        if data.shape[2] == 3:
            img = data[:, :, ::-1]  # RGB -> BGR
        elif data.shape[2] == 4:
            img = data[:, :, [2, 1, 0, 3]]  # RGBA -> BGRA
        else:
            print('invalid data shape')
            return False
        cv2.imshow(name, img)
        cv2.waitKey(0)
        cv2.destroyWindow(name)
    else:
        with tempfile.NamedTemporaryFile(suffix='.bmp') as tmp:
            make_bitmap(tmp.name, data, verbose=debug)
            cmds = get_exec_cmds(args, tmp.name)
            subprocess.run(cmds)
            # wait to open file. this is for, e.g., open command on Mac OS.
            input('Press Enter to continue')
    return True


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


def interactive_cui(tree, fname, show_func):
    import curses
    from curses.textpad import Textbox, rectangle
    cpath = PurePath('.')
    tv = tree_viewer(tree, '.')

    def editer_cmd(key):
        if key == 10:       # Enter
            return 7        # Ctrl-G
        elif key == 127:    # back space
            return 263      # Ctrl-h
        else:
            return key

    def curses_main(cpath, tv, stdscr):
        # clear screen
        stdscr.clear()
        winy, winx = stdscr.getmaxyx()
        win_h = 3   # height of top window
        win_w = int(winx*3/10)  # width of side bar
        search_h = 1    # height of search window
        scroll_h = 5
        scroll_w = 5
        scroll_side = 3
        win_pwd = curses.newwin(win_h, winx, 0, 0)
        win_side = curses.newwin(winy-win_h, win_w, win_h, 0)
        win_main = curses.newwin(winy-win_h, winx-win_w, win_h, win_w)
        win_search = curses.newwin(search_h, winx-win_w-2, win_h+2, win_w+1)

        # pwd background
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_GREEN)
        # bar background
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
        # error
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        # file info
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        # dir index
        curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_WHITE)
        # file index
        curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_WHITE)
        win_pwd.bkgd(' ', curses.color_pair(1))
        win_side.bkgd(' ', curses.color_pair(2))

        sel_idx = 0
        side_shift_ud = 0
        side_shift_lr = 0
        files, dirs = tv.get_contents(cpath)
        contents = dirs+files

        main_info = []
        main_err = None
        main_shift_ud = 0
        main_shift_lr = 0
        sel_cont = ''

        key = ''
        search_word = ''
        is_search = False
        stdscr.refresh()
        while key != 'q':
            # showed indices are side_shift_ud ~ side_shift_ud+(winy-win_h)

            if key == 'KEY_DOWN':
                if len(contents) <= winy-win_h:
                    # all contents are shown
                    if sel_idx < len(contents)-1:
                        sel_idx += 1
                elif side_shift_ud+(winy-win_h) < len(contents):
                    # not bottom
                    sel_idx += 1
                    if sel_idx >= side_shift_ud+(winy-win_h):
                        side_shift_ud += 1
                else:
                    # bottom
                    if sel_idx < len(contents)-1:
                        sel_idx += 1

            elif key == 'KEY_UP':
                if len(contents) <= winy-win_h:
                    # all contents are shown
                    if sel_idx > 0:
                        sel_idx -= 1
                elif side_shift_ud > 0:
                    # not top
                    sel_idx -= 1
                    if sel_idx <= side_shift_ud:
                        side_shift_ud -= 1
                else:
                    # top
                    if sel_idx > 0:
                        sel_idx -= 1

            elif key == 'KEY_RIGHT':
                side_shift_lr += scroll_side

            elif key == 'KEY_LEFT':
                if side_shift_lr < scroll_side:
                    side_shift_lr = 0
                else:
                    side_shift_lr -= scroll_side

            elif key in ['KEY_SR', 'KEY_SUP']:
                if is_search:
                    files, dirs = tv.get_contents(cpath)
                    sel_idx = 0
                    side_shift_ud = 0
                    side_shift_lr = 0
                    main_info = []
                    main_err = None
                    main_shift_ud = 0
                    main_shift_lr = 0
                    sel_cont = ''
                    search_word = ''
                    is_search = False
                elif str(cpath) != '.':
                    cpath = cpath.parent
                    files, dirs = tv.get_contents(cpath)
                    sel_idx = 0
                    side_shift_ud = 0
                    side_shift_lr = 0
                    main_info = []
                    main_err = None
                    main_shift_ud = 0
                    main_shift_lr = 0
                    sel_cont = ''
                    search_word = ''

            elif key in ["\n", 'KEY_ENTER']:
                sel_cont = contents[sel_idx]
                if sel_cont in dirs:
                    if is_search:
                        cpath = PurePath(sel_cont)
                    else:
                        cpath = cpath/sel_cont
                    files, dirs = tv.get_contents(cpath)
                    main_info = []
                    main_shift_ud = 0
                    main_shift_lr = 0
                    sel_idx = 0
                    side_shift_ud = 0
                    side_shift_lr = 0
                    sel_cont = ''
                    search_word = ''
                    is_search = False
                else:
                    if is_search:
                        fpath = sel_cont
                    else:
                        fpath = str(cpath/sel_cont)
                    main_info, main_err = show_func(fpath, True)
                    main_info = "\n".join(main_info).split("\n")
                    main_info = [ln.replace("\t", "  ") for ln in main_info]
                    main_shift_ud = 0
                    main_shift_lr = 0

            elif key == 'j':
                if len(main_info) < (winy-win_h-1):
                    # all contents are shown
                    pass
                elif main_shift_ud < len(main_info)-scroll_h-1:
                    main_shift_ud += scroll_h

            elif key == 'k':
                if len(main_info) < (winy-win_h-1):
                    # all contents are shown
                    pass
                elif main_shift_ud < scroll_h:
                    main_shift_ud = 0
                else:
                    main_shift_ud -= scroll_h

            elif key == 'l':
                main_shift_lr += scroll_w

            elif key == 'h':
                if main_shift_lr < scroll_w:
                    main_shift_lr = 0
                else:
                    main_shift_lr -= scroll_w

            elif key == '/':
                # search mode
                win_main.clear()
                win_main.addstr(0, 0, 'search word: (empty cancel)',
                                curses.A_REVERSE)
                rectangle(win_main, 1, 0, search_h+2, winx-win_w-1)
                win_main.refresh()
                win_search.clear()
                box = Textbox(win_search)
                box.edit(editer_cmd)
                search_word = box.gather()
                search_word = search_word.replace("\n", '').replace(" ", '')
                if len(search_word) == 0:
                    win_main.clear()
                    win_main.refresh()
                else:
                    old_files = files.copy()
                    old_dirs = dirs.copy()
                    tmp_files, tmp_dirs = get_list(tree)
                    files = []
                    dirs = []
                    for i, f in enumerate(tmp_files):
                        if re.search(search_word, f):
                            files.append(f)
                    for i, d in enumerate(tmp_dirs):
                        if re.search(search_word, d):
                            dirs.append(d)
                    if len(files)+len(dirs) != 0:
                        is_search = True
                        sel_idx = 0
                        side_shift_ud = 0
                        side_shift_lr = 0
                        main_info = []
                        main_err = None
                        main_shift_ud = 0
                        main_shift_lr = 0
                        sel_cont = ''
                        search_word = ''
                    else:
                        files = old_files
                        dirs = old_dirs
                    key = ''

            contents = dirs+files
            if key in ['', 'KEY_UP', 'KEY_DOWN',
                       'KEY_LEFT', 'KEY_RIGHT',
                       'KEY_SR', 'KEY_SUR', "\n", 'KEY_ENTER']:
                # side bar window
                win_side.clear()
                for i in range(winy-win_h):
                    if i+side_shift_ud >= len(contents):
                        break
                    cont = contents[i+side_shift_ud]
                    cidx = '{:2d} '.format(i+side_shift_ud)
                    if cont in dirs:
                        win_side.addstr(i, 0, cidx, curses.color_pair(5))
                        attr = curses.A_BOLD
                    elif cont in files:
                        win_side.addstr(i, 0, cidx, curses.color_pair(6))
                        attr = curses.A_NORMAL
                    cont = cont[side_shift_lr:side_shift_lr+win_w-len(cidx)-1]
                    if i+side_shift_ud == sel_idx:
                        win_side.addstr(i, len(cidx), cont, curses.A_REVERSE)
                    else:
                        win_side.addstr(i, len(cidx), cont, attr)
                win_side.refresh()

            if key in ['', "\n", 'KEY_ENTER', 'KEY_SR', 'j', 'k', 'h', 'l']:
                # main window
                win_main.clear()
                win_main.addstr(0, 0, sel_cont, curses.A_REVERSE)
                if len(sel_cont) != 0:
                    win_main.addstr(0, len(sel_cont)+2,
                                    '{}/{}'.format(main_shift_ud+1,
                                                   len(main_info)),
                                    curses.color_pair(4))
                if main_err is None:
                    for i in range(1, winy-win_h):
                        if i-1+main_shift_ud >= len(main_info):
                            break
                        info = main_info[i-1+main_shift_ud][main_shift_lr:main_shift_lr+winx-win_w-2]
                        if curses_debug:
                            info = "{:d} ".format(i+main_shift_ud)+info
                        try:
                            win_main.addstr(i, 0, info)
                        except Exception as e:
                            win_main.addstr(i, 0, "!! {}".format(e))
                else:
                    win_main.addstr(1, 0, main_err, curses.color_pair(3))
                win_main.refresh()

            if key in ['', "\n", 'KEY_ENTER', 'KEY_SR']:
                # top, print-working-directory window
                win_pwd.clear()
                win_pwd.addstr(0, 3, 'file: {}'.format(fname), curses.A_BOLD)
                win_pwd.addstr(1, 5, 'current path: {}'.format(str(cpath)))
                win_pwd.addstr(2, 1, 'q:quit ↑↓←→:select shift+↑:go back enter:open jkhl:scroll /:search')
                win_pwd.refresh()

            if curses_debug:
                win_pwd.addstr(0, int(winx*2/3), ' '*(int(winx/3)-1))
                win_pwd.addstr(0, int(winx*2/3),
                               '{}x{} {}x{} {}x{} k:{}'.format(
                                   win_h, winx, winy-win_h, win_w,
                                   winy-win_h, winx-win_w, key))
                win_pwd.addstr(1, int(winx*2/3), ' '*(int(winx/3)-1))
                win_pwd.addstr(1, int(winx*2/3),
                               's:{}-{}-{}-{} m:{}-{}-{}'.format(
                                   len(contents),
                                   side_shift_ud, side_shift_lr, sel_idx,
                                   len(main_info),
                                   main_shift_ud, main_shift_lr))
                win_pwd.addstr(2, int(winx*2/3), ' '*(int(winx/3)-1))
                win_pwd.addstr(2, int(winx*2/3),
                               'srch: {}'.format(search_word.replace("\n", '')[:int(winx/3)-1-6]))
                win_pwd.refresh()

            key = stdscr.getkey()

    curses.wrapper(partial(curses_main, cpath, tv))


def print_key(key_name):
    cprint('<<< {} >>>'.format(key_name), '', fg='k', bg='y')
