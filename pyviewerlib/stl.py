from stl import mesh

from . import get_image_viewer


def main(fpath, args):
    print('Warning! This type is testing yet.')
    img_viewer = get_image_viewer(args)
    if img_viewer is None:
        print("I can't find any libraries to show image. Please install Pillow or matplotlib.")
        return

    data = mesh.Mesh.from_file(fpath)

    if img_viewer == 'matplotlib':
        import matplotlib.pyplot as plt
        from mpl_toolkits import mplot3d
        fig1 = plt.figure()
        ax11 = fig1.add_subplot(111, projection='3d')
        ax11.add_collection3d(
                mplot3d.art3d.Poly3DCollection(
                    data.vectors, linewidth=0.7,
                    edgecolors='Black', facecolor='Grey'))
        scale = data.points.flatten()
        ax11.auto_scale_xyz(scale, scale, scale)
        # ax11.axis('off')
        ax11.set_xticks([])
        ax11.set_yticks([])
        ax11.set_zticks([])
        plt.show()
    else:
        print('Currently this type only supports matplotlib as an image viewer.')
        return
