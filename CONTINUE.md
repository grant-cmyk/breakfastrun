# CONTINUE - Breakfast Run

**Stamped:** 2026-11-16 SAST (the choose screen added; the rest as of 2026-11-15 15:17) · machine: Claude cloud container · branch: claude/breakfast-run-layout-ik0vpe (not yet merged to main) · commit: see `git log -1`
**Lifecycle:** Active

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
