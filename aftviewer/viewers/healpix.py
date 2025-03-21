import argparse
from pathlib import Path
from logging import getLogger

import healpy as hp
# healpy requires numpy, matplotlib, and astropy!
import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt

from aftviewer import (GLOBAL_CONF, Args,
                       args_chk, help_template, get_config, add_args_key,
                       print_error,
                       )
logger = getLogger(GLOBAL_CONF.logname)


def add_args(parser: argparse.ArgumentParser) -> None:
    add_args_key(parser,
                 help='Specify the index of field/HDU. To see the details,'
                 ' please run "aftviewer FILE -t fits -k".')
    parser.add_argument('--projection', help='specify the projection',
                        choices=['mollweide', 'gnomonic',
                                 'cartesian', 'orthographic'],
                        )
    parser.add_argument('--cl', help='show power spectra',
                        action='store_true')
    parser.add_argument('--norm', help='specify color normalization',
                        choices=['hist', 'log', 'None'])
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


def main(fpath: Path, args: Args):
    fname = Path(fpath).name
    if args_chk(args, 'key'):
        if len(args.key) == 0:
            with fits.open(fpath) as hdul:
                hdul.info()
            return
        else:
            fields = [int(k) for k in args.key]
    else:
        fields = [0]

    # set projection
    if hasattr(args, 'projection') and args.projection is not None:
        projection = args.projection
    elif get_config('projection') is not None:
        projection = get_config('projection')
    else:
        projection = 'mollweide'

    # set viewer (visualization function)
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

    # set max/min of map
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

    # set normalization method
    if hasattr(args, 'norm') and args.norm is not None:
        norm = args.norm
    elif get_config('norm') is not None:
        norm = get_config('norm')
    else:
        norm = 'None'
    if norm == 'None':
        norm = None

    # set coordinate
    if hasattr(args, 'coord') and args.coord is not None:
        coord = args.coord
    elif get_config('coord') is not None:
        coord = get_config('coord')
    else:
        coord = []
    if len(coord) == 0:
        coord = None

    # show C_\ell or not
    if hasattr(args, 'cl'):
        cl = args.cl
    else:
        cl = False

    # get field names
    names = []
    with fits.open(fpath) as hdul:
        for i in fields:
            names.append(hdul[i].name)
    # get and show maps
    heal_maps = hp.read_map(fpath, field=fields)
    if len(fields) == 1:
        heal_maps = [heal_maps]
    assert len(names) == len(heal_maps)
    for i, name in enumerate(names):
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
               coord=coord, norm=norm, fig=1, sub=(len(fields), 1, i+1))

    if cl:
        fig2 = plt.figure(figsize=(10, 5))
        ax2s = [fig2.add_subplot(len(fields), 1, i+1)
                for i in range(len(fields))]
        for i, field in enumerate(fields):
            # LMAX = 1024
            cl = hp.anafast(heal_maps[i])  # , lmax=LMAX)
            ell = np.arange(len(cl))
            cl = cl[2:]
            ell = ell[2:]
            ax2s[i].plot(ell, ell*(ell+1)/(2*np.pi) * cl)
            ax2s[i].set_xlabel(r'$\ell$')
            ax2s[i].set_ylabel(r'$\ell(\ell+1)/2\pi\ C_{\ell}$')
            # ax2s[i].set_yscale('log')
    plt.show()
