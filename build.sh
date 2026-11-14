#!/usr/bin/env bash
# Build Breakfast Run: build/racer.tap (with its BASIC loader), racer.bin and racer.sym.
# Usage: build.sh [big|small] [128|136]     the cars (default big) and the window's height (default 128)
# Run from anywhere. Needs pasmo and the retro plugin's zxspectrum skill (its build.sh).
# A build that is not the default is also copied to build/racer_<cars>_<height>.tap.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CARSOPT="${1:-big}"; ROWS="${2:-128}"
TALL=0; [ "$ROWS" = "136" ] && TALL=1
printf '; Build options (written by build.sh)\nOPT_TALL equ %s                  ; 0: the window 176 x 128; 1: 176 x 136 (the message bar on row 0)\n' "$TALL" > "$ROOT/src/options.asm"
CARS="$CARSOPT" python3 "$ROOT/tools/make_data.py" | grep -i "cars:"
cd "$ROOT/src"
B=$(ls /root/.claude/plugins/synced/*/retro/skills/zxspectrum/scripts/build.sh 2>/dev/null | head -1)
B=${ZX_BUILD:-$B}
bash "$B" asm racer.asm ../build/racer.tap racer
pasmo racer.asm ../build/racer.bin ../build/racer.sym
grep -i -E "^(code_end|init_end)\s" ../build/racer.sym
cp ../build/racer.tap "../build/racer_${CARSOPT}_${ROWS}.tap"
