import argparse
from pathlib import Path

import uproot
try:
    import ROOT
except ImportError:
    ROOT = None

from aftviewer import Args, help_template


def add_args(parser: argparse.ArgumentParser) -> None:
    # parser.add_argument()
    pass


def show_help() -> None:
    helpmsg = help_template('root', 'Open a ROOT file.', add_args)
    print(helpmsg)


def show_canvas(fpath: Path, cname: str) -> None:
    if ROOT is not None:
        f = ROOT.TFile.Open(str(fpath))
        c = f.Get(cname)
        c.Draw()
        ROOT.gApplication.Run()()
        f.close()
    else:
        print("ROOT is not available. Cannot display TCanvas.")


def show_tree() -> None:
    pass


def show_hist1d() -> None:
    pass


def show_hist2d() -> None:
    pass


def main(fpath: Path, args: Args):
    rfile = uproot.open(fpath)
    for k, t in rfile.classnames().items():
        print(f"{k}: {t}")
        if t == "TCanvas":
            show_canvas(fpath, k)
        elif t.startswith("TH1"):
            show_hist1d()
        elif t.startswith("TH2"):
            show_hist2d()
        elif t == "TTree":
            show_tree()
