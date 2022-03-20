# PyViewer

CUI view tool made by python.
## supported files
hdf5, pickle, numpy, tar, zip, sqlite3, raw_image, jupyter, xpm.

## usage
```bash
usage: pyviewer [-h] [-t {hdf5,pickle,numpy,tar,zip,sqlite3,raw_image,jupyter,xpm}] [-iv IMAGE_VIEWER] [--encoding ENCODING] [-v | -k [KEY ...] | -i | -c] file

show the constitution of a file. support file types ... hdf5, pickle, numpy, tar, zip, sqlite3, raw_image, jupyter, xpm

positional arguments:
  file                  input file

options:
  -h, --help            show this help message and exit
  -t {hdf5,pickle,numpy,tar,zip,sqlite3,raw_image,jupyter,xpm}, --type {hdf5,pickle,numpy,tar,zip,sqlite3
,raw_image,jupyter,xpm}
                        file type
  -iv IMAGE_VIEWER, --image_viewer IMAGE_VIEWER
                        set image viewer. supported args are 'matplotlib' (use matplotlib.pyplot.imshow), 'PIL' (use PIL.Image.show), 'OpenCV' (use cv2.imshow), and other string is treated as an external command (e.g. gosr, open).
  --encoding ENCODING   specify the encoding format in pickle and zip file.
  -v, --verbose         show details
  -k [KEY ...], --key [KEY ...]
                        Dictionary key name in a pickle, path to a Group/Dataset in hdf5, a path to a file/dictionary in tar/zip, a table[/column[,column2...]] in sqlite3 or a key name in npz. If no key is specified, return the list of keys.
  -i, --interactive     open a file with interactive mode. support pickle, hdf5, tar, zip, sqlite3.
  -c, --interactive_cui open a file with interactive CUI mode. support hdf5, tar, zip, sqlite3.
```

## costomize

You can change some default values by creating `$XDG_CONFIG_HOME/pyviewer/setting.json` or `~/.config/pyviewer/setting.json`.
The json file should contain one dictionary. The possible key names of this are following.

- image_viewer (str)
    - The method to show images. The role of the argument is the same as the command-line argument (-iv). If image viewer is specified in both json file and command-line arguments, the latter one is applied.
- exec_cmd (list)
    - The executed command used to show an image. '%c' and '%s' are replaced by the command and file name individually. Note that this option is effective when the image viewer is nor 'PIL', 'matplotlib', and 'OpenCV'.
- zip_encoding (str)
    - The character code used to encode the zip file.
- pickle_encoding (str)
    - The character code used to encode the pickle file.
- type (list)
    - List to extend supported files. The list should contain dictionaries, and each dictionary contains 'type_name', 'lib' and 'ext'.
    - type_name (str)
        - Name of additional type. Any string is OK.
    - lib (str)
        - Lib name to show additional type file. The lib should contain the main_'type' function and the function takes two arguments, file path, and arguments. 'png_sample.py' is the sample to show png, jpeg file.
    - ext (str)
        - Extensions of additional type files. It is a string separated with ','. When the file ends with these extensions, the main_'type' function in the lib is called.


