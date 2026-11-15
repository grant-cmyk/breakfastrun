# CONTINUE - Breakfast Run

**Stamped:** 2026-11-15 08:19 SAST · machine: Claude cloud container · branch: claude/breakfast-run-layout-ik0vpe (not yet merged to main) · commit: see `git log -1`
**Lifecycle:** Active

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
