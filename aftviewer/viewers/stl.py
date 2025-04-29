import argparse
import re
from pathlib import Path
from logging import getLogger

from stl import mesh
# stl depends on numpy.
import numpy as np

from .. import GLOBAL_CONF, Args, help_template, get_config, print_error

logger = getLogger(GLOBAL_CONF.logname)


def check_color(col):
    colors = ['black', 'white', 'red', 'green', 'blue',
              'cyan', 'magenta', 'yellow', 'gray']
    if type(col) is str:
        if re.match('^#[0-9a-f]{6}$', col) is not None:
            # color code
            return True
        elif col in colors:
            # color name
            return True
        else:
            logger.warning(f'incorrect color setting: {col}')
            print_error(f'incorrect color setting: {col}')
            return False
    elif col is None:
        return True
    else:
        logger.warning(f'incorrect color setting type: {col}')
        print_error('incorrect color setting type.')
        return False
    return False


def plotly_stl2mesh3d(mesh_data: mesh.Mesh):
    p, q, r = mesh_data.vectors.shape
    vertices, ixr = np.unique(mesh_data.vectors.reshape(p*q, r),
                              return_inverse=True, axis=0)
    mI = np.take(ixr, [3*k+0 for k in range(p)])
    mJ = np.take(ixr, [3*k+1 for k in range(p)])
    mK = np.take(ixr, [3*k+2 for k in range(p)])
    return vertices, mI, mJ, mK


def add_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('--viewer', help='specify the viewer',
                        choices=['matplotlib', 'plotly'],
                        default=None)


def show_help() -> None:
    helpmsg = help_template('stl', 'display the stl 3D model.'
                            ' Viewers currently supported to display'
                            ' the models are'
                            ' "matplotlib" and "plotly".', add_args)
    print(helpmsg)


def main(fpath: Path, args: Args):
    assert hasattr(args, 'viewer'), 'something wrong; viewer is not in args.'
    if args.viewer is None:
        viewer = get_config('viewer')
        logger.info(f'set viewer from config file; {viewer}.')
    else:
        viewer = args.viewer
        logger.info(f'set viewer from args; {viewer}.')
    if viewer is None:
        if 'plotly' in GLOBAL_CONF.pack_list:
            viewer = 'plotly'
        elif 'matplotlib' in GLOBAL_CONF.pack_list:
            viewer = 'matplotlib'
        logger.info(f'set viewer if viewer is available; {viewer}.')

    mesh_data = mesh.Mesh.from_file(str(fpath))
    logger.debug(f'mesh shape: {mesh_data.vectors.shape}')
    ecol: None | str = get_config('edgecolors')
    fcol: None | str = get_config('facecolors')
    bcol: None | str = get_config('backgroundcolors')
    if not check_color(ecol):
        ecol = None
    if not check_color(fcol):
        fcol = None
    if not check_color(bcol):
        bcol = None

    if viewer == 'matplotlib':
        # https://github.com/WoLpH/numpy-stl/?tab=readme-ov-file#plotting-using-matplotlib-is-equally-easy
        from mpl_toolkits import mplot3d
        import matplotlib.pyplot as plt
        if bcol is None:
            bcol = plt.rcParams['axes.facecolor']
        fig1 = plt.figure()
        ax11 = fig1.add_subplot(projection='3d')
        d3_pol = mplot3d.art3d.Poly3DCollection(mesh_data.vectors,
                                                linestyle=':',
                                                edgecolors=ecol,
                                                facecolors=fcol,
                                                )
        ax11.add_collection3d(d3_pol)
        ax11.xaxis.pane.set_facecolor(bcol)
        ax11.yaxis.pane.set_facecolor(bcol)
        ax11.zaxis.pane.set_facecolor(bcol)
        ax11.set_facecolor(bcol)

        # Auto scale to the mesh size
        scale = mesh_data.points.flatten()
        ax11.auto_scale_xyz(scale, scale, scale)

        plt.show()
    elif viewer == 'plotly':
        # https://chart-studio.plotly.com/~empet/15276/converting-a-stl-mesh-to-plotly-gomes/#/
        import plotly.graph_objects as go
        vertices, mI, mJ, mK = plotly_stl2mesh3d(mesh_data)
        x, y, z = vertices.T
        if fcol is None:
            fcol = '#a0a0a0'
        colorscale = [[0, fcol], [1, fcol]]

        mesh3D = go.Mesh3d(x=x, y=y, z=z, i=mI, j=mJ, k=mK,
                           flatshading=True,
                           colorscale=colorscale,
                           intensity=z, name=fpath.name,
                           showscale=False)
        layout = go.Layout(paper_bgcolor='rgb(230, 230, 230)',
                           title_text=fpath.name,
                           font_color='black',
                           scene=dict(aspectmode='data'),
                           scene_camera=dict(eye=dict(x=1.25, y=-1.25, z=1)),
                           )
        fig1 = go.Figure(data=[mesh3D], layout=layout)
        fig1.update_layout(scene=dict(
            xaxis_title='',
            yaxis_title='',
            zaxis_title='',
            xaxis=dict(backgroundcolor=bcol,
                       ),
            yaxis=dict(backgroundcolor=bcol,
                       ),
            zaxis=dict(backgroundcolor=bcol,
                       ),
            ),
        )
        fig1.show()
    elif viewer is None:
        print('viewer is not found.')
    else:
        print(f'incorrect viewer: "{viewer}".')
