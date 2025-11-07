import json
import argparse
import os
import pprint
from functools import partial
from pathlib import Path, PurePath
from logging import getLogger

from pymeflib.tree2 import show_tree

from aftviewer import (Args, GLOBAL_CONF, args_chk, get_config,
                       show_keys_dict, get_item_dict,
                       get_contents_dict, show_func_dict,
                       interactive_view, interactive_cui,
                       help_template, add_args_specification,
                       add_args_encoding)

logger = getLogger(GLOBAL_CONF.logname)


def add_info(data, pargs, cpath):
    # remove root dir = file name.
    path = '/'.join(PurePath(cpath).parts[1:])
    tmp_data = get_item_dict(data, path)
    if isinstance(tmp_data, dict):
        return '', ''
    else:
        res = pprint.pformat(tmp_data, **pargs)
        return '', f' :{res}'


def add_args(parser: argparse.ArgumentParser) -> None:
    add_args_encoding(parser)
    add_args_specification(parser, verbose=True, key=True,
                           interactive=True, cui=True)


def show_help() -> None:
    helpmsg = help_template('show_json', 'Show contents in the JSON file.',
                            add_args)
    print(helpmsg)


def main(fpath: Path, args: Args):
    if args_chk(args, 'encoding'):
        logger.info('set encoding from args')
        encoding = args.encoding
    else:
        encoding = get_config('encoding')
    logger.info(f'encoding: {encoding}')
    pargs = get_config('pp_kwargs')

    with open(fpath, 'r', encoding=encoding) as f:
        data = json.load(f)
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
                addinfo = partial(add_info, data, pargs)
            else:
                addinfo = None
            show_tree(fname, gc, logger=logger, add_info=addinfo)
    else:
        pprint.pprint(data, **pargs)
