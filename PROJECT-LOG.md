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
