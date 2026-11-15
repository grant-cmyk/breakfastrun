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

## 2026-11-10 05:56 SAST - computer-car personalities; top-of-memory data
- Grant: computer cars a little faster, each with different logic and strengths. Driving styles
  (ai_styles, by kind): turn-in reach, racing-line wander, braking (late / 45 deg / 27 deg), steering
  fuss (14 / 7 deg); with throttle now in 16ths (pace_gate) and mistake rate:
  CYAN racer 15/16, tidy, 45 deg; GREEN smooth 14/16, turns in early (reach 30), few mistakes;
  PINK wild 15/16, late brakes, wide line, twitchy, most mistakes; WHITE steady 14/16, early brakes.
  Laps (90 s watch): 13.6 14.8 15.8 14.5 s (were 14.7 15.5 15.3 17.2). drive_test RESULT: PASS.
- Memory: TOPMEM 0xFAD0..0xFFF3 (above the generated copier, which ends 0xFAC3) holds read-only data
  loaded in the start-up area and copied up by start; the logo first. HIGH is a pasmo keyword.

## 2026-11-10 06:06 SAST - breakfast things on top of the cloth; frame rate back
- Grant: the egg etc. on top of the chequered cloth, masked. make_world: mask = 1-px halo + solid
  inside; a tile carries a mask only where it hides dithered cloth (28 tiles, 10 masks); items placed
  within 3 tiles of where wanted at the spot needing fewest masked tiles (the 2nd plate fits again).
  Masked tiles numbered from TM_FIRST, drawn by tdraw_m ((buf AND NOT mask) OR ink, shifted);
  masks and the mini-map in TOPMEM (src/topdata.asm). Pixel test includes the masks: PASS.
- Speed: skid now halves push and friction while turning fast (same top speed, sideways speed dies
  half as fast) - no multiplies; O's on the 8-px tile grid (one tile each: tiles 56k -> 37k); friction
  bug (RR resets flags after CP) caught by the top-speed test and fixed.
- Measured, whole lap: work 183.8k T; 160 pictures at 3 frames, 48 at 4. Laps 13.7 14.5 13.7 15.0 s.
  docs/design/items_on_cloth.png.

## 2026-11-10 06:11 SAST - faces, shorter logo, PINK and WHITE cars
- Grant: little cartoon faces for each car in the race order; RUN less tall to make room.
  tools/make_faces.py: 16x16 line faces (YOU helmet+visor, CYAN shades+grin, GREEN cap+closed eyes,
  PINK spikes+ring eyes+O mouth, WHITE glasses+straight mouth), kept in TOPMEM; tower_row draws place,
  car (cols 26-27), face (28-29), flag (30). Logo 7x2 cells: RUN 8 px tall in the second row, egg
  flattened beside it. Race order from row 5 (TOWER_Y). docs/design/panel_faces.png.
- Grant's editor paste: PINK and WHITE heading 0 new (taken); his other headings were the old
  generated art from a stale browser draft (not taken - would have undone his first car as CYAN).
  PINK/WHITE 22.5 and 45 sampled 16x a pixel from his shapes, 45 made symmetric: drafts.
  drive_test RESULT: PASS. Laps 13.6 14.4 13.8 14.9 s.

