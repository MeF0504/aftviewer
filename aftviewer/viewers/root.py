import argparse
from pathlib import Path
import pprint
from logging import getLogger


import uproot
import numpy as np  # uproot requires NumPy!

from .. import (GLOBAL_CONF, Args, get_config, args_chk,
                print_key, print_warning,
                help_template, add_args_key, add_args_verbose)
from .numpy import show_summary
from pymeflib import plot as mefplot


logger = getLogger(GLOBAL_CONF.logname)
__drawer: None | str = None
__pargs = get_config('pp_kwargs')


def add_args(parser: argparse.ArgumentParser) -> None:
    add_args_key(parser,
                 help='Specify the Object name to show.'
                      ' If nothing is specified, show the list of objects.')
    add_args_verbose(parser,
                     help='show details.'
                     ' In TTree object, use -v to show summary of each branch,'
                     ' and -vv to show full contents.'
                     ' In other objects, -v show all members.',
                     action='count', default=0)
    parser.add_argument('--drawer', '-d', help='Specify the Object drawer.',
                        choices=['ROOT', 'matplotlib'],
                        type=str, default=None)


def show_help() -> None:
    helpmsg = help_template('root', 'Open a ROOT file.', add_args)
    print(helpmsg)


def chk_drawer(drawer: str, args: Args) -> bool:
    res = False
    if args.drawer == drawer:
        res = True
    elif args.drawer is None and get_config('drawer') == drawer:
        res = True
    return res


def is_drawer_root(args) -> bool:
    global ROOT
    global __drawer
    if __drawer == 'ROOT':
        return True

    if chk_drawer('ROOT', args):
        try:
            import ROOT
        except ImportError as e:
            logger.debug(f'failed to import ROOT: {e}')
            return False
        else:
            __drawer = 'ROOT'
            logger.debug(f'set drawer as ROOT: {ROOT}')
            return True
    else:
        return False


def is_drawer_mpl(args) -> bool:
    global plt
    global __drawer
    if __drawer == 'matplotlib':
        return True

    if chk_drawer('matplotlib', args):
        try:
            import matplotlib.pyplot as plt
        except ImportError as e:
            logger.debug(f'failed to import mpl: {e}')
            return False
        else:
            __drawer = 'matplotlib'
            logger.debug(f'set drawer as mpl: {plt}')
            return True
    else:
        return False


def draw_root(fpath: str, cname: str) -> None:
    f = ROOT.TFile.Open(fpath)
    c = f.Get(cname)
    c.Draw()
    ROOT.gApplication.Run()()
    f.close()


def show_all_members(obj, shift: str = ' ') -> None:
    if hasattr(obj, 'all_members'):
        for key, val in obj.all_members.items():
            if hasattr(val, 'all_members'):
                print(f'{shift}{key}:')
                show_all_members(val, shift=shift + '  ')
            else:
                print(f'{shift}{key}: {val}')


def show_canvas(fpath: Path, cname: str, args: Args) -> None:
    if is_drawer_root(args):
        draw_root(str(fpath), cname)
    else:
        print('TCanvas only supports "ROOT" drawer.'
              f' => `aftviewer {fpath} -d ROOT`')


def show_tree(tree: uproot.models.TTree.Model_TTree_v20, args: Args) -> None:
    if args.verbose == 0:
        tree.show()
        return

    print(f'=== Title: {tree.title} ===')
    for key in tree.keys():
        array = tree[key].array(library='np')
        print(f'--- Branch: {key} ---')
        if args.verbose == 1:
            show_summary(array)
        else:
            print(' ~~~ All members ~~~')
            show_all_members(tree[key])
            print('~~~ Values ~~~')
            print(array)
            print()


def show_hist1d(hist: uproot.models.TH.Model_TH1D_v3, args: Args) -> None:
    if args.verbose > 0:
        show_all_members(hist)
    if is_drawer_mpl(args):
        vals, edges = hist.to_numpy(flow=True)
        xlabel = hist.axis().all_members.get('fTitle', '')
        title = hist.title if hist.title else ''
        fig1 = plt.figure()
        ax11 = fig1.add_subplot(1, 1, 1)
        ax11.step(edges, np.append(vals, vals[-1]), where='post')
        ax11.set_xlabel(xlabel)
        ax11.set_title(f'{title} ({hist.name})' if title else hist.name)
        ax11.grid(False)
    elif is_drawer_root(args):
        # 複数のhist表示がこれだと出来ない？ fを出しても駄目
        draw_root(hist.file.file_path, hist.name)
    else:
        print('Neither matplotlib nor ROOT is available. Cannot display TH1.')


