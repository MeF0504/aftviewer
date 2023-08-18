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
curl https://raw.githubusercontent.com/MeF0504/pyviewer/main/installer.py | python
```
or in Windows OS,
```bash
curl.exe https://raw.githubusercontent.com/MeF0504/pyviewer/main/installer.py | python
```
By default, this script installs pyviewer repository in `~/.config/pyviewer/src`.
If you want to specify the install path,
```bash
python -c "$(curl https://raw.githubusercontent.com/MeF0504/pyviewer/main/installer.py)" path/to/install
```

## Usage
```bash
usage: pyviewer [-h]
                [-t {hdf5,pickle,numpy,np_pickle,tar,zip,sqlite3,raw_image,jupyter,xpm}]
                [-iv IMAGE_VIEWER] [--encoding ENCODING] [--ask_password]
                [-v | -k [KEY ...] | -i | -c]
                file

show the constitution of a file. support file types ... hdf5, pickle, numpy,
np_pickle, tar, zip, sqlite3, raw_image, jupyter, xpm

positional arguments:
  file                  input file

options:
  -h, --help            show this help message and exit
  -t {hdf5,pickle,numpy,np_pickle,tar,zip,sqlite3,raw_image,jupyter,xpm}, --type {hdf5,pickle,numpy,np_pickle,tar,zip,sqlite3,raw_image,jupyter,xpm}
                        specify the file type. "pyviewer help -t TYPE" will
                        show the detailed help.
  -iv IMAGE_VIEWER, --image_viewer IMAGE_VIEWER
                        set image viewer. Supported args are 'matplotlib' (use
                        matplotlib.pyplot.imshow), 'PIL' (use PIL.Image.show),
                        'cv2' (use cv2.imshow), and other string is treated as
                        an external command (e.g. gosr, open).
  --encoding ENCODING   specify the encoding format.
  --ask_password, -p    ask for the password for the file if needed.
  -v, --verbose         show details
  -k [KEY ...], --key [KEY ...]
                        specify the key name to show. If no key is specified,
                        return the list of keys.
  -i, --interactive     open a file with interactive mode.
  -c, --interactive_cui
                        open a file with interactive CUI mode.

PyViewer has some subcommands, 'pyviewer update' updates this command,
'pyviewer config_list' shows the current optional configuration, and 'pyviewer
help -t TYPE' shows the detailed help of each type.
```

