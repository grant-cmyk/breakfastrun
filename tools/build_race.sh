#!/usr/bin/env bash
# RACE OR COMBAT (Grant, 18 Nov 2026: "Now I need a game option - combat or race ... I would like to try a traditional race
# ... the idea is to make it competitive so you don't run away with it. 70% speed is good"). The 70% armour tape (the
# gentler NOS) with the title's M choosing the game: RACE (to start with) or COMBAT (the armour tape's game). Two tapes:
#   bash tools/build_race.sh   -> build/racer_race70.tap           RACE as it is (no rubber band)
#                                 build/racer_race70_elastic.tap   RACE with the rubber band: a computer car behind the
#                                                                  leader gets a small push (ai_tune.asm, EL_...)
#                                 then the plain game, last
# What RACE is: src/race.asm (the top); the computer drivers in it: src/ai_tune.asm, the RACE part.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
T="RACEMODE=1 ARMOUR=1 CARDS=1 PACEFIX=1 GRIP1=1 AI=${AI:-1} RT_ROADW=56 RT_CORNER=27 RT_PIN_GAP=1 RT_PIN_W=1 RT_PIN=solid RT_NOLINE=1 RACETRACK=1 NOS=${NOS:-2} NOS_FR=${NOS_FR:-100} GAME_SPEED=${SPEED:-70}"
env $T OUT=racer_race70 BDIR=racer_race70 bash build.sh | tail -2
env $T ELASTIC=1 OUT=racer_race70_elastic BDIR=racer_race70_elastic bash build.sh | tail -2
bash build.sh > /dev/null && echo "the plain game built last: src/options.asm is the plain game's again"
