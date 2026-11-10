# Breakfast Run - project log

Authoritative log for this workstream (house rule 5.2). Newest at the bottom. Times SAST.

## 2026-11-09 15:20 - started
- Grant: build a top-down car game on the ZX Spectrum as a personal home project to learn
  Spectrum coding; likes Ironman Super Off Road and Super Sprint, wants something like Micro Machines.
- Identity: Personal (chat ran on grant@ttro.com; filing follows the owner). Repo: grant-cmyk/breakfastrun.
- Original game in the genre - no names, art or tracks from the games named.

## 2026-11-09 15:25 - stage 1 built (cloud session, Claude)
- src/racer.asm: one car, 16 headings, 8.8 fixed-point momentum, friction 1/8 road, 1/4 grass,
  XOR sprite at any pixel, attribute read for surface, screen-edge stops.
- tools/make_data.py generates src/data.asm: thrust table, 16 car frames (PLACEHOLDER art,
  maths-generated), 32x24 track attributes (oval, red/white kerbs, start line).
- tests/drive_test.py on the real 48K ROM (zx 0.13.15): 10/10 PASS. One failure on the first run
  was the test's own fault (held O 17 frames, angle wrapped past 0); fixed the test, not the game.
- Not playtested by Grant yet. Known: possible flicker (erase+redraw per frame), placeholder car.

## 2026-11-09 15:29 SAST - named Breakfast Run
- Grant created grant-cmyk/breakfastrun (PUBLIC - Claude had suggested private; flagged).
- Repo attach (push) blocked by the session's permission check; local commit ready to push.

## 2026-11-09 15:32 SAST - pushed and tracked
- Grant gave the Claude GitHub App access to breakfastrun; stage 1 pushed to main (f0ca1a6), remote verified.
- Notion Workstreams row created: "Breakfast Run (ZX Spectrum)",
  https://app.notion.com/p/41342c9abb32810d8672e5281550b1ac

## 2026-11-09 15:47 SAST - stage 2: scrolling (cloud session, Claude)
- Grant: "that is a great start" on stage 1; next: scrolling like Micro Machines, car in the
  centre, track scrolls around it; straight top-down, not 3D.
- Tagged stage1-verified on 8501179 locally; the tag push was refused (403 - cloud sessions
  cannot push tags). WAITING ON GRANT to create and push it from his machine.
- Decision (Claude, flagged to Grant): the scrolling window is ONE colour pair. Spectrum colour
  is per 8x8 block and cannot follow a 1-pixel scroll (same lesson as Zarnon). Track drawn in ink.
- tools/make_world.py: breakfast-table world 72 x 56 tiles (576 x 448 px), 144 distinct tiles,
  road with 2-px edge lines, chicane, start-line checker, cereal hoops off-road, surface map.
  World border sized so the camera never meets the world edge while on the track.
- src/racer.asm rewritten: 24-bit car position, camera, column-major back buffer (one page per
  8-px column), 16 shift tables (A = spill left, B = stay right), blank tiles skipped, shadow
  registers for the map scan, PUSH-clear of the buffer with interrupts on, row-address table.
  Physics runs once per elapsed TV frame (FRAMES), so speed holds while drawing is slow.
- Measured: 12.5 pictures/s first, 17.0 after the clear/scan/row-table changes (3 TV frames each).
- Bugs found by the tests on the way: start position on the infield edge (road centre is y=320,
  not 280); map row multiply still x64 after widening to 72 (pixel check: ~2,000 wrong) - now one
  row_offset routine with an assembler check on MAPW; steering test held O too long (test fault).
- tests/drive_test.py: 11/11 PASS, including the window matching the world map pixel for pixel
  (0 wrong) at the start, after scrolling, and after a jump across the map.
- Looked at: build/stage2_drive.gif (117 distinct frames). Cannot judge beam tearing in this
  emulator (it renders from memory) - the copy is slower than the beam, so a tear line is possible.

