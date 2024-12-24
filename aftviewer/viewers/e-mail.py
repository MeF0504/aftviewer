import argparse
from pathlib import Path
from email.parser import BytesParser
from email import policy
from logging import getLogger

from .. import (GLOBAL_CONF, Args, help_template, print_key,
                add_args_encoding, add_args_specification, get_config)
logger = getLogger(GLOBAL_CONF.logname)


def add_args(parser: argparse.ArgumentParser) -> None:
    kwargs_k = dict(help='Specify the key of header info.')
    kwargs_v = dict(help='Show all header names and its values.')
    add_args_specification(parser, verbose=True, key=True,
                           interactive=False, cui=False,
                           kwargs_k=kwargs_k, kwargs_v=kwargs_v)
    add_args_encoding(parser)


def show_help() -> None:
    helpmsg = help_template('e-mail', 'Read an e-mail file.',
                            add_args)
    print(helpmsg)


def main(fpath: Path, args: Args):
    with open(fpath, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)

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
        for k in keys:
            if k in msg:
                print(f'{k}: {msg[k]}')
            else:
                logger.error(f'"{k}" not found in the email header.')
        if msg.is_multipart():
            logger.info('multi part')
            for part in msg.walk():
                cont_type = part.get_content_type()
                cont_dp = str(part.get("Content-Disposition"))
                logger.info(f'type: {cont_type}, disposition: {cont_dp}')

                if cont_type == "text/plain" and \
                   "attachment" not in cont_dp:
                    payload = part.get_payload(decode=True)
                    print(payload.decode(encoding, errors="replace"))
        else:
            logger.info('single part')
            payload = msg.get_payload(decode=True)
            print(payload.decode(encoding, errors="replace"))
