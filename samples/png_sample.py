import os
import subprocess

from . import clear_mpl_axes, get_exec_cmds, get_image_viewer, show_image_file


def main(fpath, args):
    img_viewer, mod = get_image_viewer(args)
    show_image_file(fpath, args)
    # if img_viewer == 'PIL':
    #     Image = mod
    #     image = Image.open(fpath)
    #     image.show(title=os.path.basename(fpath))
    # elif img_viewer == 'matplotlib':
    #     plt = mod
    #     fig1 = plt.figure()
    #     ax1 = fig1.add_axes((0, 0, 1, 1))
    #     image = plt.imread(fpath)
    #     ax1.imshow(image)
    #     clear_mpl_axes(ax1)
    #     plt.show()
    # elif img_viewer == 'OpenCV':
    #     cv2 = mod
    #     image = cv2.omread(fpath)
    #     cv2.imshow(os.path.basename(fpath), image)
    # else:
    #     cmds = get_exec_cmds(args, fpath)
    #     subprocess.run(cmds)

if __name__ == '__main__':
    print('hello')