## 2026-11-09 17:05 SAST - stage 3: car art, two computer cars, back to 17 pictures a second (cloud session, Claude)
- Grant on stage 2: "smooth enough, no tear line". Tagged stage2-verified on 2ce33b7 locally
  (WAITING ON GRANT to push it - cloud sessions cannot push tags).
- Grant asked: car art; two computer cars, slower, variable driving that can make mistakes; then
  "if they touch - bump away from each other"; then "use all the zx spectrum skills accumulated to
  improve smoothness and framerates".
- Car art (one-bit-art skill loaded first): 16x16, value plan scaled from Grant's top-down Traverse
  USA cars - tyres dither, glass paper, roof solid ringed by paper, nose solid, identifying mark in
  negative space (you: nose notch; CPU A: roof stripe; CPU B: open cockpit). Rule T1: no pixel
  rotation - each heading re-rasterised from the key shapes (one sample per pixel; averaging made
  noise), 22.5 deg drawn on a 2:1 slope (26.6 deg) for even steps, 67.5 = diagonal mirror, the rest
  exact quarter-turns. Mask = car + 1px halo. First attempt (averaged sampling) read as noise: redone.
  Preview: build/cars_preview.png. Not yet reviewed by Grant.
- Engine: every car is one 25-byte record through the same physics; controls come from the keys or
  from ai_drive. AI: waypoints every ~32 px (34), aim offset -8..+7 px re-rolled per waypoint, decide
  every REACT frames (A 2, B 4), throttle PACE of 8 frames (A 6, B 5), ease off past 45 degrees,
  mistakes at a waypoint with chance ERR/256 (A 14, B 24): late turn-in, lift, wobble - all at the
  car's own pace. Overshoot rule: if the next waypoint is nearer, move on (no U-turns).
