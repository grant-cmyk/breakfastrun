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
# RACETRACK=1: A TRIAL - a traditional race track: black road, green grass to the pixel, a dashed white limit line, each car
# its own colour (src/racetrack.asm; Grant, 16 Nov 2026). Track 1 -> build/racer_racetrack.tap. It needs the room the savings
# give, so it turns them on; it builds in its own folder (build/racetrack); tools/make_world.py reads RACETRACK too.
if [ "${RACETRACK:-0}" = "1" ]; then
  export RACETRACK TILE1=1 FLIP=1 TOWER=1 LOOP=1
  # RT_NOLINE=1 with it: no limit line (quicker: a concession for Grant to judge) -> build/racer_racetrack_noline.tap
  RTN=""; [ "${RT_NOLINE:-0}" = "1" ] && RTN="${RTN}_noline"
  # RT_DASH=sparse with it: the limit line's dashes 8 on, 24 off (quicker too) -> build/racer_racetrack_sparse.tap
  [ "${RT_DASH:-}" = "sparse" ] && RTN="${RTN}_sparse"
  # RT_PIN=solid or dash with RT_NOLINE=1: the limit as a thin green line just inside the grass's edge -> ..._noline_pin.tap, _pindash.tap
  [ "${RT_PIN:-}" = "solid" ] && RTN="${RTN}_pin"
  [ "${RT_PIN:-}" = "dash" ] && RTN="${RTN}_pindash"
  # RT_ROWS=16 with it (15 to 18): A SMALLER PLAY WINDOW - only the window's first 16 rows of squares scroll; the rows under
  # them are a black band that holds the mini-map, the crew chief's bubble, the spoons and the mug -> ..._rows16.tap
  [ "${RT_ROWS:-19}" != "19" ] && RTN="${RTN}_rows${RT_ROWS}"
  # GRIP1=1 with it: your car's grip sums once a picture (a trial switch, below) -> ..._grip1.tap
  [ "${GRIP1:-0}" = "1" ] && RTN="${RTN}_grip1"
  BDIR="${BDIR:-racetrack$RTN}"; OUT="${OUT:-racer_racetrack$RTN}"
elif [ "${GRIP1:-0}" = "1" ]; then
  BDIR="${BDIR:-grip1_t${TRACK:-1}}"; OUT="${OUT:-racer_grip1}"      # (GRIP1=1 without RACETRACK: today's game with the switch -> build/racer_grip1.tap. It needs a few bytes: TILE1=1 FLIP=1 TOWER=1 GRIP1=1 bash build.sh)
