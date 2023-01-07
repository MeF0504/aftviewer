import os
import sys
import tempfile
import subprocess
from pathlib import Path

import rawpy

sys.path.append(str(Path(__file__).parent.parent))
from pymeflib.color import make_bitmap
from . import get_image_viewer, clear_mpl_axes, get_exec_cmds,\
    debug_print, debug, show_image_ndarray
try:
    from screeninfo import get_monitors
except ImportError:
    get_screen = False
else:
    get_screen = True


def main(fpath, args):
    img_viewer, mod = get_image_viewer(args)
    if img_viewer is None:
        print("I can't find any libraries to show image. Please install Pillow or matplotlib.")
        return

    with rawpy.imread(str(fpath)) as raw:
        rgb = raw.postprocess(demosaic_algorithm=rawpy.DemosaicAlgorithm.LINEAR)

    debug_print('{}\n  use {}'.format(rgb.shape, img_viewer))
    show_image_ndarray(rgb, os.path.basename(fpath), args)
    # if img_viewer == 'PIL':
    #     Image = mod
    #     img = Image.fromarray(rgb)
    #     img.show(title=os.path.basename(fpath))
    # elif img_viewer == 'matplotlib':
    #     plt = mod
    #     if get_screen:
    #         height = get_monitors()[0].height
    #     else:
    #         height = 1080   # assume a full-HD display
    #     rate = rgb.shape[0]/height*100
    #     h = int(rgb.shape[0]/rate)
    #     w = int(rgb.shape[1]/rate)
    #     fig1 = plt.figure(figsize=(w, h))
    #     # full display
    #     ax1 = fig1.add_axes((0, 0, 1, 1))
    #     ax1.imshow(rgb)
    #     clear_mpl_axes(ax1)
    #     plt.show()
    # elif img_viewer == 'OpenCV':
    #     cv2 = mod
    #     img = rgb[:, :, ::-1]  # RGB -> BGR
    #     cv2.imshow(os.path.basename(fpath), img)
    #     cv2.waitKey(0)
    #     # cv2.destroyAllWindows()
    # else:
    #     with tempfile.NamedTemporaryFile(suffix='.bmp') as tmp:
    #         make_bitmap(tmp.name, rgb, verbose=debug)
    #         cmds = get_exec_cmds(args, tmp.name)
    #         subprocess.run(cmds)
    #         # wait to open file. this is for, e.g., open command on Mac OS.
    #         input('Press Enter to continue')
