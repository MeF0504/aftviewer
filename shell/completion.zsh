# pyviewer completion setting for zsh

_pyviewer_cmp()
{
    _arguments \
        '(- *)'{-h,--help}'[show help]' \
        '(-t --type)'{-t,--type}'[type]:type:_pyviewr_types' \
        '(-iv --image_viewer)'{-iv,--image_viewer}'[image viewer]:image viewer:_pyviewer_iv' \
        '(-p --ask_password)'{-p,--ask_password}'[ask pass]:pass' \
        '(-v --verbose)'{-v,--verbose}'[verbose]:verbose' \
        '(-k --key)'{-k,--key}'[keys]:keys' \
        '(-i --interactive)'{-i,--interactive}'[interactive mode]:interactive' \
        '(-c --interactive_cui)'{-c,--interactive_cui}'[interactive cui mode]:interactive cui' \
        --encoding'[encoding]:encoding' \
        '*:target file:_files'
}
_pyviewr_types()
{
    _values 'types' \
        $(_get_pyviewr_types)
}
_pyviewer_iv()
{
    _values 'image viewer' \
        'PIL' 'matplotlib' 'OpenCV'
}
compdef _pyviewer_cmp pyviewer

