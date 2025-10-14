import argparse
from pathlib import Path
import pprint
from logging import getLogger


import uproot
import numpy as np  # uproot requires NumPy!
try:
    import ROOT
except ImportError:
    ROOT = None
try:
    import matplotlib
    import matplotlib.pyplot as plt
except ImportError:
    plt = None
else:
    if matplotlib.get_backend() == 'agg':
        plt = None  # No display available

from .. import (GLOBAL_CONF, Args, get_config, args_chk,
                print_key, print_warning,
                help_template, add_args_key, add_args_verbose)
from .numpy import show_summary


logger = getLogger(GLOBAL_CONF.logname)
__pargs = get_config('pp_kwargs')


def add_args(parser: argparse.ArgumentParser) -> None:
    add_args_key(parser,
                 help='Specify the Object name to show.'
                      ' If nothing is specified, show the list of objects.')
    add_args_verbose(parser,
                     help='show details.'
                     ' In TTree object, use -v to show summary of each branch,'
                     ' and -vv to show full array contents.'
                     ' In other objects, -v show all members.',
                     action='count', default=0)


def show_help() -> None:
    helpmsg = help_template('root', 'Open a ROOT file.', add_args)
    print(helpmsg)


def show_all_members(obj, shift: str = ' ') -> None:
    if hasattr(obj, 'all_members'):
        for key, val in obj.all_members.items():
            if hasattr(val, 'all_members'):
                print(f'{shift}{key}:')
                show_all_members(val, shift=shift + '  ')
            else:
                print(f'{shift}{key}: {val}')


def show_canvas(fpath: Path, cname: str) -> None:
    if ROOT is not None:
        f = ROOT.TFile.Open(str(fpath))
        c = f.Get(cname)
        c.Draw()
        ROOT.gApplication.Run()()
        f.close()
    else:
        print("ROOT is not available. Cannot display TCanvas.")


def show_tree(tree: uproot.TTree, args: Args) -> None:
    # print(tree.name)
    # print(tree.object_path)
    # print(tree.num_entries)
    if args.verbose == 0:
        tree.show()
        return

    print(f'=== {tree.title} ===')
    for key in tree.keys():
        array = tree[key].array(library='np')
        if args.verbose == 1:
            print(f'------ {key} ------')
            show_all_members(tree[key])
            show_summary(array)
        else:
            print(f'{key}: {array}')


def show_hist1d(hist: uproot.models.TH.Model_TH1D_v3, args: Args) -> None:
    if args.verbose > 0:
        show_all_members(hist)
    vals, edges = hist.to_numpy(flow=True)
    if plt is not None:
        xlabel = hist.axis().all_members.get('fTitle', '')
        title = hist.title if hist.title else ''
        fig1 = plt.figure()
        ax11 = fig1.add_subplot(1, 1, 1)
        ax11.step(edges, np.append(vals, vals[-1]), where='post')
        ax11.set_xlabel(xlabel)
        ax11.set_ylabel('Entries')
        ax11.set_title(f'{title} ({hist.name})' if title else hist.name)
        ax11.grid(False)
    elif ROOT is not None:
        # 複数のhist表示がこれだと出来ない？ fを出しても駄目
        f = ROOT.TFile.Open(hist.file.file_path)
        h = f.Get(hist.name)
        h.Draw()
        ROOT.gApplication.Run()()
        f.close()
    else:
        print('Neither matplotlib nor ROOT is available. Cannot display TH1.')


def show_hist2d(hist: uproot.models.TH.Model_TH2D, args:Args) -> None:
    pass


def show_profile() -> None:
    pass


def show_ntuple() -> None:
    pass


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
        if k not in rfile:
            print_warning(f"Key '{k}' not found in the ROOT file.")
            continue
        t = rfile[k].classname
        print_key(f"{k}: {t}")
        if t == "TCanvas":
            show_canvas(fpath, k)
        elif t.startswith("TH1"):
            show_hist1d(rfile[k], args)
        elif t.startswith("TH2"):
            show_hist2d(rfile[k], args)
        elif t == "TTree":
            show_tree(rfile[k], args)
        elif t == 'TProfile':
            show_profile()
        elif t == 'TNtuple':
            show_ntuple()
        else:
            print_warning(f"Object type '{t}' is not supported yet."
                          " Please let me know!"
                          " -> https://github.com/MeF0504/aftviewer/issues")
    if plt is not None and plt.get_fignums():
        plt.show()
    rfile.close()
