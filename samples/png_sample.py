from . import show_image_file, help_template


def add_args(parser):
    pass


def show_help():
    helpmsg = help_template('png_sample', 'show a png image.')
    print(helpmsg)


def main(fpath, args):
    show_image_file(str(fpath), args)
