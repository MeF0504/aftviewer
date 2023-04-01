#! /usr/bin/env bash

./bin/pyviewer -h

sleep 1

test_pyviewer()
{
    path=$1
    if ! [[ -f "$path" ]]; then
        echo "$path is not exist."
        return
    fi
    echo $path
    sleep 1
    args=$2

    ./bin/pyviewer "$path"
    sleep 1
    command shift 2
    for opt in "$@"; do
        case "$opt" in
            k)
                echo "~~~~~~~~~~~keys~~~~~~~~~~"
                ./bin/pyviewer "$path" $args -k
                read -p "key: " KEY
                ./bin/pyviewer "$path" $args -k "$KEY"
                read -p "key: " KEY
                ./bin/pyviewer "$path" $args -k "$KEY"
                sleep 1
                ;;
            v)
                echo "~~~~~~~~~~~verbose~~~~~~~~~~"
                ./bin/pyviewer "$path" $args -v
                sleep 1
                ;;
            i)
                echo "~~~~~~~~~~~interactive~~~~~~~~~~"
                ./bin/pyviewer "$path" $args -i
                ;;
            c)
                echo "~~~~~~~~~~~cui~~~~~~~~~~"
                ./bin/pyviewer "$path" $args -c
                ;;
        esac
    done
}

