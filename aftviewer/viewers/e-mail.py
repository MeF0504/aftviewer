from __future__ import annotations

import argparse
import tempfile
import base64
import shutil
from pathlib import Path, PurePath
from email.parser import BytesParser
from email import policy, message, header
import mailbox
from logging import getLogger
from functools import partial

from .. import (GLOBAL_CONF, Args, help_template, print_key, print_error,
                show_image_file, get_config, run_system_cmd, get_timezone,
                args_chk, add_args_encoding, add_args_specification,
                add_args_imageviewer, interactive_cui, ReturnMessage as RM)
logger = getLogger(GLOBAL_CONF.logname)


def add_args(parser: argparse.ArgumentParser) -> None:
    kwargs_k = dict(help='Show the specified header info. '
                    'If no key is specified, show all header names and info.')
    kwargs_v = dict(help='Show the messages.')
    kwargs_c = dict(help='Show the file with interactive CUI mode.'
                    ' eml file is not supported.')
    add_args_specification(parser, verbose=True, key=True,
                           interactive=False, cui=True,
                           kwargs_k=kwargs_k, kwargs_v=kwargs_v,
                           kwargs_c=kwargs_c)
    add_args_imageviewer(parser)
    add_args_encoding(parser)
    parser.add_argument('--mailtype', '-mt',
                        help='Specify the package used to open the file.',
                        choices=['eml', 'mbox'], default=None)
    parser.add_argument('--html',
                        help='Show mail as html file if it possible.',
                        action='store_true')


def show_help() -> None:
    helpmsg = help_template('e-mail', 'Read an e-mail file.',
                            add_args)
    print(helpmsg)


def get_contents(mbox: mailbox.mbox,
                 path: PurePath) -> tuple[list[str], list[str]]:
    if path == Path('.'):
        file_list = []
        for i, msg in enumerate(mbox):
            headers = get_headers(['Subject'], msg)
            if len(headers) > 0:
                file_list.append(f'{i}: {headers[0]}')
            else:
                file_list.append(f'{i}: No Subject')
        return [], file_list
    else:
        return [], []


def show_func(mbox: mailbox.mbox, args: Args,
              in_tmp: tempfile.TemporaryDirectory,
              cpath: str, **kwargs) -> RM:
    title = PurePath(cpath).name
    idx = int(title.split(': ')[0])
    return get_msg(mbox[idx], args, in_tmp)


def get_headers(keys: list[str], msg: message.Message) -> list[str]:
    res = []
    for k in keys:
        if k in msg:
            info = msg[k]
            if hasattr(info, 'datetime'):
                date_fmt = get_config('date_format')
                tz = get_timezone()
                date = info.datetime.astimezone(tz)
                res.append(f'{k}: {date.strftime(date_fmt)}')
            else:
                b, enc = header.decode_header(info)[0]
                if enc is None:
                    if type(b) is bytes:
                        head = b.decode()
                    else:
                        head = b
                else:
                    try:
                        head = b.decode(enc)
                    except UnicodeDecodeError as e:
                        logger.error(f'Failed to decode header 1: {e}')
                        head = info
                    except LookupError as e:
                        logger.error(f'Failed to decode header 2: {e}')
                        head = info
                res.append(f'{k}: {head}')
        else:
            logger.error(f'"{k}" not found in the email header.')
    return res


def show_headers(keys: None | list[str], msg: message.Message) -> None:
    if keys is None:
        keys = get_config('headers')
    elif len(keys) == 0:
        for key, val in msg.items():
            print_key(key)
            print(val)
        return
    for head in get_headers(keys, msg):
        print(head)


def get_msg(msg: message.Message, args: Args,
            in_tmp: None | tempfile.TemporaryDirectory = None) -> RM:
    if args.encoding is None:
        encoding = 'utf-8'
    else:
        encoding = args.encoding

    ret_msg = []
    keys = get_config('headers')
    ret_msg += get_headers(keys, msg)
    ret_msg.append('')
    if msg.is_multipart():
        logger.info('multi part')
        if in_tmp is None:
            tmpdir = tempfile.TemporaryDirectory()
        else:
            tmpdir = in_tmp
        idx = 1
        for part in msg.walk():
            cont_type = part.get_content_type()
            cont_dp = str(part.get("Content-Disposition"))
            logger.info(f'type: {cont_type}, disposition: {cont_dp}')

            if cont_type == "text/plain" and \
               "attachment" not in cont_dp and not args.html:
                payload = part.get_payload(decode=True)
                logger.info('add text')
                ret_msg.append(payload.decode(encoding, errors="replace"))
            elif cont_type.startswith('image'):
                payload = part.get_payload(decode=False)
                img_bin = base64.b64decode(payload.encode())
                ex = cont_type.split('/')[1]
                fname = f'{tmpdir.name}/image{idx}.{ex}'
                idx += 1
                with open(fname, 'wb') as tmp:
                    tmp.write(img_bin)
                ret = show_image_file(fname, args, wait=True)
                logger.info(f'show image {ret}')
                if ret is None:
                    ret_msg.append('image viewer is not found.')
                elif not ret:
                    ret_msg.append('failed to open an image.')
            elif args.html and cont_type == 'text/html':
                logger.info('show html')
                fname = f'{tmpdir.name}/out{idx}.html'
                idx += 1
                payload = part.get_payload(decode=True)
                with open(fname, 'w') as f:
                    f.write(payload.decode(encoding, errors="replace"))
                run_system_cmd(fname)
        if args.html and not args_chk(args, 'cui'):
            input('Enter to close')
        if in_tmp is None:
            tmpdir.cleanup()
    else:
        logger.info('single part')
        payload = msg.get_payload(decode=True)
        ret_msg.append(payload.decode(encoding, errors="replace"))
    return RM('\n'.join(ret_msg), False)


def show_eml(fpath: Path, args: Args):
    with open(fpath, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)
    if args_chk(args, 'verbose') or (hasattr(args, 'html') and args.html):
        print(get_msg(msg, args).message)
    else:
        show_headers(args.key, msg)


def show_mbox(fpath: Path, args: Args):
    tmpdir = tempfile.TemporaryDirectory()
    if args_chk(args, 'cui'):
        mbox = mailbox.mbox(fpath, create=False)
        gc = partial(get_contents, mbox)
        sf = partial(show_func, mbox, args, tmpdir)
        interactive_cui(fpath.name, gc, sf)
    else:
        for i, msg in enumerate(mailbox.mbox(fpath, create=False)):
            term_size = shutil.get_terminal_size()
            print(f'|{i:<d}|',
                  '=-'*int((term_size.columns-8-len(str(i))*2)/2))
            if args_chk(args, 'verbose') \
               or (hasattr(args, 'html') and args.html):
                print(get_msg(msg, args, tmpdir).message)
            else:
                show_headers(args.key, msg)
    tmpdir.cleanup()


def main(fpath: Path, args: Args):
    if args.mailtype == 'eml':
        show_eml(fpath, args)
    elif args.mailtype == 'mbox':
        show_mbox(fpath, args)
    elif args.mailtype is None and fpath.name.endswith('.eml'):
        show_eml(fpath, args)
    elif args.mailtype is None and fpath.name.endswith('.mbox'):
        show_mbox(fpath, args)
    else:
        print_error(f'Not supported file extension: {fpath}.')
