# Extensions

This directory contains scripts that are outside the basic concept.

## plotly.py

This script is an extension to show images using the [Plotly](https://plotly.com/python/) and the [Pillow](https://pillow.readthedocs.io/) library.

### How to use

1. Install the required libraries
```bash
pip install numpy plotly Pillow
```

2. Install the extension
```bash
aftviewer-libinstaller plotly.py image-viewer
```

3. Use the extension, e.g.,
```bash
aftviewer HOGE.fit -iv plotly
```

## sixel.py

This script is an extension to show images in the terminal using [libsixel](https://github.com/saitoha/libsixel).

### How to use
1. Install the libsixel with a Python wrapper.
See the instructions [here](https://github.com/saitoha/libsixel/tree/master/python#install).

2. Install the extension
```bash
aftviewer-libinstaller sixel.py image-viewer
```

3. Use the extension, e.g.,
```bash
aftviewer HOGE.ipynb -iv sixel
```
