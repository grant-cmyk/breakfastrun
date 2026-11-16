#!/usr/bin/env bash
# Build the tape with the CHOOSE SCREEN: build/racer_choose.tap (.bin, .sym).
#   bash tools/build_choose.sh
# Tracks 1, 2 and 3 in one load; at the title 1 or 2 goes to the choose screen (track, driver, car, extra - src/choose.asm).
# It is the several-tracks build (tools/make_multi.py) with the choose screen switched in (CHOOSE=1) and the memory savings
# that build needs: the screen copy as a loop, one tile routine, the cars drawn upside down, the race order's cars from
# their frames (docs/design/OPTIMISATION-PLAN.md). More options can be added in front: PACEFIX=1 bash tools/build_choose.sh
# Needs pasmo, gcc (for the packer in tools/zx0, built the first time), python3 with the zx package, and the retro plugin's
# zxspectrum skill (as build.sh). The four one-track tapes are not touched; src/ is put back to the default build's at the end.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PF=""; [ "${PACEFIX:-}" = "1" ] && PF="PACEFIX=1 "
MULTI_ENV="CHOOSE=1 ${PF}TILE1=1 FLIP=1 TOP_ROWS=292" OUT=racer_choose python3 "$ROOT/tools/make_multi.py" "1 2 3"
# put src/options.asm, data.asm and bigcars.asm back as the default build has them (the default tape itself is left alone)
OUT=multi/default_check bash "$ROOT/build.sh" > /dev/null
echo "build/racer_choose.tap is ready"
