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
T="SCRUB=${SCRUB:-5} NOSBOX=1 RACEMODE=1 RACEONLY=1 ARMOUR=1 CARDS=1 PACEFIX=1 GRIP1=1 AI=${AI:-1} RT_ROADW=56 RT_CORNER=27 RT_PIN_GAP=1 RT_PIN_W=1 RT_PIN=solid RT_NOLINE=1 RACETRACK=1 NOS=${NOS:-1} NOS_FR=${NOS_FR:-100} STEADY=${STEADY:-5} GAME_SPEED=75"
env $T OUT=racer_cars75 BDIR=racer_cars75 bash build.sh | tail -2
env $T ELASTIC=1 OUT=racer_cars75_elastic BDIR=racer_cars75_elastic bash build.sh | tail -2
# Grant, 22 Nov 2026 ("32 should be fine"; "that tap played better"): the race-only pair again at 32 headings for every car
# (HEAD32=all), every car's left-facing headings mirrored as they are drawn (MIRROR=all - the room for it), 2,400 bytes of the
# frames under 0x8000 and the rest in the program (BIG_LO_ROOM) - build/racer_cars75_h32.tap, racer_cars75_h32_elastic.tap
T="$T HEAD32=all MIRROR=all BIG_LO_ROOM=2400"
env $T OUT=racer_cars75_h32 BDIR=racer_cars75_h32 bash build.sh | tail -2
env $T ELASTIC=1 OUT=racer_cars75_h32_elastic BDIR=racer_cars75_h32_elastic bash build.sh | tail -2
# Grant, 22 Nov 2026 ("I want that track narrower with more severe corners - more difficult turns"): the 32-heading tape on
# two tighter tracks to choose from - B: the road 48 px, the corners 16, the chicane 64 deep (racer_cars75_h32_w48.tap);
# D: 40, 12, 64 (racer_cars75_h32_w40.tap). (Track 1 as it was: 56, 27, 40.)
# Then (Grant: "Its internal corners are square, can you make them slightly rounded. The roads on the left, could you add a
# turn there? ... also make the chicane at the top middle more severe"): both with the inside corners rounded (RT_INROUND 6),
# a turn on the left straight (RT_LEFT 40) and the chicane 80 deep and 16 wide at its foot (RT_CHICANE, RT_CHW)
TT="RT_CHICANE=80 RT_CHW=16 RT_LEFT=40 RT_INROUND=6"
env $T $TT RT_ROADW=48 RT_CORNER=16 OUT=racer_cars75_h32_w48 BDIR=racer_cars75_h32_w48 bash build.sh | tail -2
env $T $TT RT_ROADW=40 RT_CORNER=12 OUT=racer_cars75_h32_w40 BDIR=racer_cars75_h32_w40 bash build.sh | tail -2
# Then (Grant: "The track is very angular - the corners need to be more rounded, but sharp round turns"): B with its centre
# line smoothed (RT_SMOOTH 3: every bend a round turn) - 256 edge pictures, the most one map can hold
env $T $TT RT_ROADW=48 RT_CORNER=16 RT_SMOOTH=3 OUT=racer_cars75_h32_round BDIR=racer_cars75_h32_round bash build.sh | tail -2
env $T $TT RT_ROADW=48 RT_CORNER=16 RT_SMOOTH=3 ELASTIC=1 OUT=racer_cars75_h32_round_elastic BDIR=racer_cars75_h32_round_elastic bash build.sh | tail -2   # (Grant: "B rounded is good" - THE RACE TAPE now, balanced)
# Grant, 22 Nov 2026 ("in a much earlier release we use the breakfast look and feel with loops of the edges and a table look
# and feel. Can we try this with that in place. I want to see if it is any more fun compared to this. The track just feels
# bland"): the same game on the breakfast table (track 1 as it was, the cereal O's): build/racer_cars75_breakfast.tap
env NOSTURN=1 WEIGHT=1 FLASHME=1 GRID_PLACE=${GRID_PLACE:-3} MUG=1 SCRUB=${SCRUB:-5} NOSBOX=1 RACEMODE=1 RACEONLY=1 ARMOUR=1 CARDS=1 PACEFIX=1 GRIP1=1 AI=${AI:-1} NOS=${NOS:-1} NOS_FR=${NOS_FR:-100} STEADY=${STEADY:-5} GAME_SPEED=75 TILE1=1 FLIP=1 TOWER=1 LOOP=0 RT_FACESLOW=1 HEAD32=all MIRROR=all BIG_LO_ROOM=3000 OUT=racer_cars75_breakfast BDIR=racer_cars75_breakfast bash build.sh | tail -2
# (LOOP=0 since 22 Nov 2026 - Grant: "improve the performance speed/smoothness ... I don't want to compromise smoothness": the
# table has room for the unrolled screen copy at COPIER, 6,500 T a picture quicker than the loop the race track needs.) And a
# TRIAL of the quicker rhythm: every picture 4 TV frames (STEADY=4), 12.5 a second - build/racer_cars75_breakfast_fast.tap
# (Grant, 22 Nov 2026: "still too slow, but it is smooth ... make the NOS a bit stronger": this one at 85% (BF_SPEED), NOS=3 - THE TAPE NOW)
env NOSTURN=1 WEIGHT=1 FLASHME=1 GRID_PLACE=${GRID_PLACE:-3} MUG=1 SCRUB=${SCRUB:-5} NOSBOX=1 RACEMODE=1 RACEONLY=1 ARMOUR=1 CARDS=1 PACEFIX=1 GRIP1=1 AI=${AI:-1} NOS=3 NOS_FR=${NOS_FR:-100} STEADY=4 GAME_SPEED=${BF_SPEED:-85} TILE1=1 FLIP=1 TOWER=1 LOOP=0 RT_FACESLOW=1 HEAD32=all MIRROR=all BIG_LO_ROOM=3000 OUT=racer_cars75_breakfast_fast BDIR=racer_cars75_breakfast_fast bash build.sh | tail -2
# TRIAL (Grant, 22 Nov 2026: "are you able to make the race track map slightly larger?"): the same tape with the mini-map
# 40 px wide, not 24 (MAPW40, as chosen 16 Nov) - build/racer_cars75_breakfast_fast_map40.tap
env NOSTURN=1 WEIGHT=1 FLASHME=1 GRID_PLACE=${GRID_PLACE:-3} MUG=1 SCRUB=${SCRUB:-5} NOSBOX=1 RACEMODE=1 RACEONLY=1 ARMOUR=1 CARDS=1 PACEFIX=1 GRIP1=1 AI=${AI:-1} NOS=3 NOS_FR=${NOS_FR:-100} STEADY=4 GAME_SPEED=${BF_SPEED:-85} TILE1=1 FLIP=1 TOWER=1 LOOP=0 RT_FACESLOW=1 HEAD32=all MIRROR=all BIG_LO_ROOM=3000 MAPW40=1 OUT=racer_cars75_breakfast_fast_map40 BDIR=racer_cars75_breakfast_fast_map40 bash build.sh | tail -2
# TRIAL (Grant, 22 Nov 2026: "If you are several seconds ahead, then 2 of the cars can benefit from NOS at different
# times ... a deterministic rule"): the chasers' NOS - build/racer_cars75_breakfast_fast_cnos.tap (src/cnos.asm)
env NOSTURN=1 WEIGHT=1 FLASHME=1 GRID_PLACE=${GRID_PLACE:-3} MUG=1 SCRUB=${SCRUB:-5} NOSBOX=1 RACEMODE=1 RACEONLY=1 ARMOUR=1 CARDS=1 PACEFIX=1 GRIP1=1 AI=${AI:-1} NOS=3 NOS_FR=${NOS_FR:-100} STEADY=4 GAME_SPEED=${BF_SPEED:-85} TILE1=1 FLIP=1 TOWER=1 LOOP=0 RT_FACESLOW=1 HEAD32=all MIRROR=all BIG_LO_ROOM=3000 CNOS=1 OUT=racer_cars75_breakfast_fast_cnos BDIR=racer_cars75_breakfast_fast_cnos bash build.sh | tail -2
# (A plain-tablecloth version - CLOTHPLAIN=1, about 6,000 T a picture quicker - was built and tried; Grant, 22 Nov 2026: "fast
# tape, dotted cloth ... happy with that - lets stick to that".)
bash build.sh > /dev/null && echo "the plain game built last: src/options.asm is the plain game's again"
