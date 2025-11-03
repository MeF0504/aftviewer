import pickle
import os
import pprint
from pathlib import PurePath
from functools import partial
from logging import getLogger

from .. import (GLOBAL_CONF, args_chk, get_config,
                show_keys_dict, get_item_dict,
                get_contents_dict, show_func_dict,
                interactive_view, interactive_cui,
                help_template, add_args_specification, add_args_encoding,
                )

from pymeflib.tree2 import show_tree
logger = getLogger(GLOBAL_CONF.logname)
pargs = get_config('pp_kwargs')


def add_info(data, cpath):
    # remove root dir = file name.
    path = '/'.join(PurePath(cpath).parts[1:])
    tmp_data = get_item_dict(data, path)
    if isinstance(tmp_data, dict):
        return '', ''
    else:
        res = pprint.pformat(tmp_data, **pargs)
        return '', f' :{res}'


def add_args(parser):
    add_args_encoding(parser)
    add_args_specification(parser, verbose=True, key=True,
                           interactive=True, cui=True)


def show_help():
    helpmsg = help_template('pickle', 'show the contents of the pickled file.',
                            add_args)
    print(helpmsg)


def main(fpath, args):
    if args_chk(args, 'encoding'):
        logger.info('set encoding from args')
        encoding = args.encoding
    else:
        encoding = get_config('encoding')
    logger.info(f'encoding: {encoding}')
    with open(fpath, 'rb') as f:
        data = pickle.load(f, encoding=encoding)
    fname = os.path.basename(fpath)
    gc = partial(get_contents_dict, data)

    if isinstance(data, dict):
        if args_chk(args, 'key'):
            show_keys_dict(data, args.key)
        elif args_chk(args, 'interactive'):
            interactive_view(fname, gc, partial(show_func_dict, data))
        elif args_chk(args, 'cui'):
            interactive_cui(fname, gc, partial(show_func_dict, data))
        else:
            if args_chk(args, 'verbose'):
                addinfo = partial(add_info, data)
            else:
                addinfo = None
            show_tree(fname, gc, logger=logger, add_info=addinfo)
    else:
        pprint.pprint(data, **pargs)
