#! /usr/bin/env python3

import json
from pathlib import Path

with open(Path(__file__).parent.parent/'aftviewer/core/default.json') as f:
    default = json.load(f)

# "config"
#      |__ key
#            |__ parameter: value
config_desc = {
    "defaults": {
        "image_viewer": ['string/null', """The name of the method to show images.
The treatment of this option is the same as the command-line argument (-iv).
If "PIL", "matplotlib", or "cv2" are set, use
[PIL.Image.show()](https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.show),
[matplotlib.pyplot.imshow()](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.imshow.html),
or [cv2.imshow()](https://docs.opencv.org/) respectively.
If another string is given, it is treated as a shell command.
The detailed behavior of this shell command can be set by
the "iv_exec_cmd" option.
If null is set, search the possible modules from "PIL", "matplotlib", and "cv2".
If the image viewer is specified in both the json file and
a command-line argument, the command-line argument is applied."""],
        "image_viewer_cui": ['string/null', """This is the same as "image_viewer", but used when opening a file with CUI mode.
If both "image_viewer" and "image_viewer_cui" are set, the value of "image_viewer_cui" is used in CUI mode and that of "image_viewer" is used in other cases.
If this option is not set and "image_viewer" is set, the value of "image_viewer" is used in CUI mode and other cases.
This option is useful when a shell command is set in "image_viewer" since a shell command is not supported in CUI mode."""],
        "iv_exec_cmd": ['list of string', """Arguments used when the shell command is specified as the image viewer.
Some special keywords are available; "%c" and "%s".
"%c" is replaced by the command (image viewer).
"%s" is replaced by the file path of the image.
These arguments are passed to the [subprocess.run()](https://docs.python.org//3/library/subprocess.html#subprocess.run) function after replacement.
Note that the file path does not necessarily match the file path given in the command line.
In some types, an image file is extracted in a temporary directory."""],
        "system_cmd": ['string/null', """A command called when opening a file with a system command.
In interactive_cui mode, you can open a file with the system (shell) command through the [subprocess.run()](https://docs.python.org//3/library/subprocess.html#subprocess.run) function by shift+↓ key.
If set to null, "start", "open" or "xdg-open" is set in Windows OS, macOS, and Linux OS respectively."""],
        "system_cmd_args": ['list of string', """A setting to control the behavior when opening a file in interactive_cui mode.
This setting can specify the command and arguments of that.
Arguments used when opening a file with system command in interactive_cui mode.
"%c" and "%s" are replaced like "iv_exec_cmd" case."""],
        "pp_kwargs": ['dictionary', """A dictionary passed to the `pprint.pprint()` or `pprint.pformat()` functions as a keyword arguments.
Please see [Python document](https://docs.python.org/3/library/pprint.html#pprint.PrettyPrinter) for available options."""],
        "numpy_printoptions": ['dictionary', """A dictionary to specify the NumPy print format.
This dictionary is passed through to the `numpy.set_printoptions()` directly as a keyword argument.
Please see the [NumPy document](https://numpy.org/doc/stable/reference/generated/numpy.set_printoptions.html) for available options."""],
        "cui_linenumber": ['bool', """If true, show the line number in the main window of CUI mode."""],
        "cui_wrap": ['bool', """If true, texts in the main window of CUI mode are wrapped to display."""],
        },
    "pickle": {
        "encoding": ['string', """The encoding used to load the pickle file.
If you mainly use pickle files made by Python2 script, please set "latin1".
This option is overwritten by the '--encoding' command-line option."""],
        },
    "np_pickle": {
        "encoding": ['string', """The encoding used to load the pickle file.
If you mainly use pickle files made by Python2 script, please set "latin1".
This option is overwritten by the '--encoding' command-line option."""],
        },
    "jupyter": {
        "show_number": ['bool', """ If true, show `(current index)/(number of cells)` at the cell number line."""],
        },
    "stl": {
        "viewer": ['"matplotlib" or "plotly"', """module to display STL file.
Currently "matplotlib" or "plotly" is supported."""],
        "facecolors": ['null/string', """face color of the displayed model.
Since this parameter is used in both Matplotlib and Plotly, available values are limited.
null, full-color code (#xxxxxx), or color name (black, white, red, green, blue,
cyan, magenta, or yellow) is available."""],
        "edgecolors": ['null/string', """edge color of the displayed model.
This is only used in Matplotlib.
The available value is the same as "facecolors"."""],
        },
    }

