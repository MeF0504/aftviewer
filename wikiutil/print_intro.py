#! /usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path
import subprocess

sysver = sys.version_info
if sysver.major*100+sysver.minor >= 311:
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError as e:
        print(f'aftviewer requires Python >= 3.11 or tomli: {e}')
        sys.exit(1)

debug = False
default = False
setting_file = Path('~/.config/aftviewer/setting.toml').expanduser()
if setting_file.is_file():
    with open(setting_file, 'rb') as f:
        setting = tomllib.load(f)
    if 'debug' in setting and setting['debug']:
        debug = True
    if 'force_default' in setting and setting['force_default']:
        default = True

assert debug, 'debug is off.'
assert default, 'force_default is off.'

res = subprocess.run(['aftviewer', '-h'], capture_output=True)
helpmsg = res.stdout.decode()

print('''**Welcome to the AFTViewer wiki!**

# Introduction

Any File Type Viewer (AFTViewer) is a CUI/TUI tool made by Python to view any kind of packaged, archived, or binary files.

# Usage

```bash
{}
```


# Requirements

The basic process of this software is designed to work with standard libraries of recent [Python3](https://www.python.org/).  
[Pygments](https://pygments.org/) is an optional requirement for `Jupyter`.

To show images, imaging-related libraries ([PIL (Pillow)](https://pillow.readthedocs.io/)
by default)
or shell commands (e.g., "open" in macOS) with supporting bitmap (.bmp) files are required.

# Installation

`pip` command is available.

```bash
python -m pip install git+https://github.com/MeF0504/aftviewer
```
or in Windows OS,
```bash
py -m pip install git+https://github.com/MeF0504/aftviewer
```

# Add viewers and image viewers
You can install additional viewers and image viewers by following;
```
aftviewer - libinstall URL
```
See https://github.com/topics/aftviewer for available viewers.
'''.format(helpmsg))
