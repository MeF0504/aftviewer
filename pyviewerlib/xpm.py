import os
import sys
import tempfile
import subprocess
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from pymeflib.xpm_loader import XPMLoader
from pymeflib.color import make_bitmap
from . import get_image_viewer, clear_mpl_axes, get_exec_cmds,\
    debug_print, debug


def main(fpath, args):
    img_viewer, mod = get_image_viewer(args)
    if img_viewer is None:
        print("I can't find any libraries to show image. Please install Pillow or matplotlib.")
        return

    xpm = XPMLoader(fpath)
    xpm.xpm_to_ndarray()
    data = xpm.ndarray
    width = xpm.info['width']
    height = xpm.info['height']

    debug_print('{}\n  use {}'.format(data.shape, img_viewer))
    if img_viewer == 'PIL':
        Image = mod
        img = Image.fromarray(data)
        img.show(title=os.path.basename(fpath))
    elif img_viewer == 'matplotlib':
        plt = mod
        fig1 = plt.figure(figsize=(width/100, height/100))
        # full display
        ax1 = fig1.add_axes((0, 0, 1, 1))
        ax1.imshow(data)
        clear_mpl_axes(ax1)
        plt.show()
    elif img_viewer == 'OpenCV':
        cv2 = mod
        img = data[:, :, [2, 1, 0, 3]]  # RGBA -> BGRA
        cv2.imshow(os.path.basename(fpath), img)
        cv2.waitKey(0)
        # cv2.destroyAllWindows()
    else:
        with tempfile.NamedTemporaryFile(suffix='.bmp') as tmp:
            make_bitmap(tmp.name, data, verbose=debug)
            cmds = get_exec_cmds(args, tmp.name)
            subprocess.run(cmds)
            # wait to open file. this is for, e.g., open command on Mac OS.
            input('Press Enter to continue')
