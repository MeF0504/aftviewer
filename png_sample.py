import os
import subprocess
import importlib.machinery as imm
pyv = imm.SourceFileLoader('pyv', './pyviewer').load_module()

def main_png(fpath, args):
    if args.image_viewer == 'PIL':
        from PIL import Image
        image = Image.open(fpath)
        image.show(title=os.path.basename(fpath))
    elif args.image_viewer == 'matplotlib':
        import matplotlib.pyplot as plt
        fig1 = plt.figure()
        ax1 = fig1.add_axes((0, 0, 1, 1))
        image = plt.imread(fpath)
        ax1.imshow(image)
        pyv.clear_mpl_axes(ax1)
        plt.show()
    elif args.image_viewer == 'OpenCV':
        import cv2
        image = cv2.omread(fpath)
        cv2.imshow(os.path.basename(fpath), image)
    else:
        cmds = pyv.get_exec_cmds(args, fpath)
        subprocess.run(cmds)

if __name__ == '__main__':
    print('hello')

