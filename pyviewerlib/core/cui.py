import sys
import re
import curses
from functools import partial
from curses.textpad import Textbox, rectangle
from pathlib import Path, PurePath

sys.path.append(str(Path(__file__).parent.parent.parent))
from pymeflib.tree2 import TreeViewer

curses_debug = False


def editer_cmd(key):
    if key == 10:       # Enter
        return 7        # Ctrl-G
    elif key == 127:    # back space
        return 263      # Ctrl-h
    else:
        return key


def get_all_items(tree_view):
    res_dirs = []
    res_files = []
    tv = TreeViewer('.', tree_view.get_contents)
    for cpath, dirs, files in tv:
        res_dirs += [str(cpath/d) for d in dirs]
        res_files += [str(cpath/f) for f in files]
    return res_dirs, res_files


def curses_main(fname, show_func, cpath, tv, stdscr):
    # clear screen
    stdscr.clear()
    winy, winx = stdscr.getmaxyx()
    win_h = 3   # height of top window
    win_w = int(winx*3/10)  # width of side bar
    search_h = 1    # height of search window
    scroll_h = 5
    scroll_w = 5
    scroll_side = 3
    exp = 'q:quit ↑↓←→:select shift+↑:go back enter:open jkhl:scroll /:search'
    if winx <= len(exp)+1:
        raise AssertionError(winx, len(exp)+1)
    win_pwd = curses.newwin(win_h, winx, 0, 0)
    win_side = curses.newwin(winy-win_h, win_w, win_h, 0)
    win_main = curses.newwin(winy-win_h, winx-win_w, win_h, win_w)
    win_search = curses.newwin(search_h, winx-win_w-2, win_h+2, win_w+1)
    # |                        | ^
    # |                        | | win_h
    # |________________________| v
    # |      |                 | ^
    # |      |                 | |
    # |      |                 | | winy-win_h
    # |      |                 | |
    # |      |                 | v
    #  <----> <--------------->
    #  win_w     winx-win_w

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
    dirs, files = tv.get_contents(cpath)
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
                dirs, files = tv.get_contents(cpath)
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
                dirs, files = tv.get_contents(cpath)
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
                dirs, files = tv.get_contents(cpath)
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
                tmp_dirs, tmp_files = get_all_items(tv)
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
                   'KEY_SR', 'KEY_SUP', "\n", 'KEY_ENTER']:
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

        if key in ['', "\n", 'KEY_ENTER', 'KEY_SR', 'KEY_SUP',
                   'j', 'k', 'h', 'l']:
            # main window
            win_main.clear()
            win_main.addstr(0, 0, sel_cont, curses.A_REVERSE)
            if len(sel_cont) != 0:
                if winx-win_w > len(sel_cont)+2:
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
                        win_main.addstr(i, 0, "!! {}".format(e),
                                        curses.color_pair(3))
            else:
                win_main.addstr(1, 0, main_err, curses.color_pair(3))
            win_main.refresh()

        if key in ['', "\n", 'KEY_ENTER', 'KEY_SR', 'KEY_SUP']:
            # top, print-working-directory window
            win_pwd.clear()
            win_pwd.addstr(0, 3, 'file: {}'.format(fname), curses.A_BOLD)
            win_pwd.addstr(1, 5, 'current path: {}'.format(str(cpath)))
            win_pwd.addstr(2, 1, exp)
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


def interactive_cui(fname, get_contents, show_func):
    # should be imported after set_param.
    from . import debug
    global curses_debug
    curses_debug = debug
    cpath = PurePath('.')
    tv = TreeViewer('.', get_contents)
    try:
        curses.wrapper(partial(curses_main, fname, show_func, cpath, tv))
    except AssertionError as e:
        winx, lenexp = e.args
        print('Window width should be larger than {:d} (current: {:d})'.format(lenexp, winx))
