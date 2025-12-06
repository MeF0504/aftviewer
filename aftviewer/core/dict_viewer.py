import pprint
from pathlib import PurePath
from logging import getLogger
from typing import Any

from . import GLOBAL_CONF, print_key, print_error, get_config
from .types import ReturnMessage as RM

logger = getLogger(GLOBAL_CONF.logname)


def show_keys_dict(data: dict, key: list[Any]):
    """
    Show the detailed information of specified keys in the dictionary.
    If key is an empty list, list all the keys in the dictionary.

    Parameters
    ----------
    data: dict
        target data.
    key: list[Any]
        List of keys to be shown.

    Returns
    -------
    None
    """
    pargs = get_config('pp_kwargs')
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
    """
    Get the value of the specified path.

    Parameters
    ----------
    data: dict
        target data.
    cpath: str
        path to the item. In this function, the dictionary is treated
        like a directory, and other values are treated like files.

    Returns
    -------
    None
    """
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


def get_contents_dict(data: dict, path: str) -> tuple[list[str], list[str]]:
    """
    Get lists of directories and files for a specified path.
    This function is available as the input to the interactive
    and interactive_cui viewers.
    See https://github.com/MeF0504/aftviewer/wiki/Extension#get_contents.

    Parameters
    ----------
    data: dict
        target data.
    path: str
        path to the item.

    Returns
    -------
    list[str], list[str]
        lists of directories and files.
    """
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


def show_func_dict(data: dict, cpath: str, **kwargs) -> RM:
    """
    Return the detailed information of the specified path.
    This function is available as the input to the interactive
    and interactive_cui viewers.
    See https://github.com/MeF0504/aftviewer/wiki/Extension#show_func.

    Parameters
    ----------
    data: dict
        target data.
    cpath: str
        path to the item shown.

    Returns
    -------
    ReturnMessage
        result message. This includes the detailed information message
        of the specified path and the flag of the error message.
    """
    tmp_data = get_item_dict(data, cpath)
    pargs = get_config('pp_kwargs')
    if tmp_data is None:
        return RM(f'warning! no key {cpath} or the value is None', False)
    res = pprint.pformat(tmp_data, **pargs)
    return RM(res, False)
