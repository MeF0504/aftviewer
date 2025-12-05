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

A sample script of an additional file type viewer.
This script shows how to use image-viewing related functions.

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

## show_json.py

A sample script of an additional file type viewer.
This script shows how to treat dictionary-like objects.

### How to use
1. Install this script
```sh
aftviewer-libinstaller show_json.py json
```
See [wiki page](https://github.com/MeF0504/aftviewer/wiki/Extension) for details.

2. Open image files using AFTViewer.
```sh
aftviewer sample.json [-t show_json]
```

## extensions
Samples of extension scripts that are outside the basic concept.
See [README](extensions/README.md) in the extension directory for details.

## gif

Sample GIF images of `aftviewer` command with various file types.
See [README](gif/README.md) in the gif directory for details.
