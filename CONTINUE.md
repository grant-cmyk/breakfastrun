# CONTINUE - Breakfast Run

**Stamped:** 2026-11-19 22:06 SAST (wrap-up) · machine: Claude cloud container · branch: claude/breakfast-run-layout-ik0vpe (not merged to main) · commit: 4e7a7d1 (wrap-up; game change 96b7f86, race mode: computer cars skid more)
**Lifecycle:** Active

**LATEST (22 Nov 2026, 18:41 SAST) - same game, build/racer_cars75_breakfast_fast.tap (dotted cloth - Grant: "lets stick to that").** Bumps now by how the hit happens (weight.asm wt_kick): ram a side - they are kicked sideways and hurt, you keep 3/4 of your speed and take a quarter; hit from behind - pushed on, no damage; head-on - both bounce, both hurt. Your damage a quarter. Your car flashes on the grid only with the lights up. PROJECT-LOG 22 Nov 18:41. Waiting on Grant: drive it, try ramming sides.

**LATEST (22 Nov 2026, 17:17 SAST) - THE GAME GRANT PLAYS NOW: build/racer_cars75_breakfast_fast.tap** - the breakfast table, race only, every car its own card and WEIGHT (bumps and damage), 32 headings, the 4-frame rhythm (12.5 a second; 82% of pictures make it), 85% speed, NOS 1.75x, the coffee mug (damage hurts less), your car flashing on the grid, you start 3rd. Level-1 difficulty (careful autopilot last, ~8 s behind). Next: speed (task: make the 4-frame rhythm hold - tiles 34k and cars 34k T a picture are the targets; the cloth is already PUSH-filled); levels (harder later - not designed).

