from importlib import metadata
import warnings


def chk_deps(filetype: str) -> bool:
    deps = {
            'numpy': ['numpy'],
            'np_pickle': ['numpy'],
            'raw_image': ['rawpy'],
            'hdf5': ['h5py'],
            'stl': ['numpy-stl'],
            'fits': ['astropy'],
            'healpix': ['healpy'],
            'excel': ['openpyxl', 'xlrd'],
            'root': ['uproot'],
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
