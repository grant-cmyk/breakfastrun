# CONTINUE - Breakfast Run

**Stamped:** 2026-11-09 19:46 SAST · machine: Claude cloud container · commit: see `git log -1`
**Lifecycle:** Active

**Status:** The race screen is built as agreed on the Claude Design canvas, then revised: window 23 x 16
(left), panel with logo, race order and mini-map; message bar (lights, GO!, FINAL LAP!, FINISHED);
LAP / TIME / BEST (time, car, lap) under the window; Q races again. Five cars; computer cars run at
half rate. Kerbs and breakfast-table scenery. Real-ROM test 38/38 PASS.
Frame rate over a whole lap: 140 pictures at 3 TV frames (16.7/s), 65 at 4 (12.5/s); busy stretches hold
a steady 4 instead of 3,4,3,4.

**Next step:** Grant plays `build/racer.tap` and decides on the frame-rate options below.

**Frame-rate options (each measured or estimated in PROJECT-LOG.md):**
1. Accept as is (steady 16.7 in clear places, steady 12.5 in busy ones).
2. Window 15 rows instead of 16: ~8k T a picture (estimate).
3. Four cars instead of five: ~8-10k (estimate).
4. Less on screen near the track (kerbs are the main tile cost now).

**Constraint:** MEMORY - code and data end 0xBFA7, 89 bytes below the back buffer. Before any new
feature: share the car masks across kinds (frees ~2 KB) or move data into the free bytes at the bottom
of the buffer's third page.

**Waiting on Grant:** playtest; car art and breakfast art review; push tags stage1-verified (8501179) and
stage2-verified (2ce33b7) from C:\Users\grant\repos\breakfastrun; confirm the repo should be public.

Full history: PROJECT-LOG.md · Notion row: https://app.notion.com/p/41342c9abb32810d8672e5281550b1ac ·
Design canvas: https://claude.ai/artifact/1EoS3CaKDwVeBd7vqpeWjw
