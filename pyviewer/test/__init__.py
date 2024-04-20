import sys
from pathlib import Path


def chk_deps(filetype: str) -> bool:
    deps = {
            'numpy': ['numpy'],
            'raw_image': ['rawpy'],
            'hdf5': ['h5py'],
            }
    if filetype not in deps:
        return True
    flag = [False for x in deps[filetype]]
    for i, mod in enumerate(deps[filetype]):
        for sp in sys.path:
            if (Path(sp)/mod).is_dir():
                flag[i] = True
                break
            if (Path(sp)/f'{mod}.py').is_file():
                flag[i] = True
                break

    return all(flag)