- Bump: first version swapped speeds (rear car stopped dead). Grant asked for bouncing apart: now each
  car is kicked 0.75 px/frame away along the larger gap and nudged 2 px. IY must not be used (the
  ROM's interrupt needs it) - the first draft did; rewritten with a copy of car b.
- Race start: the computer cars wait on the grid until your first Q (found because the test loader is
  instant and the cars had lapped and rammed the parked player before the test looked). Grid is now
  three abreast so you pull away instead of rear-ending slower cars.
- Bug found in review before building: both computer cars shared one dot/cross pair, so each car's
  throttle used the other's figures - now a per-car C_EASE flag.
- PERFORMANCE (method from the zxspectrum skill's performance-and-profiling.md and
  scrolling-and-parallax.md: measure per stage in T-states, draw less, straight-line copies beat
  clever loops, keep a steady rhythm, mind the frames-per-tick feedback loop). tests/profile.py,
  T-states per picture with three cars in view:
    first build:   tiles 87k, copy 79k, ticks 45k (4 a picture), cars 21k, clear 19k = 3.9 frames (12.5/s)
    buffer in SCREEN LAYOUT + generated POP/PUSH copy (gen_copy.asm, DI, ~13.5 T a byte): copy 45k
    per-row lists of non-blank tiles (the 4 KB map is gone) + 8 generated tile routines, one per
    camy AND 7, so the character-row crossing is built in (gen_tiles.asm) + blank tile lines
    skipped: tiles 64k
    surface map packed to bits (4 KB -> 0.5 KB), looked up 1 frame in 4 per car; bump looks before
    it copies: ticks 31k (3 a picture)
    car stream reordered mask-then-ink, mask applied to both columns first: cars 20k (an interleaved
    first try with a memory temp went UP to 26.5k)
    fixed rhythm: a new picture every 3 TV frames exactly (PACE_FR)
  Result: ~186k T of work against 209.7k for 3 frames; 16.7 pictures a second on every stretch of an
  autopilot lap (tests/lap_capture.py), 17.0 in the drive test.
- tests/drive_test.py: 22/22 PASS on the real ROM (frame-rate floor raised 12 -> 16 to hold the gain).
  Laps: A ~16.9 s, B ~20.3 s, yours ~13.6 s. On road 100%/99%. ~20 mistakes in 90 s. Window pixel-exact.
- Looked at: build/stage3_sheet.png and build/stage3_lap.gif (autopilot lap with both computer cars).

## 2026-11-09 17:45 SAST - stage 4: five cars (cloud session, Claude)
- Grant: "we need to add another car or two if we can". Added two: CPU C (pace 6/8, grille slot in
  the nose) and CPU D (pace 5/8, sunroof, the most mistakes). Grid: 3 abreast + 2 behind.
- Memory: each car is 1 KB of pictures. The 5.6 KB POP/PUSH copier is no longer carried on the tape:
  make_copier WRITES it at start-up into 0xE800-0xFE03 (above the tables, below the UDGs). Code area
  now ends 0xB327; the tape went from 15.7 KB to 12 KB with two more cars.
- Engine generalised to NCARS (loops for AI and physics; bumps generated as gen_bumps.asm, all 10 pairs
  checked in full with fixed addresses, bump called only within 11 px both ways).
- PERFORMANCE, measured (tests/profile.py, five cars bunched on the grid, the worst case):
    5 cars as first built: ticks 85k/picture (21k a tick, 4 a picture) -> 4.0 frames
    quarter-squares multiply (sq4 table; targets scaled to +-63): ~140 T against ~450
    waypoint distance worked out once per decision; friction unrolled; empty car rows skipped
    computer cars TAKE TURNS to think (one full decision per frame; REACT = turns skipped)
    edge checks on the high byte first (an assembler check caught that the world is 576 px wide)
    physics keeps each speed in registers: one read, one write per axis
    -> a tick 21k -> ~13.5k (physics 7.5k, AI 4.3k, bumps 1.6k); grid start ~211k = 3-4 frames
  Along a whole autopilot lap: 16.7 pictures a second on 32 of 34 stretches, 13.9-14.8 on the first
  two (five cars bunched off the start). Accepted and flagged to Grant rather than cutting further.
- Test: the pixel check now stops the emulator exactly at copy_done (screen, camera and cars from the
  same picture), so the car margin is the 1px halo instead of 6 px. Found on the way: the emulator
  calls on_breakpoint at its own marks too - check the PC. drive_test.py 20/20 PASS; laps 16.5 / 20.2 /
  17.2 / 19.2 s; on road 99-100%; 45 mistakes in 90 s across four cars.

## 2026-11-09 19:07 SAST - stage 5: competitive computer cars, laps, position, a frame (cloud session, Claude)
- Grant: "make the other cars a little faster / better around the track - to be more competitive";
  then "now add laps and position"; then "put a border around the play area" and asked the play
  area's size: window 192x128 px = 24x16 character cells, of 256x192 (32x24): 75% of the width, 67% of
  the height, 50% of the area.
- Tuning harness tests/tune_ai.py (real ROM, 90 s races, laps and time on road per car). Measured
  (A/B/C/D lap s): today 16.1/19.7/16.5/19.9; pace 7,7,7,6 13.9/14.2/14.2/16.0; pace 8,7,7,6
  12.8/14.4/14.0/16.4; pace 8,8,7,7 12.2/12.5/14.0/14.5 - all 99-100% on road. Chosen: pace 7,7,7,6,
  every car thinks every 4 frames, ERR 8/14/10/20. Pace 8 would beat the autopilot's 13.5 s and a
  person on a keyboard is likely slower. REACH is now a named constant.
- Laps: counted when a car reaches waypoint WS (31, the first after the start line); LAPS = 3. Your car
  passes waypoints within 40 (or the one after, if you went wide). Progress = laps*NWP + passed; your
  position = 1 + cars with more progress. HUD below the window in the ROM font, printed only on change
  (skill: never reprint text every frame): LAP n/3, POS 1ST..5TH, FINISHED nTH. Title above.
- Frame: 2 px black round the window, drawn once at start.
- tests/drive_test.py: 28/28 PASS - reads the HUD text off the screen by matching ROM font cells;
  frame pixels; finish shows FINISHED. Laps 14.2/14.7/14.6/16.4 s. Off the start, 5 cars bunched: 13.5/s.

## 2026-11-09 19:10 SAST - HUD layout mock-ups (cloud session, Claude)
- Grant: "make the play area a character row less wide - and mockup some designs for a HUD - where
  would the HUD fit around the game area". Read as one character narrower. 23 cells cannot be centred
  on 32 (4 + 5), so both 23 (off-centre, with a side panel) and 22 (centred) are shown.
- Four layouts drawn as real Spectrum screens (tools/make_hud_mockups.py: a race frame captured on the
  real ROM, the ROM font, the real car pictures, the 15 Spectrum colours, one attribute per cell):
  A bottom strip (22), B position tower (23, panel right), C top banner (22, moved down), D wings (22).
  Files: docs/hud/mock_a.png .. mock_d.png; page docs/hud/hud-layouts.html, published as the artifact
  "Breakfast Run HUD Layouts" https://claude.ai/artifact/4c3E8kwVkzfxTsPK1SAzTT
- Recommended: B. Not built yet - WAITING ON GRANT to pick. Speed saving from a narrower window is an
  ESTIMATE (about 5k T at 23, 11k at 22), not measured.

## 2026-11-09 19:16 SAST - screen design on Claude Design, and the logo (cloud session, Claude)
- Grant: "take it through claude design to give it a smarter layout around the screen, so within the
  zx spectrum limitations and colour sprites use the 1 bit pixel skill to look at a small logo -
  breakfast run". Also asked: is the scroll 1, 2 or 4 px? Answer: pixel-exact (positions in 1/256 px,
  8 shift tables); per picture the window moves however far you went in 3 TV frames - ~5 px flat out.
