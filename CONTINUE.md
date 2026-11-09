# CONTINUE - Breakfast Run

**Stamped:** 2026-11-09 21:53 SAST · machine: Claude cloud container · branch: trial-window-22 · commit: see `git log -1`
**Lifecycle:** Active

**Status (branch trial-window-22, not yet merged to main):** window 22 x 15 cells (176 x 120), an arcade
bezel round it. The table is a blue and white chequered cloth (32-px checks, dark ones dithered, one
ink colour because the scroll is pixel by pixel); cereal O's mark both sides of the road; breakfast
things on the cloth. Cars masked. YOU and CYAN are Grant's own open-wheel cars (heading 0 his, 22.5 and
45 rebuilt by Claude); the others are the older generated cars. Own IM2 interrupt routine (counts frames
only). Real-ROM test PASS (pixel-exact window incl. the cloth).
Frame rate over a whole lap: work 187.0k T a picture; 179 pictures at 3 TV frames (16.7/s), 34 at 4.

**Next step:** Grant plays `build/racer_22wide_trial.tap` (this branch) and says whether to merge it to main.

**Options measured, not applied:**
1. O's 18 px apart instead of 15 (106 O's, not 131): work 181.9k, 191 at 3 frames / 26 at 4.
2. Masks on the O's and breakfast things (white halo, solid inside): reads better on the cloth, costs
   an estimated 25-40k T - not measured.

**Car editor:** https://claude.ai/artifact/2EqdSKs3fDfUqERTX9pTzL (built by tools/make_car_editor.py from
the game's art). Hand-drawn cars live in tools/car_art.txt; make_data.py uses them.

**Constraint:** memory - about 590 bytes free below the back buffer (code_end 0xBDB5).

**Waiting on Grant:** playtest the branch; draw or approve the 22.5 / 45 headings of his cars; art for the
other three cars if wanted; push tags stage1-verified (8501179) and stage2-verified (2ce33b7) from
C:\Users\grant\repos\breakfastrun; confirm the repo should be public.

Full history: PROJECT-LOG.md · Notion row: https://app.notion.com/p/41342c9abb32810d8672e5281550b1ac ·
Design canvas: https://claude.ai/artifact/1EoS3CaKDwVeBd7vqpeWjw
