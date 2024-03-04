import sys
import json
import base64
import tempfile
from pathlib import Path

from . import args_chk, cprint, debug_print, show_image_file, \
    get_config, help_template, get_image_viewer, \
    add_args_imageviewer, add_args_output, add_args_verbose


def show_output(output, args, out_obj):
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
                img_viewer = get_image_viewer(args)
                if img_viewer == 'None':
                    if out_obj == sys.stdout:
                        print('image viewer is None')
                else:
                    img_code = out_data['image/png']
                    img_bin = base64.b64decode(img_code.encode())
                    with tempfile.NamedTemporaryFile(suffix='.png') as tmp:
                        tmp.write(img_bin)
                        show_image_file(tmp.name, args)


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
    debug_print('keys: {}'.format(data.keys()))
    if args_chk(args, 'output'):
        outp = Path(args.output)
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
        debug_print('{}'.format(meta))
        print(f'{header}kernel   : {meta["kernelspec"]["display_name"]}',
              file=outf)
        if 'language_info' in meta:
            print(f'{header}language : {meta["language_info"]["name"]}-{meta["language_info"]["version"]}',
                  file=outf)
        if 'colab' in meta:
            print(f'{header}colab : {meta["colab"]["name"]}', file=outf)

    for cell in data['cells']:
        debug_print('{}\n{}\n{}'.format(
            ' ---- cell ----', cell, '---------------'))
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
            debug_print('not a supported type of cell: {}'.format(cell['cell_type']))

        if not (args_chk(args, 'verbose') or args_chk(args, 'output')):
            input(' >>> Press ENTER to continue')

    outf.close()
