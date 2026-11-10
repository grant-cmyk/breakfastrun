# CONTINUE - Breakfast Run

**Stamped:** 2026-11-10 13:50 SAST · machine: Claude cloud container · branch: main (trial-window-22 merged) · commit: see `git log -1`
**Lifecycle:** Active

**Status:** Track 1, BREAKFAST AT TIFFANY'S. Window 22 x 15 cells (176 x 120) in an arcade bezel; the
table a blue-on-cyan chequered cloth (dark checks 25% dots); cereal O's (solid - cars bounce off) mark
the road; breakfast things masked on top. Five of Grant's own cars (YOU, CYAN, GREEN the slow 3-axle
truck, PINK the tracked car, WHITE = Slim Jane's open-wheeler), each computer car with its own driving style; skids at speed;
a staggered grid; the race order shows faces on the grid, then each car's gap to the leader (8
checkpoints, small font), its lap (then a mini flag once in), a clock beside the best-lap holder,
the best lap under it; the cloth's dots 1 in 8, staggered (option F); RACE FINISHED when all are in. Beeper engine (pitch from your speed) and crash sound, played in the wait time. Own IM2
interrupt routine. Real-ROM test PASS (pixel-exact window).
Whole lap: work 205.9k T a picture (3 frames = 209.7k); 180 pictures at 3 TV frames, 26 at 4.

**Next step:** Grant plays `build/racer.tap` and says what to change next.

**Tools:** car editor https://claude.ai/artifact/2EqdSKs3fDfUqERTX9pTzL (tools/make_car_editor.py; hand
cars in tools/car_art.txt; tools/turn_car.py drafts the angled headings); mock-up scripts in tools/;
tests/drive_test.py, tests/profile_lap.py, tests/smooth_cpu.py.

**Constraints:** memory - TOPMEM (0xFAD0..0xFFF3) about 25 bytes left; low memory about 55 bytes;
bottom-row strips used: BUFA faces, BUFB logo, BUFC variables, BUFD tables, BUFE row index, BUFG
waypoints (BUFF and BUFH free). Road option H (thin dots only on the road) is on branch
trial-road-h: pixel-exact but too slow (~84k T a picture). A pool
driver (tools/pool_art.txt: SPECS, the old WHITE) needs 1 KB for his car - none free in the 48K now.
Any code moved ahead of hud.asm must not use equs defined later (pasmo first-pass values).
Frame time: about 4k T of headroom on an average picture now.

**Waiting on Grant:** playtest; angled headings of his cars are drafts (redraw in the editor if any
look wrong); confirm the repo should be public; push a tag for this build from his machine (cloud
sessions cannot push tags).

Track names for later tracks (verified): The Breakfast Club, Green Eggs and Ham, The Dish Ran Away
with the Spoon, Paddington's Marmalade, Goldilocks' Porridge, Breakfast in America.
Full history: PROJECT-LOG.md · Notion row: https://app.notion.com/p/41342c9abb32810d8672e5281550b1ac
