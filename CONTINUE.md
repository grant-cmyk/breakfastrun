# CONTINUE - Breakfast Run

**Stamped:** 2026-11-14 05:23 SAST · machine: Claude cloud container · branch: claude/breakfast-run-layout-ik0vpe (not yet merged to main) · commit: see `git log -1`
**Lifecycle:** Active

**Status:** Track 1, BREAKFAST AT TIFFANY'S. Window 176 x 120 in an arcade bezel; five cars at 20 x 20.
The layout review is built: your place and lap large in the message bar with the race time, no lap
digits in the race order, 16 x 16 faces in 2 x 2 cell panels, the bubble on columns 11-20, border
flashes (green GO, red crash, white NOS). NEW: your car's set-up - GRIP, SPEED, ACCEL at levels
1..5, keys 1 2 3 add a point (2 to spend) before Q, 0 takes them back; shown on the HUD's bottom
row; the computer cars stay at 1, 1, 1.

**Speed:** measure with tests/zxlap.py (zxdev: real TV frames a picture, cost by routine) - NOT
profile_ticks.py alone, which under-counts late pictures (the copy with interrupts off loses a
frame count). zxdev lap: 3 frames x 308, 4 x 12 (was 195 / 104). Biggest now: the copy 36k,
draw_car 30-34k, cloth 29k, tiles 12k+, physics 19k, thinking 11k. The pictures still late have
4-5 cars in view.

**Next step:** Grant chooses the angled cars (docs/design/angled_cars_options.png: A as now, B the
number upright, C rebuilt from parts - Claude recommends B) and marks up the new cast drafts
(docs/design/new_cast_mockup.png). Then, in this order: (1) build the approved set-up box and
in-window NOS (docs/design/setup_box_mockup.png, tools/make_setup_mockup.py - "good enough", 14 Nov);
(2) a memory plan and a mock-up for the title / attract screen (logo, keys, hi-score, 1 or 2
players, choose a driver then a car: six drivers - 3 ladies, 3 men - and ten cars, each with
strengths and weaknesses; two players later); (3) the extra window row (176 x 128, about +5.4k T).

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

**Constraints:** memory - main area 203 bytes free (code_end 0xBF35), more in the gap before sq4
(cf_init left it); TOPMEM 15; the copier ends 0xF8E2, 493 below TOPMEM. Big cars 0-3 below the
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