fi
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
# TILE1=1: the eight unrolled tile routines as one, patched once a picture (src/gen_tiles1.asm): about 1 KB of program
printf 'OPT_TILE1 equ %s                ; 1: one tile routine (TILE1=1 bash build.sh)\n' "${TILE1:-0}" >> "$ROOT/src/options.asm"
# PACEFIX=1: the computer cars' throttle counted in pictures, not TV frames (their pace no longer depends on the picture rate)
printf 'OPT_PACEFIX equ %s              ; 1: pace_gate counts pictures (PACEFIX=1 bash build.sh)\n' "${PACEFIX:-0}" >> "$ROOT/src/options.asm"
# AI=1 or 2: the computer cars' level - 0 EASY (as they were), 1 NORMAL, 2 HARD (src/ai_tune.asm has every number; Grant, 17 Nov 2026)
printf 'OPT_AI equ %s                   ; the computer cars: 0 as they were, 1 NORMAL, 2 HARD (AI=1 bash build.sh; ai_tune.asm)\n' "${AI:-0}" >> "$ROOT/src/options.asm"
# ROADW=1: A TRIAL - the road on white paper, by colour square (src/roadwhite.asm; Grant, 16 Nov 2026: "Try E as a trial tape").
# ROADW=2: that, and no dots on the road's squares. It needs room: build it with TILE1=1 FLIP=1 TOWER=1 (PROJECT-LOG, 16 Nov 2026).
printf 'OPT_ROADCOL equ %s              ; the trial road paper: 7 white, 6 yellow (ROADCOL=6 ROADW=1 bash build.sh)\n' "${ROADCOL:-7}" >> "$ROOT/src/options.asm"
printf 'OPT_ROADBR equ %s               ; 1: the trial road paper bright (ROADCOL=5 ROADBR=1 ROADW=1 bash build.sh: bright cyan)\n' "${ROADBR:-0}" >> "$ROOT/src/options.asm"
printf 'OPT_ROADW equ %s                ; 1: the road white (ROADW=1 bash build.sh); 2: and plain, no dots (ROADW=2) - a trial\n' "${ROADW:-0}" >> "$ROOT/src/options.asm"
# MAPW40=1: the mini-map 40 pixels wide, not 24 (Grant, 16 Nov 2026: "C wide please"). Its ink no longer fits the spare strip it
# lives in, so it needs room in the program: build it with TILE1=1 FLIP=1 TOWER=1. It builds in its own folder (build/map40_tN)
# -> build/racer_map40.tap (track 1) or build/racer_map40_trackN.tap; tools/make_world.py reads MAPW40 too.
printf 'OPT_MAP40 equ %s                ; 1: the mini-map 40 wide, its ink in the program (MAPW40=1 bash build.sh)\n' "${MAPW40:-0}" >> "$ROOT/src/options.asm"
if [ "${MAPW40:-0}" = "1" ]; then
  T40=racer_map40; [ "${TRACK:-1}" != "1" ] && T40="racer_map40_track${TRACK:-1}"
  BDIR="${BDIR:-map40_t${TRACK:-1}}"; OUT="${OUT:-$T40}"
fi
printf 'OPT_RT equ %s                   ; 1: the race track trial - black road, green grass (RACETRACK=1 bash build.sh)\n' "${RACETRACK:-0}" >> "$ROOT/src/options.asm"
# CHOOSE=1: the choose screen between the title and the race - track, driver, car, extra (src/choose.asm). Only with the
# several-tracks build: use tools/build_choose.sh -> build/racer_choose.tap
printf 'OPT_CHOOSE equ %s               ; 1: the choose screen (tools/build_choose.sh: not for build.sh alone)\n' "${CHOOSE:-0}" >> "$ROOT/src/options.asm"
# GRIP1=1: A TRIAL SWITCH - your car is moved once a picture like the computer cars, its grip sums once a picture (it still
# steers every TV frame). Quicker, but it changes the handling a little: off unless asked for (PROJECT-LOG, 17 Nov 2026).
printf 'OPT_GRIP1 equ %s                ; 1: your car moved, and its grip worked out, once a picture (GRIP1=1 bash build.sh)\n' "${GRIP1:-0}" >> "$ROOT/src/options.asm"
# TWOP=1: A TRIAL - the title's 2 starts a two-player race in one shared view (src/twoplayer.asm; Grant, 17 Nov 2026: "two
# players would exist in the same screen"). With RACETRACK=1; it needs about 900 bytes. TWOP_PTS=N with it: the POINTS rule.
printf 'OPT_2P equ %s                   ; 1: two players in one view (TWOP=1 RACETRACK=1 bash build.sh)\n' "${TWOP:-0}" >> "$ROOT/src/options.asm"
printf 'OPT_2PPTS equ %s                ; two players, the POINTS rule: first to this many points (0: the LEASH rule; TWOP_PTS=3)\n' "${TWOP_PTS:-0}" >> "$ROOT/src/options.asm"
printf 'OPT_RTROWS equ %s              ; the race track trial: how many of the window'"'"'s 19 rows of squares scroll (RT_ROWS=16 RACETRACK=1 bash build.sh)\n' "${RT_ROWS:-19}" >> "$ROOT/src/options.asm"
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
