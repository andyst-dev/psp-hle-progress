#!/bin/sh
# Regenerate the coverage picture and the missing-function list.
#
#   tools/update.sh <psprecomp> <module.elf> <name> [<pspsdk>] [<reached-NIDs>]
#
# <psprecomp>      a checkout of sp00nznet/psprecomp with its build directory
# <module.elf>     the decrypted module to inspect (never committed here)
# <name>           prefix the toolkit emits under, e.g. "locoroco"
# <pspsdk>         optional pspsdk checkout, to name the NIDs that are missing
# <reached-NIDs>   optional comma-separated NID list the run reported as
#                  unimplemented; these are the ones that get a ring
#
# Then: git add -A && git commit -m "coverage: <what landed>"
set -e
TK=${1:?usage: tools/update.sh <psprecomp> <module.elf> <name> [<pspsdk>] [<reached>]}
ELF=${2:?}
NAME=${3:?}
PSPSDK=${4:-}
REACHED=${5:-}
HERE=$(cd "$(dirname "$0")/.." && pwd)

clang -O0 -I "$TK/include" "$HERE/tools/hle_dump.c" "$TK/build/libpsprecomp.a" -o /tmp/hle_dump
/tmp/hle_dump > /tmp/hle.txt
mkdir -p /tmp/emit_coverage
"$TK/build/tools/allegrexrecomp/allegrexrecomp" emit "$ELF" /tmp/emit_coverage "$NAME" > /dev/null

set -- --module "$NAME" --outdir "$HERE" --reached "$REACHED"
[ -n "$PSPSDK" ] && set -- "$@" --pspsdk "$PSPSDK"
python3 "$HERE/tools/hle_coverage.py" "/tmp/emit_coverage/${NAME}_imports.c" /tmp/hle.txt "$@"
python3 "$HERE/tools/hle_treemap.py" "$HERE/data/${NAME}-hle-cov.json" "$HERE/docs/progress/hle-coverage.svg"
echo "updated docs/progress/hle-coverage.svg and docs/progress/hle-missing.md"
