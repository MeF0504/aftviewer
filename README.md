# PyViewer

CUI view tool made by python.

## Requirements

- [Python](https://www.python.org/) > 3.7?
- [numpy](https://numpy.org/) for numpy, xpm
- [h5py](https://docs.h5py.org/) for hdf5
- [rawpy](https://letmaik.github.io/rawpy/api/rawpy.RawPy.html) for raw_image
- [matplotlib](https://matplotlib.org/) for stl

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
usage: pyviewer [-h] [-t {hdf5,pickle,numpy,tar,zip,sqlite3,raw_image,jupyter,xpm,stl}]
                [-iv IMAGE_VIEWER] [--encoding ENCODING] [-v | -k [KEY ...] | -i | -c]
                file

show the constitution of a file. support file types ... hdf5, pickle, numpy, tar, zip, sqlite3, raw_image, jupyter, xpm, stl

positional arguments:
  file                  input file / "pyviewer update" will update this file

options:
  -h, --help            show this help message and exit
  -t {hdf5,pickle,numpy,tar,zip,sqlite3,raw_image,jupyter,xpm,stl}, --type {hdf5,pickle,numpy,tar,zip,sqlite3,raw_image,jupyter,xpm,stl}
                        file type
  -iv IMAGE_VIEWER, --image_viewer IMAGE_VIEWER
                        set image viewer. supported args are 'matplotlib' (use
                        matplotlib.pyplot.imshow), 'PIL' (use PIL.Image.show), 'OpenCV'
                        (use cv2.imshow), and other string is treated as an external
                        command (e.g. gosr, open).
  --encoding ENCODING   specify the encoding format in pickle and zip file.
  -v, --verbose         show details
  -k [KEY ...], --key [KEY ...]
                        Dictionary key name in a pickle, path to a Group/Dataset in
                        hdf5, a path to a file/dictionary in tar/zip, a
                        table[/column[,column2...]] in sqlite3 or a key name in npz. If
                        no key is specified, return the list of keys.
  -i, --interactive     open a file with interactive mode. support pickle, hdf5, tar,
                        zip, sqlite3.
  -c, --interactive_cui
                        open a file with interactive CUI mode. support hdf5, tar, zip,
                        sqlite3.
```

## Customize

You can change some default values by creating `$XDG_CONFIG_HOME/pyviewer/setting.json` or `~/.config/pyviewer/setting.json`.
The json file should contain one dictionary. The possible key names of this are following.

- image_viewer (str)
    - The method to show images. The role of the argument is the same as the command-line argument (-iv). If image viewer is specified in both json file and command-line arguments, the latter one is applied.
- exec_cmd (list)
    - The executed command used to show an image. '%c' and '%s' are replaced by the command and file name individually. Note that this option is effective when the image viewer is nor 'PIL', 'matplotlib', and 'OpenCV'.
- pickle_encoding (str)
    - The character code used to encode the pickle file.
- type (dict)
    - The dictionary for extending file types. the keys are the new type name and the values are file extensions of additional type.
    - You can add any supported types by adding this dictionary and placing a file with the same name as the key in the pyviewerlib directory.
- add_args (str)
    - A string of the name of the file to add additional arguments.  
    This function should contain `main(parser)` function, and `parser` is
    the class of `argparse.ArgumentParser`.  
    You can add new arguments by calling `parser.add_arguments()`.  
    Also see `samples/add_args_sample.py`.
