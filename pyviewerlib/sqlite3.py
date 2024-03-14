import os
import sqlite3
from functools import partial
from pathlib import PurePath
from logging import getLogger
try:
    import curses
except ImportError:
    import_curses = False
else:
    import_curses = True

from . import GLOBAL_CONF, args_chk, print_key, cprint, get_col, \
    interactive_view, help_template, add_args_specification, add_args_output
from . import ReturnMessage as RM
from pymeflib.tree2 import branch_str, TreeViewer
from .core.cui import CursesCUI
try:
    from tabulate import tabulate
except ImportError:
    print("I can't find tabulate library.")
    is_tabulate = False
else:
    is_tabulate = True
sel_items = ''
logger = getLogger(GLOBAL_CONF.logname)


def show_table(cursor, tables, table_path,
               verbose=True, output=None, **kwargs):
    shift = '  '
    res = []
    is_csv = (type(output) is str) and output.endswith('csv')
    if '/' in table_path:
        table, column = table_path.split('/')
        if column == '':
            column = None
        # debug_print('table, column: {}, {}'.format(table, column))
        logger.debug(f'table, column: {table}, {column}')
    else:
        table = table_path
        column = None
        # debug_print('table: {}'.format(table))
        logger.debug(f'table: {table}')

    if table not in tables:
        return RM('{} not in tables'.format(table), True)
    cursor.execute("pragma table_info('{}')".format(table))
    table_info = cursor.fetchall()

    if is_csv:
        # debug_print('save CSV file')
        logger.debug('save CSV file')
        res.append(f'# {table}')
    else:
        res.append(table)
    if not verbose:
        for tinfo in table_info:
            if tinfo[2] == '':
                ctype = 'none'
            else:
                ctype = tinfo[2]
            res.append('{}{} [ {} ]'.format(branch_str, tinfo[1], ctype))

    else:
        if column is None:
            headers = []
            for tinfo in table_info:
                headers.append(tinfo[1])
            cursor.execute('select * from {}'.format(table))
        else:
            headers = column.split(',')
            try:
                cursor.execute('select {} from {}'.format(column, table))
            except sqlite3.OperationalError:
                return RM('Incorrect columns: {}'.format(column), True)
        columns = cursor.fetchall()
        table_items = []
        for col in columns:
            table_items.append([])
            for item in col:
                table_items[-1].append(item)

        if is_csv:
            res.append(','.join(headers))
            for itms in table_items:
                res.append(','.join([str(x) for x in itms]))
        elif is_tabulate:
            table_str = tabulate(table_items, headers, tablefmt='orgtbl')
            table_str = table_str.replace('\n', '\n'+shift)
            res.append(shift + table_str)
        else:
            tmp_res = ''
            tmp_res += shift+'|'
            for hd in headers:
                tmp_res += ' {} |'.format(hd)
            res.append(tmp_res)
            for itms in table_items:
                tmp_res = ''
                tmp_res += shift+'|'
                for itm in itms:
                    tmp_res += ' {} |'.format(itm)
                res.append(tmp_res)
    if output is None or not verbose:
        return RM('\n'.join(res), False)
    else:
        with open(output, 'a') as f:
            f.write('\n'.join(res))
            f.write('\n\n')
        return RM(f'{table_path} is saved', False)


def get_contents_i(cursor, tables, path):
    return [], tables


def get_contents_c(cursor, tables, path):
    if str(path) == '.':
        # at root
        return tables, []
    else:
        files = []
        cursor.execute("pragma table_info('{}')".format(path))
        table_info = cursor.fetchall()
        for tinfo in table_info:
            name = tinfo[1]
            files.append(name)
        return [], files


