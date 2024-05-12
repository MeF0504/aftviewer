import argparse
from pathlib import Path
from logging import getLogger

from astropy.io import fits
# astropy requires NumPy!
import numpy as np

from aftviewer import (GLOBAL_CONF, Args, args_chk, cprint,
                       get_col, show_image_ndarray,
                       help_template, add_args_imageviewer, add_args_key)
logger = getLogger(GLOBAL_CONF.logname)


def add_args(parser: argparse.ArgumentParser) -> None:
    add_args_imageviewer(parser)
    add_args_key(parser)
    parser.add_argument('--log_scale', help='scale color in log.',
                        action='store_true')


def show_help() -> None:
    helpmsg = help_template('fits', 'show the image of fits file.' +
                            ' -k/--key specifies an index of HDU' +
                            ' (Header Data Unit) list, and' +
                            ' if no key is specified, show the HDU info.' +
                            ' Note that the values of each pixel are' +
                            ' subtracted by min value.',
                            add_args)
    print(helpmsg)


def main(fpath: Path, args: Args):
    fname = fpath.name
    if args_chk(args, 'key'):
        if len(args.key) == 0:
            with fits.open(fpath) as hdul:
                hdul.info()
            return
        else:
            idx = int(args.key[0])
    else:
        idx = 0

    fg, bg = get_col('msg_error')
    with fits.open(fpath) as hdul:
        if idx >= len(hdul):
            cprint(f'key index {idx} > num of HDU (max: {len(hdul)-1})',
                   fg=fg, bg=bg)
            return
        data = hdul[idx].data

    if not hasattr(data, 'shape'):
        cprint(f'data type may not correct: {type(data)}', fg=fg, bg=bg)
        return
    if len(data.shape) != 2:
        cprint(f'This function assumes 2D image. this is {data.shape}.',
               fg=fg, bg=bg)
        return
    logger.debug(f'min value: {np.nanmin(data)}')
    data -= np.nanmin(data)
    nan_rate = np.sum(np.isnan(data))/np.prod(data.shape)
    logger.debug(f'nan rate: {nan_rate:.3f}')
    data = np.where(data == data, data, 0)
    if hasattr(args, 'log_scale') and args.log_scale:
        data = np.log10(data+1)
    max_val = np.max(data)
    # convert gray-scale to RGB.
    data2 = np.zeros((data.shape[0], data.shape[1], 3))
    data2[:, :, 0] = 255.0*data/max_val
    data2[:, :, 1] = 255.0*data/max_val
    data2[:, :, 2] = 255.0*data/max_val
    data2 = data2.astype(np.uint8)
    # flip upside down (required??)
    data2 = data2[::-1]
    show_image_ndarray(data2, fname, args)
