import argparse
import tempfile
import base64
from pathlib import Path
from email.parser import BytesParser
from email import policy, message, header
import mailbox
from logging import getLogger

from .. import (GLOBAL_CONF, Args, help_template, print_key, print_error,
                show_image_file, get_config, run_system_cmd, get_timezone,
                add_args_encoding, add_args_specification,
                add_args_imageviewer)
logger = getLogger(GLOBAL_CONF.logname)


def add_args(parser: argparse.ArgumentParser) -> None:
    kwargs_k = dict(help='Specify the key of header info.')
    kwargs_v = dict(help='Show all header names and its values.')
    add_args_specification(parser, verbose=True, key=True,
                           interactive=False, cui=False,
                           kwargs_k=kwargs_k, kwargs_v=kwargs_v)
    add_args_imageviewer(parser)
    add_args_encoding(parser)
    type_group = parser.add_mutually_exclusive_group()
    type_group.add_argument('--eml', help='Fource read the file'
                            ' using the email package.', action='store_true')
    type_group.add_argument('--mbox', help='Fource read the file'
                            ' using the mailbox.mbox package.',
                            action='store_true')
    parser.add_argument('--html',
                        help='output mail as html file if it possible.',
                        action='store_true')


def show_help() -> None:
    helpmsg = help_template('e-mail', 'Read an e-mail file.',
                            add_args)
    print(helpmsg)


def show_headers(keys: list[str], msg: message.Message) -> None:
    for k in keys:
        if k in msg:
            info = msg[k]
            if hasattr(info, 'datetime'):
                date_fmt = get_config('date_format')
                tz = get_timezone()
                date = info.datetime.astimezone(tz)
                print(f'{k}: {date.strftime(date_fmt)}')
            else:
                b, enc = header.decode_header(info)[0]
                if enc is None:
                    head = b
                else:
                    head = b.decode(enc)
                print(f'{k}: {head}')
        else:
            logger.error(f'"{k}" not found in the email header.')


def show_msg(msg: message.Message, args: Args):
    if args.encoding is None:
        encoding = 'utf-8'
    else:
        encoding = args.encoding

    if args.verbose:
        for key, val in msg.items():
            print_key(key)
            print(val)
    else:
        keys = args.key
        if keys is None:
            keys = get_config('headers')
        show_headers(keys, msg)
        if msg.is_multipart():
            logger.info('multi part')
            tmpdir = tempfile.TemporaryDirectory()
            idx = 1
            for part in msg.walk():
                cont_type = part.get_content_type()
                cont_dp = str(part.get("Content-Disposition"))
                logger.info(f'type: {cont_type}, disposition: {cont_dp}')

                if cont_type == "text/plain" and \
                   "attachment" not in cont_dp and not args.html:
                    payload = part.get_payload(decode=True)
                    print(payload.decode(encoding, errors="replace"))
                elif cont_type.startswith('image'):
                    payload = part.get_payload(decode=False)
                    img_bin = base64.b64decode(payload.encode())
                    ex = cont_type.split('/')[1]
                    fname = f'{tmpdir.name}/image{idx}.{ex}'
                    idx += 1
                    with open(fname, 'wb') as tmp:
                        tmp.write(img_bin)
                    ret = show_image_file(fname, args, wait=True)
                    if ret is None:
                        print('image viewer is not found.')
                    elif not ret:
                        print('failed to open an image.')
                elif args.html and cont_type == 'text/html':
                    fname = f'{tmpdir.name}/out{idx}.html'
                    idx += 1
                    payload = part.get_payload(decode=True)
                    with open(fname, 'w') as f:
                        f.write(payload.decode(encoding, errors="replace"))
                    run_system_cmd(fname)
            if args.html:
                input('Enter to close')
            tmpdir.cleanup()
        else:
            logger.info('single part')
            payload = msg.get_payload(decode=True)
            print(payload.decode(encoding, errors="replace"))


def show_eml(fpath: Path, args: Args):
    with open(fpath, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)
    show_msg(msg, args)


def show_mbox(fpath: Path, args: Args):
    for msg in mailbox.mbox(fpath):
        show_msg(msg, args)


def main(fpath: Path, args: Args):
    if args.eml:
        show_eml(fpath, args)
    elif args.mbox:
        show_mbox(fpath, args)
    elif fpath.name.endswith('.eml'):
        show_eml(fpath, args)
    elif fpath.name.endswith('.mbox'):
        show_mbox(fpath, args)
    else:
        print_error(f'Not supported file extension: {fpath}.')
