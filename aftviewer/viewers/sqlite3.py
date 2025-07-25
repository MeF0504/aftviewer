import os
import sqlite3
from functools import partial
from pathlib import PurePosixPath
from logging import getLogger
# curses is not supported on Windows by default.
try:
    import curses
except ImportError:
    import_curses = False
else:
    import_curses = True

from .. import (GLOBAL_CONF, args_chk, print_key, cprint, print_error,
                interactive_view, help_template, add_args_specification,
                add_args_output)
from .. import ReturnMessage as RM
from pymeflib.tree2 import BRANCH_STR1, TreeViewer
from ..core.cui import CursesCUI
if 'tabulate' in GLOBAL_CONF.pack_list:
    from tabulate import tabulate
    is_tabulate = True
else:
    print("I can't find tabulate library.")
    is_tabulate = False
sel_items = ''
logger = getLogger(GLOBAL_CONF.logname)
logger.info(f'use tabulate: {is_tabulate}')


def show_table(cursor, tables, table_path,
               verbose=True, output=None, **kwargs):
    shift = '  '
    res = []
    is_csv = (type(output) is str) and output.endswith('csv')
    if '/' in table_path:
        table, column = table_path.split('/')
        if column == '':
            column = None
        logger.info(f'table, column: {table}, {column}')
    else:
        table = table_path
        column = None
        logger.info(f'table: {table}')

    if table not in tables:
        return RM('{} not in tables'.format(table), True)
    cursor.execute("pragma table_info('{}')".format(table))
    table_info = cursor.fetchall()

    if is_csv:
        logger.info('save CSV file')
        res.append(f'# {table}')
    else:
        res.append(table)
    if not verbose:
        for tinfo in table_info:
            if tinfo[2] == '':
                ctype = 'none'
            else:
                ctype = tinfo[2]
            res.append('{}{} [ {} ]'.format(BRANCH_STR1, tinfo[1], ctype))

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
        return sorted(tables), []
    else:
        files = []
        cursor.execute("pragma table_info('{}')".format(path))
        table_info = cursor.fetchall()
        for tinfo in table_info:
            name = tinfo[1]
            files.append(name)
        return [], sorted(files)


def add_col(selected_contents: str):
    global sel_items
    cols = os.path.basename(sel_items).split(',')
    logger.debug(f'cols: {cols}')
    if selected_contents not in cols:
        sel_items += f',{selected_contents}'


def add_contents(curs: CursesCUI):
    # wrapper of core.cui.CursesCUI.select_item
    global sel_items
    curs.selected = curs.sidebar.contents[curs.sidebar.idx]
    curs.search.is_word = None
    if curs.selected in curs.dirs:
        if curs.search.is_file:
            curs.cpath = curs.purepath(curs.selected)
        else:
            curs.cpath = curs.cpath/curs.selected
        curs.dirs, curs.files = curs.tv.get_contents(curs.cpath)
        curs.search.is_file = False
        curs.init_var()
    else:
        if curs.search.is_file:
            if '/' in sel_items and \
               sel_items.split('/')[0] == curs.selected.split('/')[0]:
                # same table
                add_col(curs.selected.split('/')[1])
            else:
                sel_items = curs.selected
            fpath = sel_items
        else:
            if '/' in sel_items:
                add_col(curs.selected)
            else:
                sel_items = str(curs.cpath/curs.selected)
            fpath = sel_items
        logger.info(f'set {fpath}')
        curs.mainwin.ud = 0
        curs.mainwin.lr = 0
        # message of waiting for opening an item
        curs.message = ['opening an item...']
        curs.mainwin.update()
        curs.info = curs.show_func(fpath, cui=True)
        curs.message = curs.info.message.split("\n")
        curs.message = [ln.replace("\t", "  ") for ln in curs.message]


def clear_items(curs: CursesCUI):
    global sel_items
    sel_items = ''
    curs.sidebar.go_up()


def get_db_title():
    global sel_items
    if '/' in sel_items:
        return sel_items.split('/')[1]
    else:
        return sel_items


def init_outfile(output):
    if output is None:
        return True
    if len(output) == 0:
        print_error('incorrect output file is set.')
        return False
    if os.path.isdir(output):
        print_error(f'{output} is a directory. please specify a file.')
        return False
    dirname = os.path.dirname(output)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    with open(output, 'w') as f:
        f.write('')
    print(f'file is created at {output}')
    return True


def add_args(parser):
    kwargs_k = dict(help='Specify the tables/columns to show.'
                    ' You can specify multiple columns by'
                    ' "-k table/col1,col2".')
    kwargs_v = dict(help='Show all tables and columns.')
    add_args_specification(parser, verbose=True, key=True,
                           interactive=True, cui=True,
                           kwargs_k=kwargs_k, kwargs_v=kwargs_v)
    add_args_output(parser, help='Output database information to'
                    ' the specified file.'
                    ' This option can be used when --verbose or'
                    ' --key is specified.'
                    ' If the file extension is ".csv", it is saved as'
                    ' a CSV file. Otherwise, it is saved as a text file.')


def show_help():
    helpmsg = help_template('sqlite3', 'show the contents of the database.',
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
        if not import_curses:
            print('failed to import curses.')
            return
        gc = partial(get_contents_c, cursor, tables)
        tv = TreeViewer('.', gc, purepath=PurePosixPath, logger=logger)
        curses_cui = CursesCUI()
        curses_cui.add_key_maps('\n', [add_contents, [curses_cui], '<CR>',
                                       'open/add the item in the main window',
                                       True, True, True])
        curses_cui.add_key_maps('KEY_ENTER', [add_contents, [curses_cui],
                                              '', '', True, True, True])
        curses_cui.add_key_maps('KEY_SR', [clear_items, [curses_cui], 'S-↑',
                                           'go up the path or quit'
                                           ' the search mode',
                                           True, True, True])
        curses_cui.get_title = get_db_title
        curses_cui.add_key_maps('KEY_SUP', [clear_items, [curses_cui],
                                            '', '', True, True, True])
        curses_cui.disable_stream_handler()
        curses_cui.wrap = False
        try:
            curses.wrapper(curses_cui.main, fname,
                           partial(show_table, cursor, tables),
                           PurePosixPath('.'), tv)
        except AssertionError as e:
            print(e)
    elif args_chk(args, 'key'):
        if len(args.key) == 0:
            for t in tables:
                print(t)
            return
        if not init_outfile(args.output):
            cprint('failed to created an output file.')
            return
        for k in args.key:
            print_key(k)
            info = show_table(cursor, tables, k, verbose=True,
                              output=args.output)
            if not info.error:
                print(info.message)
                print()
            else:
                print_error(info.message)
    else:
        if args_chk(args, 'verbose'):
            if not init_outfile(args.output):
                cprint('failed to created an output file.')
                return
        for table in tables:
            info = show_table(cursor, tables, table, verbose=args.verbose,
                              output=args.output)
            if not info.error:
                print(info.message)