- Logo (one-bit-art skill, tools/make_logo.py -> src/logo.asm, docs/design/logo.txt): 56 x 24 px,
  7 x 3 cells. Value plan: RUN solid, italic, 2 px paper racing stripe; BREAKFAST 5x5 line capitals;
  the egg's white is INK and the yolk a PAPER hole, so white ink on yellow paper gives a white egg with a
  yellow yolk (two colours a cell). First egg read as a ring/cereal hoop - redrawn as a lumpy white with an
  off-centre yolk. Review (one_bit_review.py): largest solid 4x4, ~52% of the envelope paper, 0 orphans,
  0 pinholes. Not yet approved by Grant.
- Layout (tools/make_screen_design.py, real Spectrum screens): window 23 x 16 cells at the left; a 7-cell
  panel on the right: logo, race order with each car's picture on its own colour (you on red), lap
  (double size), time; message bar above the window (start lights / GO! / FINAL LAP! / FINISHED nTH);
  lap-progress strip below it (a marker per car, you in a red cell). Cell budget on the canvas.
- Claude Design canvas "Breakfast Run Screen Design": https://claude.ai/artifact/1EoS3CaKDwVeBd7vqpeWjw
  (artboards: race screen mid race, what every cell is for, start, finish, logo). Images in docs/design/.
- Not built into the game yet: WAITING ON GRANT to approve the layout and the logo.

## 2026-11-09 19:32 SAST - stage 6: the race screen built (cloud session, Claude)
- Grant approved the Claude Design layout ("that looks good as a layout - lets do it"), then while it was
  being built: drop the lap strip ("that bar at the bottom can go"), put a mini-map where lap and time
  were, add a best lap with the car and the lap. Then: "go in search of methods to improve frame rates,
  speed, smoothness, I'm going to be away for an hour".
