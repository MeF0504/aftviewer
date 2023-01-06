import os
import sqlite3
from functools import partial

from . import args_chk, print_key, cprint, debug_print,\
    interactive_view, interactive_cui
from libtree import branch_str
try:
    from tabulate import tabulate
except ImportError:
    print("I can't find tabulate library.")
    is_tabulate = False
else:
    is_tabulate = True


def show_table(cursor, table_path, cui=False, verbose=True):
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
            cursor.execute('select {} from {}'.format(column, table))
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
    return res, None


def main(fpath, args):
    database = sqlite3.connect(fpath)
    cursor = database.cursor()
    cursor.execute("select name from sqlite_master where type='table'")
    tables = cursor.fetchall()

    if args_chk(args, 'interactive') or args_chk(args, 'cui'):
        # make list_tree
        list_tree = [{}]
        for table, in tables:
            debug_print('{}'.format(table))
            list_tree[0][table] = [{}]
            cursor.execute("pragma table_info('{}')".format(table))
            table_info = cursor.fetchall()
            for tinfo in table_info:
                debug_print('{}'.format(tinfo))
                name = tinfo[1]
                list_tree[0][table].append(name)
        if args_chk(args, 'interactive'):
            fname = os.path.basename(fpath)
            interactive_view(list_tree, fname, partial(show_table, cursor))
        elif args_chk(args, 'cui'):
            interactive_cui(list_tree, fpath, partial(show_table, cursor))

    elif args_chk(args, 'key'):
        if len(args.key) == 0:
            for t in tables:
                print(t[0])
        for k in args.key:
            print_key(k)
            info, err = show_table(cursor, k, verbose=True)
            if err is None:
                print("\n".join(info))
                print()
            else:
                cprint(err, fg='r')
    else:
        for table, in tables:
            info, err = show_table(cursor, table, args.verbose)
            if err is None:
                print("\n".join(info))
