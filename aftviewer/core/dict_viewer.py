import pprint
from pathlib import PurePath
from logging import getLogger
from typing import Any

from . import GLOBAL_CONF, print_key, print_error, get_config
from .types import ReturnMessage as RM

logger = getLogger(GLOBAL_CONF.logname)
pargs = get_config('pp_kwargs')


def show_keys_dict(data: dict, key: Any):
    if key:
        for k in key:
            if k in data:
                print_key(str(k))
                pprint.pprint(data[k], **pargs)
            else:
                print_error(f'"{k}" not in this file.')
    else:
        for k in data:
            print(k)


def get_item_dict(data: dict, cpath: str):
    tmp_data = data
    for k in PurePath(cpath).parts:
        tmp_data_update = False
        for key in tmp_data.keys():
            if str(key) == k:
                tmp_data = tmp_data[key]
                tmp_data_update = True
                break
        if not tmp_data_update:
            logger.error(f'key not found: {cpath}, {k}')
            return None
    return tmp_data


def get_contents_dict(data: dict, path: str):
    dirs = []
    files = []
    tmp_data = get_item_dict(data, path)
    if tmp_data is None:
        return [], []
    if isinstance(tmp_data, dict):
        for k in tmp_data.keys():
            if isinstance(tmp_data[k], dict):
                dirs.append(str(k))
            else:
                files.append(str(k))
    dirs.sort()
    files.sort()
    return dirs, files


def show_func_dict(data: dict, cpath: str, **kwargs):
    tmp_data = get_item_dict(data, cpath)
    if tmp_data is None:
        return RM(f'warning! no key {cpath} or the value is None', False)
    res = pprint.pformat(tmp_data, **pargs)
    return RM(res, False)