- Built (src/hud.asm): window 23 x 16 at cell column 1 (camera keeps you at 84,56); 2-px frame; panel:
  logo (src/logo.asm, the 1-bit logo), RACE, the race order (each car's picture on its colour, you on red;
  one row redrawn per picture at most, all five at the start), mini-map (track edges at 1/8 scale, a dot
  per car, yours 3x3 and blinking); message bar: start lights + GET READY / PRESS Q, GO!, FINAL LAP!,
  FINISHED nTH in double-size ROM letters; bottom band: LAP n/3, TIME m:ss.t, BEST m:ss.t NAME LAP n.
  Q after the finish starts a new race (every race variable reset).
- Copier: 23-byte rows = 6 pairs + 5 pairs + 1 byte (ld a,(nn)/ld (nn),a).
- Per-car lap timing (C_LST); best lap by anyone, with car and lap.
- Bugs found on the way: ranking used an address instead of the progress (ex de,hl) - order nonsense;
  XOR lap-strip markers cancelled when level (strip later removed anyway); the camera offset edit had
  not applied (car 4 px off centre) and a +-6 px test tolerance hid it - the check now stops at copy_done
  and is exact.
- Cost control: progress is one byte (saturating), ranking 25 byte compares; HUD work spread over
  pictures (order 1 in 4, map 1 in 4, clock 2 in 4); tower rows drawn with cell-address INC H loops.
- tests/drive_test.py 38/38 PASS. Frame rate: 13.0 off the start; lap 14.6 mean, 12.5 on ~14 of 34
  stretches - NEXT: the frame-rate hunt.

## 2026-11-09 19:42 SAST - frame-rate hunt while Grant was away; kerbs and scenery (cloud session, Claude)
- New tool tests/profile_lap.py: an autopilot lap with breakpoints on every stage; T-states per stage
  averaged over every picture, and how many TV frames each picture took. (The start-grid profile hid
  that the mid-lap stretches were the problem.)
- Measured, whole lap, pictures at 3 frames / 4 frames, average work per picture (limit 209,664):
    stage 6 as built            102 / 93   205.7k
    computer cars at half rate  139 / 63   199.1k   (each moves 2 frames' worth on alternate frames;
                                                     pace gate, ease-off and mistake lengths re-timed;
                                                     you stay at every frame)
    AI overshoot check only within 64 px; bumps on alternate frames; race order 1 picture in 4;
    your waypoint check every other picture
                                166 / 45   194.0k
    + kerbs (4-px chequer, world-locked) and trees/bushes/houses: tiles 60k -> 74k
                                 93 / 99   211.5k
    kerb outline line dropped (tiles 163 -> 120 distinct; 69k)
                                109 / 88   206.5k
    trees 3% -> 2%, bushes 4% -> 2.8%
                                110 / 87   204.8k
- Smoothness: the rhythm now settles on 4 frames for ~25 pictures after one runs over, then tries 3
  again - a steady 4 in busy places instead of 3,4,3,4 judder (pace, pace_hold).
- Findings: 70 tiles in view on average, 61 of them road edges at ~4 drawn lines; 53 list entries
  skipped left of the view (~2.7k); the remaining big costs are fixed (tiles ~69k, copy 45k, clear 23k).
  MEMORY is nearly full: code/data end 0xBE7B (0xC000 is the buffer).
- Head-on test made to coast (no keys): with ticks run in a burst per picture, a held Q pushed you
  forward again after the kick and hid the bounce.
- tests/drive_test.py 38/38 PASS. Grant then asked for breakfast-table scenery (eggs, bacon, knife,
  fork, juice, spoon, plate, toast) instead of trees - next.

