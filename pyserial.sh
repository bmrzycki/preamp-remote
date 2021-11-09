#!/bin/bash

unalias -a
base=$(cd $(dirname "$0") && echo "$PWD")

if [[ $1 = clean ]]; then
    (cd "$base" && rm -rf serial)
    exit 0
fi

err() {
    echo "error: $@" 2>&1
    exit 1
}

[[ -d "$base/serial" ]] && exit 0
url='https://github.com/pyserial/pyserial/archive/refs/tags/v3.4.tar.gz'
tmpd="$(mktemp -d)"
(cd "$tmpd" && curl -L "$url" | tar -zxf -) || err "unable to fetch"
(cd "$tmpd"/pyserial-* && mv serial "$base") || err "unable to move"
(cd "$base/serial" && echo "$url" >url.txt) || err "unable to make url.txt"
rm -rf "$tmpd"
