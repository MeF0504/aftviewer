import argparse
from pathlib import Path
from logging import getLogger

import healpy as hp
import numpy as np
import matplotlib.pyplot as plt

from pymeflib import plot as mefplot
from aftviewer import (GLOBAL_CONF, Args,
                       args_chk, help_template, get_config, add_args_key,
                       print_error,
                       )
logger = getLogger(GLOBAL_CONF.logname)


def add_args(parser: argparse.ArgumentParser) -> None:
    add_args_key(parser,
                 help='Specify the index to show.'
                      ' If no key is specified, show the list of map types.',
                 type=int, default=None)
    parser.add_argument('--projection', help='specify the projection',
                        choices=['mollweide', 'gnomonic',
                                 'cartesian', 'orthographic'],
                        )
    parser.add_argument('--cl', help='show power spectra',
                        action='store_true')
    parser.add_argument('--norm', help='specify color normalization',
                        choices=['hist', 'log', 'None'])
    parser.add_argument('--nest', help='read map as NEST ordering.',
                        action='store_true')
    parser.add_argument('--coord', help='Either one of "G", "E" or "C"'
                        ' to describe the coordinate system of the map,'
                        ' or a sequence of 2 of these to rotate the map from'
                        ' the first to the second coordinate system.',
                        nargs='*')


def show_help() -> None:
    helpmsg = help_template('healpix',
                            'Show the image of fits file using HealPix.',
                            add_args)
    print(helpmsg)


def set_projection(args: Args) -> str:
    if hasattr(args, 'projection') and args.projection is not None:
        projection = args.projection
        logger.info(f'projection from args: {projection}')
    elif get_config('projection') is not None:
        projection = get_config('projection')
        logger.info(f'projection from config: {projection}')
    else:
        projection = 'mollweide'
        logger.info(f'projection from default: {projection}')
    return projection


def set_limits() -> tuple[float]:
    try:
        m_limit = get_config('map_limit')
        mmin, mmax = m_limit
    except Exception as e:
        logger.error(f'failed to get map limits: {type(e).__name__}, {e}\n'
                     f'  data: {m_limit}')
        mmin = None
        mmax = None
    else:
        del m_limit
    return mmin, mmax


def set_norm(args: Args) -> str | None:
    if hasattr(args, 'norm') and args.norm is not None:
        norm = args.norm
        logger.info(f'norm from args: {norm}')
    elif get_config('norm') is not None:
        norm = get_config('norm')
        logger.info(f'norm from config: {norm}')
    else:
        norm = 'None'
        logger.info(f'norm from default: {norm}')
    if norm == 'None':
        norm = None
    return None


def set_coordinate(args: Args) -> list[str] | None:
    if hasattr(args, 'coord') and args.coord is not None:
        coord = args.coord
        logger.info(f'coord from args: {coord}')
    elif get_config('coord') is not None:
        coord = get_config('coord')
        logger.info(f'coord from config: {coord}')
    else:
        coord = []
        logger.info(f'coord from default: {coord}')
    if len(coord) == 0:
        coord = None
    return coord


def show_header(fpath: Path):
    _, headers = hp.read_map(fpath, h=True)
    info = {}
    for name, val in headers:
        if 'TTYPE' in name:
            idx = int(name[5:])
            if idx not in info:
                info[idx] = [val]
            else:
                logger.warning(f'idx overwrite? {idx}')
                info[idx][0] = val
        elif 'TUNIT' in name:
            idx = int(name[5:])
            if idx not in info:
                logger.warning(f'idx not set? {idx}')
                info[idx] = ['???', val]
            else:
                info[idx].append(val)
    idcs = list(info.keys())
    idcs.sort()
    for i in idcs:
        print(f'{i}: {info[i][0]} [{info[i][1]}]')


def main(fpath: Path, args: Args):
    fname = Path(fpath).name
    if args_chk(args, 'key'):
        if len(args.key) == 0:
            show_header(fpath)
            return
        else:
            idcs = args.key
    else:
        idcs = None

    # set viewer (visualization function)
    projection = set_projection(args)
    if projection == 'mollweide':
        viewer = hp.mollview
    elif projection == 'gnomonic':
        viewer = hp.gnomview
    elif projection == 'cartesian':
        viewer = hp.cartview
    elif projection == 'orthographic':
        viewer = hp.orthview
    else:
        print_error(f'incorrect projection: {projection}')
        return

    mmin, mmax = set_limits()
    coord = set_coordinate(args)
    norm = set_norm(args)
    # nest
    if hasattr(args, 'nest'):
        nest = args.nest
    else:
        nest = False
    # show C_\ell or not
    if hasattr(args, 'cl'):
        cl = args.cl
    else:
        cl = False

    # get and show maps
    heal_maps, headers = hp.read_map(fpath, field=None, h=True, nest=nest)
    names = []
    for h in headers:
        if 'TTYPE' in h[0]:
            names.append(h[1])
    logger.debug(f'names: {names}')
    assert len(names) == len(heal_maps), 'Number of names and maps' \
        f' does not match: {len(names)}, {len(heal_maps)}.'
    if idcs is None:
        map_idcs = range(len(names))
    else:
        map_idcs = np.array(idcs)-1
    Lmaps = len(map_idcs)
    for i in map_idcs:
        name = names[i]
        if norm == 'log':
            # is this correct?
            heal_map_plot = np.abs(heal_maps[i])
        else:
            heal_map_plot = heal_maps[i]
        NSIDE = hp.npix2nside(len(heal_map_plot))
        logger.info(f'map{i}: {name}, {heal_map_plot.shape} (NSIDE {NSIDE}).')
        if mmin is None or np.nanmin(heal_map_plot) > mmin:
            tmpmin = np.nanmin(heal_map_plot)
        else:
            tmpmin = mmin
        if mmax is None or np.nanmax(heal_map_plot) < mmax:
            tmpmax = np.nanmax(heal_map_plot)
        else:
            tmpmax = mmax
        viewer(heal_map_plot, title=f'{fname} ({name})',
               min=tmpmin, max=tmpmax,
               coord=coord, norm=norm, fig=1, sub=(Lmaps, 1, i+1))

    if cl:
        fig2 = plt.figure(figsize=(10, 5))
        if Lmaps == 1:
            # assume I map
            cls = [hp.anafast(heal_maps[0], pol=False)]
        elif Lmaps == 3:
            # assume I, Q, U map
            cls = hp.anafast(heal_maps[:3], pol=True)
            # to TT, EE, BB, TE, EB, TB
        else:
            print_error(f'Number of maps should be 1 or 3. Now {Lmaps}.')
            plt.show()
            return
        Lcl = len(cls)
        ax2s = mefplot.share_plot(fig2, len(cls), 1)
        for i, cl in enumerate(cls):
            ell = np.arange(len(cl))
            dl = ell*(ell+1)/(2*np.pi)*cl
            ax2s[i].plot(ell[2:], dl[2:], '-')
            # ax2s[i].set_yscale('log')
            if i == int(Lcl/2):
                ax2s[i].set_ylabel(r'$\ell(\ell+1)/2\pi\ C_{\ell}$')
            if i == Lcl-1:
                ax2s[i].set_xlabel(r'$\ell$')
            else:
                ax2s[i].set_xticklabels([])
    plt.show()
