from . import show_image_file, help_template, add_args_imageviewer


def add_args(parser):
    add_args_imageviewer(parser)


def show_help():
    helpmsg = help_template('png_sample', 'show a png image.', add_args)
    print(helpmsg)


def main(fpath, args):
    show_image_file(str(fpath), args)
