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
# Grant, 22 Nov 2026 ("75% was tough, I came 4th. The NOS needs to have a bigger impact ... Need to find a way to make
# movement and turning smoother"): NOS=1 (a half more push and top speed; it was 2, a quarter) and STEADY=5 (every picture
# 5 TV frames, the game moved 5 frames a picture: every jump the same size). NOS=2 STEADY=0 builds them as before.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
# Grant, 19 Nov 2026: "Any chance of speed 75%?" - the same two at 75% too (the same computer drivers' numbers serve both):
#                                 build/racer_race75.tap, build/racer_race75_elastic.tap
# SPEEDS="70" bash tools/build_race.sh builds only the 70% pair.
for SP in ${SPEEDS:-70 75}; do
T="RACEMODE=1 ARMOUR=1 CARDS=1 PACEFIX=1 GRIP1=1 AI=${AI:-1} RT_ROADW=56 RT_CORNER=27 RT_PIN_GAP=1 RT_PIN_W=1 RT_PIN=solid RT_NOLINE=1 RACETRACK=1 NOS=${NOS:-1} NOS_FR=${NOS_FR:-100} STEADY=${STEADY:-5} GAME_SPEED=$SP"
env $T OUT=racer_race$SP BDIR=racer_race$SP bash build.sh | tail -2
env $T ELASTIC=1 OUT=racer_race${SP}_elastic BDIR=racer_race${SP}_elastic bash build.sh | tail -2
done
# Grant, 22 Nov 2026 ("lets exclude the 'combat' style game, but make use of the core car graphics from that ... the joy of the
# different cars is their different behaviour"): RACEONLY=1 - the race only (no COMBAT, no M on the title), every car its own
# picture and its own driver card (tools/driver_cards.txt), driven by the race drivers: build/racer_cars75.tap and
# racer_cars75_elastic.tap. (HEAD32=1 / MIRROR=1 - 32 headings - are written and tested but not on these yet: stage 2.)
T="NOSBOX=1 RACEMODE=1 RACEONLY=1 ARMOUR=1 CARDS=1 PACEFIX=1 GRIP1=1 AI=${AI:-1} RT_ROADW=56 RT_CORNER=27 RT_PIN_GAP=1 RT_PIN_W=1 RT_PIN=solid RT_NOLINE=1 RACETRACK=1 NOS=${NOS:-1} NOS_FR=${NOS_FR:-100} STEADY=${STEADY:-5} GAME_SPEED=75"
env $T OUT=racer_cars75 BDIR=racer_cars75 bash build.sh | tail -2
env $T ELASTIC=1 OUT=racer_cars75_elastic BDIR=racer_cars75_elastic bash build.sh | tail -2
bash build.sh > /dev/null && echo "the plain game built last: src/options.asm is the plain game's again"
