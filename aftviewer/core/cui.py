from __future__ import annotations

import re
import curses
from curses.textpad import Textbox, rectangle
from pathlib import PurePath
from typing import Callable
from logging import getLogger, StreamHandler

from pymeflib.tree2 import TreeViewer, GC, PPath
from . import GLOBAL_CONF, get_config, get_col, print_error
from .types import ReturnMessage, SF
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


class CUIWin():
    def __init__(self, height: int, width: int,
                 begin_y: int, begin_x: int,
                 updatefunc: None | Callable):
        self.w = width
        self.h = height
        self.updatefunc = updatefunc
        self.b = curses.newwin(height, width, begin_y, begin_x)

    def update(self):
        if self.updatefunc is None:
            return
        self.b.clear()
        self.updatefunc()
        self.b.refresh()


class CursesCUI():
    def __init__(self, filetype: str, purepath: PPath = PurePath):
        # selected item
        self.selected = ''
        # information about selected item
        self.info = ReturnMessage('', False)
        # message shown in the main window
        self.message: list[str] = []
        # flag if display the line number or not
        self.line_number: bool = get_config('cui_linenumber', filetype)
        # flag if wrap the message
        self.wrap: bool = get_config('cui_wrap', filetype)
        # called path-like class
        self.purepath = purepath
        # entered key
        self.key = ''
        # key maps
        self.keymaps: dict[str, list] = {}
        # file type
        self.ft = filetype

    def init_win(self):
        self.winy, self.winx = self.stdscr.getmaxyx()
        win_h = 3   # height of top window
        win_w = int(self.winx*3/10)  # width of sidebar
        search_h = 1    # height of search window
        self.exp = ' '.join(['q:quit',
                             '?:help',
                             'shift+↑:back',
                             'enter:open',
                             '↓↑:move item',
                             'jkhl:scroll',
                             '/:search word',
                             'f:search file',
                             ])

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

        self.topwin = CUIWin(height=win_h, width=self.winx,
                             begin_y=0, begin_x=0,
                             updatefunc=self._update_pwd_window)

        self.sidebar = CUIWin(height=self.winy-win_h, width=win_w,
                              begin_y=win_h, begin_x=0,
                              updatefunc=self._update_side_bar)
        self.sidebar.ud = 0
        self.sidebar.lr = 0
        self.sidebar.idx = 0
        self.sidebar.contents: list[str] = []
        self.sidebar.scroll_h = 5
        self.sidebar.scroll_w = 3
        self.sidebar.down = self._down_sidebar
        self.sidebar.up = self._up_sidebar
        self.sidebar.bottom = self._bottom_sidebar
        self.sidebar.top = self._top_sidebar
        self.sidebar.left = self._shift_left_sidebar
        self.sidebar.right = self._shift_right_sidebar
        self.sidebar.go_up = self._go_up_sidebar

        self.mainwin = CUIWin(height=self.winy-win_h, width=self.winx-win_w,
                              begin_y=win_h, begin_x=win_w,
                              updatefunc=self._update_main_window)
        self.mainwin.ud = 0
        self.mainwin.lr = 0
        self.mainwin.max_lr = 0
        self.mainwin.lnwidth = 0  # width of line number
        self.mainwin.textw = 0  # width that the text is shown
        self.mainwin.scroll_h = 5
        self.mainwin.scroll_w = 5
        self.mainwin.down = self._down_main
        self.mainwin.up = self._up_main
        self.mainwin.bottom = self._bottom_main
        self.mainwin.top = self._top_main
        self.mainwin.right = self._shift_right_main
        self.mainwin.left = self._shift_left_main
        self.mainwin.hat = self._hat_main
        self.mainwin.doll = self._doll_main

        self.search = CUIWin(height=search_h, width=self.winx-win_w-3,
                             begin_y=self.winy-search_h-1, begin_x=win_w+1,
                             updatefunc=None)
        self.search.file = ''  # file name search
        self.search.is_file = False
        self.search.word = ''  # word search in current file
        self.search.cmt = ''  # comments shown in the main window
        # ↓ find-word, line, start col, end col
        self.search.is_word: None | tuple[str, int, int, int] = None

    def create_color_set(self, num, name):
        assert num < curses.COLOR_PAIRS, \
            f'color number {num} is larger than {curses.COLOR_PAIRS}'
        fg, bg = get_col(f'cui_{name}', self.ft)
        if fg in default_color_set:
            fg = default_color_set[fg]
        elif fg is None:
            fg = -1
        if bg in default_color_set:
            bg = default_color_set[bg]
        elif bg is None:
            bg = -1

        if not (type(fg) is int and fg < curses.COLORS):
            logger.debug(f'incorrect fg: {fg}')
            fg = curses.COLOR_WHITE
        if not (type(bg) is int and bg < curses.COLORS):
            logger.debug(f'incorrect bg: {bg}')
            bg = curses.COLOR_BLACK
        curses.init_pair(num, fg, bg)

    def set_color(self):
        logger.debug('default color;')
        logger.debug(f'black: {curses.COLOR_BLACK}')
        logger.debug(f'red: {curses.COLOR_RED}')
        logger.debug(f'green: {curses.COLOR_GREEN}')
        logger.debug(f'yellow: {curses.COLOR_YELLOW}')
        logger.debug(f'blue: {curses.COLOR_BLUE}')
        logger.debug(f'magenta: {curses.COLOR_MAGENTA}')
        logger.debug(f'cyan: {curses.COLOR_CYAN}')
        logger.debug(f'white: {curses.COLOR_WHITE}')
        logger.debug('use default colors')
        curses.use_default_colors()
        # main window
        self.create_color_set(1, 'main')
        # pwd window
        self.create_color_set(2, 'top')
        # bar window
        self.create_color_set(3, 'left')
        # error message
        self.create_color_set(4, 'error')
        # file info
        self.create_color_set(5, 'file_info')
        # dir index
        self.create_color_set(6, 'dir_index')
        # file index
        self.create_color_set(7, 'file_index')
        # search word
        self.create_color_set(8, 'search')
        self.mainwin.b.bkgd(' ', curses.color_pair(1))
        self.topwin.b.bkgd(' ', curses.color_pair(2))
        self.sidebar.b.bkgd(' ', curses.color_pair(3))

    def init_var(self):
        self.info = ReturnMessage('', False)
        self.message = []
        self.sidebar.idx = 0
        self.sidebar.ud = 0
        self.sidebar.lr = 0
        self.mainwin.ud = 0
        self.mainwin.lr = 0

    def set_keymap(self):
        # default key maps
        # key: [function, [args], key_symbol, help_msg,
        #       update_main, up_top, up_side]
        def_keymaps = {
                '?': [self.show_help_message, [], '?',
                      'show this help',
                      True, False, False,
                      ],
                'J': [self.sidebar.down, [1], 'J',
                      'move the sidebar cursor down by 1',
                      True, False, True,
                      ],
                'KEY_DOWN': [self.sidebar.down, [1], '↓',
                             'move the sidebar cursor down by 1',
                             False, False, True,
                             ],
                'K': [self.sidebar.up, [1], 'K',
                      'move the sidebar cursor up by 1',
                      True, False, True,
                      ],
                'KEY_UP': [self.sidebar.up, [1], '↑',
                           'move the sidebar cursor up by 1',
                           False, False, True,
                           ],
                'D': [self.sidebar.down, [self.sidebar.scroll_h], 'D',
                      'move the sidebar cursor down by'
                      f' {self.sidebar.scroll_h}',
                      False, False, True,
                      ],
                'U': [self.sidebar.up, [self.sidebar.scroll_h], 'U',
                      f'move the sidebar cursor up by {self.sidebar.scroll_h}',
                      False, False, True,
                      ],
                'KEY_SLEFT': [self.sidebar.top, [], 'S-←',
                              'move the sidebar cursor to the first line',
                              False, False, True,
                              ],
                'KEY_SRIGHT': [self.sidebar.bottom, [], 'S-→',
                               'move the sidebar cursor to the end line',
                               False, False, True,
                               ],
                'L': [self.sidebar.right, [], 'L',
                      'shift strings in the sidebar right',
                      False, False, True,
                      ],
                'KEY_RIGHT': [self.sidebar.right, [], '→',
                              'shift strings in the sidebar right',
                              False, False, True,
                              ],
                'H': [self.sidebar.left, [], 'H',
                      'shift strings in the sidebar left',
                      False, False, True,
                      ],
                'KEY_LEFT': [self.sidebar.left, [], '←',
                             'shift strings in the sidebar left',
                             False, False, True,
                             ],
                'KEY_SR': [self._go_up_sidebar, [], 'S-↑',
                           'go up the path or quit the search mode',
                           True, True, True,
                           ],
                'KEY_SUP': [self._go_up_sidebar, [], '', '',
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
                              'open the items in the system command'
                              ' if supported',
                              True, True, False,
                              ],
                'KEY_SF': [self.select_item, [True], '', '',
                           True, True, False,
                           ],
                'j': [self.mainwin.down, [self.mainwin.scroll_h], 'j',
                      'scroll down the main window',
                      True, False, False,
                      ],
                'k': [self.mainwin.up, [self.mainwin.scroll_h], 'k',
                      'scroll up the main window',
                      True, False, False,
                      ],
                'l': [self.mainwin.right, [self.mainwin.scroll_w], 'l',
                      'shift the main window right',
                      True, False, False,
                      ],
                'h': [self.mainwin.left, [self.mainwin.scroll_w], 'h',
                      'shift the main window left',
                      True, False, False,
                      ],
                'g': [self.mainwin.top, [], 'g',
                      'go to the top of the main window',
                      True, False, False,
                      ],
                'G': [self.mainwin.bottom, [], 'G',
                      'go to the bottom if main window',
                      True, False, False,
                      ],
                '^': [self.mainwin.hat, [], '^',
                      'go to the first character of the line',
                      True, False, False,
                      ],
                '$': [self.mainwin.doll, [], '$',
                      'go to the last column of the line',
                      True, False, False,
                      ],
                'f': [self.file_search, [], 'f',
                      'search file names',
                      True, False, True,
                      ],
                'W': [self.toggle_wrap, [], 'W',
                      'toggle wrap mode',
                      True, False, False,
                      ],
                '/': [self.word_search, [], '/',
                      'start the search mode',
                      True, False, False,
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
        logger.debug('set default key maps')
        for k in def_keymaps:
            if k not in self.keymaps:
                logger.debug(f'set key "{k}" as default')
                self.keymaps[k] = def_keymaps[k]
        if GLOBAL_CONF.debug:
            if 'O' in self.keymaps:
                logger.warning('debug keymap is already in use.')
            else:
                self.keymaps['O'] = [self.debug_log, [], 'O',
                                     'save info into log file.',
                                     False, False, False,
                                     ]

    def disable_stream_handler(self):
        for hdlr in logger.handlers:
            if type(hdlr) is StreamHandler:
                # basically do not show log messages in terminal.
                logger.removeHandler(hdlr)
                # hdlr.setLevel(logCRITICAL)

    def create_help_msg(self):
        help_msg = '''
key     |explanation
(S-key means shift+key)
q       |quit
'''
        for k, confs in self.keymaps.items():
            _, _, symbol, help_str, _, _, _ = confs
            if len(symbol) == 0:
                continue
            help_line = f'{symbol:8s}|{help_str}\n'
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
        tv = TreeViewer('.', self.tv.get_contents,
                        purepath=self.purepath, logger=logger)
        for cpath, dirs, files in tv:
            res_dirs += [str(cpath/d) for d in dirs]
            res_files += [str(cpath/f) for f in files]
        return res_dirs, res_files

    def get_title(self):
        return self.selected

    def _down_sidebar(self, num: int):
        if len(self.sidebar.contents) <= self.sidebar.h:
            # all contents are shown
            if self.sidebar.idx < len(self.sidebar.contents)-1:
                self.sidebar.idx += num
        elif self.sidebar.ud+self.sidebar.h < len(self.sidebar.contents):
            # not bottom
            self.sidebar.idx += num
            if self.sidebar.idx >= self.sidebar.ud+self.sidebar.h:
                self.sidebar.ud += num
        else:
            # bottom
            if self.sidebar.idx < len(self.sidebar.contents)-1:
                self.sidebar.idx += num

        if self.sidebar.idx >= len(self.sidebar.contents):
            self.sidebar.idx = len(self.sidebar.contents)-1
        if self.sidebar.ud >= len(self.sidebar.contents):
            self.sidebar.ud = len(self.sidebar.contents)-1

    def _up_sidebar(self, num: int):
        if len(self.sidebar.contents) <= self.sidebar.h:
            # all contents are shown
            if self.sidebar.idx > 0:
                self.sidebar.idx -= num
        elif self.sidebar.ud > 0:
            # not top
            self.sidebar.idx -= num
            if self.sidebar.idx <= self.sidebar.ud:
                self.sidebar.ud -= num
        else:
            # top
            if self.sidebar.idx > 0:
                self.sidebar.idx -= num

        if self.sidebar.idx < 0:
            self.sidebar.idx = 0
        if self.sidebar.ud < 0:
            self.sidebar.ud = 0

    def _bottom_sidebar(self):
        self.sidebar.down(len(self.sidebar.contents)-self.sidebar.idx-1)

    def _top_sidebar(self):
        self.sidebar.up(self.sidebar.idx)

    def _shift_left_sidebar(self):
        if self.sidebar.lr < self.sidebar.scroll_w:
            self.sidebar.lr = 0
        else:
            self.sidebar.lr -= self.sidebar.scroll_w

    def _shift_right_sidebar(self):
        len_content = len(self.sidebar.contents[self.sidebar.idx])
        if self.sidebar.idx >= 100:
            len_content += 4
        else:
            len_content += 3
        len_content += 1  # margin
        if self.sidebar.lr < len_content-self.sidebar.w:
            self.sidebar.lr += self.sidebar.scroll_w

    def _go_up_sidebar(self):
        if self.search.is_file:
            self.dirs, self.files = self.tv.get_contents(self.cpath)
            self.init_var()
            self.search.is_file = False
        elif str(self.cpath) != '.':
            self.cpath = self.cpath.parent
            self.dirs, self.files = self.tv.get_contents(self.cpath)
            self.init_var()

    def select_item(self, system):
        self.selected = self.sidebar.contents[self.sidebar.idx]
        self.search.is_word = None
        if self.selected in self.dirs:
            if self.search.is_file:
                self.cpath = self.purepath(self.selected)
            else:
                self.cpath = self.cpath/self.selected
            dirs, files = self.tv.get_contents(self.cpath)
            if len(dirs+files) == 0:
                self.message = ['empty directory.']
                self.cpath = self.cpath.parent
                return
            self.dirs = dirs
            self.files = files
            self.search.is_file = False
            self.init_var()
        else:
            if self.search.is_file:
                fpath = self.selected
            else:
                fpath = str(self.cpath/self.selected)
            self.mainwin.ud = 0
            self.mainwin.lr = 0
            # message of waiting for opening an item
            self.message = ['opening an item...']
            self.mainwin.update()
            self.info = self.show_func(fpath, cui=True,
                                       system=system, stdscr=self.stdscr)
            self.message = self.info.message.split("\n")
            self.message = [ln.replace("\t", "  ") for ln in self.message]

    def _down_main(self, num: int):
        if len(self.message) == 0:
            return
        elif self.mainwin.ud < len(self.message)-num-1:
            self.mainwin.ud += num
        else:
            self.mainwin.ud = len(self.message)-1

    def _up_main(self, num: int):
        if self.mainwin.ud < num:
            self.mainwin.ud = 0
        else:
            self.mainwin.ud -= num

    def _bottom_main(self):
        self.mainwin.down(len(self.message)-self.mainwin.ud-2)

    def _top_main(self):
        self.mainwin.up(self.mainwin.ud)

    def _shift_left_main(self, num: int):
        assert num >= 0, f'main shift left error: {num}'
        if self.mainwin.lr < num:
            self.mainwin.lr = 0
        else:
            self.mainwin.lr -= num

    def _shift_right_main(self, num: int):
        assert num >= 0, f'main shift right error: {num}'
        if self.wrap:
            return
        self.mainwin.lr += num
        if self.mainwin.max_lr-self.mainwin.lr <= self.mainwin.w-5:
            self.mainwin.lr = self.mainwin.max_lr-self.mainwin.w+5
        if self.mainwin.lr < 0:
            self.mainwin.lr = 0

    def _hat_main(self):
        self.mainwin.left(self.mainwin.lr)

    def _doll_main(self):
        self.mainwin.right(self.mainwin.max_lr-self.mainwin.lr)

    def file_search(self):
        # file name search mode
        uly = self.mainwin.h-self.search.h-2
        ulx = 0
        self.mainwin.b.clear()
        self.mainwin.b.addstr(uly-1, ulx, 'search file name: (empty cancel)',
                              curses.A_REVERSE)
        rectangle(self.mainwin.b, uly, ulx,
                  self.search.h+uly+1, self.mainwin.w-2)
        self.mainwin.b.refresh()
        self.search.b.clear()
        box = Textbox(self.search.b)
        box.edit(self.editer_cmd)
        search_file = box.gather()
        self.search.file = search_file.replace("\n", '').replace(" ", '')
        self.search.word = ''
        if len(self.search.file) == 0:
            self.mainwin.b.clear()
            self.mainwin.b.refresh()
        else:
            old_files = self.files.copy()
            old_dirs = self.dirs.copy()
            dirs, files = self.get_all_items()
            logger.debug('search files')
            logger.debug(f'files: {files}')
            logger.debug(f'dirs:  {dirs}')
            self.files = []
            self.dirs = []
            for i, f in enumerate(files):
                if re.search(self.search.file, f):
                    self.files.append(f)
            for i, d in enumerate(dirs):
                if re.search(self.search.file, d):
                    self.dirs.append(d)
            if len(self.files)+len(self.dirs) != 0:
                # find something
                self.search.is_file = True
                self.init_var()
            else:
                self.files = old_files
                self.dirs = old_dirs
            self.key = ''

    def word_search(self):
        # search mode in current file.
        uly = self.mainwin.h-self.search.h-2
        ulx = 0
        self.mainwin.b.addstr(uly-1, ulx, 'search word: (empty cancel)',
                              curses.A_REVERSE)
        rectangle(self.mainwin.b, uly, ulx,
                  self.search.h+uly+1, self.mainwin.w-2)
        self.mainwin.b.refresh()
        self.search.b.clear()
        box = Textbox(self.search.b)
        box.edit(self.editer_cmd)
        self.search.is_word = None
        search_word = box.gather()
        self.search.word = search_word.replace("\n", '')[:-1]
        self.search.file = ''
        self.jump_search_word(False)

    def jump_search_word(self, reverse=False):
        if not self.search.word:
            return
        if self.search.is_word is None:
            if reverse:
                start_line = self.mainwin.ud-1
            else:
                start_line = self.mainwin.ud
            start_col = 0
        else:
            start_line = self.search.is_word[1]
            if reverse:
                start_col = self.search.is_word[2]-1
            else:
                start_col = self.search.is_word[3]+1
        if reverse:
            lines = range(start_line, -1, -1)
        else:
            lines = range(start_line, len(self.message))
        for i in lines:
            if i == start_line:
                if reverse:
                    line = self.message[i][:start_col]
                    shift = 0
                else:
                    line = self.message[i][start_col:]
                    shift = start_col
            else:
                line = self.message[i]
                shift = 0
            self.search.cmt = f'"{self.search.word}" not found'
            if reverse:
                # find last match
                tmpall = re.findall(self.search.word, line)
                res = None
                for tmpstr in tmpall:
                    if res is None:
                        tmpst = 0
                    else:
                        tmpst += res.end()
                    res = re.search(self.search.word, line[tmpst:])
            else:
                tmpst = 0
                res = re.search(self.search.word, line)
            if res is not None:
                found_word = res.group()
                self.mainwin.down(i-self.mainwin.ud)
                col = res.start()+shift+tmpst
                if self.wrap:
                    col = col % self.mainwin.textw
                col -= self.mainwin.lr
                if col < 0:
                    self.mainwin.left(-col)
                else:
                    self.mainwin.right(col)
                self.search.cmt = ''
                self.search.is_word = (found_word, i,
                                       shift+tmpst+res.start(),
                                       shift+tmpst+res.end())
                break

    def jump_search_word_next(self):
        self.jump_search_word(False)

    def jump_search_word_pre(self):
        self.jump_search_word(True)

    def show_search_word(self, idx: int, line_cnt: int,
                         wrap_cnt: int, lr_start: int):
        if self.search.is_word is None:
            return
        if idx-1 == self.search.is_word[1]:
            if not self.wrap or \
               int(self.search.is_word[2]/self.mainwin.textw) == wrap_cnt:
                ser_st = self.search.is_word[2]-wrap_cnt*self.mainwin.textw
                ser_st -= self.mainwin.lr
                ser_end = self.search.is_word[3]-wrap_cnt*self.mainwin.textw
                if self.wrap and ser_end > self.mainwin.textw:
                    ser_end = self.mainwin.textw
                ser_end -= self.mainwin.lr
                if not self.wrap and ser_end > self.mainwin.textw:
                    ser_end = self.mainwin.textw
                if lr_start+ser_st < 0:
                    return
                elif ser_st > self.mainwin.textw:
                    return
                word_len = ser_end-ser_st
                self.mainwin.b.addnstr(line_cnt, lr_start+ser_st,
                                       self.search.is_word[0],
                                       word_len,
                                       curses.color_pair(8))

    def show_help_message(self):
        self.message = self.create_help_msg().split('\n')
        self.selected = '<help>'
        self.mainwin.ud = 0
        self.mainwin.lr = 0

    def toggle_wrap(self):
        self.wrap = not self.wrap

    def _update_side_bar(self):
        for i in range(self.sidebar.h):
            if i+self.sidebar.ud >= len(self.sidebar.contents):
                break
            cont = self.sidebar.contents[i+self.sidebar.ud]
            cidx = '{:2d} '.format(i+self.sidebar.ud)
            if cont in self.dirs:
                self.sidebar.b.addstr(i, 0, cidx, curses.color_pair(6))
                attr = curses.A_BOLD
            elif cont in self.files:
                self.sidebar.b.addstr(i, 0, cidx, curses.color_pair(7))
                attr = curses.A_NORMAL
            cont = cont[self.sidebar.lr:
                        self.sidebar.lr+self.sidebar.w-len(cidx)-1]
            if i+self.sidebar.ud == self.sidebar.idx:
                self.sidebar.b.addstr(i, len(cidx), cont, curses.A_REVERSE)
            else:
                self.sidebar.b.addstr(i, len(cidx), cont, attr)

    def _update_main_window(self):
        # show title
        title = self.get_title()
        self.mainwin.b.addnstr(0, 0, title, self.mainwin.w-1,
                               curses.A_REVERSE)
        if len(title) == 0:
            # skip if file is not set.
            return
        lentitle = len(title)+2
        if self.mainwin.w > lentitle:
            self.mainwin.b.addnstr(0, lentitle,
                                   '{}/{}, {}; {}'.format(
                                      self.mainwin.ud+1,
                                      len(self.message),
                                      self.mainwin.lr+1,
                                      self.search.cmt,
                                      ),
                                   self.mainwin.w-lentitle-1,
                                   curses.color_pair(5))
        if self.info.error:
            main_col = curses.color_pair(4)
        else:
            main_col = curses.color_pair(1)
        # show contents
        self.mainwin.lnwidth = len(str(len(self.message)))
        self.mainwin.max_lr = 0
        line_cnt = 1
        for i in range(1, self.mainwin.h):
            idx = i+self.mainwin.ud
            if idx > len(self.message):
                # reach the end of message
                break
            if self.line_number:
                textw = self.mainwin.w-self.mainwin.lnwidth-1
            else:
                textw = self.mainwin.w
            textw -= 2
            self.mainwin.textw = textw
            if self.wrap:
                messages = [self.message[idx-1][x:x+textw]
                            for x in range(0, len(self.message[idx-1]), textw)
                            ]
                if len(messages) == 0:
                    messages = ['']
            else:
                messages = [self.message[idx-1]]
            for j, msg in enumerate(messages):
                if line_cnt > self.mainwin.h-1:
                    # over the displayable line
                    break
                if self.line_number:
                    lr_st = self.mainwin.lnwidth+1
                else:
                    lr_st = 0
                if self.mainwin.max_lr <= len(msg):
                    self.mainwin.max_lr = len(msg)
                msg = msg[self.mainwin.lr:]
                try:
                    self.mainwin.b.addnstr(line_cnt, lr_st, msg,
                                           self.mainwin.w-2-lr_st,
                                           main_col)
                    self.show_search_word(idx, line_cnt, j, lr_st)
                    if self.line_number:
                        if j == 0:
                            numstr = f'{idx:0{self.mainwin.lnwidth}d}|'
                        else:
                            numstr = f'{" "*self.mainwin.lnwidth}|'
                        self.mainwin.b.addstr(line_cnt, 0, numstr)
                except Exception as e:
                    self.mainwin.b.addstr(line_cnt, 0,
                                          f'!! {e}'[:self.mainwin.textw],
                                          curses.color_pair(4))
                line_cnt += 1
        self.search.cmt = ''

    def _update_pwd_window(self):
        fname = str(self.fname)[-(self.topwin.w-3-6-1):]
        path = str(self.cpath)[-(self.topwin.w-5-14-1):]
        self.topwin.b.addstr(0, 3, f'file: {fname}', curses.A_BOLD)
        self.topwin.b.addstr(1, 5, f'current path: {path}')
        self.topwin.b.addstr(2, 1, self.exp[:self.topwin.w-1-1])

    def debug_log(self):
        log_str = f'''
===== LOG INFO =====
win size   : {self.winx}x{self.winy}
wrap       : {self.wrap}
line number: {self.line_number}
selected   : {self.selected}
key        : {self.key}
=== side bar ===
size                       : {self.sidebar.w}x{self.sidebar.h}
scrool (updown x leftright): {self.sidebar.ud}x{self.sidebar.lr}
selected index             : {self.sidebar.idx}
=== top window ===
size: {self.topwin.w}x{self.topwin.h}
=== main window ===
size                       : {self.mainwin.w}x{self.mainwin.h}
scrool (updown x leftright): {self.mainwin.ud}x{self.mainwin.lr}
max width                  : {self.mainwin.max_lr}
line number width          : {self.mainwin.lnwidth}
text width                 : {self.mainwin.textw}
=== search mode ===
size          : {self.search.w}x{self.search.h}
is_file_search: {self.search.is_file}
is_word_search: {self.search.is_word}
search_file   : {self.search.file}
search_word   : {self.search.word}
==========='''
        logger.debug(log_str)

    def debug_info(self):
        self.topwin.b.addstr(0, int(self.winx*2/3), ' '*(int(self.winx/3)-1))
        self.topwin.b.addstr(0, int(self.winx*2/3),
                             '{}x{} {}x{} {}x{} k:{}'.format(
                             self.topwin.h, self.topwin.w,
                             self.sidebar.h, self.sidebar.w,
                             self.mainwin.h, self.mainwin.w, self.key))
        self.topwin.b.addstr(1, int(self.winx*2/3), ' '*(int(self.winx/3)-1))
        self.topwin.b.addstr(1, int(self.winx*2/3),
                             's:{}-{}-{}-{} m:{}-{}-{}'.format(
                             len(self.sidebar.contents),
                             self.sidebar.ud, self.sidebar.lr,
                             self.sidebar.idx, len(self.message),
                             self.mainwin.ud, self.mainwin.lr))
        self.topwin.b.addstr(2, int(self.winx*2/3), ' '*(int(self.winx/3)-1))
        if self.search.is_word is not None:
            self.topwin.b.addnstr(2, int(self.winx*2/3), '{:d}-{:d}'.format(
                                  self.search.is_word[1],
                                  self.search.is_word[2]),
                                  int(self.winx/3)-1)
        self.topwin.b.refresh()

    def add_key_maps(self, key, config):
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
        self.sidebar.contents = self.dirs+self.files
        self.set_keymap()
        stdscr.refresh()

        while self.key != 'q':
            # showed indices are sidebar.ud ~ sidebar.ud+sidebar.h
            if self.key == '':
                upm, upt, ups = True, True, True
            else:
                upm, upt, ups = False, False, False
            if self.key in self.keymaps:
                func, args, _, _, upm, upt, ups = self.keymaps[self.key]
                func(*args)

            self.sidebar.contents = self.dirs+self.files

            if upm:
                self.mainwin.update()
            if upt:
                self.topwin.update()
            if ups:
                self.sidebar.update()
            if GLOBAL_CONF.debug:
                self.debug_info()
            self.key = self.stdscr.getkey()


def interactive_cui(fname: str, filetype: str,
                    get_contents: GC, show_func: SF,
                    purepath: PPath = PurePath) -> None:
    """
    provide the CUI (TUI) to show the contents.

    Parameters
    ----------
    fname: str
        An opened file name.
    filetype: str
        File type name of the script calling this function.
    get_contents: Callable[[PurePath], tuple[list[str], list[str]]]
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
    purepath: PurePath, PurePosixPath, or PureWindowsPath
        Specify the class to treat the path-like object.
        This is because in some case, the separator shoud be '/' not '\\'
        even if the OS is Windows.

    Returns
    -------
    None
    """
    cpath = purepath('.')
    tv = TreeViewer('.', get_contents, purepath=purepath, logger=logger)
    curses_cui = CursesCUI(filetype, purepath)
    curses_cui.disable_stream_handler()
    try:
        curses.wrapper(curses_cui.main, fname, show_func, cpath, tv)
    except AssertionError as e:
        print_error('curses closed due to an error.')
        print_error(f'error message: {e}')