def add_contents(curs):
    # wrapper of core.cui.CursesCUI.select_item
    global sel_items
    curs.sel_cont = curs.contents[curs.sel_idx]
    if curs.sel_cont in curs.dirs:
        if curs.is_search:
            curs.cpath = curs.purepath(curs.sel_cont)
        else:
            curs.cpath = curs.cpath/curs.sel_cont
        curs.dirs, curs.files = curs.tv.get_contents(curs.cpath)
        curs.is_search = False
        curs.init_var()
    else:
        if curs.is_search:
            fpath = sel_items
        else:
            if '/' in sel_items:
                cols = os.path.basename(sel_items).split(',')
                # debug_log(f'{cols}')
                logger.debug(f'cols: {cols}')
                if curs.sel_cont not in cols:
                    sel_items += f',{curs.sel_cont}'
            else:
                sel_items = str(curs.cpath/curs.sel_cont)
            fpath = sel_items
        # debug_log(f'set {fpath}')
        logger.debug(f'set {fpath}')
        curs.main_shift_ud = 0
        curs.main_shift_lr = 0
        # message of waiting for opening an item
        curs.message = ['opening an item...']
        curs.update_main_window()
        curs.info = curs.show_func(fpath, cui=True)
        curs.message = curs.info.message.split("\n")
        curs.message = [ln.replace("\t", "  ") for ln in curs.message]
        curs.scroll_doll = max([len(ln) for ln in curs.message]) -\
            (curs.winx-curs.win_w)+5
        if curs.scroll_doll < 0:
            curs.scroll_doll = 0


def clear_items(curs):
    global sel_items
    sel_items = ''
    curs.go_up_sidebar()


def init_outfile(output):
    if output is None:
        return
    dirname = os.path.dirname(output)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    with open(output, 'w') as f:
        f.write('')
    print(f'file is created at {output}')


def add_args(parser):
    add_args_output(parser)
    add_args_specification(parser, verbose=True, key=True,
                           interactive=True, cui=True)


def show_help():
    helpmsg = help_template('sqlite3', 'show the contents of the database. ' +
                            'In this type, you can specify multiple columns ' +
                            'by "-k table/col,col2". ' +
                            'NOTE: --output is supported when --verbose or ' +
                            '--key is specified. ' +
                            'If extension of the output file is".csv",' +
                            'it is saved as the CSV file.',
                            add_args)
    print(helpmsg)


def main(fpath, args):
    database = sqlite3.connect(fpath)
    cursor = database.cursor()
    cursor.execute("select name from sqlite_master where type='table'")
    tables = [table[0] for table in cursor.fetchall()]
    fname = os.path.basename(fpath)

    if args_chk(args, 'interactive'):
        gc = partial(get_contents_i, cursor, tables)
        interactive_view(fname, gc, partial(show_table, cursor, tables))
    elif args_chk(args, 'cui'):
        # interactive_cui(fname, gc, partial(show_table, cursor, tables))
        if not import_curses:
            print('failed to import curses.')
            return
        gc = partial(get_contents_c, cursor, tables)
        tv = TreeViewer('.', gc, PurePath)
        curses_cui = CursesCUI()
        curses_cui.add_key_maps('\n', [add_contents, [curses_cui], '<CR>',
                                       'open/add the item in the main window',
                                       True, True, True])
        curses_cui.add_key_maps('KEY_ENTER', [add_contents, [curses_cui],
                                              '', '', True, True, True])
        curses_cui.add_key_maps('KEY_SR', [clear_items, [curses_cui], 'S-↑',
                                           'go up the path or quit the search mode',
                                           True, True, True])
        curses_cui.add_key_maps('KEY_SUP', [clear_items, [curses_cui],
                                            '', '', True, True, True])
        try:
            curses.wrapper(curses_cui.main, fname,
                           partial(show_table, cursor, tables),
                           PurePath('.'), tv)
        except AssertionError as e:
            print(e)
    elif args_chk(args, 'key'):
        if len(args.key) == 0:
            for t in tables:
                print(t)
            return
        init_outfile(args.output)
        for k in args.key:
            print_key(k)
            fg, bg = get_col('msg_error')
            info = show_table(cursor, tables, k, verbose=True,
                              output=args.output)
            if not info.error:
                print(info.message)
                print()
            else:
                cprint(info.message, fg=fg, bg=bg)
    else:
        if args_chk(args, 'verbose'):
            init_outfile(args.output)
        for table in tables:
            info = show_table(cursor, tables, table, verbose=args.verbose,
                              output=args.output)
            if not info.error:
                print(info.message)
