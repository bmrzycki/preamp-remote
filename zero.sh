#!/bin/bash

unalias -a
base=$(cd $(dirname "$0") && echo "$PWD")
name=$(basename "$base")

if [[ $1 = clean ]]; then
    (cd "$base" && \
	 rm -f zero_*.tar.gz zero*.cfg run.sh)
    exit 0
fi

err() {
    echo "error: $@" 2>&1
    exit 1
}

rev_d=$(git -C "$base" show -s --format='%ci' HEAD 2>/dev/null)
rev=$(git -C "$base" describe --always --long --dirty --tags 2>/dev/null)
[[ -z $rev ]] && rev='unknown'

outf="$base/zero_$rev.tar.gz"
[[ -f $outf ]] && err "refusing to overwrite '$outf'"
[[ -d $base/serial ]] || "$base/pyserial.sh"

mk_cfg() {
    local dev="$1"
    echo '[net]'
    echo '  name ='
    echo '  port = 8000'
    echo
    echo '[preamp]'
    echo "  dev = $dev"
    echo
    echo '[version]'
    echo "  rev  = $rev"
    echo "  date = $rev_d"
}

mk_run() {
    local dev="$1"
    echo '#!/bin/sh'
    echo
    echo 'base=$(cd $(dirname "$0") && pwd)'
    echo
    echo "if [ -e '$dev' ]; then"
    echo '    cfg="$base/zero.cfg"'
    echo 'else'
    echo '    cfg="$base/zero-fake.cfg"'
    echo 'fi'
    echo
    echo '"$base/srv" -c "$cfg"'
}

mk_cfg /dev/ttyUSB0 > "$base/zero.cfg"
mk_cfg fake         > "$base/zero-fake.cfg"
mk_run /dev/ttyUSB0 > "$base/run.sh"
chmod 755 "$base/run.sh"

tmpf="$(mktemp)"
(cd "$base/.." && \
     tar -zcf "$tmpf" \
	 "$name"/*.py \
	 "$name"/run.sh \
	 "$name"/*.cfg \
	 "$name"/web \
	 "$name"/serial)
mv "$tmpf" "$outf"
echo "Created '$outf'"
