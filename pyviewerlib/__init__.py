from pymeflib.color import FG, BG, FG256, BG256, END
# values
from .core import debug, json_opts, type_config
# functions
from .core import debug_print, args_chk, cprint, print_key, get_col,\
    set_numpy_format, interactive_view, run_system_cmd, show_opts
# class
from .core import ReturnMessage
from .core.image_viewer import get_image_viewer, is_image,\
    show_image_file, show_image_ndarray
from .core.helpmsg import help_template
try:
    from .core.cui import interactive_cui
except ImportError as e:
    debug_print(e)

    def interactive_cui(*args, **kwargs):
        print('failed to import the interactive_cui function.')
        print('maybe the curses module is not available.')
        return
