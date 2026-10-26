#!/bin/sh
# Measure one checkout, then regenerate the report and both diagram palettes.
# Usage: tools/update.sh <psprecomp> <module.elf> <name> [<pspsdk>] [<reached-NIDs>]
# Optional: PSPRECOMP_BUILD_DIR, PSPRECOMP_COVERAGE_LABEL, PSPRECOMP_SNAPSHOT.
set -eu
TK=${1:?usage: tools/update.sh <psprecomp> <module.elf> <name> [<pspsdk>] [<reached>]}
ELF=${2:?}
NAME=${3:?}
PSPSDK=${4:-}
REACHED=${5:-}
HERE=$(cd "$(dirname "$0")/.." && pwd)
BUILD=${PSPRECOMP_BUILD_DIR:-$TK/build}
LABEL=${PSPRECOMP_COVERAGE_LABEL:-Measured checkout}
SNAPSHOT=${PSPRECOMP_SNAPSHOT:-$NAME}
command -v rsvg-convert >/dev/null || { echo "rsvg-convert is required to avoid stale PNGs" >&2; exit 1; }
BASE=${TMPDIR:-${XDG_CACHE_HOME:-$HOME/.cache}}
mkdir -p "$BASE"
WORK=$(mktemp -d "$BASE/psp-hle-progress.XXXXXX")
trap 'rm -rf "$WORK"' EXIT HUP INT TERM
REV=$(git -C "$TK" rev-parse HEAD)
if ! git -C "$TK" diff --quiet HEAD --; then
  LABEL="$LABEL (uncommitted changes)"
fi
cmake -S "$TK" -B "$BUILD"
cmake --build "$BUILD" --config Release --parallel
clang -O0 -I "$TK/include" "$HERE/tools/hle_dump.c" "$BUILD/libpsprecomp.a" -lm -pthread -o "$WORK/hle_dump"
"$WORK/hle_dump" > "$WORK/hle.tsv"
mkdir "$WORK/emit"
"$BUILD/tools/allegrexrecomp/allegrexrecomp" emit "$ELF" "$WORK/emit" "$NAME" > /dev/null
set -- --module "$NAME" --outdir "$HERE" --reached "$REACHED" --source-ref "$REV" --source-label "$LABEL"
[ "$SNAPSHOT" = "$NAME" ] || set -- "$@" --snapshot "$SNAPSHOT"
[ -z "${PSPRECOMP_OBSERVED_SOURCE:-}" ] || set -- "$@" --observed-source "$PSPRECOMP_OBSERVED_SOURCE"
[ -z "$PSPSDK" ] || set -- "$@" --pspsdk "$PSPSDK"
python3 "$HERE/tools/hle_coverage.py" "$WORK/emit/${NAME}_imports.c" "$WORK/hle.tsv" "$@"
if [ "$SNAPSHOT" = "$NAME" ]; then
  DATA="$HERE/data/${NAME}-hle-cov.json"
  python3 "$HERE/tools/hle_treemap.py" "$DATA" "$HERE/docs/progress/hle-coverage.svg"
  python3 "$HERE/tools/hle_treemap.py" "$DATA" "$HERE/docs/progress/hle-coverage-dark.svg" --dark
  rsvg-convert -w 1800 -b white -o "$HERE/docs/progress/hle-coverage.png" "$HERE/docs/progress/hle-coverage.svg"
  rsvg-convert -w 1800 -b '#0d1117' -o "$HERE/docs/progress/hle-coverage-dark.png" "$HERE/docs/progress/hle-coverage-dark.svg"
fi
if [ "$NAME" = locoroco ] && [ -f "$HERE/data/locoroco-bringup-hle-cov.json" ]; then
  python3 "$HERE/tools/update_readme.py"
fi
echo "Updated $SNAPSHOT from $REV ($LABEL)"
