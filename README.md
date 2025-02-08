# Any File Type Viewer

is a CUI/TUI tool to view any type of files made by Python.

See the [wiki page](https://github.com/MeF0504/aftviewer/wiki) for the details.

## Requirements

The basic process of this software is designed to work with standard libraries of recent [Python3](https://www.python.org/).  
To show some kinds of files, external libraries are required.

e.g.)
- [numpy](https://numpy.org/) for numpy, xpm, np_pickle
- [h5py](https://docs.h5py.org/) for hdf5
- [rawpy](https://letmaik.github.io/rawpy/api/rawpy.RawPy.html) for raw_image
- [numpy-stl](https://pypi.org/project/numpy-stl/) for stl.
- [Astropy](https://www.astropy.org/) for fits.

The following libraries are not always necessary but are useful if available.
- [numpy](https://numpy.org/) for hdf5
- [tabulate](https://pypi.org/project/tabulate/) for sqlite3
- [Matplotlib](https://matplotlib.org/) or [Plotly](https://plotly.com/python/) for stl to display 3-D model.

To show images, imaging-related libraries
(Currently supporting libraries are
[PIL (Pillow)](https://pillow.readthedocs.io/),
[Matplotlib](https://matplotlib.org/),
or [OpenCV](https://pypi.org/project/opencv-python/))
or shell commands (e.g. "open" in macOS) with supporting bitmap (.bmp) files are required.

## Install

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

## Usage
```bash
aftviewer [-t TYPE] file
```
shows the constitution of a file.
To see the detailed options, subcommands, and supported file types, type
```bash
aftviewer -h
```

---
To see the details of available options for each file type, type
```bash
aftviewer help -t TYPE
```
To update this command, type
```bash
aftviewer update
```
To show the list of current [configurations](https://github.com/MeF0504/aftviewer/wiki/Customization#parameters), type
```bash
aftviewer config_list
```
To set the shell completion, type
```bash
# bash
aftviewer shell_completion --bash >> ~/.bashrc
# zsh
aftviewer shell_completion --zsh >> ~/.zshrc
```
