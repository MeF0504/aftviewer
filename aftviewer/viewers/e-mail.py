import argparse
from pathlib import Path
from email.parser import BytesParser
from email import policy
from logging import getLogger

from .. import GLOBAL_CONF, Args, help_template, print_key, add_args_encoding
logger = getLogger(GLOBAL_CONF.logname)


def add_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('-k', '--key',
                        help='Specify the key of header info.',
                        dest='key',
                        nargs='*')
    parser.add_argument('-v', '--verbose',
                        help='Show all header names and its values.',
                        dest='verbose',
                        action='store_true')
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
