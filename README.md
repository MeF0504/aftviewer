# Any File Type Viewer

is a CUI/TUI tool to view any type of files made by Python.

See the [wiki page](https://github.com/MeF0504/aftviewer/wiki) for the details.

Sample GIFs can be found [here](samples/gif/README.md).

## Concept

This software is designed to be an universal viewer for any files.
Also, the basic functions of this software work with only the standard libraries of recent Python 3.
Third-party libraries are required and loaded only when specific file types are handled.

## Requirements

The basic process of this software is designed to work on standard libraries of recent [Python3](https://www.python.org/).  
[Pygments](https://pygments.org/) is an optional requirement for `Jupyter`.

To show images, imaging-related libraries ([PIL (Pillow)](https://pillow.readthedocs.io/)
by default)
or shell commands (e.g., "open" in macOS) with supporting bitmap (.bmp) files are required.

## Install

```bash
python -m pip install git+https://github.com/MeF0504/aftviewer
```
or in Windows OS,
```bash
py -m pip install git+https://github.com/MeF0504/aftviewer
```

## Usage
```bash
aftviewer [-t TYPE] file
```
shows the constitution of a file.
To see the detailed options, subcommands, and supported file types, enter
```bash
aftviewer -h
```

---
To see the details of available options for each file type, enter
```bash
aftviewer - help -t TYPE
```
To update this command, enter
```bash
aftviewer - update
```
To install/update the required packages for the supported file type, enter
```
aftviewer - update -t TYPE
```
To install an [additional viewer](https://github.com/topics/aftviewer), enter
```
aftviewer - libinstall URL
```
To show the list of current [configurations](https://github.com/MeF0504/aftviewer/wiki/Customization#parameters), enter
```bash
aftviewer - config_list
```
To set the shell completion, enter
```bash
# bash
aftviewer - shell_completion --bash >> ~/.bashrc
# zsh
aftviewer - shell_completion --zsh >> ~/.zshrc
```
