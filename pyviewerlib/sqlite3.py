import os
import sqlite3
from functools import partial

from . import args_chk, print_key, cprint, debug_print, get_col,\
    interactive_view, interactive_cui, help_template
from . import ReturnMessage as RM
from pymeflib.tree2 import branch_str
try:
    from tabulate import tabulate
except ImportError:
    print("I can't find tabulate library.")
    is_tabulate = False
else:
    is_tabulate = True


def show_table(cursor, tables, table_path, verbose=True, **kwargs):
    shift = '  '
    res = []
    if '/' in table_path:
        table, column = table_path.split('/')
        if column == '':
            column = None
        debug_print('table, column: {}, {}'.format(table, column))
    else:
        table = table_path
        column = None
        debug_print('table: {}'.format(table))

    if table not in tables:
        return RM('{} not in tables'.format(table), True)
    cursor.execute("pragma table_info('{}')".format(table))
    table_info = cursor.fetchall()

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
        table = []
        for col in columns:
            table.append([])
            for item in col:
                table[-1].append(item)

        if is_tabulate:
            table_str = tabulate(table, headers, tablefmt='orgtbl')
            table_str = table_str.replace('\n', '\n'+shift)
            res.append(shift + table_str)
        else:
            tmp_res = ''
            tmp_res += shift+'|'
            for hd in headers:
                tmp_res += ' {} |'.format(hd)
            res.append(tmp_res)
            for itms in table:
                tmp_res = ''
                tmp_res += shift+'|'
                for itm in itms:
                    tmp_res += ' {} |'.format(itm)
                res.append(tmp_res)
    return RM('\n'.join(res), False)


def get_contents(cursor, tables, path):
    # this is enough?
    return [], tables
    # if str(path) == '.':
    #     return tables, []
    # else:
    #     files = []
    #     cursor.execute("pragma table_info('{}')".format(path))
    #     table_info = cursor.fetchall()
    #     for tinfo in table_info:
    #         name = tinfo[1]
    #         files.append(name)
    #     return [], files


def show_help():
    helpmsg = help_template('sqlite3', 'show the contents of the database. ' +
                            'In this type, you can specify multiple columns' +
                            ' by "-k table/col,col2".',
                            sup_v=True, sup_k=True, sup_i=True, sup_c=True)
    print(helpmsg)


def main(fpath, args):
    database = sqlite3.connect(fpath)
    cursor = database.cursor()
    cursor.execute("select name from sqlite_master where type='table'")
    tables = [table[0] for table in cursor.fetchall()]
    fname = os.path.basename(fpath)
    gc = partial(get_contents, cursor, tables)

    if args_chk(args, 'interactive'):
        interactive_view(fname, gc, partial(show_table, cursor, tables))
    elif args_chk(args, 'cui'):
        interactive_cui(fname, gc, partial(show_table, cursor, tables))
    elif args_chk(args, 'key'):
        if len(args.key) == 0:
            for t in tables:
                print(t)
        for k in args.key:
            print_key(k)
            fg, bg = get_col('error')
            info = show_table(cursor, tables, k, verbose=True)
            if not info.error:
                print(info.message)
                print()
            else:
                cprint(info.message, fg=fg, bg=bg)
    else:
        for table in tables:
            info = show_table(cursor, tables, table, verbose=args.verbose)
            if not info.error:
                print(info.message)
