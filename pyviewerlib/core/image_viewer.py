import os
import sys
import tempfile
import subprocess
import mimetypes
from pathlib import Path

try:
    from screeninfo import get_monitors
except ImportError:
    get_screen = False
else:
    get_screen = True

from . import args_chk, debug_print, debug, json_opts
sys.path.append(str(Path(__file__).parent.parent.parent))
from pymeflib.color import make_bitmap
from pymeflib.util import chk_cmd

# image viewer
Image = None
plt = None
cv2 = None
img_viewer = None
run_giv = False


def get_image_viewer(args):
    global img_viewer
    global run_giv
    if run_giv:
        return img_viewer
    global Image
    global plt
    global cv2
    if args_chk(args, 'image_viewer'):
        debug_print('set image viewer from args')
        img_viewer = args.image_viewer
        if img_viewer == 'PIL':
            from PIL import Image
        elif img_viewer == 'matplotlib':
            import matplotlib.pyplot as plt
        elif img_viewer == 'OpenCV':
            import cv2
        else:
            # external command
            if not chk_cmd(img_viewer, debug):
                img_viewer = None
    else:
        debug_print('search available image_viewer')
        try:
            from PIL import Image
            debug_print(' => image_viewer: PIL')
        except ImportError:
            try:
                import matplotlib.pyplot as plt
                debug_print(' => image_viewer: matplotlib')
            except ImportError:
                try:
                    import cv2
                    debug_print(' => image_viewer: OpenCV')
                except ImportError:
                    debug_print("can't find image_viewer")
                    img_viewer = None
                else:
                    img_viewer = 'OpenCV'
            else:
                img_viewer = 'matplotlib'
        else:
            img_viewer = 'PIL'
    run_giv = True
    return img_viewer


def clear_mpl_axes(axes):
    # not display axes
    axes.xaxis.set_visible(False)
    axes.yaxis.set_visible(False)
    axes.spines['top'].set_visible(False)
    axes.spines['bottom'].set_visible(False)
    axes.spines['right'].set_visible(False)
    axes.spines['left'].set_visible(False)


def get_exec_cmds(args, fname):
    if 'exec_cmd' in json_opts:
        res = []
        for cmd in json_opts['exec_cmd']:
            if cmd == '%s':
                res.append(fname)
            elif cmd == '%c':
                res.append(args.image_viewer)
            else:
                res.append(cmd)
    else:
        res = [args.image_viewer, fname]
    debug_print('executed command: {}'.format(res))
    return res


def show_image_file(img_file, args, disable_cond=False):
    name = os.path.basename(img_file)
    img_viewer = get_image_viewer(args)
    debug_print('  use {}'.format(img_viewer))
    if disable_cond:
        return False
    if not os.path.isfile(img_file):
        debug_print('image file {} in not found'.format(img_file))
        return False
    if img_viewer is None:
        print("I can't find any libraries to show image. Please install Pillow or matplotlib.")
        return False
    elif img_viewer == 'PIL':
        with Image.open(img_file) as image:
            image.show(title=name)
    elif img_viewer == 'matplotlib':
        img = plt.imread(img_file)
        fig1 = plt.figure()
        ax11 = fig1.add_axes((0, 0, 1, 1))
        ax11.imshow(img)
        clear_mpl_axes(ax11)
        plt.show()
        plt.close(fig1)
    elif img_viewer == 'OpenCV':
        img = cv2.imread(img_file)
        cv2.imshow(name, img)
        cv2.waitKey(0)
        cv2.destroyWindow(name)
    else:
        cmds = get_exec_cmds(args, img_file)
        subprocess.run(cmds)
        # wait to open file. this is for, e.g., open command on Mac OS.
        input('Press Enter to continue')
    return True


def show_image_ndarray(data, name, args, disable_cond=False):
    img_viewer = get_image_viewer(args)
    debug_print('{}\n  use {}'.format(data.shape, img_viewer))
    if disable_cond:
        return False
    if img_viewer is None:
        print("I can't find any libraries to show image. Please install Pillow or matplotlib.")
        return False
    elif img_viewer == 'PIL':
        with Image.fromarray(data) as image:
            image.show(title=name)
    elif img_viewer == 'matplotlib':
        if get_screen:
            height = get_monitors()[0].height
        else:
            height = 540
        rate = data.shape[0]/height*100
        h = int(data.shape[0]/rate)
        w = int(data.shape[1]/rate)
        fig1 = plt.figure(figsize=(w, h))
        # full display
        ax1 = fig1.add_axes((0, 0, 1, 1))
        ax1.imshow(data)
        clear_mpl_axes(ax1)
        plt.show()
        plt.close(fig1)
    elif img_viewer == 'OpenCV':
        if data.shape[2] == 3:
            img = data[:, :, ::-1]  # RGB -> BGR
        elif data.shape[2] == 4:
            img = data[:, :, [2, 1, 0, 3]]  # RGBA -> BGRA
        else:
            print('invalid data shape')
            return False
        cv2.imshow(name, img)
        cv2.waitKey(0)
        cv2.destroyWindow(name)
    else:
        with tempfile.NamedTemporaryFile(suffix='.bmp') as tmp:
            make_bitmap(tmp.name, data, verbose=debug)
            cmds = get_exec_cmds(args, tmp.name)
            subprocess.run(cmds)
            # wait to open file. this is for, e.g., open command on Mac OS.
            input('Press Enter to continue')
    return True


def is_image(path):
    mime = mimetypes.guess_type(path)[0]
    if mime is None:
        return False
    elif mime.split('/')[0] == 'image':
        return True
    else:
        return False