**LATEST (22 Nov 2026, 16:34 SAST) - THE GAME GRANT PLAYS NOW: build/racer_cars75_breakfast.tap** - the race-only game (every car its own card, 32 headings, skids cost speed, NOS gauge, finished cars clear the line) on the BREAKFAST TABLE (cloth, cereal O's, track 1 as it was), with the coffee mug (MUG=1). Grant: "a lot more fun ... the racing is closer - lots of bumping". Built by tools/build_race.sh. The full sweep: PROJECT-LOG 22 Nov 16:34 (9 suites pass; the other failures are tests still holding the pre-18-Nov game; one question for Grant - how long a slide lasts). Balance: Grant, "This was about right - remember that it will get harder in later levels" - this is LEVEL 1's difficulty; levels (harder) not designed yet.

**LATEST (22 Nov 2026, 15:38 SAST) - THE GAME GRANT PLAYS NOW:** build/racer_cars75_h32_round.tap (and _elastic): race only, every car its own look and card, 32 headings, skids cost speed (SCRUB 5), NOS gauge, finished cars clear the line, and the ROUND-TURN TRACK - track 1 at road 48, corners 16, a turn on the left, the top chicane 80 deep, the centre line smoothed (RT_SMOOTH 3) - Grant: "B rounded is good". Balanced (good driver 7 of 10). LIMITS: the track uses all 256 edge pictures one map can hold (no more turns without lifting that - about 1 KB); the catch-up tape has ~50 bytes free in the program, ~29 under 0x8000. Open: the dashed-looking edge line where pictures were merged; the race-order half-painted-row test glitch; in-between car drawings are machine drafts; merge to main.

**LATEST (22 Nov 2026, 12:08 SAST) - THE GAME GRANT PLAYS NOW:** build/racer_cars75_h32.tap (race only, every car its own look and driver card, 32 headings, skids cost speed - SCRUB=5, NOS gauge, finished cars drive clear of the line). Grant: "the 32 tape looks smoother, balance that one" - balanced (PROJECT-LOG, 22 Nov 2026, last entries). Build: `bash tools/build_race.sh` (plain `bash build.sh` last). Tune: src/ai_tune.asm RACE ONLY part (AI_K_*, AI_H16R). Open: Spike the slowest (~1 s); the in-between drawings are machine drafts (tools/car_art.txt for YOU; the others drafted at build time); the race-order half-painted-row test question; merge to main.

**LATEST (22 Nov 2026):** race tapes rebuilt - STEADY=5 (every picture 5 TV frames, same-size jumps; view lead 1 px a picture), each computer driver its own line (race.asm rl_line; ai_tune.asm AI_L0-3: cyan classic, yellow late, magenta a bit wide, white mixes them), NOS=1 (stronger), your car keeps 75% speed on grass. All four race tapes 18/18; autopilot wins 9 of 10 at 75%. Details: PROJECT-LOG, 22 Nov 2026. Next: Grant drives racer_race75.tap. Smoother still needs more pictures a second or a slower game.

**START HERE (wrap-up, 19 Nov 2026 22:06 SAST):**
- THE TAPES TO DRIVE: build/racer_race75.tap (Race/Combat title, M toggles mode, 75% speed) and racer_race75_elastic.tap (with catch-up); 70% twins racer_race70*.tap. Raw links: https://github.com/grant-cmyk/breakfastrun/raw/claude/breakfast-run-layout-ik0vpe/build/racer_race75.tap
- LAST CHANGE (Grant: "with new drivers still too tough. Make them skid more"): src/ai_tune.asm AI_R_GRIPCUT 20 - all four RACE computer cars 20 64ths less grip (cyan 84, yellow 56, magenta 72, white 60; MAX 64). Good-driver autopilot now wins 9 of 10 at 70% and 75% (was 20 of 40), 7 of 10 with catch-up; yellow slides 26-32% of the time, white 28-37%. Cut 12 made no difference (5 of 10). If Grant says "too easy", try GRIPCUT 16. Rebuild: `bash tools/build_race.sh` then plain `bash build.sh` last; check racer.tap / racer_track2/3/5 md5 unchanged.
- MEASURE: `python3 tests/race_measure.py racer_race75 good 10` (tape NAME, not path). TEST: `python3 tests/race_mode_test.py racer_race75` - 18/18; the other three race tapes 17/18 from the known one-frame half-painted side-panel row as cars swap (test unchanged: Grant to decide whether it may read between pictures).
- WAITING ON GRANT: drive racer_race75.tap and say too easy / too hard / right; keep catch-up or not; the half-painted-row test question; whether the old breakfast-table tracks get the lap and race-order fixes; where face ideas 1 and 2 appear; whether he got stuck on grass in his screenshot (lap 2 of 3, 5:20); merge this branch to main.
- EDITORS (claude.ai artifacts): faces https://claude.ai/artifact/JXzX56aU6KkAgqKv15F3LE, driver cards https://claude.ai/artifact/QqBrPQDuifuADJvHwZaWgZ, new cars https://claude.ai/artifact/6VjghSZYLJPZHsFNHzoaAC, car editor https://claude.ai/artifact/8yqUStZiPjoVd7rhXQytT2.
- EMULATOR: zx-emulator 0.9.8 released 19 Nov 00:32 SAST (scanlines fix), delivered by auto-update.
- NEXT STEP: Grant drives racer_race75.tap (three races) and reports the difficulty.

**RACE or COMBAT (18 Nov 2026, late; each driver its own and 75%: 19 Nov 2026):** Grant: "I need a game option - combat or race ... make it competitive so you don't run away with it. 70% speed is good." `bash tools/build_race.sh` -> build/racer_race70.tap, racer_race70_elastic.tap and (Grant, 19 Nov: "Any chance of speed 75%?") racer_race75.tap, racer_race75_elastic.tap (the armour GRIP1 tape at 70% / 75%, gentler NOS; behind RACEMODE=1 / ELASTIC=1, every other tape unchanged). The title's M toggles "MODE: RACE / COMBAT" (in place of the dead "3 CHOOSE YOUR PLAYER"; RACE first; remembered between races). COMBAT = the armour game exactly. RACE = every car the racer in its colour (no numbers: Grant, "Number won't be legible - that's fine"), no armour/shells/wheels/line pulls, the race order's right-hand squares show the gap to the car ahead. THE FOUR COMPUTER DRIVERS (Grant, 19 Nov: "the racers race too similarly ... it looks like a procession"): each its own style and a slightly different car, src/ai_tune.asm RACE part (AI_RC_ cyan THE SMOOTH ONE - tight tidy line, lifts early, never slides, MAX's top speed; AI_RY_ yellow THE LATE BRAKER - cuts every corner, slides a third of the time, +4.6% top speed, least grip; AI_RM_ magenta THE WIDE ONE - nearer the middle, its own line, +9% acceleration, +2.3% top speed; AI_RW_ white THE ERRATIC ONE - wandering line, a mistake a lap, +2.3% top speed); at 75% each car 1-2 64ths slower on the straight (AI_R75) - one set does not serve both speeds. What mixes them is the line: yellow and magenta on lines a few pixels either side. The elastic tapes add the rubber band on top of each car's own pushes (+2.3% a waypoint behind the leader up to +7%; -2.3% for a car 2 s+ ahead of you). Measured (tests/race_measure.py, good-driver autopilot from the back, 3 laps, 40 races): won 19 (70%) and 20 (75%) of 40, 1.8 s behind when beaten; elastic 16 and 13 of 40, 2.1-2.3 s; the computer cars within 1.4-2.7% of each other a lap and changing places with EACH OTHER 15 times a race (3 before; elastic 24-27, was 9-10); the careful autopilot loses by 11-13 s everywhere. tests/race_mode_test.py: 18 of 18 on three race tapes, 17 of 18 on racer_race75 (a row caught half-painted after a swap - PROJECT-LOG, 19 Nov 2026; the test not changed: to decide); armour_test on these tapes with RT_MODE=combat; racetrack_test with the tape's switches (PROJECT-LOG). Pictures: docs/design/racetrack/race_mode/ (race_mix_race75.mp4: the field mixing at 75%). Next for Grant: drive racer_race75.tap - do the four look and race differently, is 75% right?

**18 Nov 2026, later (race track):** laps are no longer lost when you go off the track and come back on further round (src/lap_low.asm: a time-limited look ahead - a short cut gains nothing; not the plain game, not track 3); the race order's faces look left and right until the lights go green (tw_anim); on the ARMOUR tapes the health is Grant's option C - three blocks a row, green / yellow / red, red outlines flashing at none - the gap times and the mug have gone (425 bytes free in the program, 375 under 0x8000 on racer_armour_grip1). Details: PROJECT-LOG, 18 Nov 2026, last entry.
**Armour and weapons (17 Nov 2026, branch worktree-agent-a010b6360182407bb - not merged):** Grant: "the tank can shoot, and the clown extends its wheels on the sides - if they hit you your car spins where it is ... add 'armour' to the cars as a gauge item ... show damage on each car in the HUD". Behind `ARMOUR=1` on the driver cards (off by default; every other tape byte for byte the same): `bash tools/build_armour.sh` -> build/racer_armour.tap and racer_armour_grip1.tap (the one to drive). Every car has six pieces of armour; its card's "armour N" (tools/driver_cards.txt v2: MAX 5, FRANK 5, JANE 2, BRUNO 9, SPIKE 4, SPECS 5, DOT 8 - confirmed by Grant) sets what a piece takes (ARMOUR_PIECE in tools/make_cards.py: 22 for a 1 up to 92 for a 10; a usual knock is 10). A bump costs both cars the same, so the dragster loses pieces three times as fast as the tank. The HUD is option V: a 3-px bar of six pieces at each race-order row's right edge, a lost piece flashing about a second then leaving a dot; the mug is now YOUR armour (the old damage is off in this build; the oil can mends armour). Defaults for Grant's open questions: at no armour a car LIMPS at half speed (ARM_LIMP_SHIFT); only the computer's tank (a white shell straight ahead at a car 16-80 px in line, every 8 s) and clown car (two wheel-dots each side while a car is alongside) use weapons; a hit spins the car on the spot (one turn, 32 TV frames). Every number: src/armour_tune.asm. In 5 races: 5-6 shells a race (nearly all hit), the wheels out about 5 times (3-4 hits), Jane limps in about half the races, everyone finishes, laps within a second of the cards tape. Speed with GRIP1: 12.12 / 12.50 / 11.88 pictures a second (start / mid-lap / pack; the cards tape 12.25 / 13.0 / 12.0); about 5,000 T a picture. Memory: 103 bytes left in the program (89 with GRIP1), 471 under 0x8000 - a player's fire key (not built; about 150-250 bytes) would need room found. Tests: tests/armour_test.py 28 of 28; racetrack_test 15 of 15 (it now leaves out the shell's and wheels' squares as it does the cars'); rt_fixed_test 3 of 3. Pictures and clips: docs/design/racetrack/armour/. Waiting on Grant: drive racer_armour_grip1.tap; answer the three questions (limp or knocked out; a fire key for you; weapons for other cars); the cards page's own wording of Bruno's and Spike's weapon lines. Details and tables: PROJECT-LOG, 17 Nov 2026, last entry.
**The driver cards (17 Nov 2026, branch worktree-agent-abfbe424651a42ce8 - not merged):** Grant: "the initial grip needs to be poor - lots of skidding ... Each car has a personality ... their acceleration, speed and grip/turning as ratings out of 10". His ratings are tools/driver_cards.txt; behind `CARDS=1` (off by default; every other tape byte for byte the same) each car now drives by its card. Change a rating there and run `bash tools/build_cards.sh` -> build/racer_cards.tap and build/racer_cards_grip1.tap (the tight track, NORMAL; the GRIP1 one is the one to drive). tools/make_cards.py turns the cards into src/cards.asm and holds THE SCALE at its top (a point of speed is 3.1% above 5 and 1.6% below, so the slow cars are not lapped; acceleration 7.8% of the push a point - worth little in this game; grip: your tyres hold 6 to 21 where they held 16, and MAX's 4 is 10 - a slide 82 TV frames long where it was 58; a computer car has a speed it must be under to turn, 0.82 to 1.88 px a frame, and BRAKES down to it, going straight on while it does). The drivers' personalities are the CARDS part of src/ai_tune.asm: Frank tidy like Max; Jane 1.91 px a frame on the straight and down to about 1.0 at a corner; Bruno hardly lifts, holds the middle and moves over on a car within 40 px; Spike wanders, makes the most mistakes and lunges at a car that comes near. Laps (5 races of 3 laps, in the pack): you by a tidy autopilot 17.6, by a rough one 19.4 (4.5% on the grass); Jane 18.6, Bruno 19.2, Frank 19.4, Spike 19.2 - all within a tenth of the leader. It costs 393 bytes (1,469 free) and about 6,000 T a picture; pictures a second in the pack 10.9 (11.4 without), with GRIP1 12.0 (12.1). Tests pass (15 of 15, 3 of 3). Clips: docs/design/racetrack/cards/. Waiting on Grant: drive racer_cards_grip1.tap - is a grip of 4 poor enough, do Bruno and Spike look like their words - and settle the cards whose words and numbers disagree (SPECS "a real challenger" at 4 / 5 / 3; Frank "a little more top speed than Max" at Max's own numbers). Not combined with the choose screen or two players. Details and the scale table: PROJECT-LOG, 17 Nov 2026, last entry.
**Two players in one view (17 Nov 2026, branch worktree-agent-a32fda323d3c74788 - not merged):** Grant chose layout A, "two players would exist in the same screen". A trial on the race-track look, track 1, behind `TWOP=1` (off by default; defaults byte-identical): the title's 2 starts a two-player race - player 2 drives the cyan car (second grid place) on 6 / 7 / 0 / 5 brake / 8 NOS (not 9: keyboard ghosting with O, P and 0) with the same grip sums as player 1; the view sits between the cars; the LEASH puts a car left behind back on the road behind the leader (held 12 TV frames, flashing, a beep); a panel top right shows each player's place and lap. Tapes: build/racer_2p.tap (`TWOP=1 PACEFIX=1 AI=1 RT_ROADW=56 RT_CORNER=27 RT_PIN_GAP=1 RT_PIN_W=1 RT_PIN=solid RT_NOLINE=1 RACETRACK=1 OUT=racer_2p BDIR=racer_2p bash build.sh`), racer_2p_grip1.tap (add `GRIP1=1`: the one to drive - 10.5 pictures a second with two players against 9.4), racer_2p_points.tap (add `TWOP_PTS=3`: a plain points rule). Code: src/twoplayer.asm (and _low, _pic); every number to tune is at its top. Test: python3 tests/two_player_test.py (19 pass). Pictures and a real-speed clip: docs/design/racetrack/two_player/. Memory: 918 bytes free in the program and 777 under 0x8000 since track 1's map was packed (17 Nov; it was full). No damage in two-player races; player 2 has no crash noise, arrow or messages; the K screen does not set player 2's keys. Waiting on Grant: drive it with a second person; choose leash or points; say whether the leash's distances and its quarter-second hold feel right. Details: PROJECT-LOG, 17 Nov 2026, last entry.
**The race track's smoothness pass 4 and the leash (17 Nov 2026, branch worktree-agent-a0ea9e145ac15e1cb - not merged):** one exact stage, bigger than the one asked for: where two tiles side by side hold the same "banded" picture (every line all grass or all road - the grass's edge running level) the square's lines are copied as they are instead of shifted and joined (tools/make_world.py numbers those pictures first: RT_BAND; src/racetrack_hot.asm: rt_c1; switch OPT_RTBAND / `RT_BANDED=0`, off on track 3 which lacks the 87 bytes). In the pack, pictures a second (share of pictures taking 5 TV frames or more): track 1 green 11.75 (25%; it was 11.5, 32%), GRIP1 12.4 (6%; 19%); tight 11.4 (41%; 64%), GRIP1 12.1 (11%; 33%); track 2 11.0 (53%; 85%), GRIP1 11.9 (24%; 77%). 12.5 in the pack is not reached; the GRIP1 tapes are the nearest. The two-player leash now steps one waypoint further back when its first choice is the one the leader last passed: tests/two_player_test.py 19 of 19 on racer_2p and racer_2p_grip1; the pixel test runs on the two-player tapes (`BDIR=racer_2p TAPE=racer_2p`). tests/stage_profile.py prints the share of 5-frame pictures. Bytes free (program / under 0x8000): track 1 green 1,684 / 790; track 2 939 / 790; track 3 24 / 12; tight 1,862 / 790; racer_2p 753 / 777. Not built: the case number for each edge square (a design on paper is in PROJECT-LOG: about 650 bytes for 8,000-13,000 T) and the kinds a byte a block. One same-drive check (tight tape, in the pack, without GRIP1) parts at picture 187 and is not run to ground - PROJECT-LOG's last entry. Next for Grant: drive racer_track_green_grip1.tap and racer_track_green_track2_grip1.tap. Nobody has driven any of it.
**The race track's smoothness pass (17 Nov 2026, branch worktree-agent-aaccef13180d1b3bf - not merged):** three exact
stages in src/racetrack_hot.asm (the cars' colour rule and a short cut for a car alone on plain squares; the grass-edge
squares reached with less overhead; plain squares under a car) - nothing changed on the screen, every test as before.
Track 1 green now makes 12.0 / 12.4 / 11.4 pictures a second (start alone / mid-lap alone / in the pack; it made
11.6 / 12.0 / 10.0), with GRIP1 12.5 / 12.75 / 11.6; the tight NORMAL tape 11.75 / 12.1 / 10.4, with GRIP1 11.9 / 12.4 / 11.6;
track 2 10.75 / 10.5 / 10.0; track 3 12.0 / 12.1 / 11.5. 12.5 in the pack is NOT reached without switches. New switch
`REACT1=1` (the computer cars decide every 8th TV frame: 11,000-19,000 T, but their laps are about 1.5 s slower) -> ..._react1.tap.
Track 2's deficit is 50 more grass-edge squares in view than track 1: only roads further apart cure it. Left to do, exact:
the kinds a byte a block (8,700 T, needs 2,304 bytes) and a case number for each edge square (8,000-12,000 T, 275 bytes and
the generator); track 3 has 10 bytes free with GRIP1. Every race-track tape was rebuilt (some tight tapes had been stale).
SINCE THEN (17 Nov, branch worktree-agent-ab528df27c01b41e6): merged with the two-player mode it no longer fitted; it does
again - track 1's map is packed like tracks 2 and 3 (RT_GAPS, about 2,200 bytes) and the place plate is drawn from the fast
half of memory on tracks 1 and 2. Free now: track 1 green 1,763 bytes (+790 under 0x8000), tight 1,941, two players 918,
track 2 1,018, track 3 still 24. One more exact stage (the cars' moving sums, 5,500 T): track 1 green 12.0 / 12.5 / 11.5,
GRIP1 12.9 / 13.1 / 12.0; tight 12.0 / 12.25 / 10.6, GRIP1 12.4 / 12.75 / 11.4; track 2 10.9 / 10.5 / 10.1; two players
10.6 / 10.75 / 9.0, GRIP1 11.75 / 11.6 / 10.6. Still not 12.5 in the pack. New: tests/rt_same_drive.py (do two tapes play
the same game, byte for byte?) and tools/build_racetrack_tapes.sh (rebuilds all 34 race-track tapes, the plain game last).
tests/two_player_test.py: 19 of 19 on racer_2p_grip1, 17 of 19 on racer_2p (the leash can put a car back "0 waypoints
behind" the leader, which the game's rule allows and the test does not - to be decided). The edge squares' case numbers are
still the best exact step left, not started.
Clip: docs/design/racetrack/built/smooth_tight_before_after.mp4. Next for Grant: drive racer_track_green.tap beside
racer_track_green_grip1.tap (and the tight pair) - nobody has driven any of it. PROJECT-LOG has the table.

**The tighter track and keener cars (17 Nov 2026, branch worktree-agent-acbbf0fac92b5a806 - not merged):** on the race track trial, track 1: `RT_ROADW=56 RT_CORNER=27` (road width, the big corners' radius; tools/make_world.py) and `AI=1` or `AI=2` (the computer cars NORMAL or HARD; every number in src/ai_tune.asm). Tapes build/racer_tight_*.tap - drive racer_tight_w56s_normal.tap first, then _hard. PROJECT-LOG's last entry has the tables. Nobody has driven them.

**The green-line race track on tracks 1, 2 and 3 (17 Nov 2026, branch worktree-agent-a272a1ab88e676794 - not merged):**
Grant chose the limit marking: the thin green line just inside the grass's edge. It is now one switch -
`RACETRACK=green bash build.sh` -> build/racer_track_green.tap (track 1); `TRACK=2` or `TRACK=3` with it ->
build/racer_track_green_track2.tap, _track3.tap; `GRIP1=1` with any of them -> ..._grip1.tap (your car's grip sums once a
picture: quicker, the feel not yet judged - both kinds are kept). Always run plain `bash build.sh` last. Pictures a second,
start / mid-lap / in the pack (today's breakfast tape 12.4 / 12.4 / 12.6): track 1 11.6 / 12.0 / 10.0 (GRIP1 11.9 / 12.4 /
11.4); TRACK 2 10.1 / 10.0 / 9.25 (GRIP1 10.5 / 10.5 / 9.5) - slower because its roads lie close together and more grass
edges are in view; track 3 11.75 / 11.25 / 11.0 (GRIP1 11.9 / 12.1 / 11.5). Bytes free in the program: 549, 1,974 and 202.
All six tapes pass tests/racetrack_test.py (`TRACK=2 python3 tests/racetrack_test.py`; it now knows the green line) and
tests/rt_fixed_test.py. What tracks 2 and 3 needed is in PROJECT-LOG's last entry: look-alike edge pictures merged (3
pixels at most in a tile), the map's rows laid into each other's gaps, track 3's kinds kept in the program and its taller
mini-map given a taller box. Two faults at the window's edges were fixed in every race-track tape (the 2-pixel rim, and a
car at the left edge putting its colour 8 rows lower). Pictures and real-speed clips: docs/design/racetrack/built/green_track2_*,
green_track3_*. Track 5 (the bridge) is not built in this look: it needs a bridge design in these colours, the bridge
drawn again by the race track's squares, and room (PROJECT-LOG). Next for Grant: drive the three tapes and their _grip1
twins; say whether track 2's speed will do, and whether GRIP1 feels the same.

**The race track trial (16-17 Nov 2026, branches worktree-agent-af8779cbaad3c1b51, worktree-agent-ab8bf2b0bee0348cf, then
worktree-agent-ae2e8b23fd6243e9b - not merged):** Grant scrapped the breakfast table for a traditional track - black road,
solid green grass from 10 px beyond the road's edge, a dashed white limit line, each car its own colour, clash rule 4. A
trial of track 1: `RACETRACK=1 bash build.sh` -> build/racer_racetrack.tap (off by default; the plain build and tracks 2,
3, 5 are byte for byte unchanged). He drove it: "the look is right ... it is just not smooth", then asked for the speed
back. PROJECT-LOG's last entry (17 Nov) has the ranked menu, all built and measured (pictures a second: start / mid-lap /
in the pack; today's tape 12.4 / 12.4 / 12.6): white dashes 9.6 / 10.0 / 9.0; sparse dashes 10.5 / 10.75 / 9.9; a green
1-px line 11.6 / 12.0 / 10.0; NO LINE 12.25 / 12.75 / 11.1 (`RT_NOLINE=1`) - all with the picture exactly as it was; and
no line with `GRIP1=1` (your car moved and its grip worked out once a picture - it may change the handling, so it is a
switch, off by default) 12.9 / 13.0 / 12.25. What did it: the drawing code moved out of the slow memory under 0x8000
(src/racetrack_hot.asm), and the mini-map, plate and mug sent to the screen only when they change (tests/rt_fixed_test.py
checks them). A smaller play window is a switch too (`RT_ROWS=16`: a black band under the play area) but buys nothing in
the pack. Not built: the kinds a byte a block (no room: 1,316 bytes wanted, 747 free), the 2-pixel rim fix. Pictures and
real-speed GIFs: docs/design/racetrack/built/speed_*. Next for Grant: drive racer_racetrack_noline.tap and
racer_racetrack_noline_grip1.tap side by side (does the car feel the same?), and say whether the road reads without a
line - or pick another row of the menu.

**Latest (14 Nov 2026, 22:16 SAST) - read this before the older status below:** the window is 192 x 152
(24 columns, 19 rows); the right panel is 6 columns: the mini-map at its top, RACE and the order under it
(flag and best-lap clock share column 31); the BREAKFAST RUN logo is under the window, centred (rows 21-22);
the crew chief's pit talk is OFF (PIT=1 builds it, but the logo now sits where his bubble was). Your place,
lap and lap time are on a small plate INSIDE the window; the health gauge is a MAGENTA lightning bolt bottom
left and the NOS bottles RED bottom right, each in colour cells of its own (hud_pre, src/plate_slow.asm).
The VIEW LEADS THE CAR: up to 20 px ahead across, 16 up/down, 2 px a picture (halved 23:15) (cam_lead, src/plateco.asm;
LEAD_X / LEAD_Y / LEAD_STEP to tune). In-race music is on the AY SOUND CHIP (OPT_AY, tools/make_music_ay.py; needs a 128K or
the 48K with the AY option on - a plain 48K is silent); coloured objects OFF (OBJECTS=1; too slow). Speed alone: 40 pictures at 3 TV
frames / 225 at 4 / 5 at 5. Speed test 15 Nov 06:07: alone now 91 pictures at 3 frames / 193 / 3; the pack is ~30,000 T a picture over the faster rate (see the log's last entry for what was tried and what is left). Detail: PROJECT-LOG.md, end.

**The choose screen (16 Nov, background agent, branch worktree-agent-a31f6549f20d471a9 - not merged, not playtested):** `bash tools/build_choose.sh` -> build/racer_choose.tap: tracks 1-3 in one load; at the title 1 or 2 goes to a choose screen - TRACK, DRIVER (seven: two new faces, SPECS and DOT), CAR (seven: SALOON and TRUCK from the pool as placeholders), EXTRA (one of ACCELERATION +10.9% push, GRIP +12.5%, SPEED +9.8% top) - steer left / right, accelerate to select (src/choose.asm; OPT_CHOOSE, off by default: the other tapes are byte-identical). New cars are data: tools/choose_cars.txt + a drawing in tools/choose_car_art.txt. Memory on that tape: 375 bytes free in three pieces - none of Grant's three new cars fits beside the two placeholders; two fit in their place. Two players: the choosing works (player 2: 6, 7, 9), the race does not exist - the computer drives the second car. Test: `python3 tests/choose_test.py`; `bash tests/choose_suites.sh`. Pictures: docs/design/choose/. Detail: PROJECT-LOG.md, end.

**Optimisation investigation (16 Nov, background agent, branch worktree-agent-af7c58c90304a2ad1 - not merged, not playtested):** docs/design/OPTIMISATION-PLAN.md. 8.9 KB found by four build options (LOOP, FLIP, TILE1, TOWER - all off by default); build/racer_3tracks.tap is tracks 1, 2, 3 in one tape (T at the title, then 1); the "latent fault" was the test writing a car's place mid-move (fixed in tests/drive_test.py); the computer cars' pace depends on the picture rate (PACEFIX=1 is the fix, Grant's call). Steps to approve one at a time: the plan's section 4.

**v3 (16 Nov, background agent - not yet playtested):** the corner arrow is 24 x 15 at a fixed spot just above the crew chief's bubble (window pixels 80-103, lines 111-125; ARROW_COL, ARROW_TOP in src/arrow.asm), five pictures kept on pages D3-D7 of the buffer's strips. Program free: 23 / 40 / 30 bytes on tracks 1 / 2 / 3 - memory is the thing to watch. Detail: PROJECT-LOG.md, end.

**v2 (15 Nov late, background agent - not yet playtested):** the mini-map is 24 pixels wide, a solid ribbon in the window's own colours ORed over the picture (map_blit, hud.asm; no box, the copy routine is whole again); the corner arrow is at one fixed spot (ARROW_X, ARROW_Y in src/arrow.asm: 96, 52; 76 for dead centre). Program free 124 / 134 / 123 bytes. This replaces the paragraph below where they differ. Detail: PROJECT-LOG.md, end.

**Map in the window, corner arrows (15 Nov night, background agent - not yet playtested):** the mini-map is the window's bottom left 6 x 5 cells (on the screen only: the copy routine skips it); spoons beside the mug bottom right; a flashing arrow 32 px ahead of your car warns of bends and long straights (src/arrow.asm, src/arrowtab.asm from tools/make_world.py, frames from tools/make_arrows.py). Test: `python3 tests/arrow_test.py` (TRACK=2, 3 too); pictures: docs/design/arrows/ (`tests/arrow_shots.py`). Memory: program free 149 / 187 / 154 bytes on tracks 1 / 2 / 3; the start-up area must now end before 0xD0A0 (46-67 bytes left). Detail: PROJECT-LOG.md, end.

**Track 5, the bridge (15 Nov late night, background agent - not yet playtested):** `TRACK=5 bash build.sh` -> build/racer_track5.tap, a one-track tape: under the bridge, round, up a ramp and over it. Levels, walls, the car hidden under the deck, ramp speeds, all behind OPT_BRIDGE (src/bridge.asm); tracks 1-3 tapes unchanged. Test: `python3 tests/track5_test.py`. Detail, figures and what was simplified: docs/design/tracks/built/BUILT.md (end); pictures docs/design/tracks/built/track5_*.

**Track 5's bridge as Grant drew it (16 Nov, background agent - not playtested):** kerb walls solid (drawn by kerb_draw), concrete masked, wing and wall one shape, six more O's. 10.2 pictures a second at the crossing (was 11.7); program 2 bytes free on track 5. His choice wanted: docs/design/tracks/bridge_efficiency_options.png (E1-E4). Detail: BUILT.md's last section.

**Tracks 2 and 3 (15 Nov evening, background agent - not yet playtested):** one track a build: `TRACK=2 bash build.sh` -> build/racer_track2.tap, `TRACK=3 bash build.sh` -> build/racer_track3.tap; racer.tap is track 1, unchanged. Test: `TRACK=2 python3 tests/track2_test.py`. Detail and figures: docs/design/tracks/built/BUILT.md.

**Crew messages (15 Nov 11:48):** the chief's face and a white bubble at the foot of the play window (msg_say in src/strip.asm writes the lines; fl_draw in src/plateco.asm copies them in; the picture is kept invisibly on the screen under the window). Messages: tools/make_strip.py MSGS. **Main area: 17 bytes free.**

**Sound (15 Nov 11:16):** the speaker only - NO AY (OPT_AY 0; AY=1 builds the race tune on the chip). Kettle's On jingle before the lights (ROM BEEPER, jin_start), engine while accelerating, skid, lap beep, effects. No tune in the race. Tests hold the jingle off with jin_on = 0xFF set at the TITLE. Main area: 253 bytes free again.

**Race panel (15 Nov 09:20):** map, then RACE and the five cars (rows 5-15), the lap record (16), YOUR RACE (17) with your place at the end (18) and your lap times as you do them (19-21), the best in yellow. **MEMORY IS FULL: about 40 bytes free in each of the two main areas.**

**Title (15 Nov 09:06):** green logo band, the egg, RUN cut in yellow and red with speed lines (t_run), five cars lapping the check border (tc_step). **Podium:** card rows 5-17, fastest lap with clock and lap number, your own lap times under the panel. **Memory is nearly full everywhere** (see the log's last entry) - anything new needs room found first. Open mock-ups: sad face when off the podium (sadface_options.png), frame options, race-screen layouts.

**Race start and end (15 Nov 08:19):** after 1 at the title a ditty plays (AY) and the lights come on by themselves; at the end the podium (yellow card, steps in the drivers' colours, Grant's own faces, names YOU / FRANK / SPIKE / BRUNO / JANE) and any key returns to the title. Tests hold the automatic start off with jin_on = 0xFF. Open: where the set-up keys go; the sad face and a best-lap happy face in the HUD are ideas only; frame and race-screen layout mock-ups await a pick.

**Title screen (15 Nov 07:14):** layout B, the menu card on a red-and-white check cloth, your car lapping the border (src/title.asm, title3.asm a_runs). Race-screen layout options A-E are mock-ups only (docs/design/layout_game.png): Grant has not picked one.

**Status:** Track 1, BREAKFAST AT TIFFANY'S. Small 16 x 16 cars; the window 176 x 152 (19 rows, since 14 Nov late) in a slim
blue frame; LAYOUT G3 BUILT (docs/design/g3_built.png): logo top right, the mini-map under it, the
race order rows 10-19, bottom left your face and big place in a red block with a white strip (PRESS
Q / LAP n/3 / FINAL LAP / FINISHED!) and the time, the crew chief's bubble (rows 20-23), the L2
start lights hanging in the window, your NOS as small canisters in the window's corner. Your car:
the Skid Lab grip model, the heading settling on the pictured one; set-up keys 1 2 3 before the
start (not shown on screen). `bash build.sh` -> build/racer.tap.

**Speed:** tests/zxlap.py (zxdev). Now: 3 frames x 301, 4 x 12; 15.5 pictures a second off the
grid. Grant, 14 Nov: "speed of the game is good" - no speed hunt owed.

**Memory:** 140 bytes free in the program (code_end 0xBF74; code added before sq4.asm's include costs a whole page when it crosses one - add after faces.asm); about 1,300 bytes free under 0x8000 below LOWTAB (0x7D40: the tables that were buffer strips; contended memory - data, and code that runs rarely); the top-of-memory data has 3 bytes to spare; none in the table block at 0x5B4C.

**Next step:** MUSIC IN THE RACE - Grant wants it to "come through during the game"; every
beeper version tried on 14 Nov was "background beeping" and cost speed, so it is off (OPT_MUSIC).
Proposed and awaiting his word: play it on the AY sound chip where there is one (128K, or a 48K
with the chip; zxdev: option ay48) - held notes, three voices, almost no time - keeping the
beeper for the effects. Then: a prompt for the start key (PRESS Q went with the bottom-left
block); more quick messages on the second plate (only FINAL LAP! so far); the coloured objects
(OBJECTS=1: slow; first find why obj_paint costs 11,000 T); the tune on the title screen. The
screen now: nothing bottom left; your place, lap and lap time on the plate in the window
(docs/design/place_plate_in_game.png); the lightning health gauge bottom left of the window.

**Open:** the set-up is yours only - "rock/paper/scissors" needs the computer cars to have
set-ups too (C_PACE and the skid are their only knobs today); GRIP's step is small in the test
(52 against 55 frames of slide); the race time shows whole seconds (the mock-up had tenths);
Grant to touch up the big cars' 22.5 and 45 headings in the car editor
(https://claude.ai/artifact/2EqdSKs3fDfUqERTX9pTzL, Big cars mode); no zx.project yet for
`zxdev check`.

**Tools:** build: `bash build.sh` (pasmo + the zxspectrum skill's build.sh). Tests: drive_test,
nos_test, o_test, setup_test (zx package); zxlap (zxdev - build ../zx-emulator with
`sh build-linux.sh`; LIST=routine, FINE=n, SLOW=1 for detail); profile_ticks (stage split). Car
editor https://claude.ai/artifact/2EqdSKs3fDfUqERTX9pTzL; Skid Lab
https://claude.ai/artifact/XWjkAzJ9kFKki9naPic3V8; Layout Review
https://claude.ai/artifact/GL5FkuruWucbShFekbkLp8.

**Constraints:** memory - see MEMORY IS FULL above; the copier ends 0xF8E2. Big-car frames fill 0x5F00-0x7FFF
(contended memory) and spill into data.asm. Big cars 0-3 below the
program at 0x5F00 (contended memory). Code before hud.asm must not use equs defined later (pasmo
first-pass values). The interrupt may land while the cloth fill has SP in the buffer: it may push
only 6 bytes (A, H, L only). The cloth fill uses IY and the other register set; the copier uses
the other BC, DE, HL. A test that writes a car's place can race the game's own move (o_test).

**Waiting on Grant:** playtest this build; say whether to merge the branch to main (a pull request
has not been opened); touch-ups to the big cars' angled headings; confirm the repo should be
public; push a tag from his machine (cloud sessions cannot push tags).

Track names for later tracks (verified): The Breakfast Club, Green Eggs and Ham, The Dish Ran Away
with the Spoon, Paddington's Marmalade, Goldilocks' Porridge, Breakfast in America.
Full history: PROJECT-LOG.md · Notion row: https://app.notion.com/p/41342c9abb32810d8672e5281550b1ac
