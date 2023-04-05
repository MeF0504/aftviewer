from pymeflib.color import FG, BG, END
from .core import debug, json_opts, type_config
from .core import debug_print, args_chk, cprint, print_key, \
    interactive_view, run_system_cmd
from .core.image_viewer import get_image_viewer, clear_mpl_axes, \
    get_exec_cmds, show_image_file, show_image_ndarray, is_image
try:
    from .core.cui import interactive_cui
except ImportError as e:
    debug_print(e)

    def interactive_cui(*args, **kwargs):
        print('failed to import the interactive_cui function.')
        print('maybe the curses module is not available.')
        return
