import argparse
from pathlib import Path
from logging import getLogger

import healpy as hp
import numpy as np
import matplotlib.pyplot as plt

from pymeflib import plot as mefplot
from .. import (GLOBAL_CONF, Args, args_chk, get_config, print_error,
                help_template, add_args_key, add_args_output,
                )
logger = getLogger(GLOBAL_CONF.logname)


class LocalArgs(Args):
    projection: str | None
    cl: bool
    norm: str | None
    nest: bool
    coord: list[str] | None


def add_args(parser: argparse.ArgumentParser) -> None:
    add_args_key(parser,
                 help='Specify the index to show.'
                      ' If no key is specified, show the list of map types.',
                 default=None)
    add_args_output(parser,
                    help='Save image files at OUTPUT directory.')
    parser.add_argument('--projection', help='specify the projection',
                        choices=['mollweide', 'gnomonic',
                                 'cartesian', 'orthographic'],
                        )
    parser.add_argument('--cl', help='Calculate and show power spectra.',
                        action='store_true')
    parser.add_argument('--norm', help='Specify color normalization.',
                        choices=['hist', 'log', 'None'])
    parser.add_argument('--nest', help='Read map as NEST ordering.',
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


def set_projection(args: LocalArgs) -> str:
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


def set_limits() -> tuple[float | None, float | None]:
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


def set_norm(args: LocalArgs) -> str | None:
    norm: str | None = None
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


def set_coordinate(args: LocalArgs) -> list[str] | None:
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
        return None
    else:
        return coord


def show_header(fpath: Path):
    _, headers = hp.read_map(fpath, h=True, field=None)
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
        if len(info[i]) == 1:
            msg = f'{i}: {info[i][0]}'
        else:
            msg = f'{i}: {info[i][0]} [{info[i][1]}]'
        print(msg)


def main(fpath: Path, args: LocalArgs):
    fname = Path(fpath).name
    if args_chk(args, 'key'):
        if len(args.key) == 0:
            show_header(fpath)
            return
        else:
            try:
                idcs = [int(k) for k in args.key]
            except ValueError as e:
                print_error('--key arguments should be indices (numbers).')
                logger.debug(f'failed to convert int, {type(e).__name__}, {e}')
                return
    else:
        idcs = None

    if args_chk(args, 'output'):
        save_dir = Path(args.output)
        if not save_dir.is_dir():
            save_dir.mkdir(parents=True)
    else:
        save_dir = None

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
        show_cl = args.cl
    else:
        show_cl = False

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
        map_idcs = np.arange(len(names))
    else:
        map_idcs = np.array(idcs)-1
    Lmaps = len(map_idcs)
    MaxMaps = len(heal_maps)
    if np.any(map_idcs < 0) or np.any(map_idcs >= MaxMaps):
        print_error(f'The acceptable range of --key is 1 <= KEY < {MaxMaps}.')
        return
    for i, x in enumerate(map_idcs):
        name = names[x]
        if norm == 'log':
            # is this correct?
            heal_map_plot = np.abs(heal_maps[x])
        else:
            heal_map_plot = heal_maps[x]
        NSIDE = hp.npix2nside(len(heal_map_plot))
        logger.info(f'map{x}: {name}, {heal_map_plot.shape} (NSIDE {NSIDE}).')
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
    if save_dir is not None:
        fig1 = plt.gcf()
        fig1.savefig(save_dir/'healpix_maps.pdf')

    if show_cl:
        if Lmaps in (1, 3):
            fig2 = plt.figure(figsize=(10, 5))
            # assume I map or  I, Q, U maps
            # to TT or TT, EE, BB, TE, EB, TB
            cls = hp.anafast(heal_maps[map_idcs], pol=True)
            if len(cls.shape) == 1:
                cls = [cls]
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
            if save_dir is not None:
                fig2.savefig(save_dir/'healpix_power_spectra.pdf')
        else:
            print_error('To calculate Cl,'
                        f' the number of maps should be 1 or 3. Now {Lmaps}.')
    if save_dir is None:
        plt.show()
    else:
        plt.close()
