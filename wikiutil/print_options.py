#! /usr/bin/env python3

import json
import tomllib
from pathlib import Path

ROOTDIR = Path(__file__).parent.parent
with open(ROOTDIR/'aftviewer/core/default.json') as f:
    default = json.load(f)

with open(ROOTDIR/'wikiutil/options_text.toml', 'rb') as f:
    desc = tomllib.load(f)
    config_desc = desc['config']
    color_desc = desc['color']
    root_desc = desc['root']
    del desc


def get_def_val(val):
    if type(val) is str:
        return f'"{val}"'
    else:
        val_str = f'{val}'
        val_str = val_str.replace("'", '"')
        val_str = val_str.replace('None', 'null')
        val_str = val_str.replace('True', 'true')
        val_str = val_str.replace('False', 'false')
        return val_str


print(root_desc['intro'])

print(root_desc['add_types'])

print(root_desc['config'])

assert default['config'].keys() == config_desc.keys(), "config key not match."
assert default['config']['defaults'].keys() == config_desc['defaults'].keys(), "config defaults key not match."
print('### "defaults"')
for para in config_desc['defaults']:
    t = config_desc['defaults'][para]['type']
    desc = config_desc['defaults'][para]['desc']
    def_val = get_def_val(default["config"]["defaults"][para])
    print(f'\n- **"{para}"**  ')
    print(f'**type: {t}**  ')
    print(f'*default: {def_val}*  ')
    print(desc)
config_desc.pop('defaults')

for ft in config_desc:
    assert default['config'][ft].keys() == config_desc[ft].keys(), \
        f"config {ft} key not match."
    print(f'\n### "{ft}"')
    for para in config_desc[ft]:
        t = config_desc[ft][para]['type']
        desc = config_desc[ft][para]['desc']
        def_val = get_def_val(default["config"][ft][para])
        print(f'\n- **"{para}"**  ')
        print(f'**type: {t}**  ')
        print(f'*default: {def_val}*  ')
        print(desc)

print("\n")

print(root_desc['colors'])

assert default['colors'].keys() == color_desc.keys(), "color key not match."
assert default['colors']['defaults'].keys() == color_desc['defaults'].keys(), \
    "color defaults key not match."
print('### defaults')
for para in color_desc['defaults']:
    desc = color_desc['defaults'][para]
    def_val = get_def_val(default["colors"]["defaults"][para])
    print(f'\n- **"{para}"**  ')
    print(f'*default: {def_val}*  ')
    print(desc)
color_desc.pop('defaults')

for ft in color_desc:
    print(f'\n### "{ft}"')
    assert default['colors'][ft].keys() == color_desc[ft].keys(), \
        f"color {ft} key not match."
    for para in color_desc[ft]:
        desc = color_desc[ft][para]
        def_val = get_def_val(default["colors"][ft][para])
        print(f'\n- **"{para}"**  ')
        print(f'*default: {def_val}*  ')
        print(desc)
print()
