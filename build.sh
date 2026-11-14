#!/usr/bin/env bash
# Build Breakfast Run: build/racer.tap (with its BASIC loader), racer.bin and racer.sym.
# Usage: build.sh [small|big]     the cars (default small; the big cars need a memory plan first)
#        OBJECTS=1 build.sh        with the coloured objects (off by default: too slow yet - PROJECT-LOG, 14 Nov)
# Run from anywhere. Needs pasmo and the retro plugin's zxspectrum skill (its build.sh).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CARSOPT="${1:-small}"
CARS="$CARSOPT" python3 "$ROOT/tools/make_data.py" | grep -i "cars:"
U=15; [ "$CARSOPT" = "big" ] && U=12
OBJ=0; [ "${OBJECTS:-}" = "1" ] && OBJ=1     # OBJECTS=1 bash build.sh: the coloured objects (run OBJECTS=1 python3 tools/make_world.py first)
printf '; Build options (written by build.sh)\nOPT_TALL equ 1                  ; (always: the tables that sit in the program rather than at the top of memory)\nCAR_U    equ %s                 ; draw_car: the car frame'"'"'s x - 12 for the big cars, 15 for the small\nOPT_OBJ  equ %s                 ; 1: the coloured objects (obj_paint, objects.asm)\n' "$U" "$OBJ" > "$ROOT/src/options.asm"
cd "$ROOT/src"
B=$(ls /root/.claude/plugins/synced/*/retro/skills/zxspectrum/scripts/build.sh 2>/dev/null | head -1)
B=${ZX_BUILD:-$B}
bash "$B" asm racer.asm ../build/racer.tap racer
pasmo racer.asm ../build/racer.bin ../build/racer.sym
grep -i -E "^(code_end|init_end)\s" ../build/racer.sym