def show_hist2d(hist: uproot.models.TH.Model_TH2F_v4, args: Args) -> None:
    if args.verbose > 0:
        show_all_members(hist)
    if is_drawer_mpl(args):
        vals, edgex, edgey = hist.to_numpy(flow=False)
        xlabel = hist.axis(0).all_members.get('fTitle', '')
        ylabel = hist.axis(1).all_members.get('fTitle', '')
        title = hist.title if hist.title else ''
        fig1 = plt.figure()
        ax11 = fig1.add_subplot(1, 1, 1)
        im1 = ax11.imshow(vals.T, origin='lower',
                          extent=[edgex[0], edgex[-1], edgey[0], edgey[-1]],
                          aspect='auto')
        ax11.set_xlabel(xlabel)
        ax11.set_ylabel(ylabel)
        ax11.set_title(f'{title} ({hist.name})' if title else hist.name)
        mefplot.add_1_colorbar(fig1, im1,
                               rect=[0.92, 0.1, 0.02, 0.8])
    elif is_drawer_root(args):
        draw_root(hist.file.file_path, hist.name)
    else:
        print('Neither matplotlib nor ROOT is available. Cannot display TH2.')


def show_profile(prof: uproot.models.TH.Model_TProfile_v7, args: Args):
    if args.verbose > 0:
        show_all_members(prof)
    if is_drawer_mpl(args):
        vals = prof.values(flow=False)
        errs = prof.errors(flow=False)
        edges = prof.axis().edges(flow=False)
        widths = prof.axis().widths(flow=False)
        xlabel = prof.axis().all_members.get('fTitle', '')
        title = prof.title if prof.title else ''
        fig1 = plt.figure()
        ax11 = fig1.add_subplot(1, 1, 1)
        ax11.errorbar(np.diff(edges)+edges[:-1], vals, yerr=errs, xerr=widths,
                      fmt='.')
        ax11.set_xlabel(xlabel)
        ax11.set_title(f'{title} ({prof.name})' if title else prof.name)
        ax11.grid(False)
    elif is_drawer_root(args):
        draw_root(prof.file.file_path, prof.name)
    else:
        print('Neither matplotlib nor ROOT is available. Cannot display TH1.')


def show_contents(fpath: Path, key: str, args: Args,
                  rfile: uproot.reading.ReadOnlyDirectory):
    if key not in rfile:
        print_warning(f"Key '{key}' not found in the ROOT file.")
        return
    if hasattr(rfile[key], 'classnames'):
        print_key(key)
        for k2 in rfile[key].classnames().keys():
            # contents in directory are selectable in another key?
            # show_contents(fpath, k2, args, rfile[key])
            print(f'  {k2}: {rfile[key][k2]}')
    else:
        t = rfile[key].classname
        print_key(f"{key}: {t}")
        if t == "TCanvas":
            show_canvas(fpath, key, args)
        elif t.startswith("TH1"):
            show_hist1d(rfile[key], args)
        elif t.startswith("TH2"):
            show_hist2d(rfile[key], args)
        elif t == "TTree":
            show_tree(rfile[key], args)
        elif t == 'TProfile':
            show_profile(rfile[key], args)
        elif t == 'TNtuple':
            show_tree(rfile[key], args)
        else:
            print_warning(f"Object type '{t}' is not supported yet."
                          " Please let me know!"
                          " -> https://github.com/MeF0504/aftviewer/issues")


def main(fpath: Path, args: Args):
    rfile = uproot.open(fpath)
    if args_chk(args, 'key'):
        if len(args.key) == 0:
            print("List of objects in the ROOT file:")
            for k, t in rfile.classnames().items():
                print(f"{k}: {t}")
            rfile.close()
            return
        else:
            keys = args.key
    else:
        keys = rfile.keys()

    npopts = get_config('numpy_printoptions')
    np.set_printoptions(**npopts)

    for k in keys:
        show_contents(fpath, k, args, rfile)

    if is_drawer_mpl(args):
        if len(plt.get_fignums()) != 0:
            plt.show()
    rfile.close()
