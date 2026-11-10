# CONTINUE - Breakfast Run

**Stamped:** 2026-11-10 16:20 SAST · machine: Claude cloud container · branch: main · commit: see `git log -1`
**Lifecycle:** Active

**Status:** Track 1, BREAKFAST AT TIFFANY'S. Window 176 x 120 in an arcade bezel; blue-on-cyan
cloth (dark checks 1 dot in 8, staggered); cereal O's (solid); breakfast things masked on top. Five
of Grant's cars (YOU; CYAN; GREEN the clown car; PINK the tank; WHITE Slim Jane, the fastest), each
with a driving style; skids; a staggered grid. Race order: faces on the grid, then gaps (small font),
laps, flags, the best-lap clock. The driver strip under the window: your face, inventory (NOS),
the crew chief's radio (typed messages, a moving wave) and the crew chief. NOS: start with one,
SPACE = 1 s of twice the push; canisters A (behind the grid) and B (top area). Race over: CHEQUERED
FLAG! box in the window, everything stops, Q for a new race. Real-ROM tests PASS (drive, NOS).
Sound: an engine putter from the interrupt (9-49 flips a second by speed) plus the spare-time note
and the crash; hear it in docs/design/engine_sound.wav (tools/record_sound.py).
Whole lap: work 212.3k T a picture (3 frames = 209.7k); 170 pictures at 3 TV frames, 49 at 4.

**Next step:** Grant plays `build/racer.tap` and says what to change next.

**Tools:** car editor https://claude.ai/artifact/2EqdSKs3fDfUqERTX9pTzL (tools/make_car_editor.py; hand
cars in tools/car_art.txt; tools/turn_car.py drafts the angled headings); mock-up scripts in tools/;
tests/drive_test.py, tests/profile_lap.py, tests/smooth_cpu.py.

**Constraints:** memory nearly full - low 15 bytes + 141 in the gap before sq4; TOPMEM 61;
strips almost full; start-up area 426. Frame time: ~2k T of headroom on an average picture.
Any code moved ahead of hud.asm must not use equs defined later (pasmo first-pass values).
Road option H (thin dots only on the road) is on branch trial-road-h: pixel-exact but too slow.

**Waiting on Grant:** playtest of the strip, radio and NOS; angled headings of his cars are drafts (redraw in the editor if any
look wrong); confirm the repo should be public; push a tag for this build from his machine (cloud
sessions cannot push tags).

Track names for later tracks (verified): The Breakfast Club, Green Eggs and Ham, The Dish Ran Away
with the Spoon, Paddington's Marmalade, Goldilocks' Porridge, Breakfast in America.
Full history: PROJECT-LOG.md · Notion row: https://app.notion.com/p/41342c9abb32810d8672e5281550b1ac
