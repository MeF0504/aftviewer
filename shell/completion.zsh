# pyviewer completion setting for zsh

_pyviewer_cmp()
{
    _arguments \
        '(- *)'-h'[show help]' \
        -t'[type]:type:_pyviewr_types' \
        -iv'[image viewer]:image viewer:_pyviewer_iv' \
        -p'[ask pass]:pass' \
        -v'[verbose]:verbose' \
        -k'[keys]:keys' \
        -i'[interactive]:interactive' \
        -c'[interactive cui]:interactive cui' \
        --encoding'[encoding]:encoding' \
        '*:target file:_files'
}
_pyviewr_types()
{
    _values 'types' \
        'hdf5' 'pickle' 'numpy' 'tar' 'zip' 'sqlite3' 'raw_image' 'jupyter' 'xpm' 'stl'
}
_pyviewer_iv()
{
    _values 'image viewer' \
        'PIL' 'matplotlib' 'OpenCV'
}
compdef _pyviewer_cmp pyviewer

