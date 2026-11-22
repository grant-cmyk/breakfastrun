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
# RACETRACK=green: THE LOOK GRANT CHOSE (17 Nov 2026: "the lines on the outside look good") - the race track with the limit as
# a thin green line, 1 pixel wide, 1 pixel inside the grass's edge. Any of tracks 1, 2 and 3:
#   RACETRACK=green bash build.sh           -> build/racer_track_green.tap          (track 1)
#   TRACK=2 RACETRACK=green bash build.sh   -> build/racer_track_green_track2.tap   (and TRACK=3)
#   GRIP1=1 with either                     -> ..._grip1.tap   (your car's grip sums once a picture: quicker, the feel not yet judged)
# It is short for RT_PIN_GAP=1 RT_PIN_W=1 RT_PIN=solid RT_NOLINE=1 RACETRACK=1, which still works (and makes the same bytes).
if [ "${RACETRACK:-0}" = "green" ]; then
  [ "${TRACK:-1}" = "5" ] && { echo "RACETRACK=green: tracks 1, 2 and 3 only (track 5's bridge is not built in this look)"; exit 1; }
  export RACETRACK=1 RT_NOLINE=1 RT_PIN=solid RT_PIN_GAP=1 RT_PIN_W=1
  GN=""; [ "${TRACK:-1}" != "1" ] && GN="_track${TRACK}"
  [ "${GRIP1:-0}" = "1" ] && GN="${GN}_grip1"
  [ "${REACT1:-0}" = "1" ] && GN="${GN}_react1"      # (REACT1=1: the computer cars decide every 8th TV frame - below)
  BDIR="${BDIR:-track_green$GN}"; OUT="${OUT:-racer_track_green$GN}"
