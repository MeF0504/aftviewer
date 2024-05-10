import sys
import json
import base64
import tempfile
from pathlib import Path
from logging import getLogger

from .. import (GLOBAL_CONF, args_chk, cprint, show_image_file,
                get_config, get_col, help_template,
                add_args_imageviewer, add_args_output, add_args_verbose)
logger = getLogger(GLOBAL_CONF.logname)


def show_output(output, args, out_obj):
    fge, bge = get_col('msg_error')
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
                with tempfile.NamedTemporaryFile(suffix='.png') as tmp:
                    tmp.write(img_bin)
                    ret = show_image_file(tmp.name, args)
                    if out_obj == sys.stdout:
                        if ret is None:
                            cprint('image viewer is not found.',
                                   fg=fge, bg=bge)
                        elif not ret:
                            cprint('failed to open an image.', fg=fge, bg=bge)


def add_args(parser):
    add_args_imageviewer(parser)
    add_args_output(parser)
    add_args_verbose(parser)


def show_help():
    helpmsg = help_template('jupyter', 'show the saved jupyter notebook.' +
                            ' NOTE: If the --output option is specified,' +
                            ' the output file is saved as the python script.',
                            add_args)
    print(helpmsg)


def main(fpath, args):
    with open(fpath, 'r') as f:
        data = json.load(f)
    logger.debug(f'keys: {data.keys()}')
    if args_chk(args, 'output'):
        outp = Path(args.output)
        if outp.is_dir():
            fge, bge = get_col('msg_error')
            cprint(f'{args.output} is a directory. please specify a file.',
                   fg=fge, bg=bge)
            return
        if not outp.parent.is_dir():
            outp.parent.mkdir(parents=True)
        with open(outp, 'w') as f:
            f.write('#! /usr/bin/env python3\n')
        outf = open(outp, 'a')
        header = '# '
        fgi, bgi = ('', '')
        fgo, bgo = ('', '')
        fgt, bgt = ('', '')
    else:
        outf = sys.stdout
        header = ''
        fgi, bgi = get_config('jupyter', 'input_color')
        fgo, bgo = get_config('jupyter', 'output_color')
        fgt, bgt = get_config('jupyter', 'type_color')

    if args_chk(args, 'verbose'):
        meta = data['metadata']
        logger.debug(f'meta data: {meta}')
        print(f'{header}kernel   : {meta["kernelspec"]["display_name"]}',
              file=outf)
        if 'language_info' in meta:
            print(f'{header}language : {meta["language_info"]["name"]}-{meta["language_info"]["version"]}',
                  file=outf)
        if 'colab' in meta:
            print(f'{header}colab : {meta["colab"]["name"]}', file=outf)

    for cell in data['cells']:
        logger.debug(f'\n---- cell ----\n{cell}\n---------------')
        if cell['cell_type'] == 'code':
            cnt = cell['execution_count']
            if cnt is None:
                cnt = ' '
            # Input
            cprint(f'{header}In [{cnt}]', fg=fgi, bg=bgi, file=outf)
            for instr in cell['source']:
                print(instr, end='', file=outf)
            print(file=outf)
            # Output
            if len(cell['outputs']) != 0:
                cprint(f'{header}Out [{cnt}]', fg=fgo, bg=bgo, file=outf)
            for output in cell['outputs']:
                show_output(output, args, outf)
        elif cell['cell_type'] == 'markdown':
            cprint(f'{header}markdown', fg=fgt, bg=bgt, file=outf)
            for instr in cell['source']:
                print(f'{header}{instr}', end='', file=outf)
            print(file=outf)
        elif cell['cell_type'] == 'raw':
            cprint(f'{header}raw', fg=fgt, bg=bgt, file=outf)
            for instr in cell['source']:
                print(f'{header}{instr}', end='', file=outf)
            print(file=outf)

        else:
            logger.error(f'not a supported type of cell: {cell["cell_type"]}')

        if not (args_chk(args, 'verbose') or args_chk(args, 'output')):
            input(' >>> Press ENTER to continue')

    outf.close()
