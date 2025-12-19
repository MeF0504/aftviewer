import os
import pprint
import argparse
import plistlib
from pathlib import Path, PurePath
from functools import partial
from logging import getLogger

from .. import (Args, help_template, GLOBAL_CONF,
                args_chk, get_config, show_keys_dict, get_item_dict,
                get_contents_dict, show_func_dict,
                interactive_view, interactive_cui, add_args_specification,
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


def add_args(parser: argparse.ArgumentParser) -> None:
    add_args_specification(parser, verbose=True, key=True,
                           interactive=True, cui=True)


def show_help() -> None:
    helpmsg = help_template('plist', 'Organize and display'
                            ' the contents of a plist file.', add_args)
    print(helpmsg)


def main(fpath: Path, args: Args):
    with open(fpath, 'rb') as f:
        pl = plistlib.load(f, dict_type=dict)

    fname = os.path.basename(fpath)
    gc = partial(get_contents_dict, pl)

    if isinstance(pl, dict):
        if args_chk(args, 'key'):
            show_keys_dict(pl, args.key)
        elif args_chk(args, 'interactive'):
            interactive_view(fname, gc, partial(show_func_dict, pl))
        elif args_chk(args, 'cui'):
            interactive_cui(fname, gc, partial(show_func_dict, pl))
        else:
            if args_chk(args, 'verbose'):
                addinfo = partial(add_info, pl)
            else:
                addinfo = None
            show_tree(fname, gc, logger=logger, add_info=addinfo)
    else:
        pprint.pprint(pl, **pargs)
