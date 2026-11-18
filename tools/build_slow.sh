#!/usr/bin/env bash
# THE SLOWER GAME, A TRIAL (Grant, 18 Nov 2026: "the game plays too fast, I want it slower and smoother" - and "I would
# prefer a maximum jump of 4 pixels or even less"): the armour GRIP1 tape (tools/build_armour.sh) with the whole game at
# 60%, 55% and 50% of today's speed (GAME_SPEED, the top of tools/make_cards.py) and the gentler NOS ("gentler NOS is
# fine": NOS and NOS_FR in build.sh).
#   bash tools/build_slow.sh        -> build/racer_armour_slow70.tap, _slow60.tap, _slow55.tap, _slow50.tap, then the plain game last
#   SPEEDS="70 45" bash tools/build_slow.sh      other speeds (build/racer_armour_slowNN.tap)
# None of these is the game's default: Grant picks one by driving it.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
T="ARMOUR=1 CARDS=1 PACEFIX=1 GRIP1=1 AI=${AI:-1} RT_ROADW=56 RT_CORNER=27 RT_PIN_GAP=1 RT_PIN_W=1 RT_PIN=solid RT_NOLINE=1 RACETRACK=1"
# the gentler NOS on these tapes: a quarter more push and top speed (not twice), burning two seconds (not one)
SLOW_NOS="NOS=${NOS:-2} NOS_FR=${NOS_FR:-100}"
for s in ${SPEEDS:-70 60 55 50}; do   # (70: Grant, 18 Nov 2026, "Any chance of a 70% speed")
  env $T $SLOW_NOS GAME_SPEED=$s OUT=racer_armour_slow$s BDIR=racer_armour_slow$s bash build.sh | tail -1
done
bash build.sh > /dev/null && echo "the plain game built last: src/options.asm is the plain game's again"
