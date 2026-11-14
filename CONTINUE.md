# CONTINUE - Breakfast Run

**Stamped:** 2026-11-14 21:17 SAST · machine: Claude cloud container · branch: claude/breakfast-run-layout-ik0vpe (not yet merged to main) · commit: see `git log -1`
**Lifecycle:** Active

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
