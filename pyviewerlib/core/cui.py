import re
import curses
from curses.textpad import Textbox, rectangle
from pathlib import PurePath, Path
from typing import Callable, List

from pymeflib.tree2 import TreeViewer
from . import debug, conf_dir
curses_debug = debug

help_str = '''
key   function
(S- means shift+key)
q     quit
?     show this help
↓     select items (1 down)
J     select items (1 down)
↑     select items (1 up)
K     select items (1 up)
D     select item ({} down)
U     select item ({} up)
S-←   select item (goto top)
S-→   select item (goto bottom)
←     shift strings in the side bar left
→     shift strings in the side bar right
H     shift strings in the side bar left
L     shift strings in the side bar right
<CR>  open the item in the main window
S-↑   go up the path or quit the search mode
j     scroll down the main window
k     scroll up the main window
h     shift the main window left
l     shift the main window right
g     goto the top of main view
G     goto the bottom if main view
/     start the search mode
n     jump to next searching word
N     jump to previous searching word
f     search file names
S-↓   open the items in system command if supported
'''


class CursesCUI():

    def __init__(self):
        # side bar val
        self.sel_idx = 0
        self.side_shift_ud = 0
        self.side_shift_lr = 0
        self.contents = []
        self.sel_cont = ''
        # main window val
        self.info = []
        self.err = None
        self.main_shift_ud = 0
        self.main_shift_lr = 0
        # mode val
        self.key = ''
        self.search_word = ''  # file name search
        self.search_word2 = ''  # word search in current file
        self.is_search = False

    def init_win(self):
        self.winy, self.winx = self.stdscr.getmaxyx()
        self.win_h = 3   # height of top window
        self.win_w = int(self.winx*3/10)  # width of side bar
        self.search_h = 1    # height of search window
        self.scroll_h = 5
        self.scroll_w = 5
        self.scroll_side = 3
        self.exp = ''
        self.exp += 'q:quit ↑↓←→:sel'
        self.exp += ' shift+↑:back'
        self.exp += ' enter:open'
        self.exp += ' jkhl:scroll'
        self.exp += ' /:search'
        self.exp += ' ?:help'
        if self.winx <= len(self.exp)+1:
            raise AssertionError(self.winx, len(self.exp)+1)
        self.win_pwd = curses.newwin(self.win_h, self.winx, 0, 0)
        self.win_side = curses.newwin(self.winy-self.win_h,
                                      self.win_w, self.win_h, 0)
        self.win_main = curses.newwin(self.winy-self.win_h,
                                      self.winx-self.win_w,
                                      self.win_h, self.win_w)
        self.win_search = curses.newwin(self.search_h,
                                        self.winx-self.win_w-3,
                                        self.winy-self.search_h-1,
                                        self.win_w+1)
        # __________________________
        # |                        | ^
        # |          pwd           | | win_h
        # |________________________| v
        # |      |                 | ^
        # |  s   |                 | |
        # |  i   |       main      | | winy-win_h
        # |  d   |                 | |
        # |  e   |                 | v
        #  <----> <--------------->
        #  win_w     winx-win_w

    def set_color(self):
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
        self.win_pwd.bkgd(' ', curses.color_pair(1))
        self.win_side.bkgd(' ', curses.color_pair(2))

    def init_var(self):
        self.sel_idx = 0
        self.side_shift_ud = 0
        self.side_shift_lr = 0
        self.info = []
        self.err = None
        self.main_shift_ud = 0
        self.main_shift_lr = 0
        self.sel_cont = ''

    @staticmethod
    def editer_cmd(key):
        if key == 10:       # Enter
            return 7        # Ctrl-G
        elif key == 127:    # back space
            return 263      # Ctrl-h
        else:
            return key

    def get_all_items(self):
        res_dirs = []
        res_files = []
        tv = TreeViewer('.', self.tv.get_contents)
        for cpath, dirs, files in tv:
            res_dirs += [str(cpath/d) for d in dirs]
            res_files += [str(cpath/f) for f in files]
        return res_dirs, res_files

    def down_sidebar(self, num):
        side_h = self.winy-self.win_h
        if len(self.contents) <= side_h:
            # all contents are shown
            if self.sel_idx < len(self.contents)-1:
                self.sel_idx += num
        elif self.side_shift_ud+side_h < len(self.contents):
            # not bottom
            self.sel_idx += num
            if self.sel_idx >= self.side_shift_ud+side_h:
                self.side_shift_ud += num
        else:
            # bottom
            if self.sel_idx < len(self.contents)-1:
                self.sel_idx += num

        if self.sel_idx >= len(self.contents):
            self.sel_idx = len(self.contents)-1
        if self.side_shift_ud >= len(self.contents):
            self.side_shift_ud = len(self.contents)-1

    def up_sidebar(self, num):
        side_h = self.winy-self.win_h
        if len(self.contents) <= side_h:
            # all contents are shown
            if self.sel_idx > 0:
                self.sel_idx -= num
        elif self.side_shift_ud > 0:
            # not top
            self.sel_idx -= num
            if self.sel_idx <= self.side_shift_ud:
                self.side_shift_ud -= num
        else:
            # top
            if self.sel_idx > 0:
                self.sel_idx -= num

        if self.sel_idx < 0:
            self.sel_idx = 0
        if self.side_shift_ud < 0:
            self.side_shift_ud = 0

    def shift_left_sidebar(self):
        if self.side_shift_lr < self.scroll_side:
            self.side_shift_lr = 0
        else:
            self.side_shift_lr -= self.scroll_side

    def shift_right_sidebar(self):
        len_content = len(self.contents[self.sel_idx])
        if self.sel_idx >= 100:
            len_content += 4
        else:
            len_content += 3
        len_content += 1  # margin
        if self.side_shift_lr < len_content-self.win_w:
            self.side_shift_lr += self.scroll_side

    def go_up_sidebar(self):
        if self.is_search:
            self.dirs, self.files = self.tv.get_contents(self.cpath)
            self.init_var()
            self.is_search = False
        elif str(self.cpath) != '.':
            self.cpath = self.cpath.parent
            self.dirs, self.files = self.tv.get_contents(self.cpath)
            self.init_var()

    def select_item(self, system):
        self.sel_cont = self.contents[self.sel_idx]
        if self.sel_cont in self.dirs:
            if self.is_search:
                self.cpath = PurePath(self.sel_cont)
            else:
                self.cpath = self.cpath/self.sel_cont
            self.dirs, self.files = self.tv.get_contents(self.cpath)
            self.is_search = False
            self.init_var()
        else:
            if self.is_search:
                fpath = self.sel_cont
            else:
                fpath = str(self.cpath/self.sel_cont)
            self.info, self.err = self.show_func(fpath, cui=True,
                                                 system=system,
                                                 stdscr=self.stdscr)
            self.info = self.info.split("\n")
            self.info = [ln.replace("\t", "  ") for ln in self.info]
            self.main_shift_ud = 0
            self.main_shift_lr = 0

    def down_main(self, num):
        main_h = self.winy-self.win_h
        if len(self.info) < main_h-1:
            # all contents are shown
            pass
        elif self.main_shift_ud < len(self.info)-num-1:
            self.main_shift_ud += num

    def up_main(self, num):
        if self.main_shift_ud < num:
            self.main_shift_ud = 0
        else:
            self.main_shift_ud -= num

    def shift_left_main(self):
        if self.main_shift_lr < self.scroll_w:
            self.main_shift_lr = 0
        else:
            self.main_shift_lr -= self.scroll_w

    def shift_right_main(self):
        self.main_shift_lr += self.scroll_w

    def file_search(self):
        # file name search mode
        uly = self.winy-self.win_h-self.search_h-2
        ulx = 0
        self.win_main.clear()
        self.win_main.addstr(uly-1, ulx, 'search file name: (empty cancel)',
                             curses.A_REVERSE)
        rectangle(self.win_main, uly, ulx,
                  self.search_h+uly+1, self.winx-self.win_w-2)
        self.win_main.refresh()
        self.win_search.clear()
        box = Textbox(self.win_search)
        box.edit(self.editer_cmd)
        search_word = box.gather()
        self.search_word = search_word.replace("\n", '').replace(" ", '')
        self.search_word2 = ''
        if len(self.search_word) == 0:
            self.win_main.clear()
            self.win_main.refresh()
        else:
            old_files = self.files.copy()
            old_dirs = self.dirs.copy()
            dirs, files = self.get_all_items()
            debug_log('search files')
            debug_log('{}'.format(files))
            debug_log('{}'.format(dirs))
            self.files = []
            self.dirs = []
            for i, f in enumerate(files):
                if re.search(self.search_word, f):
                    self.files.append(f)
            for i, d in enumerate(dirs):
                if re.search(self.search_word, d):
                    self.dirs.append(d)
            if len(self.files)+len(self.dirs) != 0:
                # find something
                self.is_search = True
                self.init_var()
            else:
                self.files = old_files
                self.dirs = old_dirs
            self.key = ''

    def into_search_mode(self):
        # search mode in current file.
        uly = self.winy-self.win_h-self.search_h-2
        ulx = 0
        self.win_main.addstr(uly-1, ulx, 'search word: (empty cancel)',
                             curses.A_REVERSE)
        rectangle(self.win_main, uly, ulx,
                  self.search_h+uly+1, self.winx-self.win_w-2)
        self.win_main.refresh()
        self.win_search.clear()
        box = Textbox(self.win_search)
        box.edit(self.editer_cmd)
        search_word = box.gather()
        self.search_word2 = search_word.replace("\n", '')[:-1]
        self.search_word = ''
        self.jump_search_word(self.main_shift_ud, False)

    def jump_search_word(self, start_line, reverse=False):
        if not self.search_word2:
            return
        if reverse:
            lines = range(start_line, -1, -1)
        else:
            lines = range(start_line, len(self.info))
        for i in lines:
            line = self.info[i]
            if self.search_word2 in line:
                self.main_shift_ud = i
                break

    def show_help_message(self):
        self.info = help_str.format(self.scroll_h,
                                    self.scroll_h).split('\n')
        self.sel_cont = '<help>'
        self.main_shift_ud = 0
        self.main_shift_lr = 0

    def update_side_bar(self):
        side_h = self.winy-self.win_h
        self.win_side.clear()
        for i in range(side_h):
            if i+self.side_shift_ud >= len(self.contents):
                break
            cont = self.contents[i+self.side_shift_ud]
            cidx = '{:2d} '.format(i+self.side_shift_ud)
            if cont in self.dirs:
                self.win_side.addstr(i, 0, cidx, curses.color_pair(5))
                attr = curses.A_BOLD
            elif cont in self.files:
                self.win_side.addstr(i, 0, cidx, curses.color_pair(6))
                attr = curses.A_NORMAL
            cont = cont[self.side_shift_lr:
                        self.side_shift_lr+self.win_w-len(cidx)-1]
            if i+self.side_shift_ud == self.sel_idx:
                self.win_side.addstr(i, len(cidx), cont, curses.A_REVERSE)
            else:
                self.win_side.addstr(i, len(cidx), cont, attr)
        self.win_side.refresh()

    def update_main_window(self):
        main_h = self.winy-self.win_h
        main_w = self.winx-self.win_w
        self.win_main.clear()
        # show titme
        self.win_main.addstr(0, 0, self.sel_cont, curses.A_REVERSE)
        if len(self.sel_cont) != 0:
            if main_w > len(self.sel_cont)+2:
                self.win_main.addstr(0, len(self.sel_cont)+2,
                                     '{}/{}'.format(self.main_shift_ud+1,
                                                    len(self.info)),
                                     curses.color_pair(4))
        if self.err is None:
            # show contents
            for i in range(1, main_h):
                if i-1+self.main_shift_ud >= len(self.info):
                    break
                idx = i+self.main_shift_ud
                info = self.info[idx-1]
                if curses_debug:
                    info = "{:d} ".format(i+self.main_shift_ud)+info
                info = info[self.main_shift_lr:self.main_shift_lr+main_w-2]
                try:
                    self.win_main.addstr(i, 0, info)
                except Exception as e:
                    self.win_main.addstr(i, 0, "!! {}".format(e),
                                         curses.color_pair(3))
        else:
            # show error
            self.win_main.addstr(1, 0, self.err, curses.color_pair(3))
        self.win_main.refresh()

    def update_pwd_window(self):
        self.win_pwd.clear()
        self.win_pwd.addstr(0, 3, 'file: {}'.format(self.fname), curses.A_BOLD)
        self.win_pwd.addstr(1, 5, 'current path: {}'.format(str(self.cpath)))
        self.win_pwd.addstr(2, 1, self.exp)
        self.win_pwd.refresh()

    def debug_info(self):
        side_h = self.winy-self.win_h
        main_h = self.winy-self.win_h
        main_w = self.winx-self.win_w
        self.win_pwd.addstr(0, int(self.winx*2/3), ' '*(int(self.winx/3)-1))
        self.win_pwd.addstr(0, int(self.winx*2/3),
                            '{}x{} {}x{} {}x{} k:{}'.format(
                            self.win_h, self.winx, side_h, self.win_w,
                            main_h, main_w, self.key))
        self.win_pwd.addstr(1, int(self.winx*2/3), ' '*(int(self.winx/3)-1))
        self.win_pwd.addstr(1, int(self.winx*2/3),
                            's:{}-{}-{}-{} m:{}-{}-{}'.format(
                            len(self.contents),
                            self.side_shift_ud, self.side_shift_lr,
                            self.sel_idx, len(self.info),
                           self.main_shift_ud, self.main_shift_lr))
        self.win_pwd.addstr(2, int(self.winx*2/3), ' '*(int(self.winx/3)-1))
        if self.search_word:
            sw = self.search_word
        else:
            sw = self.search_word2
        sw = sw[:int(self.winx/3)-1-6]
        self.win_pwd.addstr(2, int(self.winx*2/3),
                            'srch: {}'.format(sw))
        self.win_pwd.refresh()

    def main(self, stdscr, fname: str,
             show_func: Callable[[str, bool, bool], List[str]],
             cpath: PurePath, tv: TreeViewer) -> None:
        self.stdscr = stdscr
        self.fname = fname
        self.show_func = show_func
        self.cpath = cpath
        self.tv = tv

        # clear screen
        self.stdscr.clear()
        self.init_win()
        self.set_color()
        self.dirs, self.files = tv.get_contents(cpath)
        self.contents = self.dirs+self.files
        stdscr.refresh()

        while self.key != 'q':
            # showed indices are side_shift_ud ~ side_shift_ud+(winy-win_h)
            if self.key in ['J', 'KEY_DOWN']:
                self.down_sidebar(1)
            elif self.key in ['K', 'KEY_UP']:
                self.up_sidebar(1)
            elif self.key == 'D':
                self.down_sidebar(self.scroll_h)
            elif self.key == 'U':
                self.up_sidebar(self.scroll_h)
            elif self.key == 'KEY_SLEFT':
                self.up_sidebar(self.sel_idx)
            elif self.key == 'KEY_SRIGHT':
                self.down_sidebar(len(self.contents)-self.sel_idx-1)
            elif self.key in ['L', 'KEY_RIGHT']:
                self.shift_right_sidebar()
            elif self.key in ['H', 'KEY_LEFT']:
                self.shift_left_sidebar()
            elif self.key in ['KEY_SR', 'KEY_SUP']:
                self.go_up_sidebar()
            elif self.key in ["\n", 'KEY_ENTER']:
                self.select_item(system=False)
            elif self.key in ['KEY_SDOWN', 'KEY_SF']:
                self.select_item(system=True)
            elif self.key == 'j':
                self.down_main(self.scroll_h)
            elif self.key == 'k':
                self.up_main(self.scroll_h)
            elif self.key == 'l':
                self.shift_right_main()
            elif self.key == 'h':
                self.shift_left_main()
            elif self.key == 'g':
                self.up_main(self.main_shift_ud)
            elif self.key == 'G':
                self.down_main(len(self.info)-self.main_shift_ud-2)
            elif self.key == 'f':
                self.file_search()
            elif self.key == '/':
                self.into_search_mode()
            elif self.key == 'n':
                self.jump_search_word(self.main_shift_ud+1, False)
            elif self.key == 'N':
                self.jump_search_word(self.main_shift_ud-1, True)
            elif self.key == '?':
                self.show_help_message()

            self.contents = self.dirs+self.files

            if self.key in ['', 'KEY_UP', 'KEY_DOWN',
                            'KEY_LEFT', 'KEY_RIGHT',
                            'KEY_SRIGHT', 'KEY_SLEFT',
                            'KEY_SR', 'KEY_SUP', "\n", 'KEY_ENTER',
                            'H', 'J', 'K', 'L',
                            'D', 'U',
                            ]:
                self.update_side_bar()
            if self.key in ['', "\n", 'KEY_ENTER',
                            'KEY_SF', 'KEY_SDOWN',
                            'KEY_SR', 'KEY_SUP',
                            'j', 'k', 'h', 'l', 'g', 'G',
                            '?', '/', 'n', 'N',
                            ]:
                self.update_main_window()
            if self.key in ['', "\n", 'KEY_ENTER', 'KEY_SR', 'KEY_SUP']:
                self.update_pwd_window()
            if curses_debug:
                self.debug_info()
            self.key = self.stdscr.getkey()


log_init = False
def debug_log(msg):
    if not curses_debug:
        return
    log_file = Path(conf_dir)/"curses_debug.log"
    global log_init
    if not log_init:
        with open(log_file, 'w') as f:
            # clear file
            pass
        log_init = True
    with open(log_file, 'a') as f:
        f.write(msg+"\n")


def interactive_cui(fname, get_contents, show_func):
    cpath = PurePath('.')
    tv = TreeViewer('.', get_contents)
    curses_cui = CursesCUI()
    try:
        curses.wrapper(curses_cui.main, fname, show_func, cpath, tv)
    except AssertionError as e:
        winx, lenexp = e.args
        print('Window width should be larger than {:d} (current: {:d})'.format(lenexp, winx))
