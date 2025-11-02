#! /usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import json
import subprocess

debug = False
default = False
setting_file = Path('~/.config/aftviewer/setting.json').expanduser()
if setting_file.is_file():
    with open(setting_file, 'r') as f:
        setting = json.load(f)
    if 'debug' in setting and setting['debug']:
        debug = True
    if 'force_default' in setting and setting['force_default']:
        default = True

assert debug, 'debug is off.'
assert default, 'force_default is off.'

res = subprocess.run(['aftviewer', '-h'], capture_output=True)
helpmsg = res.stdout.decode()

print('''**Welcome to the AFTViewer wiki!**

# Introduction

Any File Type Viewer (AFTViewer) is a CUI/TUI tool made by Python to view any kind of packaged, archived, or binary files.

# Usage

```bash
{}
```


# Requirements

The basic process of this software is designed to work with standard libraries of recent [Python3](https://www.python.org/).  
To show some kinds of files, external libraries are required.

e.g.)
- [numpy](https://numpy.org/) for numpy, xpm, np_pickle
- [h5py](https://docs.h5py.org/) for hdf5
- [rawpy](https://letmaik.github.io/rawpy/api/rawpy.RawPy.html) for raw_image
- [numpy-stl](https://pypi.org/project/numpy-stl/) for stl.

The following libraries are not always necessary but are useful if available.
- [numpy](https://numpy.org/) for hdf5
- [tabulate](https://pypi.org/project/tabulate/) for sqlite3
- [Matplotlib](https://matplotlib.org/) or [Plotly](https://plotly.com/python/) for stl to display 3-D model.

To show images, imaging-related libraries
(Currently supporting libraries are
[PIL (Pillow)](https://pillow.readthedocs.io/),
[Matplotlib](https://matplotlib.org/),
[OpenCV](https://pypi.org/project/opencv-python/),
or [bokeh](https://bokeh.org/))
or shell commands (e.g. "open" in macOS) with supporting bitmap (.bmp) files are required.

# Installation

`pip` command is available.

```bash
python -m pip install git+https://github.com/MeF0504/aftviewer
```
or in Windows OS,
```bash
py -m pip install git+https://github.com/MeF0504/aftviewer
```

If you want to install all modules used in AFTViewer,
```bash
python -m pip install "aftviewer[all] @ git+https://github.com/MeF0504/aftviewer"
# or
py -m pip install "aftviewer[all] @ git+https://github.com/MeF0504/aftviewer"
```
'''.format(helpmsg))
