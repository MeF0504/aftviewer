# PyViewer

CUI view tool made by Python.

See the [wiki page](https://github.com/MeF0504/pyviewer/wiki) for the details.

## Requirements

Basically, PyViewer works for supported [Python](https://www.python.org/) versions
without any third-party libraries.

Some third-party libraries are required to open some file types.
- [numpy](https://numpy.org/) for numpy, xpm, np_pickle
- [h5py](https://docs.h5py.org/) for hdf5
- [rawpy](https://letmaik.github.io/rawpy/api/rawpy.RawPy.html) for raw_image

### Optional Requirements

- [numpy](https://numpy.org/) for hdf5
- [tabulate](https://pypi.org/project/tabulate/) for sqlite3
- [PIL (Pillow)](https://pillow.readthedocs.io/), [matplotlib](https://matplotlib.org/) or [OpenCV](https://pypi.org/project/opencv-python/) to show a image.
    - Shell commands (e.g. "open" in macOS) are also available.  
      In this case, a bit map file (.bmp) should be supported.

## Install

```bash
python -m pip install git+https://github.com/MeF0504/pyviewer
```
or in Windows OS,
```bash
py -m pip install git+https://github.com/MeF0504/pyviewer
```

If you want to install all modules used in PyViewer,
```bash
python -m pip install "pyviewer[all] @ git+https://github.com/MeF0504/pyviewer"
# or
py -m pip install "pyviewer[all] @ git+https://github.com/MeF0504/pyviewer"
```

## Usage
```bash
usage: pyviewer [-h]
                [-t {hdf5,pickle,numpy,np_pickle,tar,zip,sqlite3,raw_image,jupyter,xpm}]
                file

show the constitution of a file. default support file types ... hdf5, pickle,
numpy, np_pickle, tar, zip, sqlite3, raw_image, jupyter, xpm

positional arguments:
  file                  input file

options:
  -h, --help            show this help message and exit
  -t {hdf5,pickle,numpy,np_pickle,tar,zip,sqlite3,raw_image,jupyter,xpm}, --type {hdf5,pickle,numpy,np_pickle,tar,zip,sqlite3,raw_image,jupyter,xpm}
                        specify the file type. "pyviewer help -t TYPE" will
                        show the detailed help.

To see the detailed help of each type, type 'pyviewer help -t TYPE'. PyViewer
has other some subcommands, 'pyviewer update' updates this command, 'pyviewer
config_list' shows the current optional configuration.
```