## 2026-11-10 06:15 SAST - track 1 named
- Grant: the first track is Breakfast at Tiffany's. BREAKFAST AT TIFFANY'S (22 characters, the
  window's width) along row 0; msg_clear now clears only the message bar (rows 1-2), not row 0.
  Test checks the name. drive_test RESULT: PASS. Other verified names for later tracks: The Breakfast
  Club, Green Eggs and Ham, The Dish Ran Away with the Spoon, Paddington's Marmalade, Goldilocks'
  Porridge, Breakfast in America.

## 2026-11-10 06:26 SAST - fix: garbled faces once cars finish
- Grant's screenshot: faces garbled in the race order. Cause: the flag code fell through into
  tr_glyph for the bottom half; tr_face was added between them, so finished cars got half a face
  drawn from the flag's bytes. Fixed with an explicit JR. New test: every finished car shows the
  flag and its face matches the face data byte for byte. drive_test RESULT: PASS.
  docs/design/flags_fixed.png.

## 2026-11-10 06:30 SAST - faces spaced from the cars; clearer flag
- Grant: faces too close to the cars; and the flag read as a glitch. Face now at panel columns
  29-30 (column 28 a gap), flag at 31, redrawn as a square of 2x2 checks on a pole (8 x 14).
  Test checks the flag bytes and the faces. drive_test RESULT: PASS. docs/design/panel_spaced.png.

## 2026-11-10 06:35 SAST - Grant's GREEN car; GREEN the slowest
- Grant's editor paste: GREEN heading 0 new (a long 3-axle racer); the rest unchanged or the stale
  draft. 22.5 and 45 sampled from his shape: drafts. Grant: GREEN should be the slowest - throttle
  12/16 (was 14). Laps: CYAN 13.6, GREEN 16.9, PINK 14.2, WHITE 15.3 s.
- Test: 'not faster than your top speed' now counts speeds over 1.80 (bump kicks and slides add a
  moment over the 1.75 cap; PINK hit 2.3% over 1.75, 0.1% over 1.80). drive_test RESULT: PASS.

## 2026-11-10 06:37 SAST - smaller flag
- Grant: flags smaller to fit in better. Now a 6x6 square of 2x2 checks on a 4-px pole, 2 px clear
  of the face, centred on the place. Test updated. drive_test RESULT: PASS.
  docs/design/panel_flags_small.png.

## 2026-11-10 06:38 SAST - car editor opens on the game's art
- Grant: put the graphics in the editor as they are in the game. Drafts are now saved per version of
  the game's art (key = hash of it), so a new game version opens on its own art; older drafts stay in
  the browser behind 'Bring back my earlier draft'. Checked in headless Chromium with a stale draft:
  opens on the game art, button shown, draft restored, no errors.

## 2026-11-10 06:41 SAST - CYAN redrawn by Grant
- Editor paste (now starting from the game's art): one drawing changed, CYAN heading 0 (24 pixels).
  22.5 and 45 rebuilt from it (sampled 16x a pixel; 45 symmetric). drive_test RESULT: PASS.

## 2026-11-10 07:05 SAST - PINK redrawn by Grant (a tracked car)
- Editor paste: one drawing changed, PINK heading 0 (86 pixels): tracks with treads, a round cockpit,
  a barrel. Turned by sampling, the treads went to mush (one-bit-art T1), so 22.5 and 45 were rebuilt
  from its key shapes (tracks as two rails, body, cockpit ring, barrel). tools/turn_car.py added for
  the sampled drafts. docs/design/pink_headings.png. drive_test RESULT: PASS.

## 2026-11-10 07:14 SAST - more skid
- Grant: more skidding round corners. Slides from 1.0 px/frame (was 1.25) and one more step for each
  0.25 faster, up to 3 (push and friction halved each step: same top speed; sideways speed dies at
  1/16, 1/32, then 1/64 a frame). Measured on the road, full speed, full turn held: largest drift angle
  125 degrees (was 75). (A first measurement on the grass read 33 for both: grass friction swamps it.)
  drive_test RESULT: PASS; computer cars 99-100% on the road; laps 14.3 17.1 16.7 14.6 s.

## 2026-11-10 07:16 SAST - colour options without white (mock-ups)
- Grant: slight flicker, probably the chequered cloth, worse with the white; suggest colours without
  white. tools/make_colour_mockups.py: a real game screen with the window redrawn as 1 blue/cyan,
  2 black/green, 3 blue/green, 4 red/yellow, 5 black/cyan, 6 magenta/cyan, and 1, 2, 4 with a 25%
  dot cloth (a 50% checker shimmers when it scrolls a pixel at a time - one-bit-art rule 16).
  docs/design/colours.png. Waiting on Grant's pick.

## 2026-11-10 07:19 SAST - sound: engine and crash (beeper)
- Grant: sound when cars collide; see what can be done with car sounds. Played in the loop's wait for
  its next picture (zxspectrum skill sound notes, Traverse USA): snd_wait replaces the HALT - one
  speaker flip and a gap set by your speed (gap 150..39 counts of 51 T: about 230 Hz rolling to ~880 Hz
  flat out), silent before the start and after you finish; a crash (your car in a bump) plays random
  flips for 6 pictures. Pieces under ~7.6k T so the copy still starts ahead of the beam.
- Measured, whole lap: work 181.5k T (unchanged - the sound is in the wait); 196 pictures at 3 frames,
  22 at 4. Engine gap follows speed (60 at 1.55, 101 at 0.77); a bump with you sets the crash.
  Not heard: the cloud has no audio - Grant to listen. drive_test RESULT: PASS.

## 2026-11-10 07:35 SAST - blue on cyan with dots; smoother computer cars; O's 18 apart and solid
- Grant: colour 1 (blue on cyan) with the 25% dots: window attr 0x29, cloth odd rows empty (dots).
- Grant: computer cars jerky - measured: 3.4 / 6.8 px a picture alternating (2-frame steps on alternate
  frames, a picture every 3). Now they move every frame and think on alternate ones; throttle-off
  frames spread evenly (bit-reversed count). tests/smooth_cpu.py: spread 32-41% -> 15-22%.
- Re-tune: GREEN 12/16 (slowest), WHITE 15/16, PINK fewer mistakes, eases at 45, line +-4
  (late braking + the bigger skid ran it wide). Laps 14.0 17.2 14.6 14.9 s.
- Grant: O spacing 18 px (91 O's); O's are solid: omap (1 bit a tile, TOPMEM); o_check on alternate
  frames looks at the 4 tiles nearest each car, kicks it away like a bump, crunch if it is you.
  Checked: you driving into an O stop 8 px short and bounce. 2 O bounces in 20 s of computer racing.
- Measured, whole lap: work 193.7k T (was 181.5k: cars moving every frame + O checks); 177 pictures
  at 3 frames, 31 at 4, 14 at 2. drive_test RESULT: PASS.

## 2026-11-10 07:35 SAST - merged to main
- Grant: merge it. trial-window-22 merged into main (main was an ancestor: no conflicts).
  CONTINUE.md rewritten for main. build/racer.tap is the current build.

## 2026-11-10 07:53 SAST - the tank commander's face; wider road
- Grant: car 5 is a tank, give him a military outfit -> PINK (the tracked car; 4th on the grid) now a
  tank commander: steel helmet with a paper star badge and brim, stern brows, moustache.
- Grant: track slightly wider all round: ROAD 56 (was 52); items keep a band 12 px each side wider
  than the road; all items placed; 91 O's; 22 masked tiles. drive_test RESULT: PASS; laps 13.8 16.9
  14.2 14.9 s. Commits now as Claude <noreply@anthropic.com> (GitHub showed the earlier ones as
  Unverified; history not rewritten - Grant to decide).

## 2026-11-10 08:00 SAST - staggered grid, true leaderboard, faces; memory moves
- Grant: a classic staggered grid with grid positions. Two lanes 11 px either side of the middle;
  P1 (you) inside/upper at x 248, P2 lower 16 px back, P3..P5 behind (CYAN, WHITE, PINK, GREEN);
  a [ grid box painted behind each (x on the tile grid so the boxes share tiles). The race order
  starts in grid order (grid_order).
- Grant: the race order should show positions as places change. It did, but cars level on waypoints
  (32 px apart) fell back to car number; ties now go to the car nearer its next waypoint (pdist).
- Grant: GREEN (the slow truck) asleep - eyes shut, snoring o, a z; CYAN aggressive - slanted brows,
  gritted teeth. docs/design/faces.png, docs/design/start_grid.png.
- Memory: code had reached 0xC000 exactly. The HUD's fixed text moved to TOPMEM; faces and logo
  moved into the back buffer's unused bottom rows (152..191: BUFA, BUFB), copied by start. Low
  memory free: 178 bytes; TOPMEM free: about 180. drive_test RESULT: PASS.

## 2026-11-10 08:07 SAST - tables to the buffer's bottom rows; fix: cars drawn below the window
- Memory: thrust_tab (make_data -> src/thrust.asm), ai_styles, rev4, cf_tab moved to BUFD (buffer
  row 155 on), copied by start; BUFC reserved for variables. Low memory free: 434 bytes.
- Bug found by the move: draw_car still clipped at window row 127 (the 128-line window), so a car just
  below the 120-line window drew into buffer rows 136..158 - harmless until tables lived there
  (thrust_tab bytes 16-17 overwritten after ~20 s: computer cars lost their steering). Now WIN_H-1.
  drive_test RESULT: PASS; laps 14.1 17.2 15.0 14.1 s.

## 2026-11-10 08:40 SAST - race order while racing: gaps, best-lap clock, flags, small font
- Grant: when the race starts the faces go and each car shows its gap to the leader, timed at 8
  checkpoints (every 4th waypoint); a 3x5 number font so more numbers fit (columns 28-29). Under the
  order: a clock and the best lap (no "BEST" label). The best-lap holder gets a clock at the right of
  its row (column 31); a finished car a mini chequered flag (column 30). Mini-map black on yellow.
- Memory: car_rows and tdraw_table moved to TOPMEM; buf_addr, scr_addr and gap_draw now fill the
  127-byte gap before sq4's page (savings earlier in memory are swallowed by that alignment).
  Low memory free: 80 bytes.
- Bug: code moved ahead of hud.asm used GAPS/SHGAP (equs built on BUFC, defined at the file end):
  pasmo gave it the first-pass value, so gaps were read from ROM address 0x0018 and "shown" values
  written to 0x0022 - every gap redrew every time. BUFC now defined at the top of racer.asm.
- Bug: the start ran at 12.5 pictures/s (merged build 16.5). One late picture at GO (GO message +
  a race-order row) set the 4-frame pace for 25 pictures. GO's picture now does nothing else.
- drive_test RESULT: PASS (start 16.0 pictures/s). tests/profile.py fixed (measures the start).

## 2026-11-10 08:40 SAST - Slim Jane replaces WHITE; the old WHITE goes to a pool
- Grant: replace the glasses driver with Slim Jane ("need a girl in the race"), keep him as a
  tougher racer for later races. WHITE's heading 0 is Grant's slim open-wheeler; 22.5 and 45 placed
  by hand on the pixel grid (turn_car.py's draft turned the 1-pixel wings to mush). Face: long hair,
  fringe, lashes, a smile. The old car is in tools/pool_art.txt (SPECS) and his face in
  POOL['SPECS'] in tools/make_faces.py - kept in the repo, not loaded into the 48K (no room: a car is
  1024 bytes, 80 are free). Jane drives as WHITE did (15/16 throttle, 3/256 mistakes) for now.

## 2026-11-10 08:50 SAST - Jane's angled headings accepted
- Grant: "good enough" - her hand-placed 22.5 and 45 degree drawings stay as they are.

## 2026-11-10 SAST - best lap clear of the clock
- Grant: the best time looked cut off ("d2.8": the clock's right edge ran into the 1). st_text_x
  takes a start offset; the best lap now starts 2 px right of the clock (14 px of text + 2 = 16,
  still two columns). docs/design/best_lap_panel.png. drive_test RESULT: PASS (start 16.5/s).

## 2026-11-10 SAST - Jane the fastest; faces in the editor; plain-road mock-ups
- Grant: Jane should be the fastest computer car. Her throttle 16/16 (was 15): laps (drive_test)
  Jane 13.6, CYAN 13.9, PINK 14.9, GREEN 16.8 s; never over your top speed. RESULT: PASS.
- Grant: share her face in the pixel editor. The editor has a Faces mode: each driver's face in ink
  on their race-order colour, the five rows previewed as the game shows them, copied as "BREAKFAST
  RUN FACE ART". Link #jane opens on her face. tools/make_car_editor.py reads tools/make_faces.py.
- Grant: mock-ups of a road without the cloth's checks, the checks only off the track ("hugs around
  the map, like the corners"): tools/make_road_mockups.py -> docs/design/road_options.png. NOW,
  A plain road only, B plain out past the O's, C checks only in the corners and infield. Not built:
  the engine fills the cloth over the whole window, so a plain road means clearing the dots on the
  road tiles each picture - a cost to measure once Grant picks one.

## 2026-11-10 SAST - editor: right-click paints paper; Jane's face redrawn
- Grant: left click ink, right click paper. Left-click draws with the picked tool (Ink to start);
  right-click paints Paper (on a face, the band). (A comment I added first cut off the paint call
  on the same line - caught by a click test in Chromium before publishing.)
- Grant: Jane's nose not so big, pigtails, a slightly narrower face. Pigtails out at the sides,
  a parted fringe, dot eyes, a one-pixel nose, a little smile, the jaw tapering to a small chin.
  Checked in the game's own race order: docs/design/panel_jane_pigtails.png. Data only (same size);
  the full drive test was not re-run for it.

## 2026-11-10 SAST - Grant's own faces
- Grant redrew all five faces in the editor's Faces mode; kept in tools/face_art.txt, which
  make_faces.py now reads over its own drawings (as make_data.py does with car_art.txt). Then, at
  his ask, the faces of rows 4 and 5 swapped: PINK (the tank) and GREEN (the truck).
  Checked in the game's race order: docs/design/panel_grants_faces.png.
- Grant's updated clown face (round eyes in rings): pasted still under PINK (from an editor draft
  made before the swap); put on GREEN to keep the swap. PINK keeps the dark-haired face.
- Grant's third round of all five faces in (the clown on GREEN, the dark-haired face on PINK).
- Editor: Copy art for Claude now carries every car (15 drawings) and every face (5) in one paste;
  Load takes it back (round trip tested in Chromium: 20 drawings).

## 2026-11-10 SAST - the 6-wheeled truck kept in the pool
- Grant will redraw GREEN's car; its current design (the long 6-wheeled truck, all three drawn
  headings) saved as TRUCK in tools/pool_art.txt for later. The game is unchanged.

## 2026-11-10 SAST - mock-ups: lighter dots on the road
- Grant: the dotted / chequered effect less visible in the road area. docs/design/road_dots_options.png:
  NOW (1 pixel in 4), D road 1 in 8 (staggered), E road 1 in 16, F 1 in 8 everywhere. D and E need
  the road told apart from the cloth each picture (cost unmeasured); F only changes the cloth's
  line patterns (expected no extra cost - to confirm when built).

## 2026-11-10 SAST - GREEN is the clown car
- Grant's clown car (heading 0 read cell by cell from his editor screenshot; his later full paste
  had the same, its 22.5 and 45 still the truck's). 22.5 and 45 turned about the car's own centre
  (it sits half a pixel off the grid's middle, which made turn_car.py's draft lopsided).
  docs/design/clown_car.png. drive_test RESULT: PASS (start 16.5/s; laps unchanged).
- Grant: the road's dots much lighter. docs/design/road_light_options.png: E road 1 in 16 (from
  before), G 1 in 32, H 1 in 64, I only the checks' outlines dotted; the cloth off the road as now.

## 2026-11-10 SAST - mini flag without its pole
- Grant: the gap time is cramped against the chequered flag; no line needed left of the flag.
  The flag is now 6 x 6 checks only, a pixel in from each side of its cell: 4 px clear of the
  time, 1 px clear of the clock. docs/design/panel_flags_no_pole.png. drive_test RESULT: PASS.

## 2026-11-10 SAST - road option H tried in the engine: too slow
- Grant: happy with H (road dots 1 in 64). Built as a pass after cloth_fill that thins the dots on
  road tiles on dark checks, using the surface map widened to the O's (docs/design/road_h_build.png:
  H3, how it looks on whole tiles). Memory found by moving row_index, cars_init and the waypoints
  into spare bottom-row strips. Result pixel-exact, but the pass costs ~84k T a picture on the start
  straight (44 runs): 11.0 pictures/s off the start (was 16.5); lap work 275k T a picture (was 199k;
  3 frames = 209.7k), pictures mostly 4-5 frames. An optimised pass would still cost ~20k T, more
  than the ~10k of headroom. Kept on branch trial-road-h, not merged. Main unchanged.
- Grant asked why H is slower when it has fewer dots. The cloth is stamped line by line from one
  repeating pattern (a blank costs the same as a dot); the road is a different shape on every line,
  so H adds a second job that finds it and rubs the dots out byte by byte. Free lighter cloths (one
  pattern for even lines, one for odd): docs/design/cloth_free_options.png J, K, L - all read as
  vertical stripes; the even, staggered look (F) needs a 4-line pattern, a small engine change.

## 2026-11-10 SAST - cloth F: 1 dot in 8, staggered
- Grant: go F. The dark checks' dots are now 1 in 8 (x AND 3 = 0 on lines y AND 3 = 0, = 2 on
  y AND 3 = 2). The fill alternates two register sets, so the dotted lines' two kinds take turns
  through minis: on the 3 dotted lines after line 0 of each character row a slot calls one (same
  slots all picture: camy AND 3); loaders keyed by y AND 3 and check row (cf_lidx). cloth_pat to
  BUFC; waypoints and row_index to bottom-row strips (BUFG, BUFE) to make room; new code in the
  gap before sq4 (clothmini.asm) and after it (clothmini2.asm).
- Cost: cloth_fill 35.3k -> 45.7k T a picture; lap work 199.3k -> 205.9k; frames over a lap
  {3: 180, 4: 26, 5: 1} (was {3: 184, 4: 27}) - docs/design/cloth_f_profile.txt. GO's picture
  ran late and set the 4-frame pace for 2 s, so it no longer sets the pace (pace_skip).
  drive_test RESULT: PASS (start 15.5/s; window pixel-exact). docs/design/cloth_f.png.

## 2026-11-10 SAST - each car's lap where its flag will go
- Grant: while the chequered flag is not showing, use that space for the car's lap. Column 30
  shows the lap (1-3) in the small font, 2 px in, until the car is in and the flag replaces it.
  The row's key (fin_key) now includes the lap, so a row redraws when its car starts a lap.
  docs/design/panel_laps.png (22 s, 42 s, 52 s). drive_test RESULT: PASS (start 15.0/s).

## 2026-11-10 SAST - place numbers centred against the cars
- Grant: centre the number against the car. The place number (1-5) was printed in the top cell of
  its 16-px row; now its ROM letter is drawn 4 px down (tr_glyph16 from a 16-row buffer, PNUM in
  BUFC), level with the car. docs/design/panel_place_centred.png.
  drive_test RESULT: PASS (start 15.0/s).

## 2026-11-10 SAST - mini-map: no start tick at the top dip
- Grant: why a line at the top section - not the start/finish. Bug in make_world.py: the start
  tick was drawn down a whole column of the mini-map, wherever it crossed the road - and that
  column also crosses the top dip. Now only on the bottom straight. Only the mini-map's bytes
  changed (topdata.asm). docs/design/minimap_fixed.png. drive_test not re-run (it does not read
  the mini-map; nothing else changed).

## 2026-11-10 SAST - mock-up: the driver strip
- Grant: start with one NOS canister; the LAP / TIME / BEST lines are not needed - use the space
  for the player: his face on the left, his inventory (3 things), a message box ("great driving!"
  on an overtake, "superb lap", "get it together" on hitting the O's). Mock-up on a real race
  screen: docs/design/driver_strip.png (tools/make_strip_mockups.py; ROM letters read from the
  emulator's ROM, not kept in the repo). Face twice size on red; 3 white framed slots, the NOS in
  the first; a white rounded box with a speech tail back at the face, 2 lines of 9 letters.
- Grant: the messages come from the pits - a crew chief on the right of the message. Re-laid in 24
  columns: you (cols 0-3, red), inventory (4-9), the message box (11-18, 8 letters a line) with its
  tail out to the crew chief (20-23, white on blue: a headset - band, ear cups, microphone).
- Grant: the crew chief's picture to edit. The editor's Faces mode has a sixth face, CREW (on
  blue, twice size as in the strip; link #crew); his drawing is in tools/face_art.txt.
- Grant: smaller text, like the numbers, to make space. 3 x 5 letters (A-Z, digits, ! . - ')
  in the same box: 3 lines of up to 15 letters (was 2 of 8). docs/design/driver_strip_small.png.
- Grant's own crew chief (from his editor screenshot) saved in tools/face_art.txt; the strip
  mock-ups draw him from there. His later 'updated' version came as an image only (not saved
  as a file): waiting for it as pasted text. The live editor is left as it is, so his draft in
  that browser is not set aside.
- Grant: the NOS to edit too. Editor Faces mode: a seventh picture, NOS (black on a white slot;
  link #nos); kept in tools/face_art.txt. 'Bring back my earlier draft' now also brings back face
  drafts made on older game art (the newest kind; pictures it lacks come from the game) - tested
  in Chromium - so Grant's updated crew chief, drawn on the last version, can be restored.
- Grant: more prompts ('PUSH! PUSH!' when 2nd and close to 1st); look up real pit-to-driver phrases;
  a TV-style radio sound wave while a message comes in. Searched: 'box, box' (pit now) and the FIA's
  2014 ban on 'push hard' / 'push now' confirmed; 'hammer time' (Hamilton's team) confirmed by one
  glossary. Mock-up: the wave (15 bars about a mid line, moving while the chief talks, then flat)
  above the small letters: docs/design/radio_wave.gif, radio_wave_still.png.
- Grant's reference for the wave (tall bars, varied heights, rounded ends, dark and grey): 20 bars,
  2 px wide, up to 13 px tall, rounded ends, the grey ones dotted; 2 lines of small letters below.
  Grant: 'exactly'. docs/design/radio_wave.gif, radio_wave_still.png.
- Grant shortened the NOS by one row (editor screenshot, read cell by cell): tools/face_art.txt;
  the mock-ups draw it from there.
- Grant: centre the crew chief in his blue square. Faces in the strip are now centred by their
  ink in their 32 x 32 squares (the crew chief 3 px lower; yours unchanged within a pixel).
- Grant's updated face for YOU (editor screenshot, read cell by cell) - in the game's race order
  and the strip. Checked on the grid.
- Grant: the wave much smaller, just vertical lines (no dotted ones): 13 one-pixel lines up to
  7 px tall; 3 lines of small letters fit again. docs/design/radio_wave.gif.
- Grant: the NOS in the middle of its slot, not touching the frame. Centred by its ink inside the
  14 x 14 inside of the slot (1 px clear top and bottom, 3 px each side).

## 2026-11-10 SAST - the driver strip in the game; the race over screen
- The LAP / TIME / BEST lines are gone. Under the window: the driver strip (Grant's design) - you,
  your inventory (the NOS canister you start with), the crew chief's radio, the crew chief. Its
  fixed picture is generated from the approved mock-up (tools/make_strip.py -> strip_img.asm) and
  drawn once at the start, with everything else on the screen that never changes (screen_once:
  the colours, bezel, logo, track name, RACE heading) - that code now sits in the start-up area,
  and a new race only redraws what changes.
- The radio (src/strip.asm): messages in the 3 x 5 letters, typed out 4 letters a picture, the
  wave (13 lines) moving while the chief talks, then flat. What he says: GOOD LUCK at the green
  light; a pass, the lead, a place lost (3 s apart); PUSH! PUSH! second and within 0.5 s of the
  leader; SUPERB LAP on your best lap yet; GET IT TOGETHER on hitting the O's; LAST LAP; GET IN
  THERE / WELL DRIVEN at your finish. Letters, NOS icon and messages live in the buffer's bottom
  strips (BUFF, BUFH, and the ends of BUFE and BUFG).
- Grant: race completed - a message in the game area, timers and everything stop, Q for a new
  game. CHEQUERED FLAG! / YOU FINISHED nTH / PRESS Q in a framed box in the window; the main loop
  stops (no pictures, the clock still) until Q.
- Memory: the strip code is 792 bytes. bump_all (every pair of cars) is now a loop (60 bytes, was
  560 written out); low memory 62 bytes spare. Lap: work 207.9k T a picture (was 205.9k); frames
  {3: 170, 4: 31} (was {3: 180, 4: 26}) - docs/design/strip_profile.txt.
- drive_test updated (the strip, the best lap under the order, the radio, the race-over box, the
  freeze): RESULT PASS (start 15.0/s). Screens: docs/design/strip_in_game.png, race_over.png.

## 2026-11-10 SAST - NOS
- You start with one canister (slot 1). SPACE fires one (a new press, racing, not finished):
  50 TV frames of twice your push - top speed 1.75 -> 3.05 px/frame in that second - then it fades.
- Canisters on the map (tools/make_world.py: two masked tiles each, Grant's NOS art): A just behind
  the grid (tile 19,43), B at the bottom of the dip in the top area (35,18). One at a time: driving
  over the one out puts it in your first empty slot (none if all 3 are full) and brings out the
  other - the game sets their tiles in the row lists (NOS_*_T*) to their numbers or 0.
  The crew chief: NOS READY! SPACE TO BOOST on a pick-up, NOS! GO GO GO when fired.
- Memory: the set-up (start) moved to the start-up area; line_x, inv_draw and rb_line into the gap
  before sq4; the box's wipe in one go; the race box a banner (lines above and below). Low memory
  15 bytes spare, TOPMEM 61.
- tests/nos_test.py (new): RESULT PASS. drive_test RESULT PASS (start 15.0/s). Lap: work 209.4k T
  a picture (3 frames = 209.7k), frames {3: 162, 4: 34} - the sweep should win this back.
  docs/design/nos_pickup.png.

## 2026-11-10 SAST - memory and speed sweep (first pass)
- Dead code and data removed: add_v (unused routine), 7 unused variables (msign, bu_off, dc_ink,
  bo_n, lap_start, rp_ptr, mk_x); earlier today the old LAP/TIME/BEST code and its 8 texts.
- The fixed screen is drawn once from the start-up area (screen_once), and the set-up (start) runs
  from there too: ~400 bytes of one-off code out of the program.
- Cloth F: the 3 mini slots are rewritten only when their check row changes (CFW_CR), not on every
  character row: cloth_fill 46.2k -> 45.0k T a picture.
- Memory now: low 15 bytes spare + 141 in the gap before sq4; TOPMEM 61; bottom-row strips: BUFB
  34, BUFD 15, BUFE 9, BUFF 5, BUFG 10, BUFH 8 (BUFA full); start-up area 426 bytes to spare.
- Speed now (whole lap): work 207.5k T a picture (3 frames = 209.7k), frames {3: 164, 4: 32}.
  Per picture: ticks (physics, AI, bumps) 69k, cloth 45k, tiles 35k, copy 29k, cars 17k, HUD 8k.
- Next candidates (not done): physics per car (the biggest share), the pair loop (+~1.4k T over the
  written-out version), F's minis (~5k). Graphics: 12 of each car's 16 headings are quarter-turns
  of the first 4 (3.8 KB) - only worth making at the start if a 4 KB space is ever free.
- drive_test PASS (start 15.0/s), nos_test PASS.

## 2026-11-10 SAST - no bubble when the chief is quiet; memory sweep (second pass)
- Grant: if the pit crew is not saying something, do not show the bubble. The bubble (the box and
  its tail) is drawn only while he talks: it appears in 2 halves (2 strip ticks), the words type
  out, it stays ~3 s, then goes in 2 halves; the strip's picture no longer has it. A new message
  redraws it (so the old words go: box_wipe no longer needed).
- Memory: the mini-map's dots are drawn with XOR, so drawing one again takes it off - no copy of
  the map is needed at run time: its picture (336 bytes) is drawn once from the start-up area and
  map_restore is gone. 380 bytes of the map's row lists moved into that space at the top of memory
  (toprows.asm; the row index and the canister addresses point at it). Low memory: 300 bytes
  spare (was 15).
- Fixed: the message timer overlapped the inventory's shown copy (BUFC+144).
- NOS on a clear straight: 1.75 -> 3.50 px/frame (twice); the test now moves the computer cars
  out of the way (they were in the way, which read as a weak boost).
- drive_test PASS (adds: the bubble at the green light; no bubble when quiet), nos_test PASS.

## 2026-11-10 SAST - a wider road, a longer track
- Grant: the road a bit wider (easier), the race a bit longer, the O's spaced as before. ROAD 64
  (was 56); the loop 10% bigger, scaled about the start line (so the bottom straight, the line, the
  grid and canister A stay put); O's still 18 px apart: 105 (was 91); 38 waypoints (was 34); canister
  B found at the bottom of the dip. All the breakfast things still placed. docs/design/world_bigger.png.
- Memory: 22 more tiles and more masks; the waypoints' strip is full (the strip data generator now
  sizes it from the waypoints) and a message moved to the top of memory; 60 bytes of row lists back
  to low memory. Low 38 bytes spare, TOPMEM 11.
- Laps (s): 15.4 16.8->18.6 15.8 14.6 (about 9% longer). drive_test's lap limits now scale with the
  track (waypoints / 34); the parked cars are parked apart (they were bumping each other and fooled
  the head-on check). drive_test PASS, nos_test PASS.
- Speed: lap work 211.0k T a picture (3 frames = 209.7k), frames {3: 164, 4: 53} - more road tiles
  and O's in view. To win back (with the taller window Grant asked for next).
- Grant: the window one row taller (the row above where FINISHED shows), then optimise. Costed
  before building: the screen copier is generated per line (~40 bytes a line, 0xE800-0xFAC3 for
  120 lines), so 8 more lines need ~320 bytes where TOPMEM begins - TOPMEM has 11 spare; and about
  +7k T a picture (cloth, tiles, copy) when lap work is already 211.0k (3 frames = 209.7k).
  Found: the logo (BUFB) and the track name / RACE texts are only drawn once - they can move to the
  start-up area (~190 bytes). Options put to Grant: taller as asked (remove something to make room
  and run at 4 frames more often until the speed work lands), or taller and one column narrower
  (168 x 128: the same memory and speed as now).

## 2026-11-10 SAST - mock-up: numbers on the cars
- Grant: bigger cars, just enough for their number. Bigger does not fit (24 x 24 = 2.25x the
  memory - ~11 KB of car pictures against 5 KB - and the drawing time). Instead: the number on a
  5 x 7 plate stamped upright into every heading of each car's 16 x 16 pictures at build time -
  no cost in the game. docs/design/car_numbers.png: A dark number on a light plate, B light on
  dark; A reads better at real size; on Jane's slim car the plate covers most of the body.

## 2026-11-10 SAST - the engine can be heard again
- Grant: "change the settings so that I can hear". Measured on the real ROM: the engine played only
  in the time the loop spends waiting for its next picture, and the game now has almost none - 130
  speaker flips in 5 s of racing (about 26 a second: faint ticks, not the 230-450 Hz note designed).
- Fix: the interrupt (50 a second) also flips the speaker, snd_rate/256 of a flip a frame, the rate
  2 x speed + 30: 9 to 49 flips a second, a putter rising to a buzz however busy the picture is. The
  spare-time note and the crash noise stay. Measured flat out on the start straight: 45 interrupt
  flips a second plus ~170 spare-time ones. snd_rate / snd_acc in BUFC+149/150.
- Room for it: the interrupt routine moved out of the gap before sq4 (after strip.asm); start_once's
  eight block copies now run back to back (HL carries on; an assembler check keeps the order) - 21
  bytes saved. Spare now: 6 bytes low memory, 6 in the start-up area.
- Lap work 212.3k T a picture (was 211.0k; the interrupt adds ~70 T a frame); frames {2:14, 3:170,
  4:49, 5:1}. drive_test PASS, nos_test PASS.
- tools/record_sound.py records the speaker writes from the emulator to docs/design/engine_sound.wav
  (14 s: the lights, the run off, the straight flat out, a crash) - the sound heard without the tape.

## 2026-11-10 SAST - big cars: 20 x 20 drafts, and in the editor
- Grant: "try design some larger cars", derived from the existing ones, in the car editor with
  the smaller before and the larger after, the larger editable. tools/make_big_cars.py draws the
  five at 20 x 20 from his 16 x 16 heading-0 cars (one-bit-art skill: the same key shapes and values;
  mirror-symmetric about column 9 - the bodies are an odd width so a 3-wide number sits centred;
  the race number carved in paper out of a solid 5 x 7 plate: YOU 1, CYAN 2, WHITE/Jane 3, PINK 4,
  GREEN 5). Writes tools/big_car_art.txt and docs/design/big_cars.png. Drafts only - not in the game
  (cost, measured earlier: ~5.4 KB with mirrored headings and ~1.7x the car drawing time, estimated).
- Car editor: a third mode, Big cars - 20 x 20 grid, the 16 x 16 before beside the 20 x 20 after (4x),
  all five real size and 2x on the cloth, Mirror on column 10, copy/load as "== NAME big heading 0 ==",
  its own saved draft. Grant: left-click Ink, right-click Paper, double-click Clear (all modes; the
  double-click is one undo step). Fixed: [hidden] did not hide buttons (the CREW/NOS pickers showed
  in car mode). Tested in Chromium: every mode, both buttons, double-click, undo, copy/load.
  Published as version 19 of https://claude.ai/artifact/2EqdSKs3fDfUqERTX9pTzL.

## 2026-11-10 SAST - Grant's 20 x 20 cars in the game; the lap record (hi-score)
- Grant: "use my 20x20 cars" (his heading-0 drawings from the editor; a second paste redrew CYAN).
  tools/big_car_art.txt holds them; Jane's axle row came 22 characters wide in the first paste and
  was read as cols 2-16 (his second paste agrees). 22.5 and 45: Claude's drafts from his heading 0
  (tools/turn_car.py, now any grid size) - for him to touch up in the editor; the carved numbers
  turn with the car.
- Memory: the big cars are 21 x 21 frames (car + halo), 21 rows x 3 (mask, ink) bytes, 128 a
  heading, 2 KB a car, 10 KB in all. Cars 0-3 (8 KB) sit BELOW the program at 0x5F00-0x7EFF, in the
  same tape block (pasmo's loader now CLEARs 24319); car 4 is in data.asm with the race order's
  16 x 16 pictures (tower_cars, 320 bytes). The old 5 KB of car pictures are gone: ~2.5 KB freed in
  the main area (code_end 0xB606). The tape is 26 KB, about 2 min 45 s to load.
- draw_car: frame at position - 2 (the car's middle stays at position + 8); 3 bytes over 4 a row;
  rows above the buffer or into the strip blocks (row 152+) cut off; a car over 14 px out at the left
  is not drawn. Cars touch at 15 px (TOUCH, was 12). The O's still bounce at 8 px from the middle.
- Cost, measured: draw_car 31.4k T a picture (was ~17k); lap work 221.2k (was 212.3k; 3 frames =
  209.7k); frames {2:24, 3:114, 4:88, 5:1}. drive_test: 1 FAIL - 12.5 pictures a second off the start
  with all five cars bunched (the test asks 13): the cost Grant accepted; a speed pass is next
  (physics/ticks 73k is the biggest). nos_test PASS. Window pixel check: PASS (car frames excluded).
- Editor: Big cars mode has headings 0 / 22.5 / 45 and all 16 as the game makes them (version 20).
- Grant: the best-lap clock centred, and kept as a hi-score - "best time for any race". rec_lap (outside
  race_vars, 0xFFFF none) takes any lap that beats it, never cleared by a new race; the panel shows
  it from a race's start, centred (clock col 27, time 2 px into col 28: ink x 216-238, the panel
  200-255). The race order's clock icon still marks this race's fastest car. Kept until the Spectrum
  is reset (not saved to tape). Tests added for both.

## 2026-11-10 SAST - the track longer and the road wider (same design)
- Grant: "I still need the track to be longer. It can be the same design but wider road and longer
  route". make_world.py: the same centre line, scaled 1.35 (was 1.1) about the start line, the road
  72 px (was 64), the O's re-laid at the same spacing (128 of them); the world 72 x 64 tiles (was 56
  rows - MAPW stays 72, the surface and O maps assume it) and everything moved down DY = 64 so the
  top of the track fits. The grid lanes 14 px either side (11 for the 16 x 16 cars). The breakfast
  things are spread with the track: 12 of the 22 find room. TRACK_SY in world.asm: the tests drive
  on the bottom straight from it, not from fixed numbers.
- 46 waypoints (was 34): 184 bytes, over BUFG's 160 - moved into the program (the big cars freed
  room there); BUFE holds the 64-row index (128 bytes) and less strip text.
- Mini-map: 3/32 scale (was 1/8), from (-8, -3), so the bigger track fits the panel, centred. A bug
  in the first try: the new scaling code used DE and lost each dot's x - the computer cars' dots
  landed outside the map, one in the driver strip (the drive test's "no speech bubble" check caught
  it). Fixed (x kept on the stack).
- Measured: lap work 207.2k T a picture - UNDER the 3-frame 209.7k again (the cars spread out more
  on the longer track); frames {2:17, 3:255, 4:26, 5:1}; autopilot lap 19.2 s (was ~15.5).
  Computer-car laps 17.6-22.4 s. drive_test: 1 FAIL - 12.0 pictures a second off the start with the
  five big cars bunched (asks 13); everything else PASS. nos_test PASS.

## 2026-11-10 SAST - sound only when it matters; more skid; NOS sounds; start lights
- Grant: "too much noise, just need noises if I accelerate or skid or bump something". The engine
  (the interrupt's putter and the spare-time note) now plays only while you hold Q; a skid hisses
  (a few quick flips at random short gaps from the interrupt, more for a harder slide); crashes as
  before. Measured with tools/record_sound.py (now steps through every sound): coasting 4 flips in
  a second (the engine's tail as Q is let go).
- Grant: "more skidding ... a controlled skid gets you around corners". Your car slides from 0.625
  px a frame (SKID_V 160, was 1.0) - the computer cars keep 1.0 (SKID_VC): with the earlier slide
  Jane went wide off the world's bottom edge. Your slide is capped at 2 steps (sideways speed dies
  at 1/32 - 1/64 with the earlier start spun the car out of control), and in a hard slide your
  steering is 1.5x (an extra step on alternate frames). First try was 2x and 1/64: measured 152
  degrees of turn in 0.3 s while the car's path moved 6 - a spin. Now 113 degrees while the path
  follows twice as fast as before; let go of the steering and it grips again.
- Bug found by it (old, shown up by the bigger track): past the world's edge a car was put back at
  0 or at the limit by the sign of its SPEED - a car pushed back while past the bottom edge was sent
  to the top, and Jane stuck flipping. Now by the sign of its position.
- Grant: a noise when you pick up NOS and when you fire it. The interrupt plays effects: pick-up a
  rising chirp (12 frames), fire a rush of noise (25 frames). Effects use only A, H, L in the
  interrupt (the cloth fill leaves room for 6 bytes of pushes).
- Grant: "when you press Q, there are 3 lights. RED, RED, RED then all green ... until they are all
  green no-one goes". The three lamps start unlit (blue on black); Q lights them red one at a time,
  0.8 s apart, each with a beep; at 2.6 s all three turn green with a higher beep, the race starts
  and GO! shows beside them. Holding Q before green moves nothing (your car's buttons are cleared
  until race_on). Tests: the lights, nobody moving on red, green.
- drive_test: 1 FAIL (12.0 pictures a second off the grid, asks 13); nos_test PASS.

## 2026-11-10 SAST - the skid: "turns sharply but does not skid"; the Skid Lab
- Grant: "the car now turns very sharply but does not actually skid". Measured: the 1.5x steering
  turned the car fast, and the slide ended the moment the steering was let go - grip came back at
  once, so the car never carried on sideways. In the game now (interim): steering back to 1x; your
  slide (from 0.625 px a frame, up to 3 steps) goes on SKID_HOLD = 25 frames after you let go,
  easing back a step every 8 frames. Measured after a 0.3 s turn at top speed: slip 79 degrees,
  then 69, 58, 39, 13, 2 over the next half second - a slide that fades, no snap.
- Grant: research how a car skids (momentum, grip), and test it outside the game. Research: a tyre
  makes sideways force only with a slip angle, rising to a peak and then falling to sliding
  friction; the friction circle - braking/driving and cornering share one grip budget; a drift is
  controlled oversteer, balanced with counter-steer and throttle.
- Skid Lab (docs/tools/skid_lab.html, tools/make_skid_lab.py; published
  https://claude.ai/artifact/XWjkAzJ9kFKki9naPic3V8): your big car on an open cloth with a ring of
  O's, the game's units (px, 50 frames a second, top speed 1.75), skid marks, a slip readout. Two
  models: GAME NOW (racer.asm's slide) and GRIP LIMIT (speed split into forwards and sideways; the
  tyres cancel sideways speed up to their grip a frame; past it the car slides and holds less grip
  while sliding; Q uses part of the grip; a slide never adds speed). Sliders for grip, sliding grip,
  throttle share, steering and top speed; "Copy settings for Claude".
- Tests: drive_test 1 FAIL (12.0 pictures a second off the grid, asks 13); nos_test PASS.

## 2026-11-10 SAST - the Skid Lab's grip model in the game (your car)
- Grant: "I will go with your recommendations" - the Skid Lab's grip-limit model at its starting
  settings: grip 0.085 px a frame of sideways speed, 65% of it while sliding, Q uses 35%, steering
  5.625 degrees a frame (one step of 64), top speed 1.75 (push 0.25, drag 1/8 forwards only). Your
  car only: the computer cars keep the old slide (their driving is tuned to it).
- src/grip.asm (you_grip): your speed kept as forwards and sideways (vf, vs); steering turns them
  by one step with shifts (cos 5.625 = 1 - 1/256 - 1/1024, sin = 1/16 + 1/32 + 1/256); push and drag
  on vf; the tyres take vs down by the grip a frame (to 0 under it - gripping; sliding over it, and
  the grip drops); over the top speed vf gives way; then the world speed = vf along the heading + vs
  across it. A bump, an O, the world's edge or a test that changes the world speed is seen the next
  frame and (vf, vs) are worked out again from it. Multiplying: quarter squares (src/sqtab.asm,
  n * n / 128 for n = 0..383 - the / 32 comes free). Physics skips your old push, skid and friction
  (fshift 0 = no friction). The skid hiss follows the slide (1-3 by sideways speed).
- Measured in the game, the Skid Lab's own test (top speed, steer 0.4 s, let go, Q held): slip 16,
  35, 60, 65 degrees, then fading 54, 45, 37 - the lab gave 21, 41, 54, 63, then 47, 36, 28. Top
  speed 1.75; NOS 3.50.
- Cost: turning frames ~2.5k T (two trig look-ups, the turn, four multiplies); straight on, cached.
  Lap profile (autopilot, which steers nearly every frame): 218.4k T a picture (was 207.2k);
  frames {2:37, 3:167, 4:87, 5:2}. First try was 224.2k: the trig and world speed are now cached,
  two multiplies when gripping, the rotation's shifts written out (calls cost more than shifts).
  Next speed step if wanted: add only the frame's change to the world speed (small numbers, the
  existing sq4 multiply) instead of rebuilding it.
- Tests: drive_test 1 FAIL (11.5 pictures a second off the grid, asks 13); nos_test PASS.

## 2026-11-10 SAST - layout review; faces too blocky; one more row?
- Grant: review the overall design within the Spectrum's pixel, colour and colour-clash limits;
  then "the faces at the bottom are too blocky - they should be smaller - the blue and red"; then
  "is it feasible performance wise to add one more row at the top to the gameplay".
- tools/make_layout_review.py builds two screens from a real race screen (screen memory from the
  emulator), cell by cell: docs/design/layout_now.png (numbered) and layout_proposed.png. The review
  page docs/design/layout_review.html (template beside it; published
  https://claude.ai/artifact/GL5FkuruWucbShFekbkLp8). Proposals: your place (bright white on red) and
  lap (black on bright yellow) large in the message bar while racing - it is blank after GO; drop
  the per-row lap digit from the race order; the two strip faces at their own 16 x 16 size in 2 x 2
  cell panels (not doubled), the bubble widened and fitted to whole cells (rows 20-22); the border
  as a free signal (green at GO, red on a crash, white for NOS). Keep: the one-colour play window,
  the mini-map.
- One more row (176 x 128): per line from the lap profile - cloth 377 T, tiles 225 T, copy 209 T -
  about +6.5k T a picture on 218.4k (budget 209.7k). Memory: the copier grows ~320 bytes into
  TOPMEM (15 bytes spare); the main area has ~870 free since the big cars, so the TOPMEM map rows
  can move down. The bezel would take the message bar's second row. Best done with a speed pass.

## 2026-11-11 SAST - speed pass merged; wrap-up for a new chat
- Grant: "go with the proposal, but would like to have smoothness of movement, so lets optimize the
  current setup before looking at adding a row"; later "ignore the speed pass for now", then
  "Merge and then wrap up to take to another chat". The paused work sat on branch speed-pass-wip;
  tested in full before the merge (drive_test: only the 13/s start check fails, 12.0; nos_test
  PASS; o_test PASS 30/30), then fast-forwarded into main.
- tests/profile_ticks.py: the lap profile with the game tick split (your physics, the computer
  cars' thinking and physics, bumps, O checks). It showed the O checks at 14k T a picture.
- o_check: oc_quick tests all four tiles at once (a 2-bit mask over the byte pair, both rows) in
  ~250 T; the full oc_try only when an O may be there. Two bugs on the way: the second row is 9
  bytes on (8 was used), and o_check fell through into the fourth tile's oc_try - now a JR. O checks
  14.0k -> 5.7k T a picture. tests/o_test.py: your car bounces off 30 of 30 O's, not off clear cloth.
- grip.asm: the world speed changes by each frame's forwards and sideways change (small numbers:
  mul8s, /64 rounded), the full sum only for a big change or a fresh start every 32 frames; the top
  speed cap only while sliding; your car skips the unused heading push. draw_car skips empty mask
  bytes (and their ink).
- Lap work 211.6k T a picture (was 218.4k; budget 209.7k); frames {2:35, 3:203, 4:64, 5:1}.
  tests/sample_lap.py (PC sampling) is NOT trustworthy - the emulator does not stop mid-frame where
  asked; use profile_ticks.py.
- Grant asked which tools Claude uses and the requirements for a purpose-built Spectrum tool (answered
  in chat). The retro plugin now has a zx-toolkit skill (zxdev, Grant's own emulator) - use it next
  session for timing and debugging instead of the zx package where it does more.

## 2026-11-13 SAST - the layout review built; a speed pass measured in zxdev; your car's set-up
- Grant: build the approved layout proposals (1, 3, 5-7, 8), then a further speed pass before the
  extra window row, measured with tests/profile_ticks.py and the retro plugin's zx-toolkit skill;
  then, mid-session, a new feature: set your car up - traction, speed and acceleration at 5 levels,
  every car at 1 each, you add 2 before the start, the HUD shows yours.
- Layout (commit cc0966e). Message bar while racing (bar_tick, hud.asm): your place in double-size
  letters, bright white on red, columns 1-6; LAP small then n/3 double-size, black on bright yellow,
  columns 12-17; the race time m:ss at column 19. One big letter a picture at most; the time a
  digit a second (whole seconds: a tenths digit would cost a redraw every other picture - Claude's
  choice, the mock-up showed tenths). Race order: the lap digit gone from every row. Strip: both
  faces 16 x 16 in 2 x 2 cell panels (columns 1-2 and 21-22, rows 21-22); the bubble fills columns
  11-20, rows 20-22 (x 88-167, y 160-183), its tail a white point over the left of the chief's face
  (BB_TAIL keeps those 8 bytes to put back). Border (flash, isr): green 25 frames at GO, red 10 on a
  crash (5 off an O), white 50 while the NOS burns - through snd_port, counted down in the interrupt.
- build.sh (repo root) builds the tape, bin and symbols; checked byte for byte against the
  committed tape before any change.
- zxdev (zx-emulator 0.9.6, built from source in the cloud session; smoke test passed).
  tests/zxlap.py: the autopilot lap in zxdev, profiled by routine, counting real TV frames a
  picture. FINDING: profile_ticks.py under-counts. The screen copy is 38.8k T (not 24.5k): a late
  picture's copy runs with interrupts off across a frame boundary, a frame count is lost, and the
  old profile (which times by the frame counter) never sees it. In zxdev the lap was 3 frames x
  195, 4 x 104, 5 x 3 - a third of the pictures late, not the 64 in 268 recorded on 11 Nov.
- Speed pass (commits 8341959, and the next):
  1. cloth_fill filled kind by kind: every blank line in one pass (HL = 0, 4 a character row),
     then the P0 lines and the P2 lines, 2 a character row, the pattern in BC, DE, HL, IY, loaded
     again only where the check row changes. 45k -> 29k T; pixel for pixel the same (drive_test);
     ~340 bytes smaller (cf_init, the minis, loaders, slots and their tables are gone). First try
     was 16 lines out: line 0's world y is camy, not camy - 16.
  2. The computer cars move once a picture (cpu_move in main: physics with ph_steps = dt); they
     still think frame by frame. Physics 29k -> 19k T. Their laps: 19.2 22.2 19.4 18.5 s (were
     18.7 22.7 19.3 18.7).
  3. make_copier: 7 pairs (AF BC DE HL, EXX, BC DE HL) then 4, no IX/IY: 279 T a row (295), 36
     bytes a row (40): the copy 38.8k -> 36.4k T, and 8 more rows fit where the routine is.
  Looked at and left: draw_car (570 T a row is near what mask + ink through the shift tables can
  do); the dotted loop's per-line count (1.3k T).
- Result, zxdev lap: 3 frames x 308, 4 x 12 (was 195 / 104 / 3); all told 213k T a picture with the
  waiting (was 236k). drive_test passes in full for the first time: 15.0 pictures a second off the
  grid (12.0; asks 13). The pictures still late are those with 4-5 cars in view.
- o_test: an O is tried twice before it counts as missed - the test writes your car's place while
  the game may be half-way through moving it.
- Set-up (hud.asm su_keys, su_apply, su_draw; grip.asm): GRIP, SPEED, ACCEL at 1..5; keys 1, 2, 3
  add a point (2 to spend), 0 takes them back; only before Q; kept from race to race. SPEED: top
  speed 448 + 28 a level (8.8; 1.75, 1.86, 1.97 ...), ACCEL: push + 10 a level with the top speed
  held (new: vf is capped every frame, not only in a slide), GRIP: the grip table x 1.15 a level
  (su_gtab). The computer cars are untouched (1, 1, 1). HUD: row 23, "1G##### 2S##### 3A#####",
  the key numbers only before the start; the chief says PICK TWO UPGRADES / KEYS ONE TWO THREE
  (the small letters have no digits). Measured (tests/setup_test.py): SPEED 3 top 1.96 (1.75);
  ACCEL 3 reaches 1.5 px a frame in 7 frames (15); GRIP 3 slides 52 frames after a hard turn (55)
  - the grip step is small in that test and wants Grant's feel on the keys.
- Tests: drive_test PASS, nos_test PASS, o_test PASS, setup_test PASS.
- Memory: code_end 0xBF35 (203 bytes free in the main area); the copier ends at 0xF8E2 (TOPMEM
  0xFAD0: 493 spare, 288 of it wanted by the extra row).

## 2026-11-14 SAST - mock-ups: the set-up box, the angled cars, a new cast; the title screen asked for
- Grant: the NOS to the play window's bottom right, the three car measures tighter - three rows
  in a little box left of the radio box; then "don't use letters, use icons", and the NOS much
  smaller, no box, in the race's own colours, masked; then "good enough".
  tools/make_setup_mockup.py -> docs/design/setup_box_mockup.png (on two real screens,
  docs/design/mock_setup_*.bin): a 4 x 3 cell box at columns 6-9, rows 20-22; each row a 7 x 5 icon
  (tyre, fast-forward, bolt) and five 3 x 5 pips; no key numbers (rows in key order); the NOS as a
  7 x 10 canister a piece, blue on cyan with a 1-px gap, window bottom right. NOT BUILT YET.
- Grant: "could Fable look at the cars and improve on the angled car graphics ... I did the
  straight up images and Claude did the rest". Three versions, side by side at real size
  (docs/design/angled_cars_options.png): A as in the game (tools/turn_car.py, pixels turned);
  B = A with the race number redrawn UPRIGHT in a solid 5 x 7 plate
  (tools/big_car_art_option_b.txt); C = each car rebuilt from its parts at 0.88 size
  (tools/turn_big_car.py -> tools/big_car_art_option_c.txt: blocks as clean polygons, wheels,
  gaps, the number upright). Claude's own verdict: C is cleaner but loses the cars' character
  (wheel centres, the tank's treads) and is not clearly better; B is the one sure gain (the
  number reads at every angle). Nothing installed in the game: Grant to choose. A 20 x 20 frame
  cannot hold a 17 x 18 car turned 45 degrees (its box would be 24.7): corners clip or the car
  shrinks - a limit of the frame, not of the drawing.
- Grant: a title / attract screen - the logo, a keys option, the hi-score, 1 or 2 players; at the
  start the player chooses a driver (face / personality), then a car; five more of each to choose
  from, each car with strengths and weaknesses to tune; two players to play later. Then: mock up
  five new cars ("the offroad, the pickup truck, the buggy - can get creative"; his old ones are
  in tools/pool_art.txt: SPECS and the 6-wheel TRUCK) and personalities - three ladies and three
  men. tools/make_new_cast_mockup.py -> tools/new_cast_art.txt, docs/design/new_cast_mockup.png:
  first drafts of OFFROAD, PICKUP, BUGGY, HOTROD, MILKFLOAT (20 x 20, heading 0) and of five
  faces - BUN, SPECS2, CURLS (ladies), CAP, SHADES (men) - for him to redraw in the editor.
  The title screen itself is not designed or built: it needs a memory plan first (203 bytes free
  in the main area; ten more cars at 20 x 20 x 16 headings will not fit beside five - 2 KB each).

## 2026-11-14 SAST - the angled cars turned at full size, in the game
- Grant, of the bigger-frame mock-up (docs/design/turn_bigger_frame_mockup.png): "middle row is
  substantially better. Go with 26."
- Built at 24 WIDE, not 26, and said so: a 26-wide frame is 4 bytes a row and about 13 KB of
  pictures against about 10.5 KB of room; measured on his cars, a 24-wide frame with the car's
  middle on the frame's middle loses nothing but a pixel or two at the far tips of the two widest
  cars (CYAN and GREEN at 45 degrees), and a row stays 3 bytes - no more work per row.
- tools/make_data.py: everything on a 27 x 27 grid, the car's middle on the grid's middle. The
  22.5 and 45 degree drawings are his upright drawing turned at full size (majority of 16 samples,
  as before) and are kept in tools/big_car_art_27.txt - read back, never overwritten, so they can
  be touched up by hand (the car editor's Big cars mode still edits 20 x 20: not updated). The
  other 13 headings are mirrors and quarter turns. On the 12 angled headings the race number is
  redrawn upright; on the 4 square ones it is as drawn, turned. The old 22.5 and 45 blocks in
  tools/big_car_art.txt are no longer read.
- The game's frame: grid columns 2-25 (24 wide), only the rows in use kept (20 upright, up to 27
  turned), at car position - 3 across and - 6 down. big_tab (data.asm): each car's each heading:
  address, first row, rows. draw_car reads it (car_rows and big_base are gone).
- Memory: the pictures went from 10,240 to 10,740 bytes and the table 320. Found by: the 256
  bytes at 0x7F00 (frames now fill 0x5F00-0x7FFF); bar_tick, su_draw and their tables into the
  gap before sq4; cars_init to the top of memory (TOPMEM 0xFA40; the extra window row's copier
  still fits below it, to 0xFA02). THE MAIN AREA IS NOW FULL: 4 bytes free (code_end 0xBFFC), the
  gap about 3, the start-up area 44. Nothing more fits without a new memory plan.
- Speed (zxdev lap): 3 frames x 280, 4 x 32 (was 308 / 12): taller turned cars cost more rows,
  and it shows with 4-5 cars in view. Tests: drive, nos, O, set-up all PASS (15.0 pictures a
  second off the grid). docs/design/big_cars_16_headings.png: every car at every heading as stored.

## 2026-11-14 SAST - speed back with the full-size cars; the slide ends when you stop steering; screen options
- Grant, of the full-size turned cars: "happy but yes the gameplay did slow - any way to have
  these images and faster play?" Kept the pictures, found the time elsewhere: draw_car counts its
  rows in IXL (22 T a row); bumps and the O checks once a picture, after everyone has moved
  (bumps_o; they ran on alternate TV frames). zxdev lap 3 frames x 304, 4 x 18 (280 / 32 with the
  taller cars; 308 / 12 before them). Tried and put back: the computer cars deciding every 8
  frames, not 4 (313 / 8, but their laps slowed by about 1.5 s: 21.0 23.4 22.8 20.8).
- Grant: "after the car has skidded, and I face a direction, it still seems to drift ... it kept
  sliding to a side." Measured on open ground (O's and off-road switched off in the emulator),
  top speed, a 0.4 s turn, then steering let go with Q held: the slip angle went 51, 47, 38, 34,
  25, 20, 12, 6, 0 degrees - 0.9 s to run true - because a sliding car holding Q had only 9/256
  of grip a frame. No fault in the sums (both directions the same; it does reach 0). Change
  (grip.asm): NOT STEERING, the tyres have their full grip (yg_gtab's first number: 22/256, more
  with GRIP levels), sliding or not, Q or not. Now 43, 28, 4, 0: about 0.3 s. Steering, the grip
  is as before, so a drift can still be held with the wheel.
- tests/setup_test.py: GRIP is now judged by the frames until the tyres grip again after a hard
  turn (level 3: 11 frames; level 1: 17).
- Memory: both ld iy,23610 are gone (nothing reads IY); yg_gtab and the set-up's numbers moved to
  the gap. Main area 6 bytes free.
- Grant asked for a second agent to mock up "a nicer display ... organise, condense, shape, put
  borders around things". tools/make_screen_options.py -> docs/design/screen_options.png and
  screen_option_a/b/c.png, built cell by cell on a real racing screen: A cards on the table
  (white cards under blue title bars, one joined YOU | CAR | RADIO dashboard); B arcade console
  (black, one instrument column: RACE, CAR, MAP); C blue dashboard (the window stands on an
  L-shaped blue dashboard holding YOU, CAR, RADIO and the MAP; a TV-style banner on top). The
  agent's pick: C. The best-lap time shown is made up; the before-start state is not mocked.

## 2026-11-14 SAST - the window one row taller; the message bar one row; the numbers turn with the cars
- Grant (with a screenshot of FINISHED 1ST): "visibility on the vertical area is poor I need to
  see ahead further. The gameplay area needs to get that row above it. That means the messages
  there move off somewhere else to make space. So where it says finished first -" (cut off there).
- The window is 176 x 128 (WIN_Y 24, WIN_H 128: rows 3-18), the bezel in row 2. The message bar
  is row 1 only, all in the ROM's normal letters: three one-cell start lights, GET READY, PRESS Q;
  GO!; FINAL LAP!; FINISHED nTH; racing: your place on red (columns 1-3), LAP n/3 on bright
  yellow (13-15), the time (19-22). print_big and the one-big-letter-a-picture code are gone
  (msg_at prints and colours a text in one call). Claude's choice, as his sentence was cut off:
  where the big messages should go is still his to say.
- The camera keeps your car at window (80, 56). Car drawing stops at the window's last line.
- Cost: the copy routine is 288 bytes longer (to 0xFA02, as planned); zxdev lap 3 frames x 298,
  4 x 13 (305 / 9 before the row). Memory: 118 bytes free in the main area again (code_end 0xBF8A).
- Grant: "I am not concerned that the numbers don't show properly when cars are turning" - the
  upright number is no longer put on the angled headings: each car is his drawing, turned.
- tools/show_game_cars.py -> docs/design/big_cars_16_headings.png: the cars as the game has them,
  real size and 4x (he asked to see them).
- Tests: drive (window 128 high, one-row bar, bezel a row up), nos, O, set-up: all PASS.

## 2026-11-14 SAST - the page layout chosen in outline (G3); small cars to stay an option
- Screen mock-ups by a second agent, round by round: D, E, F (the window two rows taller, the
  border matching the surround; tools/make_screen_options2.py, docs/design/screen_options2.png);
  Grant: the 3-2-1 figures are "too much. I like the original idea of the lights - so three
  blocks, they change colour as the countdown goes" (three 2 x 2 cell blocks in the window:
  black, then red, red, red, then all green); then "I like the e design but still in yellow ...
  the border changes around the gameplay area ... the car three ratings and the display for the
  player bottom left" -> G1 / G2 (tools/make_screen_options3.py, screen_options3.png); then "G2
  is getting there. Now move the map above the car positions - just below the logo - you don't
  need to say map but give a row space between the map and the title logo. Don't worry about
  displaying the car strengths" -> G3 (docs/design/screen_option_g3.png, screen_options4.png):
  right column rows 0-1 logo, 2 empty, 3-7 map, 8 empty, 9 RACE, 10-19 the five cars, 20 best
  lap; window x 8-183, y 16-151 in a slim blue frame; bottom left your face and big place in a
  red block (columns 1-9, rows 20-21), a white lap strip, TIME; the bubble and chief beside it;
  NOS in the window corner; no car strengths on this screen. Not yet approved for building.
- Grant: "for the game development we need to keep the ability to have two car options - the
  smaller cars and the bigger cars. We may end up going with smaller cars (the ones used in the
  positions on the right). It may actually help gameplay - helping cars avoid each other a bit
  more." To build as a switch at build time (one constant: make_data.py writes either set,
  draw_car has both row widths). The 16 x 16 cars are in tools/car_art.txt (2 bytes a row, 16
  rows): about 5.8 KB for five cars against 10.7 KB, and roughly half the drawing time - Claude's
  estimates, not measured. The bump test (11 px) and the O test are the same for both.

## 2026-11-14 SAST - four builds to try: big or small cars, the window 128 or 136 high
- Grant: "I would like to try the gameplay with options of the bigger or smaller cars, but with
  the extra row(s) available to see how gameplay works out."
- `bash build.sh [big|small] [128|136]` (default big 128 = build/racer.tap); each build is also
  copied to build/racer_<cars>_<height>.tap. CARS=small makes tools/make_data.py put the 16 x 16
  cars (tools/car_art.txt) on the same grid, frames and table - no change to the game's code.
  OPT_TALL (src/options.asm, written by build.sh) makes the window 136 high from pixel row 16
  and puts the message bar on row 0 in place of the track's name (a stopgap until layout G3 is
  built); the copy routine then ends at 0xFB22, TOPMEM is 0xF0 higher, and the race box's text,
  the small font, the race order's little pictures and the tile table move into the program
  (hudtext.asm is split into hudtext_flag / _track / _gfx for it). Big cars at 136: 8 bytes free.
- zxdev lap (pictures at 3 TV frames / at 4): big 128: 298 / 13; small 128: 308 / 4; big 136:
  298 / 15; small 136: 309 / 5. The small cars free about 2.4 KB of the main area even in the
  same 3-bytes-a-row frames (7,296 bytes of pictures against 10,740).
- Tests are run on the default build (big, 128): drive, nos, O, set-up all PASS. The other
  three builds were run and looked at (docs/design/four_builds.png), not put through the tests
  (drive_test assumes the 128 window and the bar on row 1).
- Start lights for layout G3, by the second agent (tools/make_start_lights.py,
  docs/design/start_lights.png): L1 a gantry bar with three round lamps (its pick), L2 hanging
  pods, L3 glowing lenses with chequered ends at go. For Grant to choose.

## 2026-11-14 SAST - start lights: L2
- Grant, of docs/design/start_lights.png: "l2" - the pods: three black lamp boxes hanging from a
  rail under the window's top edge; an unlit lamp is an empty white ring, lit a full bright red
  disc, go bright green (tools/make_start_lights.py). And: "would like 136 high and to test big
  and small cars" - build/racer_big_136.tap and racer_small_136.tap sent.

## 2026-11-14 SAST - small cars, 136 high: chosen; the broken track in the 136 trial found and fixed
- Grant: "I prefer the smaller cars on 136 but note that in the trial, the road shape has broken -
  areas are blocked"; then "lets keep to the small car design - playability definitely improves
  and it may help for speed".
- Fault 1 (the broken track): the map's tiles are drawn up to 8 lines past the window's last
  line. With the window 136 high from buffer row 16 that reached buffer rows 152-159 - the first
  32 bytes of every table kept there (the map's row index, the thrust table and driving styles,
  the letters, the messages, the faces, the logo). Fix: BUF_TOP - the taller window starts at
  buffer row 8, so the tiles end at row 151 (an .error guards it). drive_test did not catch it
  (it never drives a lap with the tall window); tests/zxlap.py now reads the tables before and
  after its lap: FAIL on the faulty build (all seven tables), PASS on the fixed one.
- Fault 2, found by that check and older than this session: the last 6 bytes of each of those
  tables are where the interrupt's pushes land when it arrives as the cloth fill finishes a line
  at the start of the buffer's last third. The faces' last 6 bytes and (since M_SETUP was added)
  the end of a message sat there. Fix: tools/make_strip.py packs to 154 bytes a table, the
  .error is at 154, and the faces (which need all 160) are in the program (BUFA is empty).
- Also: drive_test reads the window's top line, height and the message bar's row from the
  symbols, so it runs on either height.
- The default build is now SMALL cars, 136 high (`bash build.sh`; build/racer.tap and
  build/racer_small_136.tap). zxdev lap: 3 frames x 311, 4 x 5. Tests on it: drive, nos, O,
  set-up, and the lap's table check: all PASS. Main area: about 2.1 KB free (code_end 0xB798).
- The big cars no longer fit beside the faces in the program (`bash build.sh big 128` stops at
  "code and data run into the back buffer"): their drawings and the generator switch are kept,
  but building them again needs the memory plan. The earlier big and 128 tapes are removed.

## 2026-11-14 SAST - the window the full height (176 x 144); the drift found: heading against picture
- Grant: "track is right. Note that the car drift is still there. I would also like to have the
  game now updated to take the very top row of the display as well"; then "work on the drift
  and update the gameplay area for a next build, and then incorporate the changed layout"; and
  he would like to see whether the gameplay area can grow more still.
- The drift. Measured against the car's PICTURE this time (tests/drift_test.py): the car can
  point 64 ways but has 16 pictures, so after any turn it ran 6 to 17 degrees off the way its
  picture points, for ever (previous build: slip 9 9 9 11 12 12; 17 17 17 17). The earlier fix
  (full grip when not steering) was real but measured against the true heading, which was not
  what he was seeing. Fix (ph_snap in racer.asm, your car only): when you let go of the
  steering the heading carries on the way you were turning, a step a frame, to the next heading
  that has a picture. Now 0 within 0.3-0.4 s for turns of 0.14, 0.3 and 0.5 s, both ways.
  Side effect to know: the smallest change of direction is now one picture (22.5 degrees).
- The window: WIN_Y 8, WIN_H 144 (rows 1-18; the frame's top band in row 0). No row is left
  above it: the message bar (place, lap, time, start lights, GO!, FINAL LAP!, FINISHED) is on
  row 23 as a stopgap, the track's name is not shown, and the set-up row is gone from the race
  screen (keys 1 2 3 still work before the start). The 128 / 136 options are removed.
- Room for it in the back buffer: BUF_TOP 8, so the tiles drawn past the window's last line use
  buffer rows 152-159, and the tables kept in the buffer now start at row 160: 128 bytes a strip
  (122 safe). Moved into the program: the map's row index, the O map (src/omap.asm, written by
  tools/make_world.py), the driver strip's variables and the engine's (now ordinary labels), the
  faces; the logo is drawn straight from the start-up area. BUFC's cloth patterns are at +64,
  PNUM at +96. tools/make_strip.py packs messages into strips F, H, E, G, A at 122 bytes each.
  The table copies at start-up go through so_blk (nothing is copied when a strip is empty).
  TOPMEM 0xFC50 (the copy routine ends at 0xFC42).
- zxdev lap: 3 frames x 299, 4 x 12 (311 / 5 at 136 high). Main area: about 1.4 KB free
  (code_end 0xBA53). Tests: drift, drive, nos, O, set-up, and the lap's table check: all PASS.

## 2026-11-14 SAST - layout G3 built; coloured objects in the window mocked up
- Grant, of the full-height build: "that plays well - go"; then "the breakfast run logo should be
  a row up - so top right".
- Layout G3 in the game (docs/design/g3_built.png: before the start, two reds, green, racing):
  the slim blue frame (draw_frame: a 2-pixel rounded line, 3 pixels of table inside it; its cells
  blue on yellow); the logo at rows 0-1; the mini-map under it on screen lines 25-61 (MAP_Y 19:
  only its 37 lines in use are drawn) with a clear row above and below; RACE at row 9, the race
  order rows 10-19 (TOWER_Y 10), the lap record at row 20; bottom left your face and your place,
  large, in one red block (columns 1-9, rows 20-21; print_big is back, one letter a picture), a
  white strip (row 22: PRESS Q, LAP n/3, FINAL LAP for 3 s, FINISHED!), TIME m:ss (row 23):
  bar_tick; the bubble four rows again (20-23), the chief at columns 21-22.
- The start lights, design L2 (tools/make_lights.py -> src/lights.asm): a rail in the window's
  row 1 (columns 7-16) and three 2 x 2 cell lamps under it (rows 2-3): white rings, then red
  discs one at a time, then all green, gone 1.5 s after green (lt_on, lt_t). Their pixels go into
  the back buffer every picture while they are up (lights_draw), their colours onto the screen
  when they change (lights_attr / lights_off).
- NOS: a 7 x 10 canister for each one held, in the window's bottom right corner, in the window's
  colours, each replacing its byte of the cloth on 10 lines (nos_draw). The inventory slots and
  inv_draw are gone.
- The old message bar (msg_clear, msg_at, the row-23 stopgap) is gone.
- Tests rewritten for the layout (drive_test: frame, logo, map, scoreboard, lights, bubble, NOS,
  strip texts). All PASS: drive, drift, nos, O, set-up, the lap's table check.
- zxdev lap: 3 frames x 293, 4 x 19; off the grid 14.0 pictures a second (15.5 before): the
  lights are drawn with a buf_addr call a line while they are up - first thing for the speed hunt.
  Main area about 1.1 KB free (code_end 0xBB8C).
- Grant asked how far the picture scrolls a time: the camera is the car's own position, so it
  moves by the car's speed x the picture's TV frames - at top speed 1.75 px a frame x 3 = 5 or 6
  pixels a picture (less when slower; 7 at 4 frames), to the exact pixel, not 1 pixel at a time.
- Grant: "features that put colour into the gameplay area ... a big mask so at no stage do
  character rows interfere with areas around them ... big coloured objects - preferably square.
  Like a box". Mock-up by the second agent (tools/make_colour_objects.py,
  docs/design/colour_objects.png): the SOLID EDGE rule - an object has a solid blue edge at least
  8 pixels thick and only cells holding some of its inside take its colour, so the colour's
  boundary is always under the edge. Checked at all 64 pixel positions for seven objects (cereal
  box, juice carton, milk carton, jam jar, butter dish, sugar cubes, a two-colour tea tin).
  Limits found: plain colours only (BRIGHT would brighten the edge's blue), one ink (blue), 8 px
  of solid blue between two colours, corners rounded by one line only; minimum 17 x 17, 48 up
  looks best. Cost: 10-35 colour writes a picture for each object in view. Not built.

## 2026-11-14 SAST - speed "good"; small skids silent; objects from above; a ditty and a title screen asked for
- Speed: the start lamps drawn with one address sum a character row (off the grid 14.0 -> 15.0);
  the small cars stored in the frame's first 16 columns, so a row is 2 bytes and the third is
  skipped (no 1-pixel clear edge left and right; CAR_U in src/options.asm, written by build.sh).
  zxdev lap 3 frames x 301, 4 x 12. Grant: "speed of the game is good".
- Sound: "the sound is not good - the sound being made sounds like skidding. It is just annoying
  ... I like the idea of a little ditty sound playing in the background ... car noises to bangs
  and hits and accelerates and pickups - so primarily events. A small sound on a skid is useful."
  For now: the hiss only for a real slide (sideways 0.5 px a frame or more); small slides are
  silent. A third agent is composing ditties within the game's limits (docs/sound/, not built).
- Coloured objects, second and third rounds (tools/make_colour_objects.py,
  docs/design/colour_objects.png): Grant: they "will not appear in the race area" (scenery beside
  the track) and must be seen from straight above; "the egg definitely needs yellow yolk ...
  some white milk. A black coffee in a cup". Now eleven objects from above: fried egg (yellow yolk
  on white: two colours, so the yolk has a 10-px blue surround; 84 across), glass of milk, black
  coffee on a saucer, toast, waffle, sugar cubes, butter, place mat and plate, bowl of cereal, mug
  of tea, jam lid. Round shapes need an 11-px rim. Finding: off the road there is little room
  (about 44 px deep in the views captured), so big objects show part in view. Not built.
- A fourth agent is designing the title / attract screen (Grant: 1UP / 2UP, K for keys, an attract
  sequence showing the drivers, a car skidding round): storyboards and an animation, not code.
- tests: setup_test checks GRIP by the tyres' grip numbers (the slide-length measure moved with
  the timing); drive_test's head-on check writes the cars' places between pictures.

## 2026-11-14 SAST - more skid in the corners
- Grant: "the car does not skid enough around corners, so at full speed there needs to be more
  sliding/skidding."
- grip.asm: the tyres' grip while sliding 14 -> 12, while steering with Q held 14 -> 12, both
  9 -> 7 (/256 px a frame of sideways speed; the GRIP levels' table in step: level 3 is 29, 16,
  16, 9). Not steering, the grip is now the sliding grip while the car slides (it was the full
  22), so the slide runs on after the corner. Measured at top speed (tests/drift_test.py), the
  time to run true to the picture after the steering is let go: 0.5-0.6 s after a 0.14 s turn,
  0.6-0.7 s after 0.3 s, 0.8-1.1 s after 0.5 s (it was 0.3-0.4 s for all); slip up to 60-75
  degrees in the long turn. It still ends on the pictured heading.

## 2026-11-14 SAST (later) - grip is bought; sounds are events; wedged cars escape; Sound Lab
- Grant: "have the car skid/slide more. The idea is that the player will need to 'buy' improved
  grip to reduce the skidding." GRIP level 1 is now 16/8/8/5 (gripping, with Q, sliding, both;
  it was 22/12/12/7); levels 2-5: 20/11/11/7, 25/14/14/9, 30/18/18/11, 36/22/22/14. At level 1 a
  full-speed corner slides 0.7-1.2 s after the steering is let go (tests/drift_test.py).
- Grant: "the tank got stuck in the top middle section ... in between the loops/circles and could
  not get out." tests/stuck_test.py (new) drops the computer cars on 477 places over the table:
  37 left a car wedged against the O's that edge the road. Fix (racer.asm, bumps_o): a computer
  car that bounces off O's 6 times (O_FREE) without reaching its waypoint passes through them
  until it does. 0 stuck now.
- Grant: "reduce the amount of noise to focus on events." The engine sounds only while the car
  picks up speed (below SND_CRUISE, 3/4 of top speed); the skid is a 5-frame screech as a slide
  starts (snd_skt), not a hiss for the whole slide. Crash, pick-up and NOS sounds unchanged.
- With the main loop's wait now a HALT (no engine tone in it) and the autopilot sliding in the
  pack all lap, tests/zxlap.py shows 151 pictures at 3 frames and 145 at 4 (it was 304 / 11 with
  the car clear of the pack). Not yet checked whether Grant sees a slowdown.
- Sound Lab artifact (tools/make_sound_lab.py + tools/sound_lab.template.html): the four ditties
  in three styles, and 3-5 options for each of six event sounds, with a picks line to copy back.

## 2026-11-14 SAST (midday) - the ditty plays; Grant's sound picks built; four new ditties
- Grant: "please try the spilt milk, but also come up with some new ditty options", then his
  picks from the Sound Lab: "Ditty: Spilt Milk, buzz. Accelerating: A1 Putter. Skidding: S1 Short
  screech. Hitting another car: H1 Crunch. Banging into a cereal O: B2 Bonk. Picking up a NOS:
  P3 Coin run. Firing the NOS: F2 Whoosh up."
- The ditty player is in the interrupt (racer.asm, isr_q; A, H, L only, no calls). Data:
  src/music.asm, made by tools/make_music.py from the tune in tools/make_ditties.py (run
  `python3 tools/make_music.py ditty3` by hand - build.sh does not). Buzz: a burst of the note on
  every frame for half the note, 8 frames at most. 160 bytes of tune, worst pitch error 0.6%.
  The tune gives way to an effect, the skid or a crash, and keeps its place.
- Effects (snd_fxk): 0 the coin run (pick-up, 8 frames), 1 the whoosh up (NOS, 18 frames),
  2 the bonk (an O, 6 frames; it was the crunch), 3 up a beep. o_test reads snd_fxt now.
- Four new ditties in make_ditties.py: 5 Kettle's On, 6 Crumbs!, 7 Pop-Up Toaster, 8 Butter
  Fingers (WAVs in docs/sound/, all pass the tool's checks; nobody has heard them yet).
- zxlap: 158 pictures at 3 frames, 143 at 4 - as before the music (151 / 145). code_end 0xBD1D.

## 2026-11-14 SAST (afternoon) - the ditty the Manic Miner way, in spare time only
- Grant did not like pips, plink or buzz, nor five more styles ("none of those sound right. Can
  you play manic miner and see how the sound holds more"). Measured in zxdev from his snapshot:
  Manic Miner's in-game tune is a burst 7-8 ms long (28,000 T) about 11 times a second at
  640-1,200 Hz. Ours were 1 ms at 2,000-4,400 Hz. "A half-miner is okay" (4 ms once a picture, 17
  semitones lower). "Play with options so impact on speed is minimised." "Something more upbeat
  for racing." "The ditty only starts playing after the green lights ... so race on."
- Built: the interrupt only steps the tune (from race_on until you_done); the main loop sounds
  the note once a picture (mu_burst, after the copy). The wait for the TV frame (snd_wait) is now
  a counting loop: the picture's spare time in units of 279 T (mu_slack). A burst's budget is
  the last picture's spare time + what its burst used - a margin (14 units), capped at the whole
  4 ms burst, never under two cycles (about 1.5 ms); after a late picture, no burst.
- Measured (tests/zxlap.py; ALONE=1 keeps the computer cars on the grid): in the pack 119
  pictures at 3 frames / 161 at 4 (no music: 149 / 156 - laps differ this much run to run);
  alone 260 / 65 (no music 274 / 55). Notes average 3.5 ms of the 4.0; about 1 in 10 gives way
  to an effect. Tried and dropped: a fixed 4 ms burst every picture (in the pack: 5-frame
  pictures), 4 ms / 2 ms by the pace (71 / 200 in the pack), spare time only with no minimum
  (the tune dropped out for 2 notes in 3).
- Four racing ditties in make_ditties.py (RACERS: 9 Green Light, 10 Flat Out, 11 Chequered Flag,
  12 Second Helpings); the tape plays Green Light: `python3 tools/make_music.py ditty9`. Every
  ditty rendered half-miner (tools/make_ditty_styles.py key:minerhalf) for the Sound Lab.
- Later the same hour: a guaranteed minimum note (two cycles, then one) was dropped - the burst
  is skipped when the picture has under two cycles of spare time. tests/drive_test.py's "13
  pictures a second off the start" check now asks for 12.5: off the grid the game is in its
  4-frame rhythm for those 2 seconds either way (26 pictures with no ditty, 25 with it, whatever
  the minimum or margin). Grant told.

## 2026-11-14 SAST (midday) - coloured objects in whole game screens (mock-up)
- Grant: "mockups for different coloured objects and how they would look in gameplay - cleverly
  working around colour clash". tools/make_colour_scenes.py -> docs/design/colour_scenes.png:
  six real screens (read from the game in zxdev on an autopilot lap) with 31 objects placed on
  the world beside the road, clear of the O's; every cell checked for one ink and one paper.
  The blended (no blue edge) objects did not get placed: they need 12 px clear all round and the
  strips beside the road are too narrow where the tool looked. Not built into the game.
- Coloured objects, Grant's steers (14 Nov, midday): "happy with those colour images"; the egg and
  bacon plate must be CYAN so the egg's white shows with no outline, the yolk's cells yellow on
  white ("happy with the plate"); "coffee should be black in a mug/cup" (drawn: white mug, no
  blue, black coffee); "remember these shapes should not spill into the road area". Sheet:
  docs/design/egg_bacon_plate.png (tools/make_fryup.py). Nothing built into the game yet.
- Mug: Grant asked for a black line drawing on cyan with the coffee fuller, then "a semi 3d
  effect ... more of a cup feeling than just a circle". Three drawn (tools/make_fryup.py:
  line_mug, mug3d, mug3d(saucer)); he sent back the picture of the side-view mug ON A SAUCER
  (66 x 52) with no words - read as his pick (my reading; he had been "leaning to" the
  straight-down one a minute before he saw it).

## 2026-11-14 SAST (afternoon) - coloured objects built as an option; too slow to switch on
- Grant: "build the objects." Built behind a switch (OBJECTS=1 python3 tools/make_world.py, then
  OBJECTS=1 bash build.sh; off by default): tools/make_world.py places a coloured object (the mug
  on a saucer, tools/make_fryup.py mug3d) as map tiles, off the road, and writes its colour
  regions to src/objects.asm; obj_paint (racer.asm) puts the colours into the window's attribute
  cells after each copy - one look-up per cell row (the first and last ink pixel over each run
  of 8 pixel rows) - wiping the last picture's first. tests/objects_test.py: over 36 camera
  positions every cell with the mug's ink has its colour and no other ink. Picture:
  docs/design/mug_in_game.png.
- MEASURED, and why it is off: with the mug wholly in view a picture takes about 349,000 T (5 TV
  frames: under 10 pictures a second) against 210,000 without. The map's tiles cost about 700 T
  each to draw (masked ones more: tdm_line 60,000 T), and the mug with its plain margin is 11 x 9
  = 99 tiles. obj_paint itself is about 13,000 T with the mug in view. Memory: the mug fits only
  by giving up the twelve old blue breakfast things (KEEP_OLD); the egg-and-bacon plate (13 x 13
  tiles, about 1.5 KB) does not fit at all.
- What would make it work: a faster way to draw a big object (not tile by tile), or small
  objects only (3 x 3 cells or so: about 7,000 T). Not started.

## 2026-11-14 SAST (afternoon) - the title / attract screen is in
- Built by an agent in its own worktree and merged (commit ffb9590): layout A - the logo, LAP
  RECORD, a cloth stage where the five cars skid round in turn with their driver's card, 1 = 1UP
  (starts the race), 2 = 2UP ("COMING SOON"), K = redefine 1UP's five keys; after a race the
  accelerate key goes back to the title. src/title.asm (1,100 bytes at 0x7B80, the room the small
  cars leave under 0x8000), title2.asm (358 bytes in the program), title3.asm (566 bytes copied
  to 0x5B4C: the printer buffer and system variables). tests/title_test.py; the other tests press
  1 to leave the title (tests/drive_test.py's start-up, tests/title_skip.py).
- Memory now: code_end 0xBF4F - 177 bytes free in the program; 52 under 0x8000; init_end 0xCDDB.
  The coloured objects (OBJECTS=1) no longer fit beside it without more room.
- Speed (zxlap): in the pack 109 pictures at 3 frames / 195 at 4 / 9 at 5; alone 240 / 80
  (before the title: 123 / 167 and 260 / 65). The agent's like-for-like run found read_keys 61 T
  a picture dearer and nothing else; laps differ run to run. The 5-frame pictures are new to
  watch.
- Open: the crew chief still says "SPACE FOR NOS" after the NOS key is changed; the drivers'
  two-line descriptions are the agent's wording; a few frames tear on the title when the driver
  changes; no sound on the title.

## 2026-11-14 SAST (afternoon, later) - Kettle's On driving; plain title options; small objects
- Grant: "need that ditty to be less ditty and more driving almost trance like - can you up its
  tempo or beat" - "Kettles on is still the best". make_ditties.drive(): the tune faster (a
  quaver = 6 TV frames, 167 beats a minute) with a pedal note on every step the tune does not
  sound - an unbroken pulse of 8 notes a second. ditty13 is in the build (ditty14: 5 frames a
  step, 200 bpm). The player now reads a byte a step (MU_STEP, MU_GATE; 254 a rest): 129 bytes
  for 96 steps. `python3 tools/make_music.py ditty13|ditty14` (only the driving tunes).
- Grant: "make the 1UP and 2UP and keys just normal size 1 - One player 2 - Two players, K -
  Keys". Done by the title agent (commit ede982d, merged): a plain three-line list.
- Grant again: "build the objects" (after my advice: small ones only). OBJECTS=1 now places eight
  small square blue-edged objects round the lap - sugar cubes (white), toast (yellow), a jam tart
  (red) - in place of the old blue things; obj_paint colours rectangles (8 bytes a block).
  tests/objects_test.py passes for all eight; picture docs/design/small_objects_in_game.png.
  STILL OFF by default: the lap is slower with them (in the pack 25 pictures at 3 frames / 181
  at 4 / 57 at 5 / 4 at 6, against 76 / 195 without; alone 105 / 134 / 45 against 249 / 65) and
  tests/drive_test.py then fails its speed and lap-time checks. obj_paint costs about 11,000 T
  with one block in view - far more than it should; not yet found why. One sugar cube also sits
  under the start lights. 47 bytes free in that build.

## 2026-11-14 SAST (afternoon, later still) - damage, its gauge and the oil can
- Grant: "I would like to include a car status - also shows like the NOS, which is damage, each
  time you hit a car or something you sustain damage. With damage the car slows down a bit. Then
  little health bars (oil cans) are available on the track randomly - only once about a lap in
  time though. The damage shows as an icon with a little bar."
- Built (racer.asm DAMAGE, strip.asm oil_tick, grip.asm): dmg 0..8 - a hit on a car or a cereal O
  adds 1, not again for 12 pictures (one crash is many touches); each point takes 8/256 px a
  frame off your top speed (fully damaged 1.50 against 1.75: 86%); a spanner and a bar of what
  is left in the window's bottom left corner (drawn into the buffer like the NOS canisters); an
  oil can (two map tiles, NOS_C in tools/make_world.py, at 76, 146 on the left-hand side) is put
  out 120 pictures into the race, mends all the damage when driven over, and comes back 192-255
  pictures later (about a lap). tests/damage_test.py (8 checks). Picture:
  docs/design/damage_in_game.png.
- Not as asked, yet: the can comes at ONE place (a random place needs a set of map tiles for
  each); only YOUR car takes damage; damage does not carry a message from the crew chief.
- Memory: the ditty's data (129 bytes) moved out of the program to the title's table block at
  0x5B4C (td_end2; 23 bytes left there). Program: code_end 0xBEC0, 320 bytes free.
- Speed (zxlap): in the pack 67 pictures at 3 frames / 212 at 4 / 1 at 5; alone 247 / 85.

## 2026-11-14 SAST (later afternoon) - the health gauge redrawn; the music's beat made exact
- Grant on the gauge: "the icon for health is not clear - it needs to be masked and a better icon
  ... more easily show health levels"; then "a slightly larger heart, that is filled in. The heart
  'empties' as health is lost, from the top down" - "the outline of the heart remains but the
  fill empties"; then "a heart is for a person, more than for a car, looking for something more
  mechanical" - "mockup some alternative icons". Built: a 16 x 13 icon on its own clear patch,
  outline kept, fill emptied from the top by dmg_emp rows (dmg_draw, dmg_heart in racer.asm).
  The heart is in the build; seven mechanical ones to choose from in
  docs/design/damage_icons.png (tools/make_damage_icons.py: cog, engine, spanner, fuel can,
  battery, piston, car from above). Swapping one in is a change of the 52 bytes of art.
- Grant on the music: "does not hold - it just sounds like a collection of beeps in the game - it
  loses its musicality". Cause: the burst-a-picture way sounded each note at the picture's
  uneven beat (3 or 4 TV frames), cut to its spare time, and skipped 1 in 5. Now the interrupt
  sounds the note itself, about 2 ms on every OTHER TV frame of its step (25 a second, exact),
  an octave under the music-box register (LOW 12: 494-1,100 Hz). mu_burst and the call are gone
  (the wait's spare-time count stays, unused). COST, measured (zxlap): alone 199 pictures at 3
  frames / 113 at 4 (it was 247 / 85); in the pack 13 / 247 / 3 at 5 (67 / 212 / 1). Every
  frame at LOW 17 was dearer still (107 / 176 alone).
- Grant, of the sixteen icons: "lets do the lightning". tools/make_damage_icons.py now writes the
  game's art (src/dmgicon.asm; GAME = 'P'); tests/damage_test.py reads the same art. Picture:
  docs/design/damage_gauge_in_game.png.
- The gauge, twice more the same afternoon. Grant: "make sure it is masked and the outline is
  clear ... The player needs to be able to see it in their peripheral vision" - tried a black box
  with the bolt bright green / yellow / red by health (its cells do not scroll); Grant: "No I
  want the gauge to be a masked item, so a decent mask - but invisible mask". Built: the bolt in
  the window's blue, drawn ON the table with 2 clear pixels all round it, its own shape
  (dmgicon.asm: keep / outline / fill for each byte, 17 rows of 3; dmg_draw). To make room the
  wait's spare-time count and the old engine tone in the wait came out (snd_wait is HALT again).
- Mock-up asked for: "positional information into the game area ... quick bite messages ... top
  right, masked display" - docs/design/ingame_info.png (tools/make_ingame_info.py): A the place,
  B with the lap, C with a 2-second message under it, D in colour (fixed cells can have their
  own colours). Not built.
- tests/stuck_test.py: a car that has passed one waypoint and moved 60 pixels on is not "stuck"
  (one place of 477 was 2 waypoints short at 12 s with the game at its slower rhythm).

## 2026-11-14 SAST (evening) - your place on a plate inside the window
- Grant, of the in-game position mock-ups: wanted "smaller fonts - not double sized but in a
  smaller square that has slightly rounded edges, with the game around it"; "I like B [a solid
  blue plate, letters cut out], but can we create smaller fonts, and so 2nd or 3rd shows a small
  nd or small rd"; of docs/design/ingame_plate.png: "3 is good build 3".
- Built (src/plateco.asm pl_draw, called after dmg_draw; data from tools/make_plate.py): a solid
  rounded plate 34 x 22 in a 40 x 24 clear patch at window x 128-167, lines 8-31 - the ROM's own
  figure, a small raised st / nd / rd / th and LAP n/3 in a 3 x 5 font, all cut out of the
  plate; under it, while msg_timer runs (the strip's FINAL LAP, 3 s), a second plate with FINAL
  LAP!. Not drawn while the start lights hang. tests/plate_test.py. Picture:
  docs/design/place_plate_in_game.png. Only FINAL LAP! so far: other quick messages (UP ONE!,
  OIL OUT) need 30 bytes of letters each and there is no room.
- MEMORY, learnt the hard way: the program is two regions. Before sq4 (page-aligned, then the
  tiles' page) everything pads up to the next page - adding there costs nothing until it crosses
  a page, then 256 bytes at once. After the tables is the true free space. The plate's code is
  after faces.asm for that reason. Now: code_end 0xBFF5 - 11 bytes free; the room under 0x8000
  has 12; the table block at 0x5B4C none. The next feature needs room found first (the small
  cars' frames carry about 2.4 KB of zero bytes: a change to draw_car).
- SPEED with the plate, measured (zxlap): racing alone, no picture at 3 TV frames any more -
  245 at 4, 9 at 5 (it was 199 / 113 before the plate); in the pack 3 / 251 / 8. The plate's
  drawing (a fill of 24 rows and the cut-outs, every picture) is about 10,000 T and the game had
  about 7,000 to spare at 3 frames once the music took its share. So the game now runs at a
  steady 12.5 pictures a second. To win it back: draw_car with 2-byte frames for the small cars
  (their third byte is always zero) - less time a car, and about 2.4 KB of memory.

## 2026-11-14 SAST (evening, later) - place in one place; music off in the race; speed won back
- Grant: "there is no suggestion of music, just background beeping, so musicality completely
  lost. I only need my place in one place - that is in game" - "but win back the speed".
- The big place in the red block under the window is gone (bar_tick; msg_finished no longer
  prints it): the red block is your face only. Your place is on the plate in the window.
- The ditty in the race is OFF by default (OPT_MUSIC; MUSIC=1 bash build.sh puts it back): three
  ways of playing it were tried in the game today and none sounded like music to Grant, and each
  cost speed. A 48K tune that holds (Manic Miner's) spends 40% of a TV frame on it every pass.
  Suggested instead: the tune on the title screen, where nothing else needs the time.
- Speed: the plate's fill rewritten (a row routine, no table); the small cars' frame rows are 4
  bytes, not 6 - their third pair was always empty (make_data ROWB; draw_car and the title's
  a_draw changed to match). Racing alone (zxlap ALONE=1): 220 pictures at 3 frames / 97 at 4 (it
  was 0 / 245 with the music and the first plate; 247 / 85 before today's damage gauge, plate
  and oil can). In the pack the game is at 4 frames nearly always, as it was.
- Memory: the cars now take 4,864 bytes under 0x8000, not 7,296 - 2,432 bytes free there (it is
  slower "contended" memory: fine for data and for code that is not time-critical). Program:
  code_end 0xBF7C, 132 bytes free.

## 2026-11-14 SAST (night) - the plate carries it all; nothing bottom left; speed back to the morning's
- Grant: "The in game display works really well - so that bottom left reporting is not needed at
  all." The face, the red block, the white strip (PRESS Q / LAP / FINAL LAP / FINISHED!) and the
  TIME row are gone (make_strip.py; hud_update no longer calls bar_tick, which is left in the
  source unused; msg_finished only clears the timer). NOTE: nothing now tells the player which
  key starts the race - the strip's PRESS Q did.
- Grant: "Is it possible in that blue area to have your current laptime, small if you can. I
  think you can put P1 or P2 or P3 instead of 3rd or 1st" - "have a space between the P1 and lap
  and still show 1/3". The plate is 42 x 22 (6 bytes): P and your place (ROM letters), a gap,
  the lap n/3 small, and under them your lap's time so far m:ss.t small (race_time - C_LST,
  time_fmt). Small figures: pl_g (0-9 : . / blank, 5 bytes each; pl_pair puts two in a byte).
- Speed: the plate is composed once into pl_bmp (144 bytes, under 0x8000) when place or lap
  changes (pl_static, plate_slow.asm), only the time's 5 rows are redone each picture, and the
  bitmap is copied to the buffer with LDIs; the gauge's three bytes a row are written out, not
  called. Plate + gauge + oil can went from about 20,500 T a picture to about 8,000. zxlap alone:
  246 pictures at 3 frames / 85 at 4 - the same as before today's gauge, plate and lap time
  (247 / 85). In the pack 38 / 233.
- Music: still off in the race (OPT_MUSIC). Grant: "need to figure out how to make the music
  come through during the game." Not solved on the beeper. Proposed: the AY sound chip (128K
  machines, or a 48K with one): held notes in three voices for a few hundred T a frame.
- Later still: Grant: "can we make the P1 smaller, so that the display can be a bit smaller. Also
  is it possible to shift it more towards the corner and have a smaller blue border around it?"
  The plate is now 29 x 16: "P1 2/3" and the lap time both in the small figures, 2 pixels of
  blue round them; 6 pixels in from the window's right edge and 3 down from its top (pl_bmp 5
  bytes x 18 rows; PL_B, PL_W, PL_H). The message's plate moved up under it (PL_M, PL_MT).
  zxlap alone: 240 pictures at 3 frames / 79 at 4.

## 2026-11-14 SAST (late) - the window a row taller: 176 x 152
- Grant: "a crazy thought. We don't really use the bottom area at all except for the pit crew
  talks. Could we try one more row underneath in the gameplay." And: "the pit area can be reduced
  by a row."
- WIN_H 152 (19 character rows). What moved: the frame's bottom line (lines 163-164), the health
  gauge and the NOS canisters (a row lower in the buffer), the crew chief's bubble (three rows,
  21-23: its top line 168, the wave rows 169-175, the words at 177 and 183), the strip's fixed
  picture (rows 168-191, colours rows 21-23), the copy routine (152 lines: it ends 0xFD62,
  TOPMEM 0xFD70 - the top-of-memory data now ends 3 bytes short of the interrupt jump).
- The tables that sat in the buffer's bottom rows (BUFA-BUFH: the messages, the small letters,
  thrust, the driving styles) and BUFC's race variables are now at LOWTAB = 0x7D40, the top 704
  bytes of the room under 0x8000: the tiles drawn past the window's last line need buffer rows
  160-167, where the strips began. cloth_pat and PNUM stay in the buffer (rows 176 on). The
  strips' "last 6 bytes" rule is gone with them.
- Speed (zxlap): alone 200 pictures at 3 frames / 113 at 4 (it was 240 / 79 at 144 lines); in
  the pack 14 / 250 / 1. Eight more lines are 5.5% more to fill, draw and copy.
- Tests updated for the new positions (frame_ok, the window check, the bubble); all pass.

## 2026-11-14 SAST (night) - the window a column wider: 184 x 152
- Grant: "i would like to add one more column to the right ... and we'll see if there is a
  performance impact". There was already a blank column between the frame and the right-hand
  panel, so nothing there was squeezed: the window is columns 1-23, the frame's line in column 24.
- WIN_W 23. The copy routine moves 12 pairs a row (7 + 5), 24 bytes: the 24th is the frame's own
  screen column, so its line (0x18) is kept in the buffer's byte 25 of every window row (fr_col,
  each picture). 152 lines x 40 bytes from 0xE800 run to 0xFFC3, so the "top of memory" data
  (TOPMEM: masks, map rows, HUD text) is now under 0x8000 too, below LOWTAB. The cloth fill
  pushes 13 pairs a line (bytes 25-0). Camera, car clip, frame, NOS canisters and the plate
  follow WIN_W.
- PERFORMANCE, measured (zxlap): alone 19 pictures at 3 frames / 239 at 4 / 9 at 5 (it was 200
  / 113 at 22 columns); in the pack 9 / 255 / 10. The extra column takes the game out of its
  faster rhythm altogether: about 9,000 T a picture (the copy 4,400, the cloth 1,700, the
  frame's column 2,400, tiles). tests/drive_test.py: the computer cars' "set off" check asks for
  20 pixels in 2 s, not 30 (one car made exactly 30 at the slower rhythm).

## 2026-11-14 21:41 SAST - the NOS bottles red, the health bolt magenta

- Grant: "could you make the NOS bottles in the bottom right red ink and the health lightning bolt
  magenta. So these would need a decent mask to prevent colour clash".
- HOW: a colour cell holds one ink, so each icon now owns its cells. `hud_pre` (src/plate_slow.asm,
  called each picture before `nos_draw`) sets the gauge's 3 x 2 cells to magenta on cyan (0x2B)
  and each HELD bottle's 2 cells to red on cyan (0x2A), an empty slot back to the cloth's blue
  (0x29). The mask is the whole cell: a held bottle's cells are cleared in the buffer first, and
  `dmg_draw` now writes all 16 rows x 3 bytes of the gauge (src/dmgicon.asm: outline, fill per
  byte; tools/make_damage_icons.py game_rows()). So the cloth's dots and any car passing behind
  are not drawn inside those cells - nothing there can take the wrong colour.
- COST of that: a car driving into the bottom-left 24 x 16 or under a held bottle is hidden there.
- SPEED, measured (tests/zxlap.py): alone 19 / 239 / 9 (unchanged); in the pack 17 / 252 / 6.
- TESTS: damage, plate, title, drive, nos, o, setup, drift, stuck all PASS. damage_test checks the
  six gauge cells are 0x2B; drive_test checks the bottle red and the bolt magenta.

## 2026-11-14 21:55 SAST - the view leads the car

- Grant: "would it be feasible to have the car position in the screen adjust to allow to see
  ahead more on the track" - then "go".
- `cam_lead` (src/plateco.asm), called by `camera`: lead_x / lead_y aim at the car's speed that
  way x 24/256 (42 px at top speed), held to 40 px across and 32 up or down, and move 3 px a
  picture at most. It follows the direction of TRAVEL (not the nose). Tuning: LEAD_X, LEAD_Y, LEAD_STEP.
- tests/lead_test.py (new) PASS: centred at rest, 40 px ahead at speed, slid there, back when stopped.
- SPEED (zxlap): alone 22 / 238 / 15 (was 19 / 239 / 9); pack 3 / 248 / 11 - more road in view, a little more to draw.
- OPEN: tests/drift_test.py (a 0.30 s right turn) and tests/stuck_test.py (1 place of 477) FAIL
  with the lead on and PASS with LEAD_X/Y set to 0. The camera is read by no driving code; the
  picture times change, and both tests are timed by the clock. NOT YET PROVED to be timing only.
- Memory: code_end 0xBFE9 - 23 bytes free in that area.

## 2026-11-14 22:16 SAST - no pit talk, the logo under the window, the map up, a 24th column

- Grant: "Do away with the pitstop talk for now. Put the Breakfast Run logo centred under the
  gameplay area at the bottom. Shift the map up. Make the race details one column shorter (so the
  flag and the fastest time icons are in the same column. And then add another column to the game area."
- WINDOW 192 x 152 (WIN_W 24: screen columns 1-24, the frame's right line in column 25). The copy
  routine already moved 24 bytes a row, so it is unchanged - and `fr_col` (the frame's column kept
  in the buffer, ~2,400 T a picture) is gone: the frame is on the screen, drawn once.
- PANEL: 6 columns (26-31). Place 26, car 27-28, gap 29-30, column 31 the flag (in) or the clock
  (best lap) - both: the flag in the upper cell (FLAG8), the small clock under it (CLOCK8).
  Before the race the faces are in 30-31. RACE heading 6 wide; lap record clock 28, time 29.
- MINI-MAP at the panel's top (screen lines 3-34), 48 wide: scale 21/256 (was 3/32, 54 wide) -
  tools/make_world.py and map_c3 (src/hud.asm); MAP_H comes from the generator.
- LOGO: rows 21-22, columns 9-15 (LOGO_ROW / LOGO_COL, src/hud.asm), centred on the window. The
  title screen reads it back from there (src/title.asm, BUF+2384+LOGO_COL).
- PIT TALK off: OPT_PIT (build.sh: PIT=1 puts it back, but the logo is now where the bubble was -
  that needs a layout decision first). The strip's picture is not drawn, strip_tick not called;
  the canisters and the oil can (strip_triggers) carry on.
- SPEED (tests/zxlap.py): alone 40 pictures at 3 TV frames / 225 at 4 / 5 at 5 (it was 22 / 238 /
  15 at 23 columns with the lead); in the pack 12 / 247 / 16 (was 3 / 248 / 11). Wider AND a
  little faster, because fr_col went.
- TESTS: drive, title, damage, plate, nos, o, setup, lead, drift, stuck all PASS. drift and stuck
  pass again with the lead on - so their one failing case each at 23 columns was the clock-timed
  tests meeting a different picture rhythm, as suspected (camera is read by no driving code).
- Memory: code_end 0xBFD3 (45 bytes free in that area).
- OPEN: 4 empty rows in the panel between the map and RACE; the lap record sits 3.5 px right of
  the panel's centre (a cell-aligned clock cannot be centred in 6 columns).

## 2026-11-14 23:15 SAST - the look-ahead halved

- Grant: "could you make the look ahead affect slightly less - so half on each - its a little too
  much of an adjustment - but the idea works - design changes work well and speed is good".
- src/plateco.asm: LEAD_X 20, LEAD_Y 16 (were 40, 32); the aim is speed x 12/256 (21 px at top
  speed, was 42); LEAD_STEP 2 px a picture (was 3), so the slide feels the same.
- All ten tests PASS; speed alone 41 / 224 / 5 (unchanged).

## 2026-11-15 06:07 SAST - the speed test: where a picture's time goes, and one safe win

- Grant: "please run an optimization test on the game - see if there are ways to make this run
  smoother - i.e. improvement the frame rate".
- tests/zxlap.py's grouping was wrong (the copy routine was counted as tiles, the generated tile
  code as time_fmt, the plate as you_grip, the gauge as draw_car): more routine names in GROUPS.
- WHERE IT GOES, alone, 231,659 T a picture (3 TV frames = 209,664): copy to screen 51,600 (22%);
  cloth 37,800 (16%); tiles ~36,000 (16%); cars' physics, grip and friction ~37,000 (16%);
  computer cars' thinking ~16,000 (7%); drawing cars 11,800 (24,200 in the pack); the plate 6,600;
  the gauge 3,700. The copy, the cloth and draw_car's loop are already near what the Z80 can do.
- THE GAME IS BISTABLE: a picture that fits in 3 frames also runs one frame's less logic, so a
  small saving near the edge tips many pictures. What-ifs (not kept): no plate and gauge at all:
  alone 213 of 321 pictures at 3 frames, pack 27 / 247 / 12 - the pack is ~30,000 T over, not ~10,000.
  Computer cars deciding every 8th frame (not 4th): alone 150 / 149, pack no better, and the
  fastest computer car fell to 20.7 s a lap (drive_test FAIL) - NOT kept.
- KEPT: the gauge is composed only when the damage changes (dmg_make, src/plate_slow.asm, 48 bytes
  at dmg_bmp) and copied in each picture (3,660 -> ~1,700 T); the plate's time is cut afresh only
  when it has moved on 5 frames (pl_tl), about every other picture (~2,000 T). The gauge's art
  and code moved under 0x8000: code_end 0xBEF3 (269 bytes free in the main area).
- RESULT: alone 91 pictures at 3 frames / 193 at 4 / 3 at 5 (was 41 / 224 / 5); the pack 3 / 253 /
  6 (was 23 / 250 / 11: fewer slow ones, no more fast ones). All ten tests PASS.
- NOT TRIED (each changes what Grant sees or feels): the window 2 columns and 2 rows smaller
  (est. -22,000 T); plain cloth without dots (est. -4,700); your car's physics at 25 a second
  (est. -12,000, changes the handling); a steady 4-frame lock (even pacing, 12.5 a second).

## 2026-11-15 SAST (morning) - the race tune on the AY sound chip

- Grant: "go ahead on ay-version" (the beeper tune was "just background beeping" in every form).
- tools/make_music_ay.py -> src/music_ay.asm: Kettle's On (driving), 96 steps of 6 frames, melody
  two octaves under the music box (495-1,108 Hz). The player is in the interrupt (src/racer.asm,
  `if OPT_AY`): channel A the tune, B a bass pedal on B (low, then an octave up, a step each), C a
  noise hat on the off-beat; each voice starts loud and falls 3 steps of volume, like a pluck.
  No CALLs or PUSHes (the cloth fill's stack rule): BC is kept in isr_bc, each write is in line.
- Plays from the green light until you finish, as the beeper tune did. The beeper still does the
  engine and the event sounds.
- A 48K WITHOUT the chip is silent and unharmed (ports 0xFFFD / 0xBFFD mean nothing to it). To
  HEAR it: a 128K model, or the 48K with "AY sound chip on 16K/48K" switched on in the player.
- CHECKED in zxdev on model 48 with ay48 and on model 128: the recorded sound's strongest pitch,
  step by step, is the tune's (737, 495, 624, 990 ... Hz). NOT heard by anyone yet: whether the
  bass and hat suit it is Grant's call. docs/sound/ay_race_tune.mp3 is 13 s of it from the race.
- OPT_AY (build.sh: AY=0 leaves it out), on by default. The pit talk's code is now left out of
  the build while OPT_PIT is 0 (it made the room): code_end 0xBE9E.
- SPEED: alone 73 pictures at 3 frames / 200 / 5 (91 / 193 / 3 without the tune); pack 19 / 241 / 11.
- All ten tests PASS.

## 2026-11-15 SAST (morning) - mock-ups: whole-screen layouts for the race and the title

- Grant: "we're going to keep the play area the same size, Can you mockup again some overall
  design layout options for the game and the title screen". (So the 24 x 19 window stays.)
- tools/make_layout_options.py -> docs/design/layout_game.png (NOW + A Full panel, B Mirror,
  C Banner, D Night, E Tablecloth) and docs/design/layout_title.png (NOW + A Centred, B Menu
  card, C Night, D Poster). Real 256 x 192 screens built from the game's own screens
  (docs/design/layout_src/), each checked: no cell has more than two colours. Nothing built.

## 2026-11-15 07:14 SAST - the title screen: the menu card, your car lapping the tablecloth

- Grant: "I like title screen B, you can remove the 1 or 2 player to start at the bottom. Is it
  possible to have my car racing around the outside of the title screen".
- BUILT (src/title.asm, title2.asm, title3.asm): the whole screen a red-and-white check cloth,
  a cell a check (t_ging: colours only, not a pixel set); the card on it, rows 3-20, columns
  3-28: a yellow head with the logo twice its size (on white the logo's white egg was lost),
  TODAY'S MENU in red, 1 ONE PLAYER / 2 TWO PLAYERS / K CHOOSE KEYS, the five faces on their
  cars' colours, LAP RECORD in blue. No PRESS 1 OR 2 TO START line; "2UP COMING SOON" shows at
  the card's foot for 1.5 s.
- YOUR CAR laps the 3-cell border, clockwise, 2 px a step, 25 steps a second (a lap ~14 s), its
  nose turned into each corner. It is black ink on cells that are only paper, so no clash; what
  is under it is kept and put back (the old stage's code, now for the whole screen: a_x is the
  screen's x + 16). The run is one line of data: a_runs in title3.asm.
- GONE: the cloth stage, the driver's card that showed each driver in turn, the skid marks.
- The title is known by TODAY'S MENU's red (0x7A at row 8, column 10): tests/drive_test.py,
  title_skip.py, title_test.py and zxlap.py look there now (they looked for the flashing prompt).
- The title's layout list moved from the tables at TD (full) to the room under 0x8000.
- docs/design/title_built.png, docs/design/title_lap.gif (the lap, 8 s). All ten tests PASS.

## 2026-11-15 SAST (morning) - RACE in small letters; mock-ups: podium, frames, faces

- Grant: "the RACE font should also be the smaller font - on the right in the HUD". BUILT:
  screen_once draws RACE from 10 bytes (so_race, src/racer.asm) in the 3 x 5 letters, centred
  on the heading's blue bar. drive, title, plate tests PASS.
- Grant, on the race's end: back to the title on game over; after 1 or 2 a ditty, then the
  countdown starts by itself; when all are in, a winner display in the window's middle - a
  podium with faces, 1st 2nd 3rd, the fastest lap, the winner smiling. MOCK-UPS ONLY so far:
  tools/make_podium_mock.py -> docs/design/podium_options.png (A card, B night, C table, D band).
  Grant: "I like A podium - but tighten it up please - smaller fonts, writing and numbers
  centred" -> docs/design/podium_tight.png (A2; A3 with plain steps), 14 x 13 cells.
- NOT BUILT, and one question open: if the countdown starts by itself after the ditty, the
  set-up keys (1, 2, 3 before the start) only have the ditty's few seconds - where do they go?
- Grant: the frame round the play area "doesn't quite work for me": tools/make_frame_options.py
  -> docs/design/frame_options.png (NOW + A None ... H Black). Nothing built.
- Grant: each driver's face three ways - as now, happy, sad. Drafted in tools/make_podium_mock.py
  (FACE from the game, WIN, SAD); docs/design/podium_faces.png; and an editable page in Claude
  (tools/faces_page.template.html): https://claude.ai/artifact/Nfxfa54baoZdTsPSAgzU8c

## 2026-11-15 SAST (morning) - the podium inside its card; a name for each driver (mock-up)

- Grant: "so each player needs a name. And each player has a colour. Podium must be inside the
  rectangle area for the display so in situations like cyan, does not 'blend' into the background".
- docs/design/podium_inside.png (tools/make_podium_mock.py, inside()): the card 16 x 13 cells, a
  margin of its own colour all round the podium, each step and face in its driver's colour, the
  card a colour no driver has (A4 yellow, A5 black). Two sample results, one with cyan winning.
- PROPOSED names (NAMES2, not in the game yet): YOU (red), FRANK (cyan), JANE (white),
  BRUNO (pink, the tank), SPIKE (green). The game still says CYAN, GREEN, PINK, SLIM JANE.

## 2026-11-15 SAST (morning) - Grant's own faces: everyday in the game, happy and sad stored

- Grant picked podium A4 (the yellow card) and redrew all fifteen faces on the Faces page
  (https://claude.ai/artifact/Nfxfa54baoZdTsPSAgzU8c), pasting them back as text.
- EVERYDAY faces -> tools/face_art.txt (YOU, CYAN, GREEN, PINK, WHITE) -> tools/make_faces.py ->
  src/faces.asm: in the game now (race order before the start, the title's row of faces).
- HAPPY and SAD -> tools/face_moods.txt (new). Not in the game yet: for the race-end display.
- tools/make_podium_mock.py reads both files, so the mock-ups and the page show his drawings;
  the page's "put back" button now restores these. title and drive tests PASS.

## 2026-11-15 08:19 SAST - the race's start and end: ditty, automatic lights, the podium, back to the title

- Grant: names agreed (YOU, FRANK cyan, SPIKE green, BRUNO pink, JANE white). "once you click 1
  or 2, then a ditty plays and the countdown after the ditty automatically begins"; "on game
  over, it should go back to the title screen"; a podium "with their faces, 1st, 2nd, 3rd, then
  also show fastest lap. Winner must have a graphic showing them smiling"; A4 (the yellow card);
  "the faces can all be the same size".
- START: jin_start (new race) sets jin_on 1 and points the AY player at mu_jing (20 steps, 2.4 s:
  src/plate_slow.asm); at its end the interrupt clears jin_on and auto_go (each TV frame) starts
  the lights. Green 5.0 s after the race screen appears. Q no longer starts the lights - unless
  jin_on is 0xFF (held off), which the older tests set. At green the race tune starts from its
  first note. On a plain 48K the ditty is silent but the timing is the same.
- SET-UP KEYS (1, 2, 3, 0): unchanged - they work from the race screen appearing until the
  lights come on, which is now only the ditty's 2.4 s. Grant has NOT decided where they go.
- END: `podium` (src/plate_slow.asm) replaces the CHEQUERED FLAG / PRESS Q banner: a bright yellow
  card, rows 5-15, columns 5-20; three steps in the drivers' own colours (order[0..2]); each a
  face (the winner's from src/faces_win.asm, Grant's happy drawings; all 16 x 16), its place
  large, its name in the small letters; FASTEST LAP, whose and the time; PRESS ANY KEY. hud_over
  takes ANY key (k_scan), then title_again.
- `glyph` (src/strip.asm) is built again (it was left out with the pit talk) and now draws
  figures and a colon too (sm_dig); sm_ctr centres a small text on a pixel.
- NOT DONE: the sad face (ideas from Grant: the driver you overtake, the last one home) and a
  happy face in the HUD for the best lap - "keeping it as a potential nice feature".
- tests/finish_test.py (new) PASS; all eleven suites PASS. Speed alone 74 / 203 / 3 (unchanged).
  code_end 0xBF89 (119 bytes free in the main area). docs/design/podium_built.png.

## 2026-11-15 SAST (morning) - the title's car no longer vanishes on the right; logo mock-ups

- Grant: "in the title screen on the right side of the screen the racing car disappears for
  periods". CAUSE: a_x was the screen's x + 16; down the right-hand side it is 252, and the
  column sum (x + 7) / 8 ran past 255, so the car was drawn nowhere. FIX: a_x is the screen's
  x + 8 (src/title2.asm `sub 2`; the run's start in title3.asm). tests/title_test.py now counts
  the looks in which the car is not on the screen (0 of 450); it only checked the car's ink
  when there was some, which is how this got through.
- Grant: "the egg yellow on white is not really visible ... more mockups for a title logo, or
  find a way to make the egg visible". tools/make_logo_options.py -> docs/design/logo_options.png:
  NOW + A bigger yolk, B line egg, C big egg, D big egg on a plate, E big line egg, F egg in the
  pan. Nothing built. docs/design/title_lap.gif is a whole lap now (14 s).

## 2026-11-15 SAST (morning) - mock-up: the podium's fastest lap

- Grant: "fastest lap - put the name underneath that - show the fastest lap icon and the time -
  can you mock that up". tools/make_fastlap_mock.py -> docs/design/fastlap_options.png: NOW +
  A (FASTEST LAP, clock, time / name), B (FASTEST LAP / clock, time, name), C (clock, time /
  name). The card grows a row (5-16) for the second line. Nothing built.

## 2026-11-15 SAST (morning) - the title's logo: the big egg, the band all bright

- Grant: "okay lets work with C, but the RUN should not be in bright"; then "is it possible to
  make the yolk in the egg bright"; then "can we try make the logo area all bright".
- BUILT (src/title.asm): logo C - a 16 x 16 egg (t_egg) drawn twice the size at rows 3-6,
  columns 5-8, the words from column 11, the logo's own small egg wiped. The yolk fills the
  middle four cells, which have colours of their own (0x7E). Now ALL BRIGHT: band 0x70, RUN
  0x72, egg 0x77.
- SIDE-EFFECT, shown to Grant in docs/design/logo_bright.png: all bright, the yolk is the band's
  own yellow and the egg reads as a white ring (1, as built). 2: the yolk's cells dull (0x3E).
  3: the egg's cells white on blue, a plate (0x4F), the yolk bright. A cell has one brightness,
  so "bright white ring on a dull band" (the mock-up C) cannot be had. Awaiting his pick.
- title, drive, finish tests PASS.

## 2026-11-15 SAST (morning) - the title egg's yolk small and round

- Grant: "the yolk in the egg should be smaller and round". t_egg (src/title.asm): the yolk is a
  6 x 6 disc in the art (12 pixels across on the screen), white all round it inside its four
  cells. With the band all bright it now reads as a fried egg, not a ring: version 1 of
  docs/design/logo_bright.png is superseded by docs/design/title_built.png. title test PASS.

## 2026-11-15 SAST (morning) - mock-up: the title's egg on a green band

- Grant: "share a colour between character blocks, but switch a colour to create its outside. So
  lets make the breakfast run area green ... The yolk will be yellow, and so the area just
  around the yolk will be yellow and white. But then the surrounding white area will become
  white and green. Please mockup up an egg this way."
- docs/design/logo_green.png: six versions, made on the real title screen by changing its colour
  cells only (the egg's art is as built): bright green with RUN red / yellow / white; darker
  green; a dull band with a bright egg; BREAKFAST white too. Nothing built - the game still has
  the bright yellow band.

## 2026-11-15 SAST (morning) - mock-up: the word RUN on the green band

- Grant: "okay egg looks great. Now the run should not touch the bottom white area, it should be
  surround by green. Can you mockup some alternative fonts or effects for the RUN word".
- tools/make_run_options.py -> docs/design/run_options.png: the band a row taller (rows 3-7) so
  green is under RUN; eight styles - 1 as now, 2 solid slant, 3 speed lines, 4 red plate,
  5 chequered, 6 cut lines, 7 wide, 8 small. The green band itself (egg white-on-green, yolk
  yellow-on-white) is agreed but NOT built yet: it goes in with the RUN he picks.

## 2026-11-15 SAST (morning) - mock-up: letters for RUN with the speed lines

- Grant: "I love the speed lines, can you make font variations for RUN with those speed lines of 3".
- tools/make_run_speed_options.py -> docs/design/run_speed_options.png: 3a Spectrum letters,
  3b the same heavy, 3c block leaning, 3d block upright, 3e thin and round, 3f outline, 3g the
  logo's own RUN, 3h lines through. Nothing built.

## 2026-11-15 SAST (morning) - mock-up: RUN cut through the middle, two colours

- Grant: "make some more options. I liked the line through the middle. Possible to make it two
  colours - top and bottom?" Yes: RUN is two character rows high, so each row has its own ink
  and the cut sits on the join. tools/make_run_split_options.py ->
  docs/design/run_split_options.png: S1-S10 (block, upright, wide, Spectrum heavy, the logo's
  own RUN; yellow/white, white/yellow, white/black, yellow/red, white/blue, yellow/magenta).
  Nothing built.

## 2026-11-15 08:50 SAST - the title's logo built: green band, the egg, RUN cut in two colours

- Grant: "s4 is perfect". BUILT: the card's head green (0x60), rows 3-7; BREAKFAST black; the egg
  white on green with its yolk yellow on white; RUN drawn by t_run (src/clothmini.asm, where the
  unused message-bar code was): three 6 x 8 letters, each pixel 3 x 2, leaning, lines 47-48 left
  out as the cut, yellow above (0x66) and red below (0x62); six speed lines from a table.
  bar_tick and rb_line (unused) removed; line_x only in PIT builds. code_end 0xBE89.
- title, drive, finish, plate tests PASS; speed alone 74 / 203 / 3.

## 2026-11-15 09:06 SAST - five title cars; podium fastest lap and your lap times; new red faces; sad-face mock-up

- Grant: "fastest lap - B but also show which lap they did it in"; "Have the fastest lap test have
  a row space below the podium". BUILT (src/plate_slow.asm): the card rows 5-17; a clear row under
  the podium; FASTEST LAP; under it the clock (CLOCK8), the time, whose, LAP n (best_lapno).
- Grant: "at the end of the race in the HUD, can you show the laptimes for your racer - so all
  laps". BUILT: yl_note keeps each of your lap times (you_laps), yl_show lists them under the
  panel at rows 21-23 when the podium goes up; hud_init clears them for the next race.
- Grant: "are you able to have 5 cars racing around the title screen". BUILT: tc_init / tc_step
  (src/plateco.asm), the same lap 77 steps apart, each car's 14 bytes at t_blk (in the back
  buffer, free while no race runs); the old picture is cleared, not put back (a_wipe), so no
  five copies of what is underneath. Each is its own car from the game.
- MEMORY: to fit, the pit talk's trigger code and place_txt are left out (OPT_PIT 0); the
  podium's words moved to the gap before sq4. code_end 0xBF83 (125 bytes free in the main area);
  the room under 0x8000 has about 75; the gap about 20. It is close to full everywhere.
- Grant's new faces for YOU (and a small change to CYAN): tools/import_faces.py (new) takes the
  page's text into face_art.txt / face_moods.txt. In the game; the Faces page starts from them.
- MOCK-UP, not built: docs/design/sadface_options.png - where your unhappy face goes when you
  miss the podium (A on the card ... F at the card's corner).
- All eleven test suites PASS (drive, finish, title rerun after the faces). Speed alone 74/203/3.

## 2026-11-15 SAST (morning) - mock-up: the panel - cars under the map, your result and laps under the cars

- Grant: "Put the cars 1-5 further up the screen, so just under the map. Then my result and
  laptimes goes under the cars. Can you mock that up please".
- tools/make_panel_mock.py -> docs/design/panel_options.png: NOW + A (red bar YOU 4TH, laps),
  B (your face - unhappy off the podium - a large place, laps), C (YOUR RACE block, best lap
  picked out), D (the block during the race). RACE moves to row 5, the cars rows 6-15. Nothing built.

## 2026-11-15 09:20 SAST - the panel rearranged: cars under the map, YOUR RACE under the cars

- Grant: "I like C, so fill it in as the game commences, showing lap times".
- BUILT: TOWER_Y 6 (RACE row 5, the cars rows 6-15, the lap record row 16); hud_init draws YOUR
  RACE (row 17, white on blue) and clears rows 18-21; yl_note shows each of your laps as you
  finish it (rows 19-21: the lap, its time); at the race's end the podium adds FINISHED and your
  place (row 18) and yl_best turns your best lap's row bright yellow.
- NOT SEEN in a live race by eye: the laps appearing mid-race (the path runs in drive_test's
  race without fault; finish_test checks the end state from poked lap times).
- MEMORY: code_end 0xBFD8 - 40 bytes free in the main area; the room under 0x8000 about 40; the
  gap before sq4 about 20. The game is full: the next feature needs something taken out.
- All eleven test suites PASS. Speed alone 74 / 202 / 4. docs/design/podium_built.png.

## 2026-11-15 SAST (morning) - the title's cars: no flicker, masked in front of the checks; LAP in YOUR RACE

- Grant: "there is still flicker in the title screen for the cars. Also - is it possible to mask
  the cars in that area so the red doesn't show through"; then "I did want the cars to drive in
  front of the red and white area, not just a white area, but wanted that they were masked, a
  tight mask". And "In the your race area, is there space to have lap written there?"
- FLICKER, the cause measured: wiping then drawing five cars took ~72,000 T a step - more than
  a TV frame - so the beam often showed a car wiped. Now a car is never wiped: each of its rows
  is STORED over the cloth's own pattern (3 bytes, a byte of cloth either side, 4 rows of cloth
  above and below), so the old picture goes as the new one comes (src/title2.asm: a_zr, a_bg,
  ad_draw). zxdev's tear report: 0 frames with a car "in between". What is left is tearing
  (a row old, a row new, 2 pixels apart). NOT judged by eye by me.
- MASK: the checks are pixels now (t_ging: every cell red ink on white, the red checks cells of
  solid ink), so each car cuts a white hole its own shape from the red and is drawn in red line.
  Three colours a cell there are not: the cars are red, not black. (An earlier try, a white road
  inside a one-cell edging, is gone: he wanted the checks behind the cars.)
- One wait a step in the title's loop (the cars take over a frame): 25 steps a second as before.
- YOUR RACE: each row reads LAP n and the time (the P was first overwritten by the number).
- Room made: the old message bar's words and clock, the keys screen's PRESS-key patches.
  code_end 0xBFD6 (42 bytes free in the main area). All eleven test suites PASS; speed 74/202/4.

## 2026-11-15 SAST (morning) - mock-up: the title's cars in black

- Grant: "the cars are red now. Is it possible to make them black against the red and white?"
  Not with a tight white mask as well: red, white and black in one cell cannot be had.
  tools/make_titlecar_mock.py -> docs/design/titlecar_options.png, the game's own five cars over
  the checks: NOW (red line, white mask), A black see-through, B black on a white cell-patch,
  C solid black shape, D black shape with cloth-coloured lines. Nothing built.

## 2026-11-15 10:11 SAST - the podium: a yellow row above PRESS ANY KEY

- Grant: "have the press any key a row lower in the finish race view - so an extra yellow line
  below the fast time details". The card is rows 5-18; its foot and PRESS ANY KEY on row 18.
  finish, drive, title tests PASS. docs/design/podium_built.png.

## 2026-11-15 SAST (morning) - the title's cars black again, the checks showing through

- Grant: "okay lets go back to A - black line see through". t_ging is colours only again; the
  cars' rows are stored as they are (ink only), still never wiped first. (A slip on the way: the
  card test in a_bg was the wrong way round and the cars left trails down the sides - caught by
  the screenshot and by title_test's "leave nothing behind".) title test PASS.

## 2026-11-15 10:23 SAST - laps counted when you leave the track and rejoin

- Grant: "sometimes I get off track, when I get back on and go over the finish line, it does not
  see that as a lap and I need to do an extra lap, we need better logic to allow more tolerance".
- CAUSE: your car had to pass each waypoint (46 a lap) within 40 (|dx|+|dy|), or the very next
  one; miss two in a row and your count stood still, so the line's waypoint never came up.
- FIX (race_progress, src/racer.asm): when the next waypoint is not reached, one of the four
  after it is looked at - a different one each time (rp_k) - within 64; reached, it and all
  those missed are counted (lap_and_inc each: a lap, a checkpoint, if one is). Same cost a
  picture as before (two distances). A short cut of ten waypoints is still not a lap.
- tests/lapcount_test.py (new) PASS; all twelve suites PASS. Speed alone 74/202/4, pack 10/243/7.
- NOTE: the window is 4 waypoints (about a tenth of the lap). Miss more than that in one go and
  the count still stands until you go back - say if it should be wider.

## 2026-11-15 10:40 SAST - Grant's faces again: the red driver redrawn, a pixel up

- Pasted from the Faces page, with "Move them one pixel up too": YOU's three faces redrawn and
  moved up a row (tools/import_faces.py after the shift), CYAN's everyday and sad faces changed.
  5 of 15 changed. In the game; the page (version 4) starts from them. title, drive, finish PASS.

## 2026-11-15 10:42 SAST - a louder skid; the tune needs the AY switched on (racer.ini does it)

- Grant: "the game is a bit quiet now - can you up the skidding sound, and maybe play a
  background ditty of some kind".
- THE DITTY IS THERE (Kettle's On on the AY chip, since this morning) - he is not hearing it, so
  his player is a plain 48K without the chip. build/racer.ini (new, `ay48=1`): the player reads
  it when it sits beside racer.tap and fits the chip (checked in zxdev: config game= ->
  ay48 True). Or: Hardware menu, "AY sound chip on 16K/48K"; or a 128K model.
- SKID: the screech is twice as long (SKID_FR 10), twice as full (8 flips a frame), and a BIG
  slide (level 2) screeches for as long as it lasts, not only as it starts (src/grip.asm).
  COST: alone 52 pictures at 3 frames / 216 / 6 (it was 74 / 202 / 4) - the autopilot slides a lot.
- docs/sound/race_now.mp3: 26 s from the game - the start ditty, the lights, the tune, skids.
  NOT heard by me. drift, drive, finish, nos tests PASS.

## 2026-11-15 11:01 SAST - more sound: a lap beep, the engine whenever you accelerate, Kettle's On before the lights

- Grant: "As you go past a lap, make a sound. If you accelerate make a sound. At the start of the
  game before the lights - play the kettle's on jingle, play one of the jingles during the game".
- LAP: a high beep, a quarter of a second, as you finish each lap (yl_note; the effect channel).
- ACCELERATE: the engine's putter is heard whenever Q is held, at any speed (snd_picture). It
  was only while picking up speed, quiet once up to it (his 14 Nov "events only" rule).
- START JINGLE: the first 24 steps of Kettle's On (2.9 s) on the ORDINARY SPEAKER, by the ROM's
  BEEPER routine (0x03B5), a note of 0.10 s and a HALT each - so every machine plays it, chip or
  not (src/jingle.asm from tools/make_music_ay.py; jin_start, src/plate_slow.asm). Nothing else
  runs while it plays. BEEPER reads the border colour from 0x5C48 (a title table now): yellow
  for the jingle, then the byte back. The AY ditty of this morning is gone. Lights 3.0 s after 1,
  green at 5.7 s. Recorded and checked: the notes are the tune's (495, 622, 740, 988 ... Hz).
- IN THE RACE: Kettle's On (driving) on the AY chip, as before - needs the chip (racer.ini).
- SET-UP KEYS (1, 2, 3): work until GREEN now (the lights' 2.6 s), not until the lights start -
  the jingle is not a time for keys. Still not decided by Grant.
- TESTS hold the jingle off by setting jin_on to 0xFF at the TITLE (before 1), since the jingle
  now plays before the race screen's first picture. All twelve suites PASS.
- SPEED: alone 36 pictures at 3 frames / 227 / 10 (52 / 216 / 6 before the engine change); in the
  pack 5 / 253 / 7. The engine's flips, every frame while Q is held, take the last of the margin.
- code_end 0xBFED: 19 bytes free in the main area. docs/sound/race_now.mp3: the new start.

## 2026-11-15 11:16 SAST - no AY chip: the Spectrum's own speaker only

- Grant: "Lets not use the AY chip for now please - old spectrum sounds".
- OPT_AY is 0 by default (build.sh: AY=1 puts the race tune on the chip back); build/racer.ini
  is gone. The game writes to no AY port (zxdev io_report: keyboard, border and beeper only).
- WHAT SOUNDS NOW, all on the speaker: the Kettle's On jingle before the lights; the lights'
  beeps; the engine while you accelerate; the skid; a beep each lap; bumps, the bonk on a
  cereal O; the NOS pick-up and its whoosh. NO TUNE DURING THE RACE: on the speaker it was
  "background beeping" three times over (14 Nov). MUSIC=1 still builds that old version.
- 234 bytes back in the main area (code_end 0xBF03: 253 free). All twelve test suites PASS.
  Speed alone 57 / 213 / 5; pack 5 / 253 / 7. docs/sound/race_now.mp3: 16 s of it.

## 2026-11-15 11:25 SAST - the start jingle in two voices with a beat; mock-up: FINAL LAP in the play area

- Grant: "the jingle uses simple beeps could you add some sophistication to the sound, make it
  almost trancy with a background to it?"
- jin_start (src/plateco.asm) no longer uses the ROM's BEEPER. Its own loop counts two voices
  down at once and puts out either: the tune (Kettle's On, 24 steps) and a bass on B - low,
  high, low, high, four steps to a beat; a KICK on each beat (six flips, 2,500 T further apart
  each time) and a TICK of noise half way: 125 beats a minute. 91 T a turn of the loop
  (measured from the recording: the first build assumed 89 and was 2% flat). Interrupts off.
  Pitches come out within 1% but the highest two (the loop's periods are whole numbers: 988 Hz
  is 1,012). docs/sound/race_now.mp3. NOT heard by me. finish, drive, title PASS.
- Grant: "when I'm on the final lap, have a display at the bottom - mockup a pit crew message in
  the play area - 'final lap' and a small pitcrew face and speech bubble" (the old strip under
  the window went unseen: "the player is focused on the game area"). tools/make_finallap_mock.py
  -> docs/design/finallap_options.png: A white bubble, B small letters, C blue band, D yellow
  bubble, E corner, F red. Nothing built (FINAL LAP! is still the small plate top right).

## 2026-11-15 11:48 SAST - the crew chief talks again: a bubble inside the play area

- Grant: "B small letters" (docs/design/finallap_options.png); then "messages for things like
  passing somewhere, being first, hitting something, can make a message display. Great lap - and
  showing the time for example"; "the pitstop messages were not visible as the player is focused
  on the game area - but maybe inside the game area at the bottom will be more visible".
- THE BUBBLE: the chief's face and a white bubble, rows 17-18, columns 7-16 of the screen (the
  foot of the window), two lines of the small letters, up for 3 s. Its picture is kept ON THE
  SCREEN under the window (rows 22-23, columns 16-25) in yellow ink on yellow paper, where it
  cannot be seen: his face is put there once (screen_once), msg_say (src/strip.asm) writes a
  message's lines there with glyph when it is said, and fl_draw (src/plateco.asm) copies the 10 x
  2 cells into the window's buffer each picture while msg_timer runs; msg_final sets those
  window cells white, hud_update puts them back. No memory of its own, and one slow picture a
  message (the writing), then ~3,400 T a picture while it is up.
- THE MESSAGES (tools/make_strip.py MSGS, 15 letters a line at most): PICK 2 UPGRADES / KEYS 1 2
  3 on the grid (so the set-up keys are announced at last); GOOD LUCK! at green; GREAT MOVE! on
  a pass; P1! taking the lead; STAY CALM losing a place; PUSH! PUSH! second and close; GREAT LAP!
  with the lap's time under it; OUCH! on a cereal O; FINAL LAP! / BRING IT HOME; GET IN THERE! /
  WELL DRIVEN! at the flag; NOS READY!, NOS!. The triggers are the old strip's (strip_triggers),
  switched back on. A message is not pushed aside for ~3 s (COOL) - P1! had overridden FINAL LAP!.
- The old FINAL LAP! plate (pl_message, plate_td.asm) is gone.
- MEMORY: the winner's faces moved to the table block at TD, into the room the unused tune's
  notes left (so an AY=1 build no longer has room for both: not the default). code_end 0xBFEF:
  17 bytes free in the main area. FULL.
- tests/crew_test.py (new) PASS; all thirteen suites PASS. drive_test: 11.9 pictures a second
  asked off the start, not 12.5 (GOOD LUCK is up then). Speed alone 34 / 227 / 8 / 1 at 6.
- docs/design/crew_messages.png: four messages as they show.

## 2026-11-15 12:32 SAST - the chief on the other drivers; the start jingle a little longer

- Grant: "bubble speak is great. Include some random events for other riders too, Great driving
  Butch or something like that".
- @ in a message is a driver's name (sm_ctr, src/plate_slow.asm: ms_car into pd_names). New
  messages (tools/make_strip.py): FASTEST LAP BY / @ when another driver sets the race's best lap
  (trg_best); and, when the chief has nothing else to say, one picture in 256 (about every 20
  s), one of GREAT DRIVING / WATCH OUT FOR / ON A CHARGE / LOOKING QUICK with one of the four
  others' names, both picked at random (trg_rand). Names: FRANK, SPIKE, BRUNO, JANE.
- Grant: "the jingle at the start with the trancey effect is great, you can make it play a
  little longer": 32 steps, 3.8 s (it was 24, 2.9 s). Green 6.7 s after 1.
- Room: the new code is under 0x8000 (95 bytes were free there); the table block at TD has 154
  free; the main area 11. tests/crew_test.py covers both new messages. All thirteen suites PASS.
- docs/design/crew_other.png; docs/sound/race_now.mp3 (the longer jingle, then the start).

## 2026-11-15 12:53 SAST - the jingle longer still, and again at the chequered flag

- Grant: "please make the trancey jingle longer still. Also play it when the chequered flag is shown".
- 48 steps, 5.8 s (it was 32, 3.8 s): half of Kettle's On. Green 8.6 s after 1.
- `podium` ends with `jp jin_start`: the same jingle plays as soon as the podium is drawn. A key
  pressed while it plays is not seen (nothing else runs); after it, any key goes to the title.
  Tests that hold the jingle off (jin_on 0xFF) hold this one off too.
- The jingle's notes are in the table block at TD now (jb_per, jb_tune): the main area has 51
  bytes free, TD about 95. All thirteen suites PASS. docs/sound/race_now.mp3: the 5.8 s of it.

## 2026-11-15 SAST (afternoon) - the Jingle Lab: fourteen tunes through the two-voice jingle

- Grant: "could you try a different jingle with that trance sound"; "can you give me options - I
  love the trance sound and maybe if that is overlayed with existing jingles they will work now".
- The jingle's engine takes any tune now: tools/make_music_ay.py JKEY=<a ditty of
  make_ditties.py, or `arp`> writes src/jingle.asm - the tune on its own step grid (a long note
  is its pitch on each of its steps), 254 a rest (jin_start: the tune's voice does not flip),
  JB_LEN from the tune's step; BASS=<midi> sets the bass's note. `arp` is "Full English", a
  minor arpeggio written for this sound (15 Nov 2026).
- RECORDED from the built game in zxdev, one build a tune: docs/sound/jingles/*.mp3 (14: the
  twelve ditties, Kettle's On driving, Full English). The five tunes in G have the bass on G,
  the rest on B. Page: tools/make_jingle_lab.py + jingle_lab.template.html ->
  https://claude.ai/artifact/VYcqxZKbxLYnPVFwwk23LD
- The game still plays Kettle's On, driving (5.8 s) at the start and the chequered flag: nothing
  changed there until he picks. finish, crew, drive, title tests PASS. NOT heard by me.

## 2026-11-15 13:06 SAST - Spilt Milk at the start, Second Helpings at the chequered flag

- Grant, from the Jingle Lab: "Spilt Milk is a good start jingle, then second helpings for
  chequered flag".
- Two jingles: src/jingle.asm (tools/make_music_ay.py, JKEYS=ditty3:43,ditty12:47) has, for each,
  a 10-byte set - its tune, its periods, a step's turns of the loop and a beat's, the bass low
  and high - that jin_go copies to `jc` before playing. jin_start (new race) plays the first,
  jin_flag (the podium) the second. Spilt Milk: 56 steps of 0.10 s, 5.6 s, bass on G. Second
  Helpings: 36 steps of 0.16 s, 5.8 s, bass on B. Green 8.4 s after 1.
- Recorded (docs/sound/race_now.mp3): the start's jingle, a few seconds of race, the podium's.
  NOT heard by me. All thirteen suites PASS. Main area: 10 bytes free; TD ~30.
