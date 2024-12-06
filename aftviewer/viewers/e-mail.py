import argparse
from pathlib import Path
from email.parser import BytesParser
from email import policy

from aftviewer import Args, help_template, print_key


def add_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('-k', '--key',
                        help='Specify the key of header info.',
                        dest='key',
                        nargs='*')
    parser.add_argument('-v', '--verbose',
                        help='Show all header names and its values.',
                        dest='verbose',
                        action='store_true')


def show_help() -> None:
    helpmsg = help_template('e-mail', 'Open and read e-mail file.',
                            add_args)
    print(helpmsg)


def main(fpath: Path, args: Args):
    with open(fpath, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)

    if args.verbose:
        for key, val in msg.items():
            print_key(key)
            print(val)
