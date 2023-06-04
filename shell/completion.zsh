# pyviewer completion setting for zsh

_pyviewer_cmp()
{
    _arguments \
        '(- *)'{-h,--help}'[show help]' \
        '(-t --type)'{-t,--type}'[set type]:type:_pyviewr_types' \
        '(-iv --image_viewer)'{-iv,--image_viewer}'[set image viewer]:image viewer:_pyviewer_iv' \
        '(-p --ask_password)'{-p,--ask_password}'[password is asked when opening a file]:pass' \
        '(-v --verbose)'{-v,--verbose}'[view file with verbose mode]:verbose' \
        '(-k --key)'{-k,--key}'[set viewing keys]:keys' \
        '(-i --interactive)'{-i,--interactive}'[view file with interactive mode]:interactive' \
        '(-c --interactive_cui)'{-c,--interactive_cui}'[view file with interactive cui mode]:interactive cui' \
        --encoding'[set encoding]:encoding' \
        '*:target file:_pyviewer_targets'
}

_pyviewer_targets()
{
    _alternative \
        'files:target files:_files' \
        'alters:alters:_pyviewer_alters'
}

_pyviewer_alters()
{
    _values 'alters' \
        'update' 'config_list'
}

_pyviewr_types()
{
    _values 'types' \
        $(_get_pyviewer_types)
}
_pyviewer_iv()
{
    _values 'image viewer' \
        'PIL' 'matplotlib' 'OpenCV'
}
compdef _pyviewer_cmp pyviewer

