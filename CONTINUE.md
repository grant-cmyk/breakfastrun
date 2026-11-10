# CONTINUE - Breakfast Run

**Stamped:** 2026-11-10 08:45 SAST · machine: Claude cloud container · branch: main (trial-window-22 merged) · commit: see `git log -1`
**Lifecycle:** Active

**Status:** Track 1, BREAKFAST AT TIFFANY'S. Window 22 x 15 cells (176 x 120) in an arcade bezel; the
table a blue-on-cyan chequered cloth (dark checks 25% dots); cereal O's (solid - cars bounce off) mark
the road; breakfast things masked on top. Five of Grant's own cars (YOU, CYAN, GREEN the slow 3-axle
truck, PINK the tracked car, WHITE = Slim Jane's open-wheeler), each computer car with its own driving style; skids at speed;
a staggered grid; the race order shows faces on the grid, then each car's gap to the leader (8
checkpoints, small font), a clock beside the best-lap holder, the best lap under it, mini flags as
cars finish; RACE FINISHED when all are in. Beeper engine (pitch from your speed) and crash sound, played in the wait time. Own IM2
interrupt routine. Real-ROM test PASS (pixel-exact window).
Whole lap: work 193.7k T a picture; 177 pictures at 3 TV frames, 31 at 4.

**Next step:** Grant picks a plain-road option (docs/design/road_options.png: A, B or C); then build
it and measure the frame cost.

**Tools:** car editor https://claude.ai/artifact/2EqdSKs3fDfUqERTX9pTzL (tools/make_car_editor.py; hand
cars in tools/car_art.txt; tools/turn_car.py drafts the angled headings); mock-up scripts in tools/;
tests/drive_test.py, tests/profile_lap.py, tests/smooth_cpu.py.

**Constraints:** memory - TOPMEM (0xFAD0..0xFFF3) about 75 bytes left; low memory 80 bytes. A pool
driver (tools/pool_art.txt: SPECS, the old WHITE) needs 1 KB for his car - none free in the 48K now.
Any code moved ahead of hud.asm must not use equs defined later (pasmo first-pass values).
Frame time: about 16k T of headroom on an average picture.

**Waiting on Grant:** playtest; angled headings of his cars are drafts (redraw in the editor if any
look wrong); confirm the repo should be public; push a tag for this build from his machine (cloud
sessions cannot push tags).

Track names for later tracks (verified): The Breakfast Club, Green Eggs and Ham, The Dish Ran Away
with the Spoon, Paddington's Marmalade, Goldilocks' Porridge, Breakfast in America.
Full history: PROJECT-LOG.md · Notion row: https://app.notion.com/p/41342c9abb32810d8672e5281550b1ac
