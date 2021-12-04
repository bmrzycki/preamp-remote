#!/bin/bash

unalias -a
BASE=$(cd $(dirname "$0") && echo "$PWD")
NAME=$(basename "$BASE")

if [[ $1 = clean ]]; then
    (cd "$BASE" && \
	 rm -f rel_*.tar.gz rel*.cfg run.sh)
    exit 0
fi

err() {
    echo "error: $@" 2>&1
    exit 1
}

REV_D=$(git -C "$BASE" show -s --format='%ci' HEAD 2>/dev/null)
REV=$(git -C "$BASE" describe --always --long --dirty --tags 2>/dev/null)
[[ -z $REV ]] && REV='unknown'

outf="$BASE/rel_$REV.tar.gz"
[[ -f $outf ]] && err "refusing to overwrite '$outf'"
[[ -d $BASE/serial ]] || "$BASE/pyserial.sh"

mk_cfg() {
    local dev="$1"
    echo "# Created on $(date)"
    echo '[net]'
    echo '  name ='
    echo '  port = 8000'
    echo
    echo '[preamp]'
    echo "  dev      = $dev"
    echo '  baudrate = 115200'
    echo
    echo '[version]'
    echo "  rev  = $REV"
    echo "  date = $REV_D"
}

mk_run() {
    local dev="$1"
    echo '#!/bin/sh'
    echo
    echo 'BASE=$(cd $(dirname "$0") && pwd)'
    echo
    echo "if [ -e '$dev' ]; then"
    echo '    "$BASE/srv.py" -c "$BASE/rel.cfg"'
    echo 'else'
    echo '    "$BASE/srv.py" -c "$BASE/rel-fake.cfg"'
    echo 'fi'
}

mk_cfg /dev/ttyUSB0 > "$BASE/rel.cfg"
mk_cfg fake         > "$BASE/rel-fake.cfg"
mk_run /dev/ttyUSB0 > "$BASE/run.sh"
chmod 755 "$BASE/run.sh"

tmpf="$(mktemp)"
(cd "$BASE/.." && \
     tar -zcf "$tmpf" \
	 "$NAME"/*.py \
	 "$NAME"/run.sh \
	 "$NAME"/*.cfg \
	 "$NAME"/web \
	 "$NAME"/serial)
mv "$tmpf" "$outf"
echo "Release tarball '$outf'"
