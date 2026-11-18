#!/usr/bin/env bash
# Rebuild EVERY race-track tape in build/ from the source as it stands, then the plain game last (build.sh's option builds
# rewrite src/options.asm and the car data; the plain build puts them back). Run it after any change to the race track's
# code, so that no tape is left stale (17 Nov 2026: stale ones were found twice).
#   bash tools/build_racetrack_tapes.sh          about 5 minutes; one line a tape: its name and the bytes free in the program
# One at a time - two builds at once would trip over each other's src/options.asm.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
one() {      # one <tape name> <switches...>
  local name="$1"; shift
  if env "$@" bash build.sh > "/tmp/rt_build_$name.log" 2>&1; then
    free=$(awk 'tolower($1)=="code_end" {print $3}' "build/$name.sym" | head -1 | tr -d 'Hh')
    echo "$name: $((0xC000 - 0x$free)) bytes free"
  else
    echo "$name: DID NOT BUILD - $(grep -i -m1 'error:' "/tmp/rt_build_$name.log")"
  fi
}
G="RT_PIN_GAP=1 RT_PIN_W=1 RT_PIN=solid RT_NOLINE=1 RACETRACK=1"      # the thin green line, the long way round
# the first trial tapes (track 1, 72 px road)
one racer_racetrack                    RACETRACK=1
one racer_racetrack_noline             RT_NOLINE=1 RACETRACK=1
one racer_racetrack_noline_grip1       GRIP1=1 RT_NOLINE=1 RACETRACK=1
one racer_racetrack_noline_pin         RT_PIN=solid RT_NOLINE=1 RACETRACK=1
one racer_racetrack_noline_pindash     RT_PIN=dash RT_NOLINE=1 RACETRACK=1
one racer_racetrack_noline_pin1        $G OUT=racer_racetrack_noline_pin1 BDIR=racetrack_noline_pin1
one racer_racetrack_noline_pin1_grip1  GRIP1=1 $G OUT=racer_racetrack_noline_pin1_grip1 BDIR=racetrack_noline_pin1_grip1
one racer_racetrack_noline_rows16      RT_ROWS=16 RT_NOLINE=1 RACETRACK=1
one racer_racetrack_noline_rows16_grip1 GRIP1=1 RT_ROWS=16 RT_NOLINE=1 RACETRACK=1
one racer_racetrack_sparse             RT_DASH=sparse RACETRACK=1
one racer_racetrack_sparse_grip1       GRIP1=1 RT_DASH=sparse RACETRACK=1
# the look Grant chose, tracks 1 to 3
for t in 1 2 3; do
  n=racer_track_green; [ $t != 1 ] && n="${n}_track$t"
  one $n            TRACK=$t RACETRACK=green
  one ${n}_grip1    GRIP1=1 TRACK=$t RACETRACK=green
done
one racer_track_green_react1           REACT1=1 RACETRACK=green
one racer_track_green_grip1_react1     GRIP1=1 REACT1=1 RACETRACK=green
# the tight tracks: road width, corner radius, the computer cars' level
for w in "w56 56 54" "w56s 56 27" "w48s 48 27"; do
  set -- $w
  for a in "easy 0" "normal 1" "hard 2"; do
    set -- $w $a
    one racer_tight_$1_$4 PACEFIX=1 AI=$5 RT_ROADW=$2 RT_CORNER=$3 $G OUT=racer_tight_$1_$4 BDIR=tight_$1_$4
  done
done
T="PACEFIX=1 AI=1 RT_ROADW=56 RT_CORNER=27 $G"
one racer_tight_w56s_normal_grip1         GRIP1=1 $T OUT=racer_tight_w56s_normal_grip1 BDIR=tight_w56s_normal_grip1
one racer_tight_w56s_normal_react1        REACT1=1 $T OUT=racer_tight_w56s_normal_react1 BDIR=tight_w56s_normal_react1
one racer_tight_w56s_normal_grip1_react1  GRIP1=1 REACT1=1 $T OUT=racer_tight_w56s_normal_grip1_react1 BDIR=tight_w56s_normal_grip1_react1
# two players (on the tight 56 px track, NORMAL)
# (the two-player tapes start you on pole, as before - player 2 drives the car beside you; tests/two_player_test.py compares
#  their one-player mode with these two, the ordinary tapes built with you on pole: GRID_BACK=0)
one racer_tight_w56s_normal_pole        GRID_BACK=0 $T OUT=racer_tight_w56s_normal_pole BDIR=tight_w56s_normal_pole
one racer_tight_w56s_normal_grip1_pole  GRID_BACK=0 GRIP1=1 $T OUT=racer_tight_w56s_normal_grip1_pole BDIR=tight_w56s_normal_grip1_pole
one racer_2p         TWOP=1 $T OUT=racer_2p BDIR=racer_2p
one racer_2p_grip1   GRIP1=1 TWOP=1 $T OUT=racer_2p_grip1 BDIR=racer_2p_grip1
one racer_2p_points  TWOP_PTS=3 TWOP=1 $T OUT=racer_2p_points BDIR=racer_2p_points
# the driver cards (tools/build_cards.sh builds just these two; tools/driver_cards.txt has the ratings)
one racer_cards        CARDS=1 $T OUT=racer_cards BDIR=racer_cards
one racer_cards_grip1  GRIP1=1 CARDS=1 $T OUT=racer_cards_grip1 BDIR=racer_cards_grip1
# armour and weapons on the driver cards (tools/build_armour.sh builds just these two; src/armour_tune.asm has the numbers)
one racer_armour        ARMOUR=1 CARDS=1 $T OUT=racer_armour BDIR=racer_armour
one racer_armour_grip1  GRIP1=1 ARMOUR=1 CARDS=1 $T OUT=racer_armour_grip1 BDIR=racer_armour_grip1
# RACE or COMBAT at 70% and 75% (tools/build_race.sh builds just these four; src/race.asm says what RACE is)
R="RACEMODE=1 ARMOUR=1 CARDS=1 GRIP1=1 NOS=2 NOS_FR=100 GAME_SPEED=70 $T"
one racer_race70          $R OUT=racer_race70 BDIR=racer_race70
one racer_race70_elastic  ELASTIC=1 $R OUT=racer_race70_elastic BDIR=racer_race70_elastic
R="RACEMODE=1 ARMOUR=1 CARDS=1 GRIP1=1 NOS=2 NOS_FR=100 GAME_SPEED=75 $T"      # (Grant, 19 Nov 2026: "Any chance of speed 75%?")
one racer_race75          $R OUT=racer_race75 BDIR=racer_race75
one racer_race75_elastic  ELASTIC=1 $R OUT=racer_race75_elastic BDIR=racer_race75_elastic
# and the plain game last
bash build.sh > /tmp/rt_build_plain.log 2>&1 && echo "racer (the plain game): built last, src/options.asm is the plain game's again"
