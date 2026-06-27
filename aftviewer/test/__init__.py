from importlib import metadata
import warnings

from aftviewer.core import __def, GLOBAL_CONF

if __def:
    warnings.warn('These tests assume fource default is OFF.')

FTs = ['pickle', 'tar', 'zip', 'jupyter']
for av in GLOBAL_CONF.add_viewers:
    FTs.append(av)


def chk_deps(filetype: str) -> bool:
    deps = {
            }
    if filetype not in deps:
        return True

    pack_list = []
    for dst in metadata.distributions():
        pack_list.append(dst.metadata['Name'])
    flag = [False for x in deps[filetype]]
    for i, mod in enumerate(deps[filetype]):
        if mod in pack_list:
            flag[i] = True
        else:
            warnings.warn(f'{mod} is not installed.')

    return all(flag)
