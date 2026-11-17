#!/usr/bin/env bash
# THE ARMOUR AND WEAPONS TRIAL (Grant, 17 Nov 2026): the driver cards build (tools/build_cards.sh) with armour for every car,
# the armour bar on each row of the race order, the computer's tank that shoots and its clown car that pushes its wheels out.
#   bash tools/build_armour.sh       -> build/racer_armour.tap, then build/racer_armour_grip1.tap (your car's grip sums once a
#                                       picture: quicker - the one to drive), then the plain game last
# The armour ratings: tools/driver_cards.txt ("armour N" on each card's ratings line). What a rating is worth:
# ARMOUR_PIECE at the top of tools/make_cards.py. Every other number (ranges, cool-downs, the spin, the limp): the table at
# src/armour_tune.asm. AI=0 or 2 before it for EASY or HARD drivers (NORMAL is built).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
T="ARMOUR=1 CARDS=1 PACEFIX=1 AI=${AI:-1} RT_ROADW=56 RT_CORNER=27 RT_PIN_GAP=1 RT_PIN_W=1 RT_PIN=solid RT_NOLINE=1 RACETRACK=1"
env $T OUT=racer_armour BDIR=racer_armour bash build.sh | tail -2
env GRIP1=1 $T OUT=racer_armour_grip1 BDIR=racer_armour_grip1 bash build.sh | tail -2
bash build.sh > /dev/null && echo "the plain game built last: src/options.asm is the plain game's again"
