#!/usr/bin/env bash
# Build Breakfast Run: build/racer.tap (with its BASIC loader), racer.bin and racer.sym.
# Usage: build.sh [small|big]     the cars (default small; the big cars need a memory plan first)
#        TRACK=2 build.sh          track 2, THE BREAKFAST CLUB -> build/racer_track2.tap (racer.tap is track 1)
#        OBJECTS=1 build.sh        with the coloured objects (off by default: too slow yet - PROJECT-LOG, 14 Nov)
# Run from anywhere. Needs pasmo and the retro plugin's zxspectrum skill (its build.sh).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CARSOPT="${1:-small}"
CARS="$CARSOPT" python3 "$ROOT/tools/make_data.py" | grep -i "cars:"
U=15; [ "$CARSOPT" = "big" ] && U=12
MUS=0; [ "${MUSIC:-}" = "1" ] && MUS=1          # MUSIC=1 bash build.sh: the ditty in the race (off by default)
OBJ=0; [ "${OBJECTS:-}" = "1" ] && OBJ=1     # OBJECTS=1 bash build.sh: the coloured objects (run OBJECTS=1 python3 tools/make_world.py first)
printf '; Build options (written by build.sh)\nOPT_TALL equ 1                  ; (always: the tables that sit in the program rather than at the top of memory)\nCAR_U    equ %s                 ; draw_car: the car frame'"'"'s x - 12 for the big cars, 15 for the small\nOPT_OBJ  equ %s                 ; 1: the coloured objects (obj_paint, objects.asm)\nOPT_MUSIC equ %s                ; 1: the ditty in the race\nOPT_PIT  equ %s                 ; 1: the crew chief talks under the window (off: the logo is there)\nOPT_AY   equ %s                 ; 1: the race tune on the AY sound chip (AY=1 bash build.sh; off since 15 Nov 2026: Grant, "Lets not use the AY chip for now please - old spectrum sounds")\n' "$U" "$OBJ" "$MUS" "${PIT:-0}" "${AY:-0}" > "$ROOT/src/options.asm"
B=$(ls /root/.claude/plugins/synced/*/retro/skills/zxspectrum/scripts/build.sh 2>/dev/null | head -1)
B=${ZX_BUILD:-$B}
# ONE TRACK A BUILD (15 Nov 2026: memory has no room for two). TRACK unset or 1: track 1, from src/ as
# it stands -> build/racer.tap. TRACK=2: THE BREAKFAST CLUB -> build/racer_track2.tap (.bin, .sym):
# a copy of src/ is made in build/track2/src, tools/make_world.py writes that track's world, waypoints,
# O map, mini-map and grid into the copy, and the game is assembled there. src/ is not touched.
TRACK="${TRACK:-1}"
if [ "$TRACK" = "1" ]; then
  cd "$ROOT/src"; OUTN=racer
else
  T="$ROOT/build/track$TRACK"
  rm -rf "$T"; mkdir -p "$T/src"; cp "$ROOT"/src/*.asm "$T/src/"
  TRACK="$TRACK" WORLD_OUT="$T/src" python3 "$ROOT/tools/make_world.py"
  cd "$T/src"; OUTN="racer_track$TRACK"
fi
bash "$B" asm racer.asm "$ROOT/build/$OUTN.tap" racer
pasmo racer.asm "$ROOT/build/$OUTN.bin" "$ROOT/build/$OUTN.sym"
grep -i -E "^(code_end|init_end)\s" "$ROOT/build/$OUTN.sym"
