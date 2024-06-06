import argparse
from pathlib import Path
from logging import getLogger

from astropy.io import fits
# astropy requires NumPy!
import numpy as np

from .. import (GLOBAL_CONF, Args, args_chk, show_image_ndarray, print_error,
                help_template, add_args_imageviewer, add_args_key)
logger = getLogger(GLOBAL_CONF.logname)


def add_args(parser: argparse.ArgumentParser) -> None:
    add_args_imageviewer(parser)
    add_args_key(parser)
    parser.add_argument('--header', help='display the header info.',
                        action='store_true')
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
    if hasattr(args, 'header') and args.header:
        with fits.open(fpath) as hdul:
            print(repr(hdul[idx].header))
        return

    with fits.open(fpath) as hdul:
        if idx >= len(hdul):
            print_error(f'key index {idx} > num of HDU (max: {len(hdul)-1})')
            return
        data = hdul[idx].data

    if not hasattr(data, 'shape'):
        print_error(f'data type may not correct: {type(data)}')
        return
    if len(data.shape) != 2:
        print_error(f'This function assumes 2D image. this is {data.shape}.')
        return
    logger.debug(f'value: {np.nanmin(data)} - {np.nanmax(data)}')
    # ignore values less than or equal to 0
    data = np.where(data <= 0, np.nan, data)
    if hasattr(args, 'log_scale') and args.log_scale:
        data = np.log10(data)
    nan_rate = np.sum(np.isnan(data))/np.prod(data.shape)
    logger.debug(f'nan rate: {nan_rate:.3f} (include 0)')
    # set ignored values to zero
    data = np.where(data == data, data, 0)
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
