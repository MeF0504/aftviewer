# aftviewer completion setting for zsh

# zstyle ':completion:*:aftviewer:*' sort false

_aftviewer_cmp()
{
    if [[ "${words: -2}" == "- " ]]; then
        # Since the following completion does not work well,
        # overwrite the completion by catching up "- ".
        _arguments "*:[run subcommand]:_aftviewer_subcmds"
        return
    fi
    local cmds=($(echo ${words}))
    if [[ $cmds[-2] == "-" ]]; then
        # Also, once text is entered after "- ", the above completion looks stop.
        local comp_sub=1
        for subcmd in $(_get_aftviewer_types 'subcmds'); do
            if [[ $subcmd == $cmds[-1] ]]; then
                # If the subcommand is entered, skip
                comp_sub=0
            fi
        done
        if [[ $comp_sub == 1 ]]; then
            _arguments "*:[run subcommand]:_aftviewer_subcmds"
            return
        fi
    fi

    _arguments \
        '(- *)'{-h,--help}'[show help]' \
        '(- *)'{-V,--version}'[show version information]' \
        '(- *)'-'[run subcommand]:subcmd:_aftviewer_subcmds' \
        '(-t --type)'{-t,--type}'[set type]:type:_aftviewer_types' \
        '(-iv --image_viewer)'{-iv,--image_viewer}'[set image viewer]:image viewer:_aftviewer_iv' \
        '(-o --output)'{-o,--output}'[output file or directory]:output:_files' \
        '(-p --ask_password)'{-p,--ask_password}'[password is asked when opening a file]:pass' \
        '(-v --verbose)'{-v,--verbose}'[view file with verbose mode]' \
        '(-k --key)'{-k,--key}'[set viewing keys]:keys' \
        '(-i --interactive)'{-i,--interactive}'[view file with interactive mode]' \
        '(-c --interactive_cui)'{-c,--interactive_cui}'[view file with interactive cui mode]' \
        --encoding'[set encoding]:encoding' \
        '*:target file:_files'
}

_aftviewer_subcmds()
{
    _values 'subcmds' \
        $(_get_aftviewer_types 'subcmds')
}

_aftviewer_types()
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
