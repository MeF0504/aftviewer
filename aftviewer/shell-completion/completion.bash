# aftviewer completion setting for bash

_aftviewer_cmp()
{
    local cur prev
    cur=${COMP_WORDS[${COMP_CWORD}]}
    prev=${COMP_WORDS[${COMP_CWORD}-1]}

    local opts="-h -V -t -iv -o -p -v -k -i -c --encoding"
    if [[ "${cur:0:1}" = "-" ]]; then
        COMPREPLY=( $(compgen -W "$opts" -- "$cur") )
    elif [[ "${prev}" = "-h" ]]; then
        # show help
        COMPREPLY=()
    elif [[ "${prev}" = "-t" ]]; then
        # select type
        local types="$(_get_aftviewer_types 'type')"
        COMPREPLY=( $(compgen -W "$types" -- "$cur") )
    elif [[ "${prev}" = "-" ]]; then
        # select subcommand
        local subcmds="$(_get_aftviewer_types 'subcmds')"
        COMPREPLY=( $(compgen -W "$subcmds" -- "$cur") )
    elif [[ "${prev}" = "-iv" ]]; then
        # select image viewer
        local image_viewer="$(_get_aftviewer_types 'image_viewer')"
        COMPREPLY=( $(compgen -W "$image_viewer" -- "$cur") )
    else
        # select file
        compopt -o filenames
        COMPREPLY=( $(compgen -f -- "$cur") )
    fi
}

complete -F _aftviewer_cmp aftviewer
# aftviewer completion end
