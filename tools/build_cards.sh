#!/usr/bin/env bash
# THE DRIVER CARDS TRIAL (Grant, 17 Nov 2026): the tight race track with keener computer cars, every car driving by its card
# in tools/driver_cards.txt (acceleration, speed and grip out of 10) and every computer driver with its own personality.
#   bash tools/build_cards.sh        -> build/racer_cards.tap, then build/racer_cards_grip1.tap (your car's grip sums once a
#                                       picture: quicker), then the plain game last (it puts src/options.asm back)
# Change a rating in tools/driver_cards.txt and run this again: tools/make_cards.py turns the cards into src/cards.asm.
# AI=0 or 2 before it for EASY or HARD drivers (NORMAL is built).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
T="CARDS=1 PACEFIX=1 AI=${AI:-1} RT_ROADW=56 RT_CORNER=27 RT_PIN_GAP=1 RT_PIN_W=1 RT_PIN=solid RT_NOLINE=1 RACETRACK=1"
env $T OUT=racer_cards BDIR=racer_cards bash build.sh | tail -2
env GRIP1=1 $T OUT=racer_cards_grip1 BDIR=racer_cards_grip1 bash build.sh | tail -2
bash build.sh > /dev/null && echo "the plain game built last: src/options.asm is the plain game's again"
