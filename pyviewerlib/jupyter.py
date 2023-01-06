import json
import base64
import io
import tempfile
import subprocess
import time

from . import args_chk, cprint, debug_print,\
    clear_mpl_axes, get_image_viewer, get_exec_cmds

def main(fpath, args):
    img_viewer, mod = get_image_viewer(args)

    with open(fpath, 'r') as f:
        data = json.load(f)
    debug_print('keys: {}'.format(data.keys()))

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

    tmp_images = []
    for cell in data['cells']:
        debug_print('{}\n{}\n{}'.format(
            ' ---- cell ----', cell, '---------------'))
        if cell['cell_type'] == 'code':
            cnt = cell['execution_count']
            if cnt is None:
                cnt = ' '
            # Input
            cprint('In [{}]'.format(cnt), fg='c')
            for instr in cell['source']:
                print(instr, end='')
            print()
            # Output
            if len(cell['outputs']) != 0:
                cprint('Out [{}]'.format(cnt), fg='r')
            for output in cell['outputs']:
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
                            if img_viewer is None:
                                continue
                            img_code = out_data['image/png']
                            img_bin = base64.b64decode(img_code.encode())
                            if img_viewer == 'PIL':
                                Image = mod
                                with Image.open(io.BytesIO(img_bin)) as img:
                                    # title doesn't work?
                                    img.show(title='Out [{}]'.format(cnt))
                            elif img_viewer == 'matplotlib':
                                plt = mod
                                with tempfile.NamedTemporaryFile(suffix='.png') as tmp:
                                    tmp.write(img_bin)
                                    img = plt.imread(tmp.name)
                                fig1 = plt.figure()
                                ax11 = fig1.add_axes((0, 0, 1, 1))
                                ax11.imshow(img)
                                clear_mpl_axes(ax11)
                                plt.show()
                            elif img_viewer == 'OpenCV':
                                cv2 = mod
                                with tempfile.NamedTemporaryFile(suffix='.png') as tmp:
                                    tmp.write(img_bin)
                                    img = cv2.imread(tmp.name)
                                cv2.imshow('Out [{}]'.format(cnt), img)
                                cv2.waitKey(500)
                            else:
                                tmp = tempfile.NamedTemporaryFile(suffix='.png')
                                tmp_images.append(tmp)
                                tmp.write(img_bin)
                                cmds = get_exec_cmds(args, tmp.name)
                                subprocess.run(cmds)
                                if args_chk(args, 'verbose'):
                                    time.sleep(1.)

        elif cell['cell_type'] == 'markdown':
            cprint('markdown', fg='g')
            for instr in cell['source']:
                print(instr, end='')
            print()

        elif cell['cell_type'] == 'raw':
            cprint('raw', fg='g')
            for instr in cell['source']:
                print(instr, end='')
            print()

        else:
            debug_print('not a supported type of cell: {}'.format(cell['cell_type']))

        if not args_chk(args, 'verbose'):
            input(' >>> Press ENTER to continue')

    # image closing
    for tmp in tmp_images:
        debug_print('close {}'.format(tmp.name))
        tmp.close()
    if img_viewer == 'OpenCV':
        if args_chk(args, 'verbose'):
            cv2.waitKey(0)
        cv2.destroyAllWindows()
