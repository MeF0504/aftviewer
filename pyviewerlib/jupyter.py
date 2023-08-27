import json
import base64
import tempfile

from . import args_chk, cprint, debug_print, show_image_file,\
    get_config, help_template


def show_output(output, args):
    if 'text' in output:
        for text in output['text']:
            print(text, end='')
        print()
    elif 'data' in output:
        out_data = output['data']
        for out_type in out_data:
            if out_type == 'text/plain':
                for text in out_data['text/plain']:
                    print(text, end='')
                print()
            elif out_type == 'image/png':
                img_code = out_data['image/png']
                img_bin = base64.b64decode(img_code.encode())
                with tempfile.NamedTemporaryFile(suffix='.png') as tmp:
                    tmp.write(img_bin)
                    show_image_file(tmp.name, args)


def show_help():
    helpmsg = help_template('jupyter', 'show the saved jupyter notebook.',
                             sup_iv=True, sup_v=True)
    print(helpmsg)


def main(fpath, args):
    with open(fpath, 'r') as f:
        data = json.load(f)
    debug_print('keys: {}'.format(data.keys()))
    fgi, bgi = get_config('jupyter', 'input_color')
    fgo, bgo = get_config('jupyter', 'output_color')
    fgt, bgt = get_config('jupyter', 'type_color')

    if args_chk(args, 'verbose'):
        meta = data['metadata']
        debug_print('{}'.format(meta))
        print('kernel   : {}'.format(meta['kernelspec']['display_name']))
        if 'language_info' in meta:
            print('language : {}-{}'.format(
                    meta['language_info']['name'],
                    meta['language_info']['version']))
        if 'colab' in meta:
            print('colab : {}'.format(meta['colab']['name']))

    for cell in data['cells']:
        debug_print('{}\n{}\n{}'.format(
            ' ---- cell ----', cell, '---------------'))
        if cell['cell_type'] == 'code':
            cnt = cell['execution_count']
            if cnt is None:
                cnt = ' '
            # Input
            cprint('In [{}]'.format(cnt), fg=fgi, bg=bgi)
            for instr in cell['source']:
                print(instr, end='')
            print()
            # Output
            if len(cell['outputs']) != 0:
                cprint('Out [{}]'.format(cnt), fg=fgo, bg=bgo)
            for output in cell['outputs']:
                show_output(output, args)
        elif cell['cell_type'] == 'markdown':
            cprint('markdown', fg=fgt, bg=bgt)
            for instr in cell['source']:
                print(instr, end='')
            print()
        elif cell['cell_type'] == 'raw':
            cprint('raw', fg=fgt, bg=bgt)
            for instr in cell['source']:
                print(instr, end='')
            print()

        else:
            debug_print('not a supported type of cell: {}'.format(cell['cell_type']))

        if not args_chk(args, 'verbose'):
            input(' >>> Press ENTER to continue')
