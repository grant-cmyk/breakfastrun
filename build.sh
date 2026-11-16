#!/usr/bin/env bash
# Build Breakfast Run: build/racer.tap (with its BASIC loader), racer.bin and racer.sym.
# Usage: build.sh [small|big]     the cars (default small; the big cars need a memory plan first)
#        TRACK=2 build.sh          track 2, THE BREAKFAST CLUB -> build/racer_track2.tap (racer.tap is track 1)
#        TRACK=5 build.sh          track 5, A FRIDGE TOO FAR, the one with the bridge -> build/racer_track5.tap
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
# BRIDGE (track 5 only): OPT_BRIDGE switches in everything the crossover needs (src/bridge.asm and the "if OPT_BRIDGE" blocks);
# with 0 not one byte of tracks 1-3 changes
BR=0; [ "${TRACK:-1}" = "5" ] && BR=1
printf 'OPT_BRIDGE equ %s               ; 1: the track has a bridge (TRACK=5 bash build.sh: levels, walls, ramps - bridge.asm)\n' "$BR" >> "$ROOT/src/options.asm"
# LOOP=1: the looped screen-copy routine (about 430 bytes at COPIER, not 6,083 - docs/design/OPTIMISATION-PLAN.md)
printf 'OPT_LOOP equ %s                 ; 1: the screen copy as a loop of one character row (LOOP=1 bash build.sh)\n' "${LOOP:-0}" >> "$ROOT/src/options.asm"
# TOWER=1: the race order's car pictures drawn from the cars' own frames (tower_b, hud.asm) - 320 bytes of second copies go.
# Always so on track 5; MULTI=1 turns it on too.
MULTI="${MULTI:-0}"; TW="${TOWER:-0}"; [ "$BR" = "1" ] && TW=1; [ "$MULTI" != "0" ] && TW=1
printf 'OPT_TOWERF equ %s               ; 1: the race order draws its cars from their frames (TOWER=1 bash build.sh)\n' "$TW" >> "$ROOT/src/options.asm"
printf 'OPT_MULTI equ %s                ; 1: several tracks in one load (tools/make_multi.py sets it: not for build.sh alone)\n' "$MULTI" >> "$ROOT/src/options.asm"
# FLIP=1: the cars' headings that are another heading upside down are not kept (tools/make_data.py reads FLIP too): about 1.9 KB
printf 'OPT_FLIP equ %s                 ; 1: draw_car and the title car read such a frame last row first (FLIP=1 bash build.sh)\n' "${FLIP:-0}" >> "$ROOT/src/options.asm"
B=$(ls /root/.claude/plugins/synced/*/retro/skills/zxspectrum/scripts/build.sh 2>/dev/null | head -1)
B=${ZX_BUILD:-$B}
# ONE TRACK A BUILD (15 Nov 2026: memory has no room for two). TRACK unset or 1: track 1, from src/ as
# it stands -> build/racer.tap. TRACK=2: THE BREAKFAST CLUB -> build/racer_track2.tap (.bin, .sym):
# a copy of src/ is made in build/track2/src, tools/make_world.py writes that track's world, waypoints,
# O map, mini-map and grid into the copy, and the game is assembled there. src/ is not touched.
TRACK="${TRACK:-1}"
# BDIR=<folder under build/>: build in a copy there (track 1 too) - tools/make_multi.py and the trial builds use it, so
# that build/trackN and src/ are left alone. PREASM="command": run in the copy's src/ just before assembling.
if [ "$TRACK" = "1" ] && [ -z "${BDIR:-}" ]; then
  cd "$ROOT/src"; OUTN=racer
else
  T="$ROOT/build/${BDIR:-track$TRACK}"
  rm -rf "$T"; mkdir -p "$T/src"; cp "$ROOT"/src/*.asm "$T/src/"
  TRACK="$TRACK" WORLD_OUT="$T/src" python3 "$ROOT/tools/make_world.py"
  cd "$T/src"; OUTN="racer_track$TRACK"
fi
OUTN="${OUT:-$OUTN}"
[ -n "${PREASM:-}" ] && bash -c "$PREASM"
bash "$B" asm racer.asm "$ROOT/build/$OUTN.tap" racer
pasmo racer.asm "$ROOT/build/$OUTN.bin" "$ROOT/build/$OUTN.sym"
grep -i -E "^(code_end|init_end)\s" "$ROOT/build/$OUTN.sym"