fi
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
# GRID_BACK: on the race-track builds you start last on the grid (Grant, 18 Nov 2026); not with two players. GRID_BACK=0: on pole.
GB=0; [ "${RACETRACK:-0}" = "1" ] && [ "${TWOP:-0}" != "1" ] && [ "${GRID_BACK:-1}" != "0" ] && GB=1
printf 'OPT_GRIDBACK equ %s             ; 1: you start last on the grid (race-track builds; GRID_BACK=0 bash build.sh for pole)\n' "$GB" >> "$ROOT/src/options.asm"
printf 'OPT_2PPTS equ %s                ; two players, the POINTS rule: first to this many points (0: the LEASH rule; TWOP_PTS=3)\n' "${TWOP_PTS:-0}" >> "$ROOT/src/options.asm"
# REACT1=1: A TRIAL SWITCH - each computer car decides how to steer every 8th TV frame, not every 4th (their REACT setting
# one higher). Quicker in the pack, but they turn in a little later: off unless asked for (PROJECT-LOG, 17 Nov 2026).
printf 'OPT_REACT1 equ %s               ; 1: the computer cars decide every 8th TV frame, not every 4th (REACT1=1 bash build.sh)\n' "${REACT1:-0}" >> "$ROOT/src/options.asm"
# (RACETRACK: where the place plate's drawing lives. Tracks 1 and 2 have room in the program, where code runs at full
# speed; track 3's map leaves none, so there it stays in the slower room under 0x8000. RT_PLATEUP=0 or 1 to say otherwise.)
PUP=0; [ "${RACETRACK:-0}" = "1" ] && [ "${TRACK:-1}" != "3" ] && PUP=1
printf 'OPT_RTPUP equ %s                ; RACETRACK: 1 - the place plate is drawn from the program, not from under 0x8000 (tracks 1 and 2)\n' "${RT_PLATEUP:-$PUP}" >> "$ROOT/src/options.asm"
# RT_ARROWC: the corner arrow black over grass, green beside it (Grant, 17 Nov 2026, option C). On by default, but not on
# track 3, which has no room under 0x8000 for it (12 bytes free; it needs about 150): there the arrow stays yellow by the cars' rule.
ARC=1; [ "${TRACK:-1}" = "3" ] && ARC=0
printf 'OPT_ARROWC equ %s               ; RACETRACK: 1 - the corner arrow black over grass, green beside it (option C; not track 3)\n' "${RT_ARROWC:-$ARC}" >> "$ROOT/src/options.asm"
# FACESLOW: the drivers' looks (src/faces_mood.asm, Grant's faces of 18 Nov 2026) kept under 0x8000 on the race-track builds,
# where there is room; the plain game and track 3 have none and keep the earlier looks (src/faces_mood_plain.asm).
FSL=0; [ "${RACETRACK:-0}" = "1" ] && [ "${TRACK:-1}" != "3" ] && FSL=1
printf 'OPT_FACESLOW equ %s             ; RACETRACK: 1 - the drivers\x27 looks under 0x8000, Grant\x27s newest (not track 3, not the plain game)\n' "${RT_FACESLOW:-$FSL}" >> "$ROOT/src/options.asm"
BAND=0; [ "${RACETRACK:-0}" = "1" ] && [ "${TRACK:-1}" != "3" ] && BAND=1
printf 'OPT_RTBAND equ %s               ; RACETRACK: 1 - a pair of the same banded picture is copied as it is (rt_sq: rt_c1; 87 bytes - track 3 has not the room)\n' "${RT_BANDED:-$BAND}" >> "$ROOT/src/options.asm"
# RT_LAPFIX: your laps when you go off the track a fair bit and come back on further round (src/lap_low.asm; Grant, 18 Nov
# 2026: "I went off track for a bit, and I seemed to lose a lap"). On for the race track, but not on track 3, which has no
# room under 0x8000 for it (about 100 bytes; it has 12): there the old rule stays (the next four waypoints only).
LAPF=0; [ "${RACETRACK:-0}" != "0" ] && [ "${TRACK:-1}" != "3" ] && LAPF=1
printf 'OPT_RTLAP equ %s                ; RACETRACK: 1 - off the track and back on further round costs no lap (src/lap_low.asm; not track 3)\n' "${RT_LAPFIX:-$LAPF}" >> "$ROOT/src/options.asm"
# RT_EYES: the race order's faces look left and right before the race (src/plate_slow.asm tw_anim; Grant, 18 Nov 2026: "at
# the start of the games I want the faces animated looking left and right"). Not on track 3: no room under 0x8000 there.
printf 'OPT_RTEYES equ %s               ; RACETRACK: 1 - the race order'"'"'s faces look left and right until the lights go green (not track 3)\n' "${RT_EYES:-$LAPF}" >> "$ROOT/src/options.asm"
printf 'OPT_RTROWS equ %s              ; the race track trial: how many of the window'"'"'s 19 rows of squares scroll (RT_ROWS=16 RACETRACK=1 bash build.sh)\n' "${RT_ROWS:-19}" >> "$ROOT/src/options.asm"
# CARDS=1: A TRIAL - THE DRIVER CARDS (Grant, 17 Nov 2026): every car's acceleration, top speed and grip come from its card in
# tools/driver_cards.txt (ratings out of 10; change a number there and build again - tools/make_cards.py turns them into
# src/cards.asm), and each computer driver has a personality (src/ai_tune.asm, the CARDS part). Grip is poor to start with.
# For the race-track builds: tools/build_cards.sh -> build/racer_cards.tap
printf 'OPT_CARDS equ %s                ; 1: the driver cards - each car its own speed, acceleration and grip (CARDS=1; tools/build_cards.sh)\n' "${CARDS:-0}" >> "$ROOT/src/options.asm"
# ARMOUR=1 with CARDS=1 and RACETRACK=1: A TRIAL - ARMOUR AND WEAPONS (Grant, 17 Nov 2026): every car has six pieces of armour
# (its card's "armour" rating says how much a piece takes), lost in bumps and shown as a bar on each row of the race order; a
# car with none left limps; the computer's tank shoots and its clown car pushes its wheels out (src/armour_tune.asm has every
# number). tools/build_armour.sh -> build/racer_armour.tap
printf 'OPT_ARMOUR equ %s               ; 1: armour, the bar on the HUD and the two weapons (ARMOUR=1 CARDS=1; tools/build_armour.sh)\n' "${ARMOUR:-0}" >> "$ROOT/src/options.asm"
[ "${ARMOUR:-0}" = "1" ] && [ "${CARDS:-0}${RACETRACK:-0}" != "11" ] && { echo "ARMOUR=1 needs CARDS=1 and RACETRACK=1 (tools/build_armour.sh)"; exit 1; }
# GAME_SPEED=60 (with CARDS=1 and BDIR=...): A TRIAL - THE WHOLE GAME SLOWER (Grant, 18 Nov 2026: "the game plays too fast, I
# want it slower and smoother"): every car's top speed, push, tyres and corner speeds at that percent of today's (the top of
# tools/make_cards.py), and the few other numbers that go with speed (GAME_SPEED in the code). 100 (the default): as it was.
# NOS=1 (or 2): a GENTLER NOS - the push and top speed up a half (or a quarter) where they double today; NOS_FR=100: it burns
# that many TV frames (50 today). tools/build_slow.sh builds the slow trial tapes.
# RACEMODE=1 with ARMOUR=1 (Grant, 18 Nov 2026: "I need a game option - combat or race ... a traditional race"): one tape, two
# games, chosen on the title with M - COMBAT (the armour tape's game, exactly) or RACE (every car the racer in its own colour
# with a number on its roof, the same card for all, no armour and no weapons, the gap to the car ahead in the race order).
# src/race.asm, src/ai_tune.asm (the RACE drivers). ELASTIC=1 with it: the computer cars behind the leader get a small push.
# tools/build_race.sh builds the two tapes.
printf 'OPT_RACE equ %s                 ; 1: the title offers RACE or COMBAT (RACEMODE=1 ARMOUR=1: tools/build_race.sh)\n' "${RACEMODE:-0}" >> "$ROOT/src/options.asm"
printf 'RT_SMOOTHN equ %s               ; the track'"'"'s centre line smoothed this many times (RT_SMOOTH: the round-turn track - ai_tune.asm balances its cars)\n' "${RT_SMOOTH:-0}" >> "$ROOT/src/options.asm"
printf 'OPT_SCRUB equ %s                ; 0: as before; n: a slide costs speed - yours 1/2^n of it a TV frame, a computer car twice the drag (SCRUB=n)\n' "${SCRUB:-0}" >> "$ROOT/src/options.asm"
printf 'OPT_NOSBOX equ %s               ; 1: the NOS you hold shown as a canister in a rounded box, one colour square each (NOSBOX=1)\n' "${NOSBOX:-0}" >> "$ROOT/src/options.asm"
printf 'OPT_RACEONLY equ %s             ; 1: RACE only - no COMBAT, every car its own picture and driver card (RACEONLY=1 RACEMODE=1)\n' "${RACEONLY:-0}" >> "$ROOT/src/options.asm"
H32V=${HEAD32:-0}; [ "$H32V" = "all" ] && H32V=2
printf 'OPT_HEAD32 equ %s               ; 1: the racer drawn at 32 headings (2, HEAD32=all: every car), the computer cars pushed 32 ways\n' "$H32V" >> "$ROOT/src/options.asm"
MIRV=${MIRROR:-0}; [ "$MIRV" = "all" ] && MIRV=2
printf 'OPT_MIRROR equ %s               ; 1: a computer car'"'"'s heading that is another'"'"'s frame mirrored is not kept (MIRROR=1, with FLIP=1; 2, MIRROR=all: yours too)\n' "$MIRV" >> "$ROOT/src/options.asm"
printf 'OPT_STEADY equ %s               ; 0: as before; 5: every picture 5 TV frames and the game moved 5 frames a picture (STEADY=5)\n' "${STEADY:-0}" >> "$ROOT/src/options.asm"
printf 'OPT_ELASTIC equ %s              ; 1: RACE mode - a computer car behind the leader gets a small push (ELASTIC=1 RACEMODE=1)\n' "${ELASTIC:-0}" >> "$ROOT/src/options.asm"
[ "${RACEMODE:-0}" = "1" ] && [ "${ARMOUR:-0}" != "1" ] && { echo "RACEMODE=1 needs ARMOUR=1 (tools/build_race.sh)"; exit 1; }
[ "${ELASTIC:-0}" = "1" ] && [ "${RACEMODE:-0}" != "1" ] && { echo "ELASTIC=1 needs RACEMODE=1 (tools/build_race.sh)"; exit 1; }
GS=${GAME_SPEED:-100}
[ "$GS" != "100" ] && { [ "${CARDS:-0}" != "1" ] || [ -z "${BDIR:-}" ]; } && { echo "GAME_SPEED needs CARDS=1 and a BDIR= (tools/build_slow.sh)"; exit 1; }
printf 'GAME_SPEED equ %s             ; the whole game'"'"'s speed, percent of today'"'"'s (GAME_SPEED=60 CARDS=1: tools/build_slow.sh)\n' "$GS" >> "$ROOT/src/options.asm"
printf 'OPT_NOS equ %s                  ; NOS: 0 twice the push and top speed; 1 a half more; 2 a quarter more (NOS=1 bash build.sh)\n' "${NOS:-0}" >> "$ROOT/src/options.asm"
printf 'NOS_FR equ %s                  ; NOS: how many TV frames one canister burns (NOS_FR=100 bash build.sh)\n' "${NOS_FR:-50}" >> "$ROOT/src/options.asm"
[ "${CARDS:-0}" = "1" ] && GAME_SPEED=100 python3 "$ROOT/tools/make_cards.py"
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
[ "$GS" != "100" ] && GAME_SPEED=$GS CARDS_OUT=. python3 "$ROOT/tools/make_cards.py" | tail -1   # (the slow cards: in the copy only)
[ -n "${PREASM:-}" ] && bash -c "$PREASM"
bash "$B" asm racer.asm "$ROOT/build/$OUTN.tap" racer
pasmo racer.asm "$ROOT/build/$OUTN.bin" "$ROOT/build/$OUTN.sym"
grep -i -E "^(code_end|init_end)\s" "$ROOT/build/$OUTN.sym"