## 2026-11-09 19:46 SAST - breakfast-table scenery (cloud session, Claude)
- Grant: "for the scenery - things that sit at a breakfast table. Eggs, bacon, knife, fork, juice ...
  spoon, dinner plate, toast". tools/make_breakfast.py draws them top-down, one-bit-art value plan:
  plate (two rings), fried egg (lumpy outline, solid yolk, 1 px shine - first try read as a rounded
  square, redrawn), toast (solid crust, 25% dither), juice (ring, 50% dither, paper highlight), bacon (two
  wavy rashers, dithered meat), knife/fork/spoon (solid handles). Trees, bushes and houses removed.
  A place setting in the infield (fork, plate, knife, spoon) plus 15 more items round the table.
- Memory: 47 bytes over at first. sq4 needs a page boundary and wasted 143 bytes of padding; the 34
  waypoints (136 bytes) now sit in that gap (src/waypoints.asm, src/sq4.asm split out). Code/data end
  0xBFA7: 89 bytes spare - MEMORY IS THE NEXT CONSTRAINT.
- Whole lap: 140 / 65 pictures at 3 / 4 frames, 200.1k average (cheaper than the trees - sparser near
  the track). Autopilot lap 15.4 pictures a second mean. drive_test 38/38 PASS.

## 2026-11-09 20:43 SAST - playtest
- Grant on the race-screen build (cdda3e9): "play well". Tagged race-screen-verified locally (cloud sessions cannot push tags - WAITING ON GRANT to push it with the other two).

## 2026-11-09 20:51 SAST - window trial mock-ups
- Grant asked the impact of one column less vs one row less, mocked up at a corner. tools/make_window_trial.py
  renders today / 22x16 / 23x15 / what each loses from a real screen captured at the first bend
  (docs/design/window_trial.png). Estimates (not measured): column ~8k a picture (tiles, copy, and the
  copy's odd byte goes), row ~8.5k (tiles, copy, clear). Waiting on Grant to pick one to build as a trial.

## 2026-11-09 20:53 SAST - trial: window one column less (branch trial-window-22)
- Grant: "one column less is doable". WIN_W 22 (176 px); copier 12 + 10 bytes, no odd byte; 23 tiles across;
  camera keeps you at 80,56. drive_test 38/38 PASS (window, frame and centring checks updated).
- Measured, whole lap: 195.0k average (was 200.1k), 144 / 60 pictures at 3 / 4 frames (was 140 / 65);
  copy 44.8k -> 41.3k. About 5k saved, not the 8k estimated: the tiles that drop out are mostly blank.
- On a branch until Grant has played it beside today's build (build/racer_23wide.tap vs
  build/racer_22wide_trial.tap).

## 2026-11-09 20:56 SAST - surround mock-ups
- Grant: "the outside rectangle for the game is really quite boring ... a few mockups". tools/make_surround_mockups.py
  on a real corner screen of the 22-wide trial: A gingham tablecloth (red/white 2x2-cell checks, dithered
  where they cross, white rim), B chequered-flag frame on green, C wooden table (yellow-on-red grain) with a
  lace placemat edge, D blue-and-white kitchen tiles. HUD text on plain strips. All drawn once at start:
  no cost per picture. docs/design/surrounds.png (+ _a.._d at 3x). Waiting on Grant's pick.

## 2026-11-09 21:00 SAST - window-edge mock-ups
- Grant does not like the solid 1-pixel rectangle round the play window. tools/make_edge_mockups.py: eight
  edges with no plain line - A none (colour change), B drop shadow, C corner brackets, D red/white kerb band,
  E tyre wall on grass, F square china plate rim on blue, G stitched hem on red, H thick rounded arcade bezel.
  All in the cells outside the window, drawn once: no cost per picture. docs/design/edges.png,
  edges_corners.png (top-left corner at 5x), edges_a.._h.png at 3x. Waiting on Grant's pick.

## 2026-11-09 21:04 SAST - arcade bezel built in
- Grant picked H, the arcade bezel. draw_frame now draws a 7-pixel black band outside the window with
  rounded outer corners (4 rows of corner bytes in df_corn), drawn once. Test frame_ok checks the bands,
  the rounded corners and that nothing spills outside. drive_test RESULT: PASS. build/racer_22wide_trial.tap.

