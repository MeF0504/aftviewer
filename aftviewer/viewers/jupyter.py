from __future__ import annotations

import sys
import json
import base64
import tempfile
from pathlib import Path
from logging import getLogger
from typing import Any

from .. import (GLOBAL_CONF, Args, args_chk, cprint, show_image_file,
                print_error, get_config, get_col, help_template,
                add_args_imageviewer, add_args_output, add_args_verbose)
logger = getLogger(GLOBAL_CONF.logname)


def show_output(output: dict[str, Any], args: Args, cnt: str,
                out_obj, tmpdir: None | tempfile.TemporaryDirectory):
    if out_obj == sys.stdout:
        header = ''
    else:
        header = '# '
    if 'text' in output:
        for text in output['text']:
            print(f'{header}{text}', end='', file=out_obj)
        print(file=out_obj)
    elif 'data' in output:
        out_data = output['data']
        for out_type in out_data:
            if out_type == 'text/plain':
                for text in out_data['text/plain']:
                    print(f'{header}{text}', end='', file=out_obj)
                print(file=out_obj)
            elif out_type == 'image/png':
                img_code = out_data['image/png']
                img_bin = base64.b64decode(img_code.encode())
                if out_obj != sys.stdout:
                    # --output case
                    continue
                elif tmpdir is None:
                    # normal case
                    with tempfile.NamedTemporaryFile(suffix='.png') as tmp:
                        tmp.write(img_bin)
                        ret = show_image_file(tmp.name, args, wait=True)
                else:
                    # --verbose case
                    tmpfile = f'{tmpdir.name}/out-{cnt}.png'
                    add_idx = 0
                    while Path(tmpfile).is_file():
                        tmpfile = f'{tmpdir.name}/out-{cnt}_{add_idx}.png'
                        add_idx += 1
                    with open(tmpfile, 'wb') as tmp:
                        tmp.write(img_bin)
                        ret = show_image_file(tmpfile, args, wait=False)
                    pass
                if ret is None:
                    print_error('image viewer is not found.')
                elif not ret:
                    print_error('failed to open an image.')


def add_args(parser):
    add_args_imageviewer(parser)
    add_args_verbose(parser, help='Show all cells at once.')
    add_args_output(parser, help='Output the information to'
                    ' the specified file as a Python script.')


def show_help():
    helpmsg = help_template('jupyter', 'show the saved jupyter notebook.',
                            add_args)
    print(helpmsg)


def main(fpath, args):
    with open(fpath, 'r') as f:
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

    tmpdir = None
    meta = data['metadata']
    logger.debug(f'meta data: {meta}')
    if args_chk(args, 'verbose'):
        tmpdir = tempfile.TemporaryDirectory()
        logger.info(f'tmpdir: {tmpdir.name}')
        print(f'{header}kernel   : {meta["kernelspec"]["display_name"]}',
              file=outf)
        if 'language_info' in meta:
            print(f'{header}language : {meta["language_info"]["name"]}-{meta["language_info"]["version"]}',
                  file=outf)
        if 'colab' in meta:
            print(f'{header}colab : {meta["colab"]["name"]}', file=outf)

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
                    outtext = f'{header}{instr}'
                elif instr.startswith('%'):
                    outtext = f'{header}{instr}'
                else:
                    outtext = instr
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
    if tmpdir is not None:
        tmpdir.cleanup()
        logger.info('cleanup tmpdir.')
