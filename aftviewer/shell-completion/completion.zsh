# aftviewer completion setting for zsh

_aftviewer_cmp()
{
    _arguments \
        '(- *)'{-h,--help}'[show help]' \
        '(- *)'{-V,--version}'[show version information]' \
        '(-t --type)'{-t,--type}'[set type]:type:_pyviewr_types' \
        '(-iv --image_viewer)'{-iv,--image_viewer}'[set image viewer]:image viewer:_aftviewer_iv' \
        '(-o --output)'{-o,--output}'[output file or directory]:output:_files' \
        '(-p --ask_password)'{-p,--ask_password}'[password is asked when opening a file]:pass' \
        '(-v --verbose)'{-v,--verbose}'[view file with verbose mode]' \
        '(-k --key)'{-k,--key}'[set viewing keys]:keys' \
        '(-i --interactive)'{-i,--interactive}'[view file with interactive mode]' \
        '(-c --interactive_cui)'{-c,--interactive_cui}'[view file with interactive cui mode]' \
        --encoding'[set encoding]:encoding' \
        '*:target file:_aftviewer_targets'
}

_aftviewer_targets()
{
    _alternative \
        'files:target files:_files' \
        'alters:alters:_aftviewer_alters'
}

_aftviewer_alters()
{
    _values 'alters' \
        'help' 'update' 'config_list' 'shell_completion'
}

_pyviewr_types()
{
    _values 'types' \
        $(_get_aftviewer_types 'type')
}
_aftviewer_iv()
{
    _values 'image viewer' \
        $(_get_aftviewer_types 'image_viewer')
}
compdef _aftviewer_cmp aftviewer
# aftviewer completion end
