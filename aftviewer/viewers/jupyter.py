from __future__ import annotations

import os
import sys
import json
import base64
import tempfile
from pathlib import Path
from logging import getLogger
from typing import Any

from .. import (GLOBAL_CONF, Args, args_chk, cprint, show_image_file,
                print_error, get_config, get_col, help_template,
                add_args_imageviewer, add_args_output, add_args_verbose,
                add_args_encoding)

if 'Pygments' in GLOBAL_CONF.pack_list:
    from pygments import highlight
    from pygments.lexer import Lexer
    from pygments.lexers import get_lexer_by_name
    from pygments.formatters import TerminalFormatter, Terminal256Formatter
    from pygments.util import ClassNotFound
    use_pygments = True
else:
    use_pygments = False

logger = getLogger(GLOBAL_CONF.logname)
logger.info(f'use_pygments: {use_pygments}')


def show_output(output: dict[str, Any], args: Args, cnt: str,
                out_obj, tmpdir: tempfile.TemporaryDirectory):
    if out_obj == sys.stdout:
        header = ''
    else:
        header = '# '
    if 'text' in output:
        for text in output['text']:
            print(f'{header}{text}', end='', file=out_obj)
        print(file=out_obj)
    if 'data' in output:
        out_data = output['data']
        for out_type in out_data:
            if out_type == 'text/plain':
                for text in out_data['text/plain']:
                    print(f'{header}{text}', end='', file=out_obj)
                print(file=out_obj)
            elif out_type == 'image/png':
                if out_obj != sys.stdout:
                    # --output case
                    continue
                img_code = out_data['image/png']
                img_bin = base64.b64decode(img_code.encode())
                tmpfile = f'{tmpdir.name}/out-{cnt}.png'
                add_idx = 0
                while Path(tmpfile).is_file():
                    tmpfile = f'{tmpdir.name}/out-{cnt}_{add_idx}.png'
                    add_idx += 1
                with open(tmpfile, 'wb') as tmp:
                    tmp.write(img_bin)
                    ret = show_image_file(tmpfile, args, wait=False)
                if ret is None:
                    print_error('image viewer is not found.')
                elif not ret:
                    print_error('failed to open an image.')


def syntax_text(text: str, out_obj, lexer: Lexer | None,
                fmter: TerminalFormatter | Terminal256Formatter | None
                ) -> str:
    if not use_pygments:
        return text
    elif fmter is None:
        return text
    elif lexer is None:
        return text
    elif text.startswith('!') or text.startswith('%'):
        return text
    elif out_obj != sys.stdout:
        return text
    else:
        return highlight(text, lexer, fmter)


def add_args(parser):
    add_args_imageviewer(parser)
    add_args_verbose(parser, help='Show all cells at once.')
    add_args_output(parser, help='Output the information to'
                    ' the specified file as a Python script.')
    add_args_encoding(parser)
    parser.add_argument('--language', '-l',
                        help='Specify the language for syntax highlight.',
                        default=None)


def show_help():
    helpmsg = help_template('jupyter', 'show the saved jupyter notebook.',
                            add_args)
    print(helpmsg)


def main(fpath, args):
    if args_chk(args, 'encoding'):
        enc = args.encoding
    else:
        enc = get_config('encoding')

    with open(fpath, 'r', encoding=enc) as f:
        data = json.load(f)
    logger.debug(f'keys: {data.keys()}')
    if args_chk(args, 'output'):
        outp = Path(args.output)
        if outp.is_dir():
            print_error(f'{args.output} is a directory. please specify a file.')
            return
        if not outp.parent.is_dir():
            outp.parent.mkdir(parents=True)
        with open(outp, 'w') as f:
            f.write('#! /usr/bin/env python3\n')
        outf = open(outp, 'a')
        header = '# '
        fgi, bgi = (None, None)
        fgo, bgo = (None, None)
        fgt, bgt = (None, None)
    else:
        outf = sys.stdout
        header = ''
        fgi, bgi = get_col('input_color')
        fgo, bgo = get_col('output_color')
        fgt, bgt = get_col('type_color')

    tmpdir = tempfile.TemporaryDirectory()
    logger.info(f'tmpdir: {tmpdir.name}')

    meta = data['metadata']
    logger.debug(f'meta data: {meta}')
    if args_chk(args, 'verbose'):
        print(f'{header}kernel   : {meta["kernelspec"]["display_name"]}',
              file=outf)
        if 'language_info' in meta:
            print(f'{header}language : {meta["language_info"]["name"]}-{meta["language_info"]["version"]}',
                  file=outf)
        if 'colab' in meta:
            print(f'{header}colab : {meta["colab"]["name"]}', file=outf)

    # set formatter
    hi_text = get_config('syntax_highlight')
    fmt_style = get_config('highlight_style')
    if not hi_text or not use_pygments:
        fmter = None
    elif os.environ.get('TERM') == 'xterm-256color':
        fmter = Terminal256Formatter(style=fmt_style)
    else:
        fmter = TerminalFormatter(style=fmt_style)
    logger.debug(f'formatter: {fmter} / {fmt_style}')

    # set language and Lexer
    if args.language is not None:
        lang = args.language
    else:
        lang = get_config('language')
    if lang is None and 'language_info' in meta:
        lang = meta['language_info']['name']
    logger.info(f'language: {lang}')
    if lang is None or not use_pygments:
        lexer = None
    else:
        try:
            lexer = get_lexer_by_name(lang)
        except ClassNotFound:
            logger.warning(f'lexer for {lang} not found.')
            lexer = None
    logger.debug(f'lexer: {lexer}')

    L = len(data['cells'])
    show_num = get_config('show_number')
    for i, cell in enumerate(data['cells']):
        logger.debug(f'\n---- cell ----\n{cell}\n---------------')
        if show_num:
            num = f' ({i+1}/{L})'
        else:
            num = ''
        if cell['cell_type'] == 'code':
            cnt = cell['execution_count']
            if cnt is None:
                cnt = ' '
            # Input
            cprint(f'{header}In [{cnt}]{num}',
                   fg=fgi, bg=bgi, file=outf)
            for instr in cell['source']:
                if instr.startswith('!'):
                    # shell command
                    outtext = f'{header}{instr}'
                elif instr.startswith('%'):
                    # magic command
                    outtext = f'{header}{instr}'
                else:
                    outtext = syntax_text(instr, outf, lexer, fmter)
                print(outtext, end='', file=outf)
            print(file=outf)
            # Output
            if len(cell['outputs']) != 0:
                cprint(f'{header}Out [{cnt}]{num}',
                       fg=fgo, bg=bgo, file=outf)
            for output in cell['outputs']:
                show_output(output, args, cnt, outf, tmpdir)
        elif cell['cell_type'] == 'markdown':
            cprint(f'{header}markdown{num}',
                   fg=fgt, bg=bgt, file=outf)
            for instr in cell['source']:
                print(f'{header}{instr}', end='', file=outf)
            print(file=outf)
        elif cell['cell_type'] == 'raw':
            cprint(f'{header}raw{num}',
                   fg=fgt, bg=bgt, file=outf)
            for instr in cell['source']:
                print(f'{header}{instr}', end='', file=outf)
            print(file=outf)

        else:
            logger.error(f'not a supported type of cell: {cell["cell_type"]}')

        if not (args_chk(args, 'verbose') or args_chk(args, 'output')):
            key = input(' >>> Press ENTER to continue or "quit" to break: ')
            if key == 'quit':
                break

    if args_chk(args, 'verbose'):
        input('Press ENTER to close file.')
    outf.close()
    tmpdir.cleanup()
    logger.info('cleanup tmpdir.')
