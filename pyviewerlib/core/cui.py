import re
import curses
from curses.textpad import Textbox, rectangle
from pathlib import PurePath
from typing import List
from logging import getLogger, StreamHandler, CRITICAL as logCRITICAL

from pymeflib.tree2 import TreeViewer, GC, PPath
from . import GLOBAL_CONF, get_config, ReturnMessage, SF
logger = getLogger(GLOBAL_CONF.logname)

default_color_set = {
        'k': curses.COLOR_BLACK,
        'r': curses.COLOR_RED,
        'g': curses.COLOR_GREEN,
        'y': curses.COLOR_YELLOW,
        'b': curses.COLOR_BLUE,
        'm': curses.COLOR_MAGENTA,
        'c': curses.COLOR_CYAN,
        'w': curses.COLOR_WHITE,
        }


class CursesCUI():
    def __init__(self, purepath: PPath = PurePath):
        # sidebar val
        self.sel_idx = 0
        self.side_shift_ud = 0
        self.side_shift_lr = 0
        self.contents: List[str] = []
        self.sel_cont = ''
        # main window val
        self.info = ReturnMessage('', False)
        self.message: List[str] = []
        self.main_shift_ud = 0
        self.main_shift_lr = 0
        # mode val
        self.key = ''
        self.search_word = ''  # file name search
        self.search_word2 = ''  # word search in current file
        self.search_cmt = ''
        self.is_search = False
        # called path-like class
        self.purepath = purepath
        self.keymaps = {}

    def init_win(self):
        self.winy, self.winx = self.stdscr.getmaxyx()
        self.win_h = 3   # height of top window
        self.win_w = int(self.winx*3/10)  # width of sidebar
        self.search_h = 1    # height of search window
        self.scroll_h = 5
        self.scroll_w = 5
        self.scroll_side = 3
        # actually this↓ almost means the max length of messages.
        self.scroll_doll = 0
        self.exp = ''
        self.exp += 'q:quit ↑↓←→:sel'
        self.exp += ' shift+↑:back'
        self.exp += ' enter:open'
        self.exp += ' jkhl:scroll'
        self.exp += ' /:search'
        self.exp += ' ?:help'
        assert self.winx > len(self.exp)+1, \
            f'window width {self.winx} should be larger than {len(self.exp)+1}'
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

    def create_color_set(self, num, name):
        assert num < curses.COLOR_PAIRS, \
            f'color number {num} is larger than {curses.COLOR_PAIRS}'
        fg, bg = get_config('colors', f'cui_{name}')
        if fg in default_color_set:
            fg = default_color_set[fg]
        if bg in default_color_set:
            bg = default_color_set[bg]

        if not (type(fg) is int and fg < curses.COLORS):
            # debug_log(f'incorrect fg: {fg}')
            logger.debug(f'incorrect fg: {fg}')
            fg = curses.COLOR_WHITE
        if not (type(bg) is int and bg < curses.COLORS):
            # debug_log(f'incorrect bg: {bg}')
            logger.debug(f'incorrect bg: {bg}')
            bg = curses.COLOR_BLACK
        curses.init_pair(num, fg, bg)

    def set_color(self):
        # debug_log('default color;')
        logger.debug('default color;')
        # debug_log(f'black: {curses.COLOR_BLACK}')
        logger.debug(f'black: {curses.COLOR_BLACK}')
        # debug_log(f'red: {curses.COLOR_RED}')
        logger.debug(f'red: {curses.COLOR_RED}')
        # debug_log(f'green: {curses.COLOR_GREEN}')
        logger.debug(f'green: {curses.COLOR_GREEN}')
        # debug_log(f'yellow: {curses.COLOR_YELLOW}')
        logger.debug(f'yellow: {curses.COLOR_YELLOW}')
        # debug_log(f'blue: {curses.COLOR_BLUE}')
        logger.debug(f'blue: {curses.COLOR_BLUE}')
        # debug_log(f'magenta: {curses.COLOR_MAGENTA}')
        logger.debug(f'magenta: {curses.COLOR_MAGENTA}')
        # debug_log(f'cyan: {curses.COLOR_CYAN}')
        logger.debug(f'cyan: {curses.COLOR_CYAN}')
        # debug_log(f'white: {curses.COLOR_WHITE}')
        logger.debug(f'white: {curses.COLOR_WHITE}')
        # pwd background
        self.create_color_set(1, 'top')
        # bar background
        self.create_color_set(2, 'left')
        # error
        self.create_color_set(3, 'error')
        # file info
        self.create_color_set(4, 'file_info')
        # dir index
        self.create_color_set(5, 'dir_index')
        # file index
        self.create_color_set(6, 'file_index')
        self.win_pwd.bkgd(' ', curses.color_pair(1))
        self.win_side.bkgd(' ', curses.color_pair(2))

    def init_var(self):
        self.sel_idx = 0
        self.side_shift_ud = 0
        self.side_shift_lr = 0
        self.info = ReturnMessage('', False)
        self.message = []
        self.main_shift_ud = 0
        self.main_shift_lr = 0
        self.sel_cont = ''
        if hasattr(self, 'dirs'):
            self.dirs.sort()
        if hasattr(self, 'files'):
            self.files.sort()

    def set_keymap(self):
        # default key maps
        # key: [function, [args], key_symbol, help_msg,
        #       update_main, up_top, up_side]
        def_keymaps = {
                '?': [self.show_help_message, [], '?',
                      'show this help',
                      True, False, False,
                      ],
                'J': [self.down_sidebar, [1], 'J',
                      'move the sidebar cursor down by 1',
                      True, False, True,
                      ],
                'KEY_DOWN': [self.down_sidebar, [1], '↓',
                             'move the sidebar cursor down by 1',
                             False, False, True,
                             ],
                'K': [self.up_sidebar, [1], 'K',
                      'move the sidebar cursor up by 1',
                      True, False, True,
                      ],
                'KEY_UP': [self.up_sidebar, [1], '↑',
                           'move the sidebar cursor up by 1',
                           False, False, True,
                           ],
                'D': [self.down_sidebar, [self.scroll_h], 'D',
                      f'move the sidebar cursor down by {self.scroll_h}',
                      False, False, True,
                      ],
                'U': [self.up_sidebar, [self.scroll_h], 'U',
                      f'move the sidebar cursor up by {self.scroll_h}',
                      False, False, True,
                      ],
                'KEY_SLEFT': [self.top_sidebar, [], 'S-←',
                              'move the sidebar cursor to the first line',
                              False, False, True,
                              ],
                'KEY_SRIGHT': [self.bottom_sidebar, [], 'S-→',
                               'move the sidebar cursor to the end line',
                               False, False, True,
                               ],
                'L': [self.shift_right_sidebar, [], 'L',
                      'shift strings in the sidebar right',
                      False, False, True,
                      ],
                'KEY_RIGHT': [self.shift_right_sidebar, [], '→',
                              'shift strings in the sidebar right',
                              False, False, True,
                              ],
                'H': [self.shift_left_sidebar, [], 'H',
                      'shift strings in the sidebar left',
                      False, False, True,
                      ],
                'KEY_LEFT': [self.shift_left_sidebar, [], '←',
                             'shift strings in the sidebar left',
                             False, False, True,
                             ],
                'KEY_SR': [self.go_up_sidebar, [], 'S-↑',
                           'go up the path or quit the search mode',
                           True, True, True,
                           ],
                'KEY_SUP': [self.go_up_sidebar, [], '', '',
                            True, True, True,
                            ],
                '\n': [self.select_item, [False], "<CR>",
                       'open the item in the main window',
                       True, True, True,
                       ],
                'KEY_ENTER': [self.select_item, [False], '', '',
                              True, True, True,
                              ],
                "KEY_SDOWN": [self.select_item, [True], "S-↓",
                              'open the items in the system command if supported',
                              True, True, False,
                              ],
                'KEY_SF': [self.select_item, [True], '', '',
                           True, True, False,
                           ],
                'j': [self.down_main, [self.scroll_h], 'j',
                      'scroll down the main window',
                      True, False, False,
                      ],
                'k': [self.up_main, [self.scroll_h], 'k',
                      'scroll up the main window',
                      True, False, False,
                      ],
                'l': [self.shift_right_main, [self.scroll_w], 'l',
                      'shift the main window right',
                      True, False, False,
                      ],
                'h': [self.shift_left_main, [self.scroll_w], 'h',
                      'shift the main window left',
                      True, False, False,
                      ],
                'g': [self.top_main, [], 'g',
                      'go to the top of the main window',
                      True, False, False,
                      ],
                'G': [self.bottom_main, [], 'G',
                      'go to the bottom if main window',
                      True, False, False,
                      ],
                '^': [self.hat_main, [], '^',
                      'go to the first character of the line',
                      True, False, False,
                      ],
                '$': [self.doll_main, [], '$',
                      'go to the last column of the line',
                      True, False, False,
                      ],
                'f': [self.file_search, [], 'f',
                      'search file names',
                      True, False, False,
                      ],
                '/': [self.into_search_mode, [], '/',
                      'start the search mode',
                      True, False, True,
                      ],
                'n': [self.jump_search_word_next, [], 'n',
                      'jump to the next search word',
                      True, False, False,
                      ],
                'N': [self.jump_search_word_pre, [], 'N',
                      'jump to the previous search word',
                      True, False, False,
                      ],
                }
        # debug_log('set default key maps')
        logger.debug('set default key maps')
        for k in def_keymaps:
            if k not in self.keymaps:
                # debug_log(f'set key "{k}" as default')
                logger.debug(f'set key "{k}" as default')
                self.keymaps[k] = def_keymaps[k]

    def create_help_msg(self):
        help_msg = '''
key\t function
(S- means shift+key)
q\t quit
'''
        for k, confs in self.keymaps.items():
            _, _, symbol, help_str, _, _, _ = confs
            if len(symbol) == 0:
                continue
            help_line = f'{symbol}\t {help_str}\n'
            help_msg += help_line

        return help_msg

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

    def bottom_sidebar(self):
        self.down_sidebar(len(self.contents)-self.sel_idx-1)

    def top_sidebar(self):
        self.up_sidebar(self.sel_idx)

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
                self.cpath = self.purepath(self.sel_cont)
            else:
                self.cpath = self.cpath/self.sel_cont
            dirs, files = self.tv.get_contents(self.cpath)
            if len(dirs+files) == 0:
                self.message = ['empty directory.']
                self.cpath = self.cpath.parent
                return
            self.dirs = dirs
            self.files = files
            self.is_search = False
            self.init_var()
        else:
            if self.is_search:
                fpath = self.sel_cont
            else:
                fpath = str(self.cpath/self.sel_cont)
            self.main_shift_ud = 0
            self.main_shift_lr = 0
            # message of waiting for opening an item
            self.message = ['opening an item...']
            self.update_main_window()
            self.info = self.show_func(fpath, cui=True,
                                       system=system, stdscr=self.stdscr)
            self.message = self.info.message.split("\n")
            self.message = [ln.replace("\t", "  ") for ln in self.message]
            self.scroll_doll = max([len(ln) for ln in self.message]) -\
                (self.winx-self.win_w)+5
            if self.scroll_doll < 0:
                self.scroll_doll = 0

    def down_main(self, num):
        main_h = self.winy-self.win_h
        if len(self.message) < main_h-1:
            # all contents are shown
            pass
        elif self.main_shift_ud < len(self.message)-num-1:
            self.main_shift_ud += num

    def up_main(self, num):
        if self.main_shift_ud < num:
            self.main_shift_ud = 0
        else:
            self.main_shift_ud -= num

    def bottom_main(self):
        self.down_main(len(self.message)-self.main_shift_ud-2)

    def top_main(self):
        self.up_main(self.main_shift_ud)

    def shift_left_main(self, num):
        if self.main_shift_lr < num:
            self.main_shift_lr = 0
        else:
            self.main_shift_lr -= num

    def shift_right_main(self, num):
        self.main_shift_lr += num

    def hat_main(self):
        self.shift_left_main(self.main_shift_lr)

    def doll_main(self):
        self.shift_right_main(self.scroll_doll-self.main_shift_lr)

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
            # debug_log('search files')
            logger.debug('search files')
            # debug_log('{}'.format(files))
            logger.debug(f'files: {files}')
            # debug_log('{}'.format(dirs))
            logger.debug(f'dirs:  {dirs}')
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
        self.jump_search_word(self.main_shift_ud, 0, False)

    def jump_search_word(self, start_line, start_col, reverse=False):
        if not self.search_word2:
            return
        if reverse:
            lines = range(start_line, -1, -1)
        else:
            lines = range(start_line, len(self.message))
        for i in lines:
            if i == start_line:
                line = self.message[i][start_col:]
                shift = start_col
            else:
                line = self.message[i]
                shift = 0
            self.search_cmt = f'"{self.search_word2}" not found'
            if self.search_word2 in line:
                self.main_shift_ud = i
                self.main_shift_lr = line.find(self.search_word2)+shift
                self.search_cmt = ''
                break

    def jump_search_word_next(self):
        self.jump_search_word(self.main_shift_ud, self.main_shift_lr+1, False)

    def jump_search_word_pre(self):
        self.jump_search_word(self.main_shift_ud-1, 0, True)

    def show_help_message(self):
        self.message = self.create_help_msg().split('\n')
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
        # show title
        self.win_main.addstr(0, 0, self.sel_cont, curses.A_REVERSE)
        if len(self.sel_cont) != 0:
            if main_w > len(self.sel_cont)+2:
                self.win_main.addstr(0, len(self.sel_cont)+2,
                                     '{}/{}, {}; {}'.format(
                                         self.main_shift_ud+1,
                                         len(self.message),
                                         self.main_shift_lr+1,
                                         self.search_cmt,
                                         ),
                                     curses.color_pair(4))
        if not self.info.error:
            # show contents
            for i in range(1, main_h):
                if i-1+self.main_shift_ud >= len(self.message):
                    break
                idx = i+self.main_shift_ud
                message = self.message[idx-1]
                if GLOBAL_CONF.debug:
                    message = "{:d} ".format(i+self.main_shift_ud)+message
                message = message[self.main_shift_lr:self.main_shift_lr+main_w-2]
                try:
                    self.win_main.addstr(i, 0, message)
                except Exception as e:
                    self.win_main.addstr(i, 0, "!! {}".format(e),
                                         curses.color_pair(3))
        else:
            # show error
            self.win_main.addstr(1, 0, self.info.message, curses.color_pair(3))
        self.search_cmt = ''
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
                            self.sel_idx, len(self.message),
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

    def add_key_maps(self, key, config):
        # debug_log(f'add key "{key}"')
        logger.debug(f'add key "{key}"')
        self.keymaps[key] = config

    def main(self, stdscr, fname: str,
             show_func: SF,
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
        self.set_keymap()
        stdscr.refresh()

        while self.key != 'q':
            # showed indices are side_shift_ud ~ side_shift_ud+(winy-win_h)
            if self.key == '':
                upm, upt, ups = True, True, True
            else:
                upm, upt, ups = False, False, False
            if self.key in self.keymaps:
                func, args, _, _, upm, upt, ups = self.keymaps[self.key]
                func(*args)

            self.contents = self.dirs+self.files

            if upm:
                self.update_main_window()
            if upt:
                self.update_pwd_window()
            if ups:
                self.update_side_bar()
            if GLOBAL_CONF.debug:
                self.debug_info()
            self.key = self.stdscr.getkey()


def __will_be_removed_debug_log(msg):
    if not GLOBAL_CONF.debug:
        return
    log_file = GLOBAL_CONF.conf_dir/"curses_debug.log"
    global log_init
    if not log_init:
        with open(log_file, 'w') as f:
            # clear file
            pass
        log_init = True
    with open(log_file, 'a') as f:
        f.write(msg+"\n")


def interactive_cui(fname: str, get_contents: GC, show_func: SF,
                    purepath: PPath = PurePath) -> None:
    """
    provide the CUI (TUI) to show the contents.

    Parameters
    ----------
    fname: str
        An opened file name.
    get_contents: Callable[[PurePath], Tuple[List[str], List[str]]]
        A function to get lists of directories and files.
        The argument is the path to an item.
        The first return value is a list of directory names,
        and the second return value is a list of file names.
        In this context, a directory means something that includes
        files and directories, and a file means something that includes data.
    show_func: Callable[[str, **kwargs], ReturnMessage]
        A function to show the contents.
        The first argument is the path to a file.
        Other arguments are treated as keyword arguments.
        Please see the wiki for possible keywords.
        The return value is the ReturnMessage. It is treated as
        an error message if ReturnMessage.error is True. Otherwise, it is
        treated as a standard message.

    Returns
    -------
    None
    """
    cpath = purepath('.')
    tv = TreeViewer('.', get_contents, purepath)
    curses_cui = CursesCUI(purepath)
    for hdlr in logger.handlers:
        if type(hdlr) is StreamHandler:
            # basically do not show log messages in terminal.
            hdlr.setLevel(logCRITICAL)
    try:
        curses.wrapper(curses_cui.main, fname, show_func, cpath, tv)
    except AssertionError as e:
        print(e)
