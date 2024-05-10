import argparse
from pathlib import Path
from logging import getLogger

from stl import mesh

from aftviewer import GLOBAL_CONF, Args, help_template, get_config

logger = getLogger(GLOBAL_CONF.logname)


def add_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('--viewer', help='specify the viewer',
                        choices=['matplotlib', 'plotly'],
                        default=None)


def show_help() -> None:
    helpmsg = help_template('stl', 'description.', add_args)
    print(helpmsg)


def main(fpath: Path, args: Args):
    assert hasattr(args, 'viewer'), 'something wrong; viewer is not in args.'
    if args.viewer is None:
        viewer = get_config('stl', 'viewer')
        logger.info(f'set viewer from config file; {viewer}.')
    else:
        viewer = args.viewer
        logger.info(f'set viewer from args; {viewer}.')

    mesh_data = mesh.Mesh.from_file(str(fpath))
    logger.debug(f'mesh shape: {mesh_data.vectors.shape}')
    ecol = get_config('stl', 'edgecolors')
    fcol = get_config('stl', 'facecolors')

    if viewer == 'matplotlib':
        # https://github.com/WoLpH/numpy-stl/?tab=readme-ov-file#plotting-using-matplotlib-is-equally-easy
        from mpl_toolkits import mplot3d
        import matplotlib.pyplot as plt
        fig1 = plt.figure()
        ax11 = fig1.add_subplot(projection='3d')
        d3_pol = mplot3d.art3d.Poly3DCollection(mesh_data.vectors,
                                                linestyle=':',
                                                edgecolors=ecol,
                                                facecolors=fcol,
                                                )
        ax11.add_collection3d(d3_pol)

        # Auto scale to the mesh size
        scale = mesh_data.points.flatten()
        ax11.auto_scale_xyz(scale, scale, scale)

        plt.show()
    elif viewer is None:
        print('viewer is not set.')
    else:
        print(f'incorrect viewer: "{viewer}".')
