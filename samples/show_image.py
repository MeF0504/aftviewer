try:
    from PIL import Image
except ImportError as e:
    print(type(e).__name__, e)
    is_pil = False
else:
    is_pil = True

from aftviewer import show_image_file, help_template, add_args_imageviewer


def add_args(parser):
    add_args_imageviewer(parser)


def show_help():
    helpmsg = help_template('show_image', 'show an image file.', add_args)
    print(helpmsg)


def main(fpath, args):
    if is_pil:
        print('EXIF data')
        img_data = Image.open(fpath)
        img_exif = img_data.getexif()
        for key, val in img_exif.items():
            print(f' 0x{key:4x}: {val}')
    show_image_file(str(fpath), args)
