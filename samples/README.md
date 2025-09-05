# Sample files for AFTViewer

## setting_sample.json

A sample setting file for AFTViewer.

### How to use

1. Copy this file to `setting.json`.
```sh
cp setting_sample.json ~/.config/aftviewer/setting.json
```
2. Modify the parameters as needed.

See [wiki page](https://github.com/MeF0504/aftviewer/wiki/Customization) for details.

## show_image.py

A sample script of additional file type viewer.
This script shows image files using image viewer.

### How to use
1. Install this script
```sh
aftviewer-libinstaller show_image.py png jpg jpeg
```
See [wiki page](https://github.com/MeF0504/aftviewer/wiki/Extension) for details.

2. Open image files using AFTViewer.
```sh
aftviewer sample.png [-t show_image]
```

## gif

Sample GIF images of `aftviewer` command with various file types.