## 2026-11-09 21:08 SAST - car pixel editor
- Grant asked for a simple pixel editor for the car graphic. docs/tools/car_editor.html (built by
  tools/make_car_editor.py from car_editor.template.html with the game's art), published as a private
  artifact: https://claude.ai/artifact/2EqdSKs3fDfUqERTX9pTzL. Draws the 3 drawn headings (0, 22.5, 45) per car
  in ink / paper / clear, previews all 16 headings with the 1px halo over kerbs, and copies the art as text
  ('BREAKFAST RUN CAR ART v1'). Checked in headless Chromium: paint, mirror, copy/load round trip, no errors.
- When Grant's art comes back: make_data.py must read it, and car_rows must cover every car's rows (today it
  uses the player's mask only). Up heading is not mirror-symmetric (tyre checker), so mirror starts off.

## 2026-11-09 21:11 SAST - chequered tablecloth mock-ups
- Grant: stylise the table as a chequered board, dithered, cars masked; the sides of the road are cereal O's;
  one colour pair only (pixel scroll). tools/make_table_mockups.py redraws the real world: 32-px checks (dark
  ones dithered), 140 cereal O's (thick ring, glint, hole shows the cloth) 3 px outside both road edges, items
  and O's masked (white halo, solid inside), cars masked as in the game. A 50% dither, B 25% dots, C diagonal
  lines, D = A in blue ink. docs/design/table.png (+ _a.._d). Not built.
- Cost (estimate, not measured): cloth by pattern fill instead of the zero clear, about +10k T; masking the
  O's and items instead of OR, about +25-40k T. Today 195k of 209.7k: would drop to 4 frames a picture unless
  savings are found. Masks need memory (89 bytes free).

## 2026-11-09 21:19 SAST - Grant's car is YOU
- Grant drew the player car in the editor (an open-wheel racer, heading 0). Read from his screenshot pixel
  by pixel and checked against it. Claude rebuilt 22.5 and 45 from his shapes (one-bit-art T1: shape model
  reproduces his drawing exactly at 0, rasterised at 26.6 and 45, then cleaned: front hubs restored at 45,
  pinholes filled, strays removed). Review: 1 island, largest block 4x4. docs/design/you_car_review.png.
- tools/car_art.txt holds hand-drawn cars; make_data.py uses them in place of its own drawing; car_rows now
  covers every car. drive_test RESULT: PASS. Editor rebuilt with the new art.
- To do: add Grant's car to the one-bit-art exemplars (rule 15, claude-plugins-personal).

## 2026-11-09 21:23 SAST - Grant's second car is YOU, his first is CYAN
- Grant: make the first car a computer car; this one is the player's. Transcribed by eye (the screenshot
  came mid-turn, not as a file) and checked against it. 22.5 and 45 rebuilt from his shapes and cleaned as
  before. tools/car_art.txt now has YOU and CYAN. drive_test RESULT: PASS. Review sheet
  docs/design/you_car_review.png. Editor republished with both.

## 2026-11-09 21:37 SAST - tablecloth (D) and cereal O's built
- make_world.py: 131 cereal O's (snapped to a 4-px grid) replace the kerbs: 90 tiles instead of 184, about
  1 KB of memory back. Window ink blue (0x79).
- racer.asm: clear_buffer replaced by cloth_fill, after the camera: 32-px checks, dark ones a 50% dither,
  world-locked. 4 register pairs per line kind (BC DE HL AF), main and alternate sets swapped by EXX + EX
  AF,AF' through patched slots in an unrolled 8-row push; per-third setup done once. Bug found and fixed:
  the loader table straddled a page and an 8-bit add wrapped, so 1 in 4 line kinds jumped into data (a
  72-frame stall); the guard that would have caught it sat after END and was never assembled.
- Measured, whole lap: work 203.4k T a picture (cloth 42.1k, tiles 52.3k, ticks 43.7k, copy 41.3k, cars
  15.2k); 127 pictures at 3 frames, 73 at 4. Pixel-exact test now includes the cloth: RESULT PASS.

## 2026-11-09 21:48 SAST - speed-ups: own interrupt routine, cloth by character row
- IM2 with our own interrupt routine (I=0x39 at the ROM's spare 0xFF bytes -> JR at 0xFFFF -> JP isr at
  0xFFF4): it only counts FRAMES. The game reads keys from the ports and never calls the ROM. Saves the
  ROM's keyboard scan every frame (~2.9k T a picture) and pushes 6 bytes, not 10+.
- That lets the cloth fill go one character row at a time (8 lines, one per page, unrolled; dither
  phase swapped by EXX + EX AF,AF' each line; a mid-row loader call where the check row changes), and
  only bytes 0..23 of each line. Bugs caught by the pixel test and fixed: INC IXH changed F (a pattern
  register); a helper clobbered the line number.
- drive_test: laps now counted from the game's C_LAPS; the old waypoint-wrap count was fooled when the
  AI moves C_WP ahead for a moment to look ahead (car 1 'lapped' twice in 0.4 s). Real laps unchanged:
  15.0 15.1 14.9 17.4 s. RESULT: PASS.
- Measured, whole lap: work 195.7k T a picture (was 203.4k): cloth 37.7k, tiles 51.6k, ticks 41.7k,
  copy 41.1k, cars 15.0k. 149 pictures at 3 frames, 57 at 4 (was 127 / 73).

## 2026-11-09 21:52 SAST - one character row less of view (Grant's offer)
- WIN_H 120 (was 128); BAND_Y = the text rows under the window, now rows 20-21 (were 21-22); camera
  centre (80,52); 16 rows of tiles; 15 character rows of cloth; win_attr WIN_H/8. Asserts guard cf_tab.
  drive_test updated (window slice, bezel, centre, text rows): RESULT PASS.
- Measured, whole lap: work 187.0k T a picture (was 195.7k): tiles 49.3k, ticks 40.3k, copy 38.5k, cloth
  35.2k, cars 15.2k. 179 pictures at 3 frames, 34 at 4 (was 149 / 57).

## 2026-11-09 21:53 SAST - measured option, not applied
- O's 18 px apart (106, not 131): tiles 45.2k, work 181.9k, 191 at 3 frames / 26 at 4. Reverted to 15 px
  pending Grant (it changes the look). CONTINUE.md rewritten for the branch.

## 2026-11-10 05:50 SAST - skids, wider road, the finish, flags, shorter bottom text
- Grant: cars skid when turning fast; road a little wider; a car that finishes stops a little over the
  line; the race is Finished when every car is in; a chequered flag in the race order per finished car;
  bottom text cut off by the map, drop the 0: from times.
- skid (physics): above 1.25 px/frame, give back half of the sideways friction (sideways/16 a frame,
  /8 for a computer car's 2-frame step) using the quarter-square multiply; slow cars grip as before.
- ROAD 52 (was 48); the clear band for breakfast things kept at 76 px so the plate stays. 132 O's.
- Finish: car_in records each car's place (fin_at, fin_count); finished cars get no buttons and roll
  to a stop; ranking puts finished cars first in the order they came in; your time freezes on the
  clock; race over when all 5 are in (or 30 s after you); RACE FINISHED  PRESS Q. Flag 8x8 at panel
  column 30, centred on the two rows. A new race waits for Q to be let go first.
- Bottom text: times without a leading 0: ('  14.2'); BEST 14.3 CYAN  LAP 3 fits in 21 columns.
- Memory: start-up-only code (make_tables, make_copier, im2_on) moved past code_end into the back
  buffer (runs once before the buffer is used; guarded below TAB_HI). start does them once; new_race
  is where Q comes back to. drive_test RESULT: PASS.
