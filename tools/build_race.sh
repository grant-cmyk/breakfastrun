#!/usr/bin/env bash
# RACE OR COMBAT (Grant, 18 Nov 2026: "Now I need a game option - combat or race ... I would like to try a traditional race
# ... the idea is to make it competitive so you don't run away with it. 70% speed is good"). The 70% armour tape (the
# gentler NOS) with the title's M choosing the game: RACE (to start with) or COMBAT (the armour tape's game). Four tapes:
#   bash tools/build_race.sh   -> build/racer_race70.tap           RACE as it is (no rubber band)
#                                 build/racer_race70_elastic.tap   RACE with the rubber band: a computer car behind the
#                                                                  leader gets a small push (ai_tune.asm, EL_...)
#                                 build/racer_race75.tap, racer_race75_elastic.tap   the same two at 75% speed
#                                 then the plain game, last
# What RACE is: src/race.asm (the top); the computer drivers in it: src/ai_tune.asm, the RACE part.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
# Grant, 19 Nov 2026: "Any chance of speed 75%?" - the same two at 75% too (the same computer drivers' numbers serve both):
#                                 build/racer_race75.tap, build/racer_race75_elastic.tap
# SPEEDS="70" bash tools/build_race.sh builds only the 70% pair.
for SP in ${SPEEDS:-70 75}; do
T="RACEMODE=1 ARMOUR=1 CARDS=1 PACEFIX=1 GRIP1=1 AI=${AI:-1} RT_ROADW=56 RT_CORNER=27 RT_PIN_GAP=1 RT_PIN_W=1 RT_PIN=solid RT_NOLINE=1 RACETRACK=1 NOS=${NOS:-2} NOS_FR=${NOS_FR:-100} GAME_SPEED=$SP"
env $T OUT=racer_race$SP BDIR=racer_race$SP bash build.sh | tail -2
env $T ELASTIC=1 OUT=racer_race${SP}_elastic BDIR=racer_race${SP}_elastic bash build.sh | tail -2
done
bash build.sh > /dev/null && echo "the plain game built last: src/options.asm is the plain game's again"