color_desc = {
    "defaults": {
        "msg_error": 'Color of error messages.',
        "msg_warn": 'Color of warning messages.',
        "msg_key_name": 'color used to show key names.',
        "interactive_path": 'color of "current path:" text in the interactive mode.',
        "interactive_contents": 'color of "contents in this dict:" text in the interactive mode.',
        "interactive_output": 'color of "output::" text in the interactive mode.',
        "cui_main": 'Color of the main window of the CUI mode.',
        "cui_top": 'Color of the top window of the CUI mode.',
        "cui_left": 'Color of the left side bar of the CUI mode.',
        "cui_error": 'Color of error messages of the CUI mode.',
        "cui_search": 'Color to highlight found word in the CUI mode.',
        "cui_file_info": 'Color of file information (line number etc.) of the CUI mode.',
        "cui_dir_index": 'Color of index number of directories in side bar of the CUI mode.',
        "cui_file_index": 'Color of index number of files in side bar of the CUI mode.',
        },
    "jupyter": {
        "input_color": 'Color to highlight input index in jupyter file.',
        "output_color": 'Color to highlight output index in jupyter file.',
        "type_color": 'Color to highlight cell type in jupyter file.',
        },
    "hdf5": {
        "type_color": 'Color to highlight attributes of data in hdf5 file.',
        },
    }

print("""
# Introduction

This page explain how to customize the AFTViewer command.

## setting.json

You can change some setting values by creating `setting.json` file in the configuration directory.
If AFTViewer find `$XDG_CONFIG_HOME` variable, the configuration dictionary is
`$XDG_CONFIG_HOME/aftviewer`.
Otherwise the path is
`~/.config/aftviewer`.

Sample: [sample.json](https://github.com/MeF0504/aftviewer/blob/main/samples/setting_sample.json)  
Default values: [default.json](https://github.com/MeF0504/aftviewer/blob/main/aftviewer/core/default.json)

# parameters

This json file should contain one dictionary.
The keys could ne specified in this dictionary are "additional_types", "config", and "colors".  
The details are following.
""")

print("""## "additional_types"
**type: dictionary**  
A dictionary to define the additional supporting file types and their extension of files.
A module name of an additional type is the key name of the dictionary, and the value is the string of extensions with separated by space.
e.g. `"png_sample": "png jpeg jpg"`.  
Note that you need to put the script corresponding to this file type in the `additional_types` in the configuration directory.
See the [[Extension page|Extension]] for detail.
""")

print("""## "config"
**type: dictionary**  
This dictionary define default values of configuration parameters.
Possible keys in this dictionary are "defaults" or file-type names.
The "defaults" set the values used by multiple file types if the parameter is not set on each file type.
Keys of file types set the values only used in this file type.
In this key, values of both parameters in "defaults" and file-type-specific parameters are able to set.
The parameters that can be set are as follows.
""")

assert default['config'].keys() == config_desc.keys()
assert default['config']['defaults'].keys() == config_desc['defaults'].keys()
print('### "defaults"')
for para in config_desc['defaults']:
    t, desc = config_desc['defaults'][para]
    print(f'\n#### "{para}"')
    print(f'**type: {t}**  ')
    print(desc)
config_desc.pop('defaults')

for ft in config_desc:
    assert default['config'][ft].keys() == config_desc[ft].keys()
    print(f'\n### "{ft}"')
    for para in config_desc[ft]:
        t, desc = config_desc[ft][para]
        print(f'\n#### "{para}"')
        print(f'**type: {t}**  ')
        print(desc)

print("""## "colors"
**type: dictionary**  
This dictionary defines color settings.
Each color type takes two values; the first one is the foreground color and
the second one is the background color.
Available values are following:  
'k' (Black), 'r' (Red), 'g' (Green), 'y' (Yellow),
'b' (Blue), 'c' (Cyan), 'm' (Magenta), 'w' (White),
0-255 (terminal 256 colors if supported),
or None (not set)  
Keys of this dictionary is same as "config" dictionary: "defaults" or file-type names.
Parametes and values in each key also works as the same.
The parameters that can be set are as follows.""")

assert default['colors'].keys() == color_desc.keys()
assert default['colors']['defaults'].keys() == color_desc['defaults'].keys()
print('### defaults')
for para in color_desc['defaults']:
    desc = color_desc['defaults'][para]
    print(f'\n#### "{para}"')
    print(desc)
color_desc.pop('defaults')

for ft in color_desc:
    print(f'\n### "{ft}"')
    assert default['colors'][ft].keys() == color_desc[ft].keys()
    for para in color_desc[ft]:
        desc = color_desc[ft][para]
        print(f'\n#### "{para}"')
        print(desc)
