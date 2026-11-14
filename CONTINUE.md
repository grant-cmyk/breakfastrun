# CONTINUE - Breakfast Run

**Stamped:** 2026-11-14 07:31 SAST · machine: Claude cloud container · branch: claude/breakfast-run-layout-ik0vpe (not yet merged to main) · commit: see `git log -1`
**Lifecycle:** Active

**Status:** Track 1, BREAKFAST AT TIFFANY'S. DECIDED 14 Nov: the SMALL 16 x 16 cars, the window
176 x 136 (both are `bash build.sh`'s defaults; build/racer.tap). In that build the message bar is
a stopgap on row 0 (place, lap, time; the old start lights). Your car has the Skid Lab grip model
(the slide ends about 0.3 s after you stop steering) and a set-up (GRIP, SPEED, ACCEL; keys 1 2 3
before the start). NOS, lap record, crew chief's radio, border flashes as before.

**Speed:** measure with tests/zxlap.py (zxdev: real TV frames a picture, cost by routine, and a
check that the tables in the buffer's bottom rows survive the lap). Now: 3 frames x 311, 4 x 5.

**Memory:** main area about 2.1 KB free with the small cars (code_end 0xB798). The big cars do
not fit any more (the faces moved into the program): building them needs a memory plan.

**Next step:** Grant plays build/racer.tap (small cars, 136 high) and approves layout G3
(docs/design/screen_options4.png) - then build G3: the L2 start lights (pods) in the window
(docs/design/start_lights.png), no message bar, your face and big place bottom left with lap and
time, the map under the logo, the race order below it, no car strengths on the race screen, a
slim blue window frame. Then the speed hunt. Later: the title / attract screen with a choice of
driver and car (drafts: docs/design/new_cast_mockup.png).

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
