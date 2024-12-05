import argparse
from pathlib import Path
from email.parser import BytesParser
from email import policy

from aftviewer import Args, help_template


def add_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument()
    pass


def show_help() -> None:
    helpmsg = help_template('e-mail', 'Open and read e-mail (.eml) file.',
                            add_args)
    print(helpmsg)


def main(fpath: Path, args: Args):
    with open(fpath, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)
    for key, val in msg.items():
        print(f'----- {key} -----')
        print(f'    {val}')
