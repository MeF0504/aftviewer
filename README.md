# Any File Type Viewer

is a CUI/TUI tool to view any type of files made by Python.

See the [wiki page](https://github.com/MeF0504/aftviewer/wiki) for the details.

## Requirements

Basically, AFTViewer works for supported [Python](https://www.python.org/) versions
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
usage: aftviewer [-h] [--version]
                 [-t {hdf5,pickle,numpy,np_pickle,tar,zip,sqlite3,raw_image,jupyter,xpm}]
                 file

show the constitution of a file. Supported file types ... hdf5, pickle, numpy,
np_pickle, tar, zip, sqlite3, raw_image, jupyter, xpm. To see the detailed
help of each type, type 'aftviewer help -t TYPE'.

positional arguments:
  file                  input file

options:
  -h, --help            show this help message and exit
  --version, -V         show program's version number and exit
  -t {hdf5,pickle,numpy,np_pickle,tar,zip,sqlite3,raw_image,jupyter,xpm}, --type {hdf5,pickle,numpy,np_pickle,tar,zip,sqlite3,raw_image,jupyter,xpm}
                        specify the file type. "aftviewer help -t TYPE" will
                        show the detailed help.

aftviewer has some subcommands, 'aftviewer help -t TYPE' shows detailed help,
'aftviewer update' run the update command of AFTViewer, 'aftviewer
config_list' shows the current optional configuration, 'aftviewer
shell_completion --bash >> ~/.bashrc' or 'aftviewer shell_completion --zsh >>
~/.zshrc' set the completion script for bash/zsh.
```

