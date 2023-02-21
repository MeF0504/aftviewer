# pyviewer completion setting for bash

_pyviewer_cmp()
{
    local cur prev
    cur=${COMP_WORDS[${COMP_CWORD}]}
    prev=${COMP_WORDS[${COMP_CWORD}-1]}

    local opts="-h -t -iv -p -v -k -i -c --encoding"
    local types="hdf5 pickle numpy tar zip sqlite3 raw_image jupyter xpm stl"
    local image_viewer="PIL matplotlib OpenCV"
    if [[ "${cur:0:1}" = "-" ]]; then
        COMPREPLY=( $(compgen -W "$opts" -- "$cur") )
    elif [[ "${prev}" = "-h" ]]; then
        COMPREPLY=()
    elif [[ "${prev}" = "-t" ]]; then
        # type
        COMPREPLY=( $(compgen -W "$types" -- "$cur") )
    elif [[ "${prev}" = "-iv" ]]; then
        COMPREPLY=( $(compgen -W "$image_viewer" -- "$cur") )
    else
        compopt -o filenames
        COMPREPLY=( $(compgen -f -- "$cur") )
    fi
}

complete -F _pyviewer_cmp pyviewer