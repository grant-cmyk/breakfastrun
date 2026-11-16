#!/bin/bash
# A lap by autopilot in the pack and alone for each tape named (build/<name>.tap, .sym): TV frames a picture,
# pictures a second, the screen copy's T-states, cells shown torn.   Usage: bash tests/speed_table.sh racer racer_looped ...
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
for n in "$@"; do
  for mode in ${MODES:-pack 1}; do
    echo "$n $mode"
  done
done | xargs -P "${JOBS:-4}" -L 1 bash -c 'n=$0; m=$1; [ "$m" = pack ] && m=; o=$(ALONE=$m python3 tests/tearlap.py build/$n.tap build/$n.sym 2>&1); echo "$n|$(echo "$o" | head -1)|$(echo "$o" | sed -n 2p | cut -c1-70)|$(echo "$o" | sed -n 3p | grep -o "\"frames_torn\": [0-9]*, \"torn_share\": [0-9.]*")|$(echo "$o" | sed -n 4p | cut -c1-30)"' | sort
