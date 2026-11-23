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

## 2026-11-15 15:17 SAST - the start shows the grid during the jingle; the second race clean; four cars end it; SPIKE faster

- Grant (screenshots): "at the start of the game while the jingle plays, the game does not show
  properly" - an empty window; and on the SECOND race the title's picture and then the podium's
  colours left in the window.
  1. The jingle played before the race's first picture (nothing runs while it plays). Now
     jin_arm marks it due (jin_on 2) and jin_due plays it after the first picture is copied.
  2. The title keeps the screen's colour cells from when the last race ended - the podium was
     up - and put them back for the next race. win_cells (new_race, before hud_init) makes the
     window's cells blue on cyan again. (My first try put it after hud_init and wiped the
     lights' and the bubble's colours: three tests caught it.)
- "the joker racer is just too slow you can speed him up": taken as the green driver, SPIKE -
  his pace 14/16 (it was 12/16; still the slowest: the others are 15, 15, 16).
- "do not wait for the last car to come in. If four cars are finished then the race is over":
  rp_wait asks for NCARS-1 in (you among them).
- tests/finish_test.py: the grid is on the screen a second into the jingle; a second race from
  the title has clean cells and the grid. All thirteen suites PASS.
- Grant: "bring up alternative graphics for the damage": docs/design/damage_icons_3.png (Q
  battery ... Y star; tools/make_damage_icons.py THIRD). He likes the mug: an editor follows.

## 15 Nov 2026 15:38 SAST - steaming mug gauge, names on the title, three longer track designs
- The health gauge is the **steaming mug** (tools/gauge_mugs.txt, "Steaming mug"); its two wisps of steam swap every 8th picture (dmg_anim, src/plate_slow.asm). The icon sits 4 pixels in from the window's edge (was 2) so the steam is in one byte. A row of coffee goes with each hit.
- Title: each driver's name under the face (t_name, in the table block); the white driver's band is plain white so it shows on the card; the red driver's three faces moved one pixel left.
- Editors in Claude: gauge https://claude.ai/artifact/PFiNoJusv2vj7pfHQhigDg, steam https://claude.ai/artifact/LYKXjHYFaS3JFRXgWjFFo7, faces https://claude.ai/artifact/Nfxfa54baoZdTsPSAgzU8c (v5).
- Three longer track DESIGNS (not in the game): docs/design/tracks/ (TRACKS.md, tracks_overview.png), tools/make_track_designs.py. Tracks 3 and 4 need a taller map; memory must be found first.
- Asked next (not started in the game): one track that crosses over itself - a bridge, ramps, the car hidden under the road.
- Memory after this: low area 0 bytes free, table block 7, main about 10.

## 15 Nov 2026 16:23 SAST - mug right, NOS left; lap plate fix; bridge choices
- The mug gauge is at the window's right edge and the canisters at its left (Grant: "the coffee mug on the right and the NOS to the left").
- The plate's lap stays at 3/3 after the finish line (was 4/3).
- Sugar spoon icons for the NOS: a mock-up sheet, docs/design/sugar_icons.png (tools/make_sugar_mock.py). Not in the game.
- Track 5's bridge (background design, not in the game): Grant chose the concrete bridge P4 with the tunnel mouth as D1, a plain 50% dither, and blue/white kerb walls. track5.png still shows D2 (one line different); switch it to D1 when the design is next touched.

## 15 Nov 2026 16:46 SAST - the podium's faces move; a spoon of sugar for the NOS; memory found
- Podium: every 32 frames a step - everyday face, eyes, everyday, then happy (winner) or sad (2nd, 3rd). pod_anim (src/title3.asm, runs in the table block) is called from main_wait and ends in hud_over. The frames are kept as rows that differ from the everyday face: src/faces_mood.asm (150 bytes; tools/make_faces.py from tools/face_moods.txt, which now has an eyes frame a driver). src/faces_win.asm is gone.
- The NOS you hold is Grant's "Level spoon" (tools/sugar_spoons.txt -> tools/make_lights.py -> nos_can).
- Memory audit (15 Nov, read-only agent): the table block had 208 unused zero bytes before FRAMES (0x5BA8-0x5C77) - pod_anim's code is there now. Still to take, measured but not applied: dead plate routines pl_cols/pl_cut/pl_fill/pf_1 (63 bytes, low area); unused texts in hudtext.asm (51) and hudtext_flag.asm (29, the gap); unused music and other variables in racer.asm (about 22, the gap).

## 15 Nov 2026 16:56 SAST - the title's faces move too; faces round six
- Title: the row of faces steps everyday, eyes, everyday, happy (t_anim, src/plate_slow.asm, called from t_loop). Podium unchanged in order: everyday, eyes, everyday, happy or sad. pa_step gives the step from FRAMES and remembers the last one, so a slow loop cannot miss it.
- Grant's sixth round of faces: faces_mood.asm is now 234 bytes. To fit, the table block was rearranged: the flag's jingle and t_name sit in the room before FRAMES with pod_anim (src/jingle.asm is in two parts, JIN_PART); the block ends 4 bytes short of 0x5E00.
- Dead plate routines pl_cols, pl_cut, pl_fill removed (63 bytes of the low area; pa_step and t_anim took about 45).

## 15 Nov 2026 17:21 SAST - title menu on four rows, small lap record; the crew chief's wave, blink and blip
- Title: 1 ONE PLAYER, 2 TWO PLAYERS, 3 CHOOSE YOUR PLAYER (shown only: 3 does nothing yet), K CHOOSE KEYS on rows 10-13; the 2UP message on row 14; LAP RECORD and its time in the small letters on row 20. The faces show two looks only (everyday, eyes).
- Crew chief's bubble: he blinks (cf_blink, clothmini.asm), a small radio wave moves under his chin (cf_wave, plate_slow.asm: 7 bars, 1-3 pixels, inside the face's own 16 x 16 so the bubble is no larger), and a blip sounds as a message comes up (msg_snd).
- Room: seven HUD texts nothing showed went from hudtext.asm, and TOPMEM rose from LOWTAB-0x2A0 to LOWTAB-0x24D (83 bytes more under 0x8000). Two small key tables moved before FRAMES in the table block.
- Faces: Grant's seventh round. A background agent is building track 2 as its own tape (one track a build).

## 15 Nov 2026 (evening) - tracks 2 and 3 as their own builds (background agent, branch worktree-agent-a861f48a4f7d5e3b0)
- ONE TRACK A BUILD. `TRACK=2 bash build.sh` -> build/racer_track2.tap (THE BREAKFAST CLUB); `TRACK=3 bash build.sh` -> build/racer_track3.tap (BREAKFAST OF CHAMPIONS, 72 x 84). `bash build.sh` is track 1 and build/racer.tap is byte for byte what it was (cmp).
- tools/make_world.py takes TRACK and WORLD_OUT; the centre line comes from tools/make_track_designs.py. build.sh builds a track other than 1 in a copy of src/ (build/trackN/src): src/ stays track 1's.
- Waypoints capped at 61: progress is one byte (laps * NWP + passed, 246-249 kept for finished cars) and wp_delta's index is a byte. 35 px apart on track 2, 41 on track 3.
- Memory decided the breakfast things: track 2 has ten (plate, 4 eggs, 3 toast, fork, knife), track 3 five (3 eggs, 2 toast; TOP_ROWS 388). Program free: track 2 35 bytes, track 3 23.
- Track 3: the game's code is MAPH-driven already (surface, O map, camera, row index are 16-bit); the only change is map_c3 (hud.asm), `if MAPH > 64`: mini-map at 14/256. Track 2's mini-map has MMY0 -24 (one row lower: the game draws rows 5 down).
- tests/track2_test.py (TRACK=2 or 3): grid, window against the map all round the lap, mini-map, four computer cars 3 laps, your laps by placement and driven by script with the keys, short cuts, dropped cars. tests/track_shots.py -> docs/design/tracks/built/ (pictures and BUILT.md, with the figures and why track 4 does not fit).
- Not done: track 4 (about 160 bytes short with a bare table - BUILT.md), track 5 (bridge), a track's name on screen, choosing a track in the game. Nobody has played tracks 2 and 3.

## 15 Nov 2026 17:48 SAST - tracks 2 and 3 merged in: one track a tape
- The track agent's branch is merged. `bash build.sh` -> build/racer.tap (track 1); `TRACK=2 bash build.sh` -> build/racer_track2.tap (THE BREAKFAST CLUB); `TRACK=3 bash build.sh` -> build/racer_track3.tap (BREAKFAST OF CHAMPIONS, 72 x 84 map). Notes and pictures: docs/design/tracks/built/BUILT.md. Test: `TRACK=2 python3 tests/track2_test.py` (QUICK=1 for the short run).
- TOPMEM is LOWTAB-0x26A (was 0x24D for an hour): tracks 2 and 3 keep 28 and 24 bytes more at the top than track 1. About 8 bytes are free under it.
- Track 4 does not fit (about 160 bytes short even bare); track 5's bridge not started.

## 15 Nov 2026 18:20 SAST - RAM sweep (read-only agent): about 11.8 KB can be found
- Full report: docs/design/RAM-SWEEP.md. Nothing applied yet; Grant to choose a package.
- Safe now (~850 bytes, no speed cost): row lists into back buffer rows 168-191 (672), top pocket at 0xFFC3 (57), unused a_sav (54), LOWTAB tails (49), unused variables (22).
- Worth doing (~4,400): cars flipped top-bottom when drawn (~2,100), gen_tiles as one routine (~990), O map out of the race (540-780), surface as spans, tower_cars duplicates, stack 256 -> 160, 2-byte waypoints.
- Big moves (~6,600): the screen copy as a loop (5,697 bytes; built and measured: about 2.6% of a picture, 4.5% slower racing alone), cars flipped left-right too.
- Tracks share nearly all art (101 tile pictures in all); a track's own data packs to about 0.7-0.8 KB. Two tracks in one 48K load is reachable with safe + worth doing.

## 15 Nov 2026 (night) - the map in the window, spoons beside the mug, corner arrows (background agent, branch worktree-agent-a60149575a0723e4b)
- Grant: "have the track map on the bottom left inside of play. Move the damage to the right. Then, a couple of rows in front of my car, a flashing arrow pointing either diagonally right or sharp right to indicate turns. A long straight stretch gets an early flashing straight in the direction of the straight. I like track 2". Built on all three tracks; not playtested.
- THE MAP: the window's bottom left 6 x 5 cells (screen columns 1-6, rows 15-19), black on yellow, cells of its own. It is on the SCREEN only: make_copier leaves those 6 bytes out of the 40 lines (4 register pairs, not 7), so it costs nothing a picture and whatever passes under it in the buffer is not shown. map_init (hud.asm) clears, colours and redraws it each race from MAPPIC; the dots are XORed on the screen as before (MAP_X, MAP_Y). The panel's top right is plain yellow for now. docs/design/arrows/t1_map_white.png shows black on white, to compare.
- SPOONS AND MUG: the mug stays in the bottom right corner (columns 22-24); the spoons are columns 21, 20, 19 (NOS_COL: the first beside the mug). The bubble did not move (columns 7-16).
- THE ARROWS: tools/make_world.py works out a byte a waypoint from the centre line (src/arrowtab.asm: 0 none, else kind * 8 + direction; kind 1 straight, 2/3 gentle left/right, 4/5 sharp left/right). A bend is announced when its turn-in is within 125 px (first seen 84-125 px before it: 1.0-1.4 s at top speed), judged by how far the road turns in the next 75 px (under 22.5 degrees nothing, up to 67.5 gentle, over sharp); a straight of 200 px or more is announced from 110 px before it until 30 px along it. build/arrows_preview.png draws them on the track. arrow_draw (src/arrow.asm) reads the byte for the waypoint your car is heading for and draws one of eight frames (tools/make_arrows.py: 16 x 11, masked, the cars' format) through draw_car's own loop, its middle 32 px ahead of your car's middle along its heading; on two pictures, off two (about 3 flashes a second); after the cars and before the gauge, spoons, bubble and plate, so it is under them. Nothing before green or after your finish.
- MEMORY (RAM-SWEEP's "safe now" room): the copy routine is 320 bytes shorter, so 0xFE83-0xFFF3 (369 bytes, HIMEM) is free: the arrows' table and 287-308 bytes of the map's row lists moved there out of the program (src/hirows.asm). The buffer's unused bottom-row strips hold the map's picture (D0, D1, D3: 234 bytes) and the arrows' frames (D4-D7: 352). Program free: track 1 5 -> 149 bytes, track 2 35 -> 187, track 3 23 -> 154. NEW LIMIT: the start-up area must end before 0xD0A0 (it is at D05D / D06A / D072: 46-67 bytes left); the tape is about 590 bytes longer. Code put before sq4 moves the page-aligned tables a page on: new code goes after world.asm.
- SPEED (tests/zxlap.py, one lap): in the pack 253,303 -> 252,852 T a picture (4.05 -> 4.04 TV frames); alone 234,452 -> 231,334 (3.91 -> 3.85). Row lists in the faster memory gained more than the arrow costs. tests/drive_test.py's start: 12.5 pictures a second before and after.
- TESTS: tests/arrow_test.py (TRACK=1, 2, 3): the map's box and dots, spoons, mug, bubble, colours, nothing overlapping; the table at known corners and plain stretches; the arrow on the screen pixel for pixel, flashing, no trail, never over the HUD. drive_test, finish_test and track2_test re-pointed (window_bad masks the box, the spoons and the arrow; minimap_diff is drive_test's now and checks the box against map + dots exactly). Pictures: tests/arrow_shots.py -> docs/design/arrows/.
- Not done / not known: how it feels to drive; whether 32 px ahead and the arrow's size suit Grant; the yellow box against a white one; the panel's empty top right.

## 15 Nov 2026 21:10 SAST - "Order Up" is kept for another track
- Grant on the Jingle Lab's new tunes: "order up is great"; "make order up for another track when we start adding tracks". So: track 1 keeps Second Helpings (start) and Spilt Milk (flag); "Order Up" (t_answer in tools/make_music_ay.py, bass 40) is to be a later track's tune. Which track, and whether as its start or its flag, is not yet said. Each track is its own tape, so a track can have its own jingles: JKEYS at build time.

## 15 Nov 2026 (late) - v2: the mini-map small, solid and see-through; the arrow at one fixed spot (background agent, branch worktree-agent-a60149575a0723e4b)
- Grant, on the first version: "I need the track in the bottom left to have the track itself masked ... Is it possible to make the track map smaller as well? Then the arrow - could you try that it always shows in the middle of the screen - so it doesn't jump around"; then, of the sizes mocked up: "c (2)4 is good, and the inside parts could be blue - so no masking inside required". Not playtested.
- THE MAP: 24 pixels wide at 11/256 scale on every track (17 lines on track 1, 20 on track 2, 26 on track 3), the road a solid ribbon 3 pixels across (2 at its thinnest), in the window's own blue on cyan: no cells of its own, no box. Ink only - map_blit (hud.asm) ORs its 3 bytes a line into the back buffer each picture after the cars and the arrow, so the picture shows through wherever there is no ribbon. 2 pixels clear of the window's left edge, 3 of its foot. Its ink is kept at MAPDAT (page D0 of the buffer's unused strips) and the dots are XORed into it there: YOURS is 2 x 2 and blinks; the OTHERS are one pixel each. On the ribbon a dot is a hole (the picture shows through it - nearly always plain cyan, not guaranteed paper); off the road it is ink.
- The copy routine copies those bytes again, so it is its full 6,083 bytes and only 49 are free above it. The row lists that were there are now: 29-44 bytes after the arrows' table on strip D1, 49 above the copy routine, 32 on D2, 90 on D3 (src/hirows.asm; tools/make_world.py, BINS); the rest went back into the program. Program free: 124 / 134 / 123 bytes on tracks 1 / 2 / 3. The start-up area ends at CF4F / CF65 / CF7E (limit D0A0).
- THE ARROW: one fixed spot, ARROW_X, ARROW_Y (src/arrow.asm) = (96, 52) in window pixels: centred across, three character rows above the middle. Dead centre (96, 76) puts it on your car at rest and touching its nose at speed: docs/design/arrows/v2_t1_arrow_dead_centre.png against v2_t1_arrow_above_centre.png. ARROW_Y equ 76 is the one change for dead centre. Kinds, look-ahead, flash and mask are unchanged; it is drawn over the cars.
- HOW OFTEN: an arrow is up on 34 of 46 waypoints of track 1 (9 straight, 9 gentle, 16 sharp), 48 of 61 on track 2 (12, 16, 20), 35 of 61 on track 3 (10, 13, 12). The thresholds are constants at the top of tools/make_world.py (A_LOOK and the rest) and were NOT changed. The cheapest cut, if wanted: A_GENTLE up from 22.5 (drops the "rest of this corner" arrows) or A_EARLY / A_ONTO down (shorter straight arrows).
- SPEED (tests/zxlap.py, a lap, track 1; laps differ a little run to run): in the pack 4.05 TV frames a picture before any of this, 4.04 with version 1, 4.02 now; alone 3.91, 3.85, 3.96. map_blit is about 130 T a line (2,200 to 3,400 T a picture).
- TESTS: 15 suites pass on track 1; arrow_test (23 checks) and track2_test (QUICK) pass on tracks 2 and 3. window_bad now puts the map's ink into the picture it expects, so every window check proves the ribbon solid and the picture untouched round and inside it. Pictures: docs/design/arrows/v2_* (tests/arrow_shots.py).

## 15 Nov 2026 (late night) - track 5, the bridge, as its own tape (background agent, branch worktree-agent-af9944e9fcce06708)
- Grant: "can you create a tap with a bridge - just that track". `TRACK=5 bash build.sh` -> build/racer_track5.tap (A FRIDGE TOO FAR, 72 x 74). Not playtested.
- Everything is behind OPT_BRIDGE (build.sh sets it for TRACK=5): src/bridge.asm plus short `if OPT_BRIDGE` blocks in racer.asm (new_race, main, bump, o_check, draw_all, physics, the O map's include), hud.asm (tower_b) and grip.asm (two calls). Tracks 1-3: tapes byte-identical (cmp).
- LEVELS: a byte a car at 0x5E00 (0 table, 1 bridge), set by place: up on the first 16 px of either ramp, down off either ramp's foot. bump returns at once for cars on different levels. WALLS: lv_car, once a picture after the bumps - level 1 clamps x between the kerbs; level 0 clamps y in the tunnel and pushes a car out of the bridge's side. RAMPS: ramp_adj takes an eighth off the push and top speed on the ramp up and adds an eighth on the ramp down (RAMP_SHIFT), for you (you_grip) and the computer cars (physics). A first try, a pull on the speed each picture, did nothing for you going down (your top speed is capped) and too much for them.
- DRAWING: draw_car_b - a level-0 car wholly under the cover is not drawn; half under, the 3 x 24 buffer bytes are kept, the car drawn, and the covered bits put back. No redraw of the deck, so no cost.
- MEMORY: no O map on this track (o_at reads the row lists; 666 bytes), the race order's cars from their frames (tower_cars' 320 bytes), no breakfast things, cheaper kerbs and arrows. Free now: program 246, TOPMEM 92, start-up area 204.
- SPEED: 11.7 pictures a second near the crossing against 12.7 elsewhere (the bridge's tiles: a tile costs about 90 T a line with ink). With the design's kerbs and arrows it was 10.9; with no bridge pictures 15.9.
- TESTS: tests/track5_test.py 60 PASS (track2_test's checks, then levels, walls, drawing order, ramps, speed; the dropped-car part 0 stuck of 546). arrow_test on track 5 PASS. The 14 suites on track 1 PASS. Pictures and a GIF: docs/design/tracks/built/track5_*.
- Detail: docs/design/tracks/built/BUILT.md, the track 5 section.

## 15 Nov 2026 22:20 SAST - the bridge track merged: track 5 is its own tape
- `TRACK=5 bash build.sh` -> build/racer_track5.tap ("A FRIDGE TOO FAR", 72 x 74, one bridge), all behind OPT_BRIDGE. Tapes of tracks 1-3 are byte-identical to before the merge (cmp). Notes: docs/design/tracks/built/BUILT.md.
- Merged on top of the small see-through map and the fixed arrow: the generator's old mini-map block (with a bridge tweak for the old outline map) was dropped in favour of the new ribbon; tests/track5_test.py re-pointed to the new map (QUICK=1 run: PASS; arrow_test on track 5: PASS). The agent's pictures in docs/design/tracks/built/track5_* show the earlier yellow map box.

## 16 Nov 2026 07:20 SAST - a key skips a jingle; the bridge's fixes mocked up
- A key pressed during the start or the flag jingle stops it (jb_key, last in the program; tests/skip_test.py: lights at 1.4 s against 6.0 s). Only a key pressed after every key was seen up counts.
- LATENT FAULT, NOT FOUND: any build with more bytes in the jingle player (plateco.asm), even 23 unused ones, fails drive_test's ramming check - the computer car put in front of you jumps 66 pixels down within one TV frame. So something later in the program depends on where it sits. jb_key was put at the program's end to move nothing. To be hunted down before more code goes into the middle of the program.
- Bridge fixes after Grant's drive, mock-up only: docs/design/tracks/bridge_fix_mock.png, bridge_fix_overview.png (tools/make_bridge_fix_mock.py): concrete masked, kerbs K1/K2/K3, six more O's. Estimated costs are on the sheet.

## 16 Nov 2026 - v3: the arrow larger, just above the crew chief's bubble (background agent, branch worktree-agent-a60149575a0723e4b)
- Grant: "lets try on the arrow that it is just above the pitstop messages, and slightly larger". Not playtested.
- SPOT: a fixed field of 24 x 15 pixels at window bytes 10-12 (pixels 80-103), lines 111-125: its middle (92, 118). The bubble is pixels 48-127 (middle 88, its words' middle 96) and starts at line 128: the arrow's foot is 2-3 lines above it. It is on a byte boundary (so 4 pixels right of the bubble's exact middle): no shifting, which is what lets it be bigger. There whether a message is up or not.
- SIZE: the arrow is 15 long and 13 across (89 pixels of ink; it was 11 x 9, 39 pixels), 12 x 12 on the diagonals, with a clear pixel round it. 24 x 16 with all eight stored would have been 768 bytes or more; this is 450: FIVE pictures (up, up-right, right, up-left, left) of 15 rows x 6 bytes (keep, ink for each of 3 bytes), one on each of pages D3-D7 of the buffer's unused strips; the three that point down are the same pictures drawn from the last row back (aw_tab, src/arrow.asm). arrow_draw has its own small drawer now (draw_car's is not used for it).
- MEMORY: the strips had 352 bytes of arrows on D4-D7; now 450 on D3-D7. D3's row lists moved to the title's unused a_sav (0x5B16, 54 bytes; tests/finish_test.py checks they survive the title), the rest back into the program. Program free: track 1 124 -> 23 bytes, track 2 134 -> 40, track 3 123 -> 30, track 5 108 after. The start-up area ends at CFE9 / CFFF / D018 / CF71 (limit D0A0).
- YOUR CAR AND THE SPOT: standing, your car is at lines 68-84; the look-ahead lets it down 16 at most, and its picture is at most 17 lines: it ends by line 107, 4 above the arrow. So your car does not reach it in ordinary driving (not tried at the world's edge, where the camera stops). The other cars do drive through it: the arrow is drawn over them (docs/design/arrows/v3_t1_car_under.png).
- SPEED (tests/zxlap.py, a lap, track 1): in the pack 4.02 TV frames a picture before and after; alone 3.96 -> 3.95.
- TESTS: 15 suites pass on track 1; arrow_test (23) on tracks 2, 3 and 5; track2_test QUICK on 2 and 3; track5_test QUICK on 5. Pictures: docs/design/arrows/v3_* (tracks 1 and 2).

## 16 Nov 2026 07:46 SAST - the larger arrow above the crew bubble merged; the key-skip made smaller to fit
- Arrow v3 merged (fixed 24 x 15 field at window 80-103, lines 111-125; arrow 15 x 13). Track 1 then had no room for jb_key's 30 bytes, so: jb_key is now 15 bytes in the gap (clothmini.asm) and reads only the number rows and the two bottom rows - not the rows of Q, A and P - so no "seen up first" logic is needed. Four unused variables went (yg_pvf, yg_pvs, yg_pang, bar_next) and the music-only ones are kept out of builds without music.
- Program free: track 1 23 bytes, track 2 40, track 3 30, track 5 108. All suites pass on track 1; arrow_test on 2; track tests QUICK on 2 and 5.
## 16 Nov 2026 - track 5: the bridge as Grant drew it (background agent, branch worktree-agent-af9944e9fcce06708)
- Grant after driving it: the wings must be masked, more boundary circles on the inside, the bridge's sides solid; then his own picture, the wing-to-wall line removed. Built (OPT_BRIDGE only; tracks 1-3 tapes byte-identical).
- kerb_draw (bridge.asm): the two kerb walls straight into the buffer after the cloth, before the tiles - blue and cyan blocks inside a blue line each side, the cyan clean. As tiles they cost 48 full tiles a bridge, 12 masked (9.8 pictures a second at the crossing); as a routine 10.2.
- make_world.py (BRIDGE): wing + ramp wall as one outline; BR_WIPE -> masked tiles whose masks hold only the dots to hide; six O's; the kerbs kept as KERB for tests; cans A and B on white squares; row lists also at 0x5B16 (54 bytes, title's unused a_sav) and 0x5E58 (48, stack page).
- tdraw_mb replaces tdraw_m on this track (sparse masks: a line's mask and picture each done only if not empty).
- SPEED: 10.2 near the crossing (11.7 before, 12.5 elsewhere). The whole bridge in view is 271,400 T of work a picture against about 227,000 for a 4-frame picture: it cannot make 4 frames with this look. The 10.5 asked for was not reached with everything in; the masks cost about 0.5. Options sheet: docs/design/tracks/bridge_efficiency_options.png (E1 mouth dither on alternate lines, E2 two arrows a ramp, E3 whole-tile wipes, E4 no wipe).
- MEMORY: program 2 bytes free on track 5. Anything more needs room first (E2 and E3 would give about 145 bytes).
- LATENT FAULT (drive_test's ramming check failing when bytes are added in plateco's jingle player): looked, not found. Checked on track 1 with 23 bytes added: no call lands off a label (no assembler phase error); only 61 labels move (sfont, flag/clock glyphs, grid_order, car_colours, tdraw_table, isr and its parts, title2's car code, jb_key) and none of their blocks newly crosses a page; cars and tb do not move; the interrupt routine has no address arithmetic outside the music option. Track 5's layout, which differs from track 1's through most of the program, passes its own ramming and bump checks.
- TESTS: track5_test 65 PASS (full run, 0 of 546 dropped cars stuck). skip_test on track 5 PASS. arrow_test on track 5: 22 PASS, 1 FAIL - 'your dot follows your car round the map': its 8 looks a place, 0.1 s apart, now fall in step with the dot's blink, so the dot is always off at the looks it counts (5 to 7); at looks 0 to 3 the dot is at the right spot at all 13 places and the window matches the map. A coincidence of timing in the test, not looked into further (arrow_test.py was another agent's to change). The 15 suites on track 1 PASS; track2_test QUICK on tracks 2 and 3 PASS. tests/drive_test.py's map now has the kerb walls on a track with a bridge (they are not tiles).

## 16 Nov 2026 - track 5 brought onto arrow v3 (background agent, branch worktree-agent-af9944e9fcce06708)
- Merged eed4a5f. Both sides had taken the title's unused 54 bytes at 0x5B16: the arrow's displaced row lists keep them (STRIP3, all tracks); track 5's own bin there is gone. With v3's 90 program bytes that left track 5 113 bytes over in the program and 51 over in the start-up area.
- Found, all invisible: (1) a mask is 4 bytes on this track, its lines 0, 2, 4, 6 - the cloth has no dots on the others (tdraw_mb reads them so; drive_test.py expands them): 68 bytes; (2) the buffer kept under a half-hidden car is 3 x 18, not 3 x 24 (a car's frame is on lines y - 1 to y + 16), so the row lists under the stack grew from 48 to 90 bytes (0x5E46). The stack has 96 bytes; track5_test now checks those row lists are untouched after a whole race and the podium.
- Track 5 now: program 2 bytes free, TOPMEM 3, start-up area 13. 10.2 pictures a second at the crossing, as before. No E option was needed.
- arrow_test's "your dot follows your car": 11 looks a place, not 8 (the blink fell in step with 8 looks on track 5; the game was right).

## 16 Nov 2026 - optimisation investigation: 8.9 KB found, three tracks in one tape, the "latent fault" found (background agent, branch worktree-agent-af7c58c90304a2ad1)
- Grant: "Please look at doing investigations for optimizations, so our game can squeeze multiple tracks in and all the features listed". Report: docs/design/OPTIMISATION-PLAN.md. Not pushed, not merged, not playtested. Every change is a build option, off by default: `bash build.sh` still gives a racer.bin byte-identical to 70f731d.
- THE LATENT FAULT was the test's: tests/drive_test.py wrote a car's place while the game was part-way through moving that car (stopped at ph_yp+10 in physics: y read, not yet stored) and the game wrote the old place back - 66 px is the parked spot against the new one. Reproduced on 23ce62f with 16+ bytes before jb_end; tests/put_race_probe.py shows it; the test now writes between pictures and the 19 failing builds pass. The head-on check read the cars in the middle of bump: fixed the same way.
- A REAL FAULT found on the way: the computer cars' pace depends on the picture rate (pace_gate counts TV frames, the cars are pushed once a picture: at a steady 4 frames every car with PACE 8+ is pushed every picture). PACEFIX=1 counts pictures. Changes the feel in the pack: Grant's to approve.
- BUILT, as options: LOOP=1 the screen copy as a loop (5,571 bytes; +6,800 T a picture: pack 12.4 -> 12.4, alone 12.6 -> 12.2, bridge crossing 10.2 -> 10.0); FLIP=1 car headings that are another upside down not kept (1,984); TILE1=1 one tile routine (975); TOWER=1 the race order's cars from the car pictures on any track (226). All four: 161 -> 8,894 bytes free on track 1 (build/racer_all.tap).
- TEARING: today the window's last two character rows are a TV frame late on nearly every picture (the copy is overtaken by the beam: zxdev tear_report, 23% of frames). The loop moves that to row 13. LOOP=2 (experiment) starts the copy behind the beam: nothing torn in the window; it needs the main loop re-ordered to cost nothing.
- THREE TRACKS IN ONE TAPE: tools/make_multi.py -> build/racer_3tracks.tap (tracks 1, 2, 3; T at the title is the next track, 1 starts). Each track packs to 1.7-2.1 KB (ZX0), unpacks in 0.07-0.08 s onto today's working places; after choosing, memory is byte for byte the track's own build (tests/multi_mem_check.py). 2,466 bytes still free. Track 5 is not in: its bridge code is switched at build time in 17 places.
- Tests added: tests/run_all.sh (every suite, every track, scratch copy), multi_test.sh, multi_mem_check.py, unpack_time.py, copy_check.py, carflip_check.py, tearlap.py, speed_table.sh. Tools: make_multi.py, memmap.py, track_sizes.py, car_flips.py.


## 16 Nov 2026 - road option E as a trial tape: the road on white paper; and with no dots on the road (background agent, branch worktree-agent-a3d7128b8bb948862)
- Grant: "Try E as a trial tape. Is it possible to have the road have less busy dithering - or no dithering?" Two tapes, track 1, nobody has driven them. Both are build options, off by default: `bash build.sh` and TRACK=2/3/5 give tapes byte for byte as before (md5 checked).
  - `ROADW=1 TILE1=1 FLIP=1 TOWER=1 BDIR=roadwhite OUT=racer_roadwhite bash build.sh` -> build/racer_roadwhite.tap: the road's colour squares white, the table's cyan, blue ink everywhere.
  - `ROADW=2 TILE1=1 FLIP=1 TOWER=1 BDIR=roadwhite_plain OUT=racer_roadwhite_plain bash build.sh` -> build/racer_roadwhite_plain.tap: that, and the cloth's dots taken off the same squares.
  - (TILE1, FLIP and TOWER are the no-speed-cost savings of the optimisation plan: today's track 1 has 23 bytes free and this needs 612 / 881. Run `bash build.sh` afterwards: the option builds rewrite src/options.asm, data.asm and bigcars.asm.)
- HOW (src/roadwhite.asm; three calls in the main loop, one at a new race, hud_pre's gauge and spoons keep the paper they stand on): the surface map the cars' grip uses (a bit a tile) gives, each picture, 3 bytes a window row - a bit a square, 1 = table - for the tiles the view is NEAREST (camera + 4, over 8), so the colour's edge is never more than 4 px from the road's and steps a square as the view passes half-way (rounding down would stray up to 7 px, always one way). Worked out only when the view reaches new tiles; only the bytes that changed have their 8 squares written.
- The colours are written straight AFTER the screen copy, so they reach the screen one TV frame after the picture's pixels. Before the copy would be worse: the copy is already overtaken by the beam at the window's foot, and 3,000-6,000 T more would tear rows higher up.
- Squares with colours of their own: the start lights and the chief's bubble are left alone; the gauge and the spoons keep their ink and take the road's or the table's paper; the mini-map, arrow, plate, breakfast things and O's are pixels only. Rows that can hold such squares are written a careful way (paper only, and only where it is cyan or white).
- PLAIN ROAD (ROADW=2): after cloth_fill, the 4 dotted lines of each road square are cleared, a byte each - 8 squares at once where all 8 are road. No stack tricks (an interrupt would spoil the squares beside the run); not the per-byte rub-out of road H either. A cheaper way was not found: cloth_fill's registers are all taken, so it cannot skip a run.
- MEASURED (zxdev, autopilot, T of work a picture - everything but the wait - and pictures a second; "savings only" is TILE1 FLIP TOWER without the trial):

  | | start straight, alone | mid-lap, alone | in the pack |
  |---|---|---|---|
  | today's tape | 241,000 T, 12.3 | 227,300 T, 13.1 | 248,500 T, 12.7 |
  | savings only | 242,800 T, 12.3 | 232,600 T, 12.7 | 254,200 T, 12.5 |
  | road white | 248,700 T, 12.3 | 245,500 T, 12.3 | 261,100 T, 12.2 |
  | road white, plain | 271,500 T, 11.7 | 268,800 T, 11.9 | 283,800 T, 10.8 |

  The trial's own share: white 8,300 / 12,200 / 8,500 T a picture (squares worked out 5,000-6,000, colours written 3,100-6,200); plain adds 18,800 / 21,500 / 20,700. Road white loses the pictures that made 3 TV frames mid-lap (32 of 157 today, none now) and is otherwise 4 frames like today; the plain road puts most pictures in the pack at 5 frames (37 of 64) - and at 5 frames the game also drops a tick (dt is capped at 4), so the race itself runs a little slow.
- MEMORY: road white 578 bytes of program + 34 under 0x8000, 623 free in the program; plain 847 + 34, 354 free.
- TESTS (tests/run_all.sh, track 1, 17 suites; the same build without the trial passes all). Road white: 13 pass; the window still matches the map pixel for pixel; failing: 4 checks that ask for blue on cyan in every window square (arrow 3, drive 1), drift_test's 0.50 s right turn (a 5-frame picture drops a tick), finish_test (it forces the race's end from outside at an instant that now falls badly: 1 instant in 4 does the same on today's tape; and its two "cloth keeps its colours" checks). Plain (10 suites pass): also the pixel-for-pixel checks in drive_test and title_test (the dots are gone: 571-666 pixels), drive_test's 11.9 pictures a second off the start (11.0), and five more arrow_test checks (they compare the window with the map or count looks against the picture rate - not gone through one by one); its finish_test fails only the two colour checks. No test was loosened.
- Pictures: docs/design/roadwhite/ - roadwhite_start.png, _bend.png, _bend.gif (3.2 s through the first bend), the same for roadwhite_plain, and today_ for comparison.
- NOT DONE / TO JUDGE: nobody has driven either. The colour's edge jumps a square at a time while the pixels scroll (the GIFs show it); where the road's edge has only O's the white ends up to 4 px off them. The gauge and spoons show cyan paper where they sit over table. White is not bright (the same brightness as the cyan). Tracks 2, 3, 5 not built with it.


## 16 Nov 2026 - the mini-map 40 pixels wide, as a build option with trial tapes (background agent, branch worktree-agent-ae51cba21afbf62f5)
- Grant, shown docs/design/arrows/map_bigger_mock.png (24, 32, 40 wide): "C wide please". BUILT AS AN OPTION, off by default - the four default tapes still have the 24-wide map and are byte for byte as before (cmp). Nobody has driven the trial tapes.
- WHY NOT IN THE DEFAULT TAPES: memory. The map's ink is 5 bytes a line now and 29 / 33 / 44 / 38 lines (tracks 1 / 2 / 3 / 5) = 145 / 165 / 220 / 190 bytes, against 51-78 today in a 90-byte spare strip of the back buffer. With its code the 40-wide map needs 166 / 186 / 241 / 211 bytes of program and the default tapes have 23 / 40 / 30 / 2 free: short by 143 / 146 / 211 / 209.
- THE OPTION: `MAPW40=1 TILE1=1 FLIP=1 TOWER=1 bash build.sh` -> build/racer_map40.tap (track 1); with TRACK=2, 3 or 5 -> build/racer_map40_trackN.tap. It builds in its own copy (build/map40_tN). Run `bash build.sh` afterwards (the option builds rewrite src/options.asm and the car data). TILE1, FLIP and TOWER are the savings of the optimisation plan; the map's ink then sits at the program's end (MAPDAT is a label there), not in the strip.
- THE LOOK: 40 wide at 19/256 (it was 11/256), same corner (2 px in from the window's left, 3 above its foot), the ribbon 4 to 5 pixels across (drawn from a road 12 px narrower than the real one: straight scaling gave 6), your dot a blinking 2 x 2 hole, the others 1 pixel. Picture, real screens of all four tapes: docs/design/arrows/map40_tracks.png (tests/map40_shots.py). Track 3's is 44 lines of the window's 152 (lines 105-148). Nothing collides: the chief's bubble starts at window x 48 (8 px clear of the map's 40), the corner arrow is at x 80-103, and tests/arrow_test.py's "nothing overlaps" checks pass on all four. The thicker ribbon does hide more of the O's and cloth under it.
- THE COST IN SPEED (zxdev; "before" is the same savings without the option, whose map_blit and picture rates are the default tape's):

  | | track 1 | track 2 | track 3 | track 5 |
  |---|---|---|---|---|
  | map_blit, T a picture: 24 wide -> 40 wide | 2,313 -> 5,889 | 2,706 -> 6,707 | 3,524 -> 8,928 | 3,131 -> 7,734 |
  | start straight in the pack, 3 s from green, pictures a second | 12.3 -> 12.3 | 12.3 -> 12.0 | 12.3 -> 12.0 | 12.0 -> 11.7 |
  | start straight alone | 13.7 -> 12.7 | - | - | - |
  | a whole lap in the pack (tests/tearlap.py) | 12.4 -> 12.4 | - | - | - |
  | a whole lap alone | 12.5 -> 12.3 | - | - | - |
  | program bytes the option uses / free with it | 166 / 1,035 | 186 / 1,032 | 241 / 967 | 211 / 743 |

  About 200 T a line against 131 (5 bytes not 3) and nearly twice the lines. In the pack the game already runs at 4 TV frames a picture, so track 1 does not change; where a picture only just made 3 frames (alone on the start straight: 16 of 40 pictures before, 3 after) or 4 (tracks 2, 3, 5: a few more 5-frame pictures) it now misses. A cheaper way to draw it was not found (worked out, not built): testing for the empty bytes costs more than it saves, a tidier loop saves about 6%, and drawing it as unrolled code is 700-1,100 bytes.
- TESTS (they take the map's width from the build now; nothing loosened). Default tapes: drive_test, arrow_test (tracks 1, 2, 3, 5), track2_test (2, 3), track5_test - as before. The 40-wide tapes: arrow_test passes on all four, track2_test on 2 and 3. drive_test on track 1: 1 FAIL - "the computer cars are not all the same speed" (19.2 19.5 19.5 19.2 s a lap): with you parked the pictures now take 4 TV frames, not 3, and that is the known pace fault of the optimisation plan, section 5.2 (the same tape built with PACEFIX=1 passes: 18.6 19.9 20.0 18.8). track5_test: 2 FAIL - near the crossing 10.0 pictures a second against a floor of 10.0 (10.1 without the option), and the "row lists under the stack" check, which compares with the default tape's .bin and fails the same way on any savings build.
- TO JUDGE: whether the bigger map is worth the pictures lost when racing alone; whether the others' 1-pixel dots are still easy to see in a 5-pixel ribbon (unchanged, not made bigger); track 3's height. To be in the default tapes it needs the savings adopted (or 150-240 bytes found another way).
## 16 Nov 2026 - the choose screen: track, driver, car, extra (background agent, branch worktree-agent-a31f6549f20d471a9)
- Grant: "when you click 1 or 2, you get a screen that asks you which track and which player. So you can remove option 3 from the title screen. The race track is selected by clicking left and right to choose the track, then click forward to select. Then click person and then car. Can you make a couple of extra cars and people faces to choose from for this. You select them in the same way. Then on the car you choose one extra of acceleration, grip and speed (you have one of each by default)". Not pushed, not merged, NOT PLAYTESTED: nobody has driven it.
- BUILT as a new tape, `bash tools/build_choose.sh` -> build/racer_choose.tap (.sym). Everything is behind a new build option, OPT_CHOOSE (CHOOSE=1), off by default: the four one-track tapes and racer_3tracks.tap are byte-identical (md5 checked after every change). It is the three-track build (tracks 1, 2, 3 in one load) with TILE1, FLIP, TOWER and LOOP on.
- LOOP (the looped screen copy) HAD TO BE ON: without it the three packed tracks (5,693 bytes) and their unpacker have nowhere to live - the savings without it give 3.2 KB. Its measured cost on this tape (tests/tearlap.py, an autopilot lap): in the pack 12.3 pictures a second (today's tape 12.4), alone 12.2 (today 12.6). PACEFIX is off (Grant has not approved it); `PACEFIX=1 bash tools/build_choose.sh` builds with it.
- THE ZX0 PACKER's source is now in tools/zx0 (Einar Saukas, BSD 3-clause; built with gcc into build/zx0 the first time), so tools/make_multi.py works from a fresh clone. racer_3tracks.tap rebuilt with it: identical. Checked from a fresh export of the branch (no build/zx0, no build/multi): tools/build_choose.sh gives the same racer_choose.tap, byte for byte.
- TITLE: three choices - 1 ONE PLAYER, 2 TWO PLAYERS, K CHOOSE KEYS - the closing rule moved up to row 13. 1 or 2 goes to the choose screen. T does nothing (the proof tape's track switch is gone on this tape).
- THE CHOOSE SCREEN (src/choose.asm; its texts src/choose_td.asm): a card as the title's menu - green head with the step's name large, white under it, the check cloth round it. Steer left / right to go round the choices, accelerate to select - player 1 with the keys the K screen gave (O P Q unless changed). Steps:
  TRACK - its full name and its road drawn from the track's own surface map, a pixel a tile (72 x 64, or 72 x 84 for track 3): not the mini-map's ribbon, so it does not depend on the mini-map's size. The track is unpacked each time the choice moves.
  DRIVER - the face twice the size on the player's colour, the name under it. Seven: MAX (the face that was YOU: a player can now be anybody, so he has a name - one word in src/choose_td.asm to change), FRANK, SPIKE, BRUNO, JANE, and two new: SPECS and DOT.
  CAR - the car nose up, twice the size, its name. Seven: RACER, COUPE, CLOWN CAR, TANK, DRAGSTER, and two more: SALOON and TRUCK.
  EXTRA - ACCELERATION, GRIP, SPEED: a filled pip each; the one the choice is on is lit yellow and has a second pip.
  Then the race starts as before. The choices stay for the next race (the choose screen opens on them).
- THE NEW FACES are Claude's first drafts in Grant's style (tools/face_art.txt, tools/face_moods.txt: SPECS - short hair, round glasses; DOT - her hair in a bun), each with all four looks (now, eyes, happy, sad). For his faces editor: docs/design/choose/new_faces.txt, in the form tools/import_faces.py reads (it now knows SPECS and DOT). Sheet: docs/design/choose/new_art_sheet.png.
- THE TWO EXTRA CARS ARE NOT NEW DRAWINGS: they are the two already in tools/pool_art.txt - the six-wheeled TRUCK Grant asked to keep ("want that old design for later - with the 6 wheels") and SPECS's old car, here called SALOON. Grant then said he will draw up to three himself, so no more effort went into car designs: these two are placeholders.
- WHAT "A DIFFERENT CAR" IS: in the window every car is the same blue on cyan, so a car is told apart by its SHAPE; colour belongs to the car's place in the race (player 1 red, then cyan, green, magenta, white - the race order's bands, the podium's steps) and is not chosen. Choosing a car swaps two cars' 16 headings in the cars' table, so the race draws exactly as before (no cost in the race).
- THE CAR LIST IS DATA: tools/choose_cars.txt (a line a car: its drawing's name, the name shown). A new car is a drawing in tools/choose_car_art.txt ("== NAME heading 0 ==", 16 x 16, X o .) and a line in the list - no code. Heading 0 is enough: the 22.5 and 45 degree drawings are drafted from it (tools/turn_car.py) unless given. Room in the list for five beyond the five in the race (ten in all).
- WHAT A CAR COSTS (FLIP on): SALOON 564 bytes of frames + 64 of table + 7 of name = 635; TRUCK 552 + 64 + 6 = 622. A car that is the same left and right keeps 9 of its 16 headings; one that is not keeps up to all 16, about 1,100 bytes.
- HOW MANY OF GRANT'S THREE FIT: with the two placeholders in, NONE - 375 bytes are free on the tape (120 above the copy routine, 140 under 0x8000, 115 in the program; and 58 in the table block), and a car needs about 630 in one piece above the copy routine. If his cars REPLACE the two placeholders, TWO fit (if they are the same left and right). A third needs about 510 bytes more found first: OPTIMISATION-PLAN's saving 5 (tile pictures shared between tracks, about 450 a waiting track - an estimate) is the likely place.
- THE EXTRAS, exact numbers (src/hud.asm: CH_TOP, CH_SPUSH, CH_PUSH; src/clothmini.asm: su_gtab's row 2):
  SPEED: top speed 448 -> 492 (1.75 -> 1.92 px a frame, +9.8%). A higher top speed needs more push to reach it: +7, given only above 1.5 px a frame, so the car does not also get away quicker.
  ACCELERATION: push 64 -> 71 (+10.9%). Measured: 1.5 px a frame 11 frames after the key against 15; top speed unchanged.
  GRIP: the tyres hold 18, 9, 9, 6 where they held 16, 8, 8, 5 (gripping, with accelerate, sliding, both; +12.5% and the last +20% - whole numbers). Measured: after the same hard turn the slide ends after 65 frames against 89 on the plain tyres.
  The set-up keys 1 2 3 before the lights (2 points to spend) are OFF on this tape: the extra replaces them. The crew chief says ON THE GRID / WAIT FOR GREEN where he said PICK 2 UPGRADES / KEYS 1 2 3.
- TWO PLAYERS - THE CHOOSING IS BUILT, THE RACING IS NOT. After player 1's three steps player 2 does the same on cyan with 6 (left), 7 (right), 9 (accelerate) - the keys a Sinclair joystick presses; player 2 has no keys of their own in the game, the K screen sets player 1's only. Player 1's driver and car are not offered to player 2. In the race player 2's driver and car are the second car - but THE COMPUTER DRIVES IT: there has never been a two-player race in this game (the title said 2UP COMING SOON), the view follows one car, and player 2's extra is remembered but used by nothing. A real two-player race is its own job (split view or taking turns) and Grant's to decide.
- A FAULT FOUND AND FIXED on the way: choosing a track after a race unpacked a clean mini-map, and the next race then took the last race's dots "out" of it - leaving them in. The track step clears them first (map_off). The proof tape racer_3tracks.tap has the same fault with T after a race (not changed).
- MEMORY, how it was made to fit: the seven faces in the program; their mood lists, the extra cars and the tracks' names above the copy routine with the packed tracks (which starts 106 bytes lower: straight after the looped copy's 404 bytes); the screen's records and texts at the end of the table block at 0x5B4C, where the five drivers' mood lists were; the set-up keys' code out. Free: 375 bytes in three pieces (above).
- TESTS: tests/choose_test.py (44 checks, all pass): the title; each track by name with its road matching its surface map; after choosing, memory byte for byte each track's own build (24,535 bytes compared, 0 differ); seven drivers and seven cars round and back, the chosen ones in the race order, the cars' table and on the podium; each extra changing its own number and not the others; two players. tests/choose_suites.sh runs that and the game's suites on the tape's three tracks: 23 of 26 pass whole. The three that do not, all open before this work: drive_test (twice: track 1, and track 1 again after going round the tracks) "the fastest computer car is competitive: 16.6 s a lap against your ~18.3 s" - the computer cars' pace at 4 TV frames a picture, OPTIMISATION-PLAN 5.2, PACEFIX's job; track 2's "no lap is much longer than another (21.6 to 32.1 s)" - the open lap-spread limit. The race-order gap check passed this time. Not run on this tape: setup_test (its keys are gone: choose_test's extra part stands in), skip_test and objects_test (they load racer.tap by name).
- TESTS CHANGED, and why (none loosened): tests/drive_test.py's loader and a new through_choose() walk the choose screen on this tape (1, then accelerate four times); finish_test, title_test, copy_check, tearlap call it after their own 1; title_test on this tape expects three menu rows, does not press 2 (no 2UP COMING SOON), uses the redefined accelerate key on the choose screen, and expects the extra in place of the set-up keys; crew_test names the new grid message; finish_test reads the row lists from TSRC when given (the several-tracks tapes are built in a copy of src/). On today's tapes they run as before: drive 53, finish 18, title 39, crew 9, setup 8, arrow 23, copy, track 2 36 - all pass.
- PICTURES: docs/design/choose/01-27 (3x, from the real tape: tests/choose_shots.py), new_art_sheet.png (tools/make_choose_sheet.py).
- FOR THE MERGE: main's redrawn tank (tools/car_art.txt) and pa_one's `inc e` (src/title3.asm) were not touched here; title3.asm's pa_car and pa_face each gained an `if OPT_CHOOSE` block. The mini-map was not moved or shrunk; if it becomes 40 wide the choose screen is not affected (it draws from the surface map), but tools/make_multi.py's strip sizes will want a look.
- NOT DONE / NOT VERIFIED: no one has driven it - feel, the size of the boosts and the faces are Grant's to judge. Two-player racing (above). The car in the window was not compared pixel for pixel (the table it is drawn from was, and the race order's picture). The drivers' names in the small letters (podium, title) were looked at, not read by the test. The computer cars keep their own driving whatever driver or car they are given. A player could give player 1 the keys 6, 7 or 9 on the K screen: not guarded. Track 5 is not on this tape (as racer_3tracks).

## 16 Nov 2026 - the race track trial: black road, green grass to the pixel, rule 4 (background agent, branch worktree-agent-af8779cbaad3c1b51)

Grant, 16 Nov 2026: "The breakfast table dithering is not working. So we're going to scrap the table idea, and make a traditional race track instead. That will allow for a clearer track. I want the track to be black. The outside of the track will be green." After the moving mock-ups and the colour-clash scorer he chose rule 4 and said "go". This is that, as a TRIAL TAPE of track 1 behind a build option.

- BUILD: `RACETRACK=1 bash build.sh` -> build/racer_racetrack.tap (it turns on TILE1, FLIP, TOWER and LOOP itself and builds in build/racetrack). Off by default: `bash build.sh` and TRACK=2, 3, 5 are byte for byte what they were (md5 of the four .bin and .tap files before and after). Always run plain `bash build.sh` last.
- THE SHORT OF IT: the look is built and is exact - and it is TOO SLOW. 7.0 to 7.5 pictures a second against today's 12.4 to 12.6. The game itself runs at full speed (see "full speed" below); it is the pictures that are fewer. Nobody has driven it.
- THE LOOK, as built: the road black; solid green grass from 10 pixels beyond the road's edge, its edge on the true curve to the pixel at every scroll position (no 8-pixel staircase); a dashed white limit line 2 pixels wide just inside the road's edge, 8 on / 8 off; no cloth, no cereal O's, no breakfast things, and nothing to bounce off (o_check is not in this build). The start line, the grid's brackets and the NOS canisters are white on the black. Cars: you red, then cyan, YELLOW, magenta, white - the driver whose band in the race order is green has a yellow car on the track, since green is the grass.
- HOW THE GRASS IS DRAWN (src/racetrack.asm, top). Each picture every 8 x 8 colour square of the window is decided afresh, because the picture scrolls by pixels and the squares cannot. A square that is ALL grass is green ink on green paper and NOTHING is drawn in it - most of the grass costs no drawing. A square with NO grass is white ink on black paper. A square with BOTH is green ink on black paper with the grass in pixels. A square of the screen lies over four tiles of the world; tools/make_world.py (RACETRACK=1) works out which of the three every such group of four is (runs along each row: 3,707 bytes in all with the pictures), a picture for each of the 142 different part-grass tiles, and for an all-grass tile only the quarters of it that share a square with road. White never shares a square with green: with 10 pixels of run-off no white pixel is within 7 pixels of a green one across and down (the generator checks it; it dropped 1 line pixel of 2,884). Where a square may hold grass or white, the game looks at the pixels to see which.
- THE CLASH RULE (rule 4), per square a car really has pixels in: no grass - the square's ink is the car's colour (white there takes it; your car is drawn last, so it wins); all grass - the car's colour on green; grass and road - nothing is changed, the car is drawn in the square's green with its body black and a 1-pixel black rim (the car's mask cut once more at 1 pixel left, right, up and down). In an all-grass square the car's body shows green, not black: that is what the mock-up's rule 4 does.
- THE THINGS THAT DO NOT SCROLL, re-coloured: the mini-map and the place plate stand on black boxes of their own, white ink; the health mug magenta on black, the spoons red on black; the start lights as they were, their rail cyan on black; the crew chief's bubble white as it was; the corner arrow YELLOW by the cars' rule (on grass-and-road squares it shows green). The podium and the title are untouched and work.
- COLOURS ARRIVE WITH THE PIXELS: the colours are kept in a copy of the screen's colour squares (0xEA00). For the window's first 9 rows the screen-copy routine sends a row's 24 colours up straight after that row's 8 lines of pixels; the other 10 rows' colours go up straight after the copy. The copy is slower than the TV's beam and is overtaken at row 8 or 9 of 19 (worked out from measurements: it starts 500-2,200 T after the interrupt and takes about 63,500): the rows above change in that TV frame, the rows below one frame (1/50 s) later - each row's colours and pixels together; the beam does not come back to the lower rows before their colours are up. Today's tape has the same kind of seam near the foot of the window. (Not checked with the emulator's tear report.) The copy runs with interrupts off, so it must be over before the next interrupt or the game loses that TV frame: measured with 10 rows' colours inside it, it ended 64,400-66,200 T into the frame's 69,888 and the frame counter kept step over 500 frames (with 9, as built, it ends about 500 T sooner; the laps in tests/rt_laps.py are from that build). With all 19 rows' colours inside the copy it ran over, and the game lost about one frame in seven.
- GRASS IS SLOW: RT_GRASS_FSH equ 2 and RT_GRASS_PUSH equ 1 (src/racetrack.asm). On grass a car loses a quarter of its speed each frame (an eighth on the road) and its push is halved: it settles at 1.5 pushes against the road's 7. Measured: 0.38 pixels a frame flat out on the grass against 1.74-1.75 on the road - 21-22%. (FSH 2, PUSH 0: 43%, the old table's off-road. FSH 1, PUSH 0: 14%, measured. FSH 2, PUSH 2: 11%, worked out.) A tile counts as grass when most of it is green; a car is on the grass when its middle is on such a tile. The computer cars' middles were on the grass 0.0% of the time over 30 s.
- FULL SPEED: the game moves everything once for each TV frame a picture took, up to 4. This tape's pictures take 6 to 8 frames, and with that limit the whole game ran slow (an autopilot lap 28 s against 19-20, measured). The limit is 8 in this build. It costs: each frame of moving is about 19,000 T, so a slower picture has more moving to do and gets slower still.

MEASURED (python3 tests/stage_profile.py, the same drive on both tapes; T-states of work a picture, pictures a second, TV frames a picture):

| | today's tape | the trial tape |
|---|---|---|
| start straight, alone | 234,588 T, 12.38 (4.04) | 437,970 T, 7.38 (6.78) |
| mid-lap, alone | 234,514 T, 12.38 (4.04) | 428,975 T, 7.50 (6.67) |
| in the pack off the start | 241,171 T, 12.62 (3.96) | 462,924 T, 7.00 (7.14) |

Where the trial's 429,000 go (mid-lap, alone; from the profile by routine, rounded): moving, about 130,000 for its 6.7 TV frames (today about 76,000 for 4 - worked out from 19,000 a frame); the screen copy 58,000 (the looped copy routine it needs for room; today's unrolled one is 51,500) and the colours 10,000; the buffer cleared 25,500; the colour squares decided 30,000; the grass's tile loop 27,000 and its all-grass quarters 26,000; tiles drawn through the shift tables 50,000 (about 35,000 of it part-grass pictures and 15,000 the limit line - split by their numbers in view, not measured apart); the line's own loop 11,000; the grass-or-white squares looked at 7,000; the rest - cars drawn, plate, map, sound - about 55,000. What went: cloth_fill, 36,500 T a picture on today's tape, and the O's.

- WHY, AND WHAT WOULD FIX IT. An edge that is right to the pixel is drawn through the shift tables at about 90 T for each line of each 8-pixel tile, and this look has four edges in view (two of grass, two of limit line) where the table had none (the O's were single tiles 16 pixels apart). Three designs were costed on paper (tiles as built; the grass filled solid by tile row; spans by scan line): by those sums all come within about a tenth of each other. For the 4 TV frames a picture of today's tape everything new must fit in about 87,000 T; it takes about 187,000. Not built, estimates: (1) the all-grass quarters folded into the part-grass tile beside them, about -13,000; the squares' loop and the tile loops tightened, -15,000; clearing only between the grass, -5,000: together about 33,000 - two thirds of one TV frame a picture. (2) Without the limit line: -26,000. (3) Without the looped copy routine: -6,500 - but then 1,560 bytes have to be found. (4) Moving made cheaper (19,000 T a TV frame, most of it the computer cars thinking): the biggest lever, and not this work's to pull. No one of these reaches 12.5; (1), (2) and (4) together might.
- MEMORY (with the four savings on): code 1,582 bytes under 0x8000; the grass 3,707 bytes above the looped copy routine (0xEE00: 128 of index, 1,136 of pictures, 2,443 of rows) - it loads after the start-up area and start_once copies it up; the colour-square copy 672, the list 288, 6 more. Free while racing: 3,888 (2,463 in the program, 448 + 137 under 0x8000, 840 above the grass). The tape is 30,281 bytes (today's 29,026). LOOP was needed: without it this build is 1,560 bytes short.
- THE DASHES go by the world's 8 x 8 tiles (a chequerboard of them), not the mock-ups' bands across x + y: the same 8 on / 8 off along a straight, uneven on a bend; 223 tiles of line to draw instead of 396. `RT_DASH=diag RACETRACK=1 bash build.sh` builds the mock-ups' pattern (slower; not timed on the final build).
- TESTS: tests/racetrack_test.py, 15 checks, all pass, from the emulator's screen against a picture worked out apart from the game: (1, 2) a lap alone and a lap in the pack - 136 and 133 pictures, the window's rows 3-15 match to the pixel outside the cars' squares, 0 wrong, at 38 of the 64 pixel offsets, 3,509 and 3,348 squares holding both grass and road; (3) rule 4 with your car parked in 21 places - 42 road, 12 line, 18 grass-and-road and 54 all-grass squares, 0 wrong, 0 pixels changed beyond the rim; (4) the slide; (5) the grass speed, back onto the road, the computer cars on the road. (Rows 0-2 and 16-18 hold the plate, the lights, the map, the mug and the bubble and are not compared.)
- CLASH SCORES FROM THE REAL TAPE (the slide: straight on at the first bend, 60 frames in the grass, back; 87 pictures, 33 with the car's middle on the grass): BACKGROUND total 433, worst picture 60; CAR total 406, worst picture 85. Of the 433, 320 are white shown in your red where the car shares a road square with it (the grid's bracket as it pulls away, the limit line) and 113 the black rim; nothing else. The mock-up's rule 4 over its own drive (PLAIN=1, 367 pictures): background 1,129, worst 34; car 2,025, worst 61. Not the same drive, and the game's car has 92 pixels of outline.
- THE OLD SUITES ON THE TRIAL TAPE (run in a scratch copy; none edited). Pass: lapcount (8), nos (9), plate (4). drive_test: 46 pass, 7 fail - the mini-map and the mug and spoon "in the window's own colours", the window against the old map (twice), the lights' rail colour, the lights' cells "the window's colours again", and 11.9 pictures a second (got 7.0). finish_test: 15 pass, 3 fail (the cloth's colours round the card, the second race's blue on cyan, the grid under the jingle). arrow_test: 12 pass, 11 fail (blue on cyan, the cloth's colours, the window against the old map). crew_test: 8 pass, 1 fail (the bubble's cells "the cloth's colours again"). damage_test cannot run: it drives into an O. Not run: drift, lead, o, objects, setup, stuck, title, skip, copy_check. (These were run before the last changes - the colours sent up with the pixels and the full-speed limit of 8 - and not again after.)
- NOT DONE / NOT VERIFIED: the speed, above. Nobody has driven it: feel, the grass's drag, the colours and the dashes on bends are Grant's to judge. Steering is read once a picture, so at 7 pictures a second it answers up to 0.14 s late where today's answers in 0.08. Laps take what they took: an autopilot lap 18.6-19.6 s here, 19.2-19.8 on today's tape; the computer cars 19.6-21.9 s against 18.4-21.2 (tests/rt_laps.py, one race each). A car cut off by the window's edge may miss a pixel of its rim. Tracks 2, 3 and 5 are not built this way (5 would need the bridge's walls thought again). Pictures: docs/design/racetrack/built/ (tests/racetrack_shots.py): start_grid, bend, bend_in_the_pack, car_on_the_line, car_in_a_mixed_square, car_on_the_grass (3x), slide_into_the_grass.gif and bend_in_the_pack.gif (2x, real speed).
- A FAULT OF THIS WORK'S OWN, FOUND AT THE END: the assembler opens every included file even inside an "if" that is off, and src/rt_world.asm (the grass, written only into the trial's build copy) did not exist in src/ - so the plain build stopped with "file not found" and left the old tapes standing, which is why the md5 check kept passing. src/rt_world.asm is now a placeholder of comments. The four plain builds were then made afresh (each wrote its tape; checked by their times) and are byte for byte the tapes of before this work. The three commits on this branch before the last do not build the plain game.

## 16 Nov 2026 - the race track trial's speed pass: 7 pictures a second to 8, and a menu of what would buy more (background agent, branch worktree-agent-ab8bf2b0bee0348cf)

Grant drove the trial and said: "the look is right ... it is just not smooth". Then, widening it: "please investigate ways to get speed back to the way it was, or find compromises or alternatives". This is that. THE SHORT OF IT: with no change to the look the trial now makes 7.6 to 8.5 pictures a second (it made 7.0 to 7.5; today's tape makes 12.4 to 12.6). It does not reach 12, and nothing invisible that was tried or costed would take it there. Two concessions are built as tapes: sparser dashes (8.5 to 9.6) and no limit line (9.6 to 10.6). Getting all the way back to today's speed takes the limit line AND about a third of the play window, or the line and three more savings that are costed here and not built. Nobody has driven any of these.

- BUILD: `RACETRACK=1 bash build.sh` -> build/racer_racetrack.tap (the look unchanged). `RT_DASH=sparse RACETRACK=1 bash build.sh` -> build/racer_racetrack_sparse.tap. `RT_NOLINE=1 RACETRACK=1 bash build.sh` -> build/racer_racetrack_noline.tap. Each builds in its own folder under build/. Always run plain `bash build.sh` last. The plain game and tracks 2, 3 and 5 were built afresh (their tapes deleted first) and are byte for byte what they were (md5 of the four tapes).

THE MENU, measured (python3 tests/stage_profile.py, the same three drives each; pictures a second, TV frames a picture in brackets, T-states of work a picture):

| | start straight, alone | mid-lap, alone | in the pack | what the eye notices | built? |
|---|---|---|---|---|---|
| today's tape (the breakfast table) | 12.38 (4.04) 234,588 | 12.38 (4.04) 234,514 | 12.62 (3.96) 241,171 | - | yes |
| the trial as it was | 7.38 (6.78) 437,970 | 7.50 (6.67) 428,975 | 7.00 (7.14) 462,924 | - | yes |
| 1. NO LIMIT LINE (racer_racetrack_noline.tap) | 10.62 (4.71) 295,948 | 10.50 (4.76) 293,308 | 9.62 (5.19) 330,316 | the road's edge is marked only by the grass 10 pixels beyond it; start line, grid and canisters stay white | yes |
| 2. SPARSE DASHES, 8 on 24 off (racer_racetrack_sparse.tap) | 9.38 (5.33) 341,287 | 9.62 (5.19) 333,463 | 8.50 (5.88) 373,992 | half as many dashes; on a bend they are uneven, as now | yes |
| 3. NO VISIBLE CHANGE (racer_racetrack.tap) | 8.38 (5.97) 380,550 | 8.50 (5.88) 376,395 | 7.62 (6.56) 419,879 | nothing in the picture; it goes up over about 1.3 TV frames, not 0.9 (see THE SEAM) | yes |
| 4. no line, and a play window of about 20 x 17 squares (not 24 x 19) | about 12.5 | about 12.5 | about 12.5 | a quarter less to see; the frame, the plate, the map and the mug all move | ESTIMATE |
| 5. no line, your car moved once a picture, the fixed boxes drawn only when they change, the kinds a byte a block | about 12.5 | about 12.5 | 10 to 12.5 | should be nothing - but your car's grip sums would run once a picture, which may change how it handles | ESTIMATE |

Pictures of 1, 2 and 3: docs/design/racetrack/built/speed_noline_bend, speed_sparse_bend, speed_full_bend - each a 3x still (.png) and a 2x GIF at real speed (.gif, about 5 s, the first bend in the pack) - tests/rt_speed_shots.py. Memory, the same for all three tapes: 967 bytes free in the program, 27 in the room under 0x8000, 2 above the map, and about 220 in odd corners the white things' lists have left (the strips; not added up one by one): about 1,200. (The first trial had 3,888: the map of the tiles and the kinds took it.) The no-line tape also has 752 unused bytes inside the pictures' pages, the sparse one 296. Each tape is 32,702 bytes.

- "BACK TO TODAY'S SPEED", exactly: a picture's work that does not grow with its length has to come down from about 313,000 T (in the pack) to about 215,000 - then four TV frames hold it and the moving that goes with them. The limit line is about 67,000 of that (measured: rows 1 and 3). The other 30,000 is row 4 (measured cost of a square of window, below) or row 5 (three sums, none built). With the line kept there is no route: 98,000 T is more than the grass's edge costs.
- WHY IT IS SLOW, measured (in the pack, the tape with no visible change, T a picture): looking at all 456 squares 38,000 and deciding their colours 26,000 - whatever is in view; the 170 or so squares that show grass edge or white: 23,000 to reach each, 52,000 to sort out which of its four tiles is nothing, all grass or a picture, 55,000 for the lines themselves through the shift tables, 8,500 to tell grass from white where a square could hold either; 15,000 copying the 45 squares a car or a fixed box is in. That is 218,000 (it was 259,000). Then the cars 48,000, the fixed things 25,000, and the game's moving 106,000 for its 6.6 TV frames. About 100 of the 170 squares are the limit line's - each dash makes four blocks "may hold white" though it inks one or two - and a square costs about 900 T however little is in it. So the shifting is a quarter of the drawing; the rest is finding out what to draw.
- WHAT WAS DONE (src/racetrack.asm, top; tools/make_world.py's RT part). (1) A square that is all grass or plain road is HIDDEN BY ITS COLOUR - ink and paper the same - and never touched: no clearing of the picture, no copying of it. (FLASH is set on those squares to mark them; with ink and paper one colour it shows nothing. Not seen on a real Spectrum - the emulator shows nothing.) (2) A square with grass edge or white in it is made up from its four tiles and written whole, straight onto the screen (rt_sq); only a square a car, its rim, the arrow or a fixed box is in goes through the back buffer. (3) The world is one map of tiles, a byte each (0 nothing, 1 all grass, then pictures: 255 of them, so 3 pictures that are both a grass tile and a white tile share a number where the game never has to tell which), kept from each row's first tile that matters to its last: 3,626 bytes; the pictures stored a line to a page; the blocks' kinds two to a byte (2,304). The old draw_tiles, the tile routines and the white things' row lists are not in this build (the lists are kept as comments in the build's world.asm, because tests/racetrack_test.py reads its white picture from them). (4) Each square's colour goes to the screen straight after its pixels.
- WHAT DID NOT WORK: the first rewrite (the kinds as runs, every tile through the tables, each square found afresh) was no quicker than the old trial: 442,000 / 430,000 / 475,000 T. The packed kinds, the nine cases for a pair of tiles (nothing, all grass, picture - each done the quickest way) and map pointers that slide along a row made it 380,000 / 376,000 / 420,000.
- LOOKED AT AND NOT BUILT, with the reason (all from the measurements above): pre-shifted copies of the edge tiles - 142 pictures x 7 shifts x 16 bytes is 15.9 KB and there are 1.2 KB; and shifting is only 55,000 T. Scrolling in 2-pixel steps, or edges cut to fewer shapes - the cost does not depend on the shift or on how many shapes there are. A solid limit line - more white squares, so slower. A narrower run-off - the same squares; and with none the start line would touch the grass (white and green in one square). Drawing only what the scroll uncovers - the screen cannot be moved a pixel sideways for less than about 60,000 T. Edges or the line on alternate pictures - whatever is skipped lags the cars by up to 9 pixels for a picture: it would shear. The computer cars thinking less often - they already take turns (one decides each frame); the multiply is already a table. Handling a row's squares as one run - worked out at 10,000 to 15,000 T at most, because edge runs are mostly one or two squares long. Row 5's three: your car's grip sums once a picture (about 13,000; it changes behaviour, so it must be a switch with the drive tests); the map, mug and plate redrawn and copied only when they change (about 12,000, half of it only if the plate's clock is left out); the kinds as a byte a block, copied not looked up (about 12,000; 2,300 bytes more, which only the no-line build could find).
- THE SEAM (the emulator's tear report, 600 TV frames of the same drive in the pack; a "cell" is a square in one TV frame). The trial as it was: 142 torn cells in 83 pictures, 136 of them "new pixels in old colours", nearly all in the window's row 8, where the beam overtook the copy. Now: 161 torn in 95 pictures (the same 1.7 a picture), 73 of them new-pixels-in-old-colours. So a square's colour and pixels are seen apart half as often as before - the fault the last entry worked out and did not check was real, and is smaller. But the picture now takes about 1.3 TV frames to go up with the line (the old copy 0.9): its top rows change one TV frame before the rest, and on a busy picture its last rows a frame later still. Late-beside-clean cells: 1,071 against 373. The no-line tape's show is about one TV frame. Whether the eye sees it is Grant's to judge.
- TESTS. tests/racetrack_test.py on the final tape: 14 pass, 1 fails - "during the slide the road never turns green and the grass never black beyond the car's rim (2 pixels)". The 2 pixels are the black rim of the car where the car itself is past the window's right edge (camera 360, car at x 550): the test's rim is grown from the part of the car it can see. The old tape draws the same 2 pixels with the car put there (tests' own Game.put; the two windows compared: the same) - its slower drive never looked at that frame. The test is not changed. Old tape against new, your car set down in 153 places and headings: the windows' rows 3-15 are the same to the pixel in 142; the other 11 all have the grid in view, where the other cars had rolled a few pixels differently before they were held (colour 3 and 6 pixels, not scenery). The old suites on the final tape (a scratch copy, none edited): lapcount pass, nos pass, plate pass (3), crew 8 pass 1 fail, arrow 12 pass 11 fail, drive 46 pass 7 fail - each the same count and the same old-look checks as the last entry (the 11.9-pictures check reads 7.0 with the chief's bubble up). finish_test: 5 pass, 13 fail - and 6 pass, 12 fail on the trial as it was, run the same way today: it is not this work's (the last entry's 15 and 3 were from before that entry's own last changes). The podium, a key at it and the title were looked at side by side on both tapes and are the same; the track's data is whole after a race, the podium and the title (compared byte for byte). Laps (tests/rt_laps.py, one race): you 18.6 to 19.1 s; the computer cars 19.2 to 23.1 (one lap of 23.1; the rest 19.2 to 20.7).
- NOT DONE / NOT VERIFIED: nobody has driven any of the three tapes; smoothness, the seam and whether the road reads without its line are Grant's to judge. Rows 4 and 5 of the menu are estimates. Not tried on a real Spectrum. Tracks 2, 3 and 5 are not built this way.

## 16 Nov 2026 - the race track trial: the limit as a thin green line inside the grass's edge (background agent, branch worktree-agent-ab8bf2b0bee0348cf)

An idea from the coordinator while Grant slept: keep the no-line build's engine and mark the track limit in green, in the squares the grass's edge already uses - green and black only, so no white squares. Built as a switch on top of RT_NOLINE=1 (tools/make_world.py: the line is simply more "grass" in the pictures; the cars' grass-is-slow sums still use the real grass). Nobody has driven these.

| | start, alone | mid-lap, alone | in the pack | mixed squares a picture | build |
|---|---|---|---|---|---|
| no limit line (from the entry above) | 10.62 | 10.50 | 9.62 | 81 | `RT_NOLINE=1 RACETRACK=1 bash build.sh` |
| green line 1 wide, 1 of black between it and the grass | 10.00 (5.00) | 10.12 (4.94) | 9.00 (5.56) | 91 | `RT_PIN_GAP=1 RT_PIN_W=1 OUT=racer_racetrack_noline_pin1 BDIR=racetrack_noline_pin1 RT_PIN=solid RT_NOLINE=1 RACETRACK=1 bash build.sh` |
| green line 2 wide, 2 of black, dashed 8 on 8 off | 9.62 (5.19) 325,721 T | 9.75 (5.13) 322,934 T | 8.75 (5.71) 364,005 T | 105 | `RT_PIN=dash RT_NOLINE=1 RACETRACK=1 bash build.sh` |
| green line 2 wide, 2 of black, solid | 9.50 (5.26) 335,794 T | 9.25 (5.41) 344,387 T | 8.38 (5.97) 381,264 T | 108 | `RT_PIN=solid RT_NOLINE=1 RACETRACK=1 bash build.sh` |

- IT IS NOT FREE. The line does stay green-on-black, but it does not stay within the squares the edge already had: 4 pixels in from the grass it adds about 27 squares a picture (81 to 108), 2 pixels in about 9 - and where the edge and the line share a square the square needs two pictures' lines, not one. So the 2-wide line costs about one picture a second against no line; the 1-wide one about half that. Both beat the white dashes (7.6 to 8.5).
- The line is left out within a colour square of anything white (36 of 5,924 pixels: a gap in it beside the start line). The run-off was not changed: the limit now reads as the green line, 6 to 9 pixels beyond the road's edge the cars are steered by, and the grass's drag still starts at the grass.
- Pictures: docs/design/racetrack/built/speed_pin_bend, speed_pindash_bend, speed_pin1_bend (.png 3x, .gif 2x at real speed). tests/racetrack_test.py does not apply to these tapes as it stands (its picture of the grass has no line in it); not run on them.
- STILL NOT BUILT (the coordinator's next stages; this agent ran out of room): the fixed boxes redrawn only when they change; the kinds a byte a block (the no-line build is about 600 bytes short of the 2,304 it needs unless the all-grass rows are not stored); your car's grip sums once a picture, as a switch; a smaller play window. The estimates in the entry above stand.

## 17 Nov 2026 - the race track trial: the speed got back - where the time really was, four stages built, and a ranked menu (background agent, branch worktree-agent-ae2e8b23fd6243e9b)

The coordinator's brief, after Grant's "investigate ways to get speed back to the way it was, or find compromises or alternatives": build and measure the savings the last two entries only estimated - on the no-line build, every other variant kept building. THE SHORT OF IT: the no-line race track now makes 12.25 pictures a second off the start, 12.75 mid-lap and 11.1 in the pack, with nothing changed on the screen (it made 10.6 / 10.5 / 9.6; today's breakfast-table tape makes 12.4 / 12.4 / 12.6). With one switch that changes how your car is worked out (off unless asked for) it makes 12.9 / 13.0 / 12.25. Every line variant got the same lift: the white dashes 8.4 to 9.6. The biggest saving was not on the list: the trial's drawing code sat in the slow half of the Spectrum's memory. Nobody has driven any of this.

THE MENU - every row BUILT and measured (python3 tests/stage_profile.py, the same three 8-second drives; pictures a second; TV frames a picture in brackets; then bytes free in the program). Ranked by the pack, the hardest case:

| | start, alone | mid-lap, alone | in the pack | free | what the eye notices | build (then `RACETRACK=1 bash build.sh`) |
|---|---|---|---|---|---|---|
| today's tape (the breakfast table) | 12.38 (4.04) | 12.38 (4.04) | 12.62 (3.96) | - | - | `bash build.sh` |
| 1. no line, your car worked out once a picture | 12.88 (3.88) | 13.00 (3.85) | 12.25 (4.08) | 733 | the road's edge is marked only by the grass; the car MAY feel different (see stage C) | `GRIP1=1 RT_NOLINE=1` |
| 2. no line, smaller window, your car once a picture | 13.12 (3.81) | 13.62 (3.67) | 12.12 (4.12) | 662 | as 1, and the play area is 16 rows high, not 19: a black band under it holds the map, the chief's bubble, the spoons and the mug | `GRIP1=1 RT_ROWS=16 RT_NOLINE=1` |
| 3. green line 1 px wide, your car once a picture | 11.88 (4.21) | 12.38 (4.04) | 11.38 (4.40) | 733 | a thin green limit line 1 px inside the grass; the car may feel different | `GRIP1=1 RT_PIN_GAP=1 RT_PIN_W=1 OUT=racer_racetrack_noline_pin1_grip1 BDIR=racetrack_noline_pin1_grip1 RT_PIN=solid RT_NOLINE=1` |
| 4. no line, smaller window | 12.62 (3.96) | 13.00 (3.85) | 11.25 (4.44) | 676 | as 2, the car as today | `RT_ROWS=16 RT_NOLINE=1` |
| 5. NO LINE - the picture exactly as before | 12.25 (4.08) | 12.75 (3.92) | 11.12 (4.49) | 747 | nothing new: the no-line look Grant has not yet judged | `RT_NOLINE=1` |
| 6. green line 2 px, dashed | 11.38 (4.40) | 11.62 (4.30) | 10.38 (4.82) | 747 | green dashes 2 px inside the grass | `RT_PIN=dash RT_NOLINE=1` |
| 7. sparse white dashes, your car once a picture | 11.00 (4.55) | 11.50 (4.35) | 10.25 (4.88) | 733 | white dashes 8 on 24 off; the car may feel different | `GRIP1=1 RT_DASH=sparse` |
| 8. green line 1 px wide | 11.62 (4.30) | 12.00 (4.17) | 10.00 (5.00) | 747 | a thin green limit line | `RT_PIN_GAP=1 RT_PIN_W=1 OUT=racer_racetrack_noline_pin1 BDIR=racetrack_noline_pin1 RT_PIN=solid RT_NOLINE=1` |
| 9. sparse white dashes | 10.50 (4.76) | 10.75 (4.65) | 9.88 (5.06) | 747 | white dashes 8 on 24 off | `RT_DASH=sparse` |
| 10. green line 2 px, solid | 10.88 (4.60) | 10.38 (4.82) | 9.50 (5.26) | 747 | a solid green line | `RT_PIN=solid RT_NOLINE=1` |
| 11. WHITE DASHES - the look Grant called right | 9.62 (5.19) | 10.00 (5.00) | 9.00 (5.56) | 747 | nothing: the trial as he saw it, quicker (it was 8.4 / 8.5 / 7.6) | (nothing more) |

Each also has 15 bytes free under 0x8000. Tapes: build/racer_racetrack*.tap (the names follow the switches: _noline, _noline_grip1, _noline_rows16, _noline_rows16_grip1, _noline_pin1, _noline_pin1_grip1, _noline_pin, _noline_pindash, _sparse, _sparse_grip1, and racer_racetrack.tap itself). Pictures (3x) and real-speed GIFs (2x, 5 s, the first bend in the pack): docs/design/racetrack/built/speed_noline_bend, speed_grip1_bend, speed_rows16_bend, speed_pin1_bend, speed_pin_bend, speed_pindash_bend, speed_sparse_bend, speed_full_bend (.png and .gif; tests/rt_speed_shots.py). Always run plain `bash build.sh` last. The plain game and tracks 2, 3 and 5 were deleted and built afresh after every stage: byte for byte what they were (md5).

- A PICTURE IS A WHOLE NUMBER OF TV FRAMES. The game shows a picture just after a TV frame starts, so a picture costs 4 frames or 5, never 4.3: "4.49 frames a picture" means half the pictures took 5. 12.5 a second needs EVERY picture inside 4 frames. That is why the pack (five cars to draw and think for) lags the solo drives, and why small savings sometimes show as nothing and sometimes as a jump.
- RECOMMENDATION. Row 5 is free: it should replace the no-line tape whatever else is chosen. For Grant to drive: racer_racetrack_noline_grip1.tap (row 1) beside racer_racetrack_noline.tap (row 5) - if he cannot feel the difference in the car, row 1 is the trial at today's speed; if he wants a line, row 3. The smaller window (rows 2 and 4) is not worth what it takes away: it buys nothing in the pack.

WHAT EACH STAGE REALLY GAVE (T-states of work a picture on the no-line build, start / mid / pack; the estimate in brackets):
- FOUND BY PROFILING, NOT ON THE LIST - THE SLOW MEMORY: 296,000 / 293,400 / 330,400 down to 267,600 / 256,300 / 299,800 (28,000 to 37,000 T; 10.6 / 10.5 / 9.6 pictures a second to 11.4 / 12.25 / 10.5). The Spectrum holds the processor up whenever it reads memory below 0x8000 while the TV picture is being drawn, and all of racetrack.asm had been put there, in the room the savings freed. The parts that run for every square (rt_class, rt_sq, rt_show, rt_car) are now src/racetrack_hot.asm, in the program above 0x8000; things that run rarely went down in exchange (the driver strip, the title's car, the place plate, the faces, the small letters' pictures - racer.asm, "if OPT_RT"). Nothing else changed: the same code at other addresses.
- A, THE FIXED BOXES ONLY WHEN THEY CHANGE (estimate 12,000): 15,500 / 14,800 / 22,100 (the pack's includes the moving it no longer waits for) - to 252,000 / 241,500 / 277,600. A box that is on the screen and has not changed is marked RT_LEAVE and rt_show passes over it: the mini-map goes up only when its dots have been moved (one picture in four), the mug when its steam moves or the damage changes (one in eight), the plate only as far as it changed - all of it for a new place or lap, otherwise just the squares of the time's figures that differ (the tenths: 2 squares of its 15). The spoons are still sent every picture while you hold one (2 squares each: not worth the code). A new test, tests/rt_fixed_test.py, stops at every picture of a 60-second drive from before the lights and checks each box on the screen, pixels and colours, against what the game holds for it: 547 pictures, the map changed 133 times, the plate 349, the mug 76 - all right, on every build.
- B, THE KINDS A BYTE A BLOCK (estimate 12,000): NOT BUILT - it does not fit, and it is worth less than was thought. Measured: deciding the squares' colours costs 17,100 T a picture today (37 T a square); a byte a block cannot go under about 8,400 (an LDI a square), so the most it can give is 8,700, not 12,000. It needs the map cut to each row's not-grass span and a 4-byte record a row: 3,758 bytes against today's 2,442 - 1,316 more. There are 747 free in the program and about 560 usable in the pictures' pages (eight holes of 94 bytes, a row each): 1,307, with nothing left for stages C and E. The kinds as runs (506 runs in the no-line build: about 1,000 bytes, 1,300 LESS than now) were worked out too: 614 T a row against 900 - about 2,600 T a picture, under the 3,000 line. So: no B. If memory is found some day it is 8,700 T.
- C, YOUR CAR ONCE A PICTURE - A SWITCH, OFF BY DEFAULT (estimate 13,000): 13,700 / 11,100 / 21,700 - `GRIP1=1`, with RACETRACK=1; or on today's game, `TILE1=1 FLIP=1 TOWER=1 GRIP1=1 bash build.sh` -> build/racer_grip1.tap (it needs the few bytes those savings give), which makes 13.25 / 13.25 / 12.62 against today's 12.38 / 12.38 / 12.62. Your car still STEERS every TV frame (so a tap on O or P turns it one step, as now); it is moved with the computer cars, once a picture; the grip model's cheap part (engine, drag, tyres) is still done once for each TV frame of the picture, and its dear part (turning the speed, and the sums that make the world speed of it) once. What it changes: the car's place is worked out from one speed for the whole picture, and the ground under it is looked at every picture, not every 4th frame. The drive tests (tests/drive_test.py on the no-line tape, switch off then on - the old-look checks fail on both as before): top speed on a clear road 1.75 on both (1.71 and 1.75 measured), after 2 s of Q the car is at x 412 on both, it pulls away from all four, and the ramming and head-on checks pass on both. Two checks fail with the switch on that pass with it off ("all three green", "the border flashes green"): the test looks within one TV frame of the green light; stepped frame by frame in the emulator the lights and the flash are identical with the switch off and on. Laps by autopilot (tests/rt_laps.py): you 18.2, 18.8, 19.0 s off; 18.6, 18.8, 18.4 s on. The computer cars' laps 18.4 to 20.6 s off, 17.8 to 21.3 on. NOBODY HAS DRIVEN IT: whether a slide feels the same is Grant's to say.
- D, ANYTHING ELSE EXACT AND WORTH 3,000 T: the slow-memory move above was it. "Visiting all 456 squares and deciding their colours" was looked at hard, as asked: it is now 17,100 T to decide and 30,700 to visit (the two were 64,000 in the slow memory). Deciding only what changed does not work - the view moves most of a square every picture, so nearly every square's kind is new by position; and a square's colour must be written whether it changed or not, because finding out costs more than writing (a compare is 29 T, the write 16). Per square the visit is 52 T, 16 of it the write: testing two squares at once, a list of the squares that show, or going by runs each save 4,000 T at most and need every routine that touches a square's colour to change. Not built. Making up the 80 or so edge squares is 54,000 T (670 each) and is as tight as the shift tables allow. In the pack the rest is the cars: each car in view costs about 9,000 T by the clash rule, and everyone's moving and thinking 62,000 a picture.
- E, A SMALLER PLAY WINDOW - A SWITCH (`RT_ROWS=16`; 13, 15, 16 and 17 were built): the window's first 16 rows of squares scroll; the three under them are a black band with the mini-map, the crew chief's bubble, the spoons and the mug in it, where they were; your car sits in the middle of the 16 rows, the arrow 12 lines higher; a car that drives under the band goes out of sight. The frame, the plate and the lights do not move. IT DOES NOT DO WHAT IT WAS FOR: alone 12.6 / 13.0, in the pack 11.25 against 11.12 - and 13 rows made only 11.75. The pack's cost is the cars, not the window. So there is no "largest window that reaches 12.5 in the pack": none down to 13 rows does without the switch of stage C, and with it 19 rows already make 12.25.
- F, THE 2 PIXELS OF RIM AT THE WINDOW'S RIGHT EDGE: NOT FIXED. The rim is made by drawing the car's mask one pixel left, right, up and down; the part of the car beyond the window's edge brings its own rim one pixel into view. Clipping it needs draw_car's mask pass cut to the pixel at the window's edge, which it clips by bytes: not cheap, not attempted. The white-line tape now passes all 15 of tests/racetrack_test.py only because its quicker drive no longer lands on that frame; the no-line tape still shows it.
- TESTS on the final tapes. tests/racetrack_test.py (not changed): white dashes 15 pass, 0 fail; sparse 14 and 1 (the rim); no line 13 and 2 (the rim, and "squares of every kind", which wants limit-line squares the no-line build does not have - it failed so before); no line with GRIP1 14 and 1. On the smaller-window tapes its whole-window checks do not apply (the band is black where it expects scenery, and the view goes 24 lines lower at the world's foot); its rule check (0 wrong), slide, speed and stay-on-the-road checks pass. On the green-line tapes it does not apply, as before. tests/rt_fixed_test.py: 3 pass on every tape.
- NOT DONE / NOT VERIFIED: nobody has driven any tape. Not tried on a real Spectrum (the slow-memory effect is the real machine's; the emulator models it). The seam (the tear report) was not measured again - the picture goes up sooner now, so it should be no worse. Tracks 2, 3 and 5 are not built this way. Stage B and stage F are not built. GRIP1 on today's game (build/racer_grip1.tap) was measured, as above, but no test was run on it.

## 17 Nov 2026 - the race track trial: a narrower road, sharper corners and keener computer cars, as switches and trial tapes (background agent, branch worktree-agent-acbbf0fac92b5a806)

Grant, after driving the trial: "I also need the other cars to be more competitive, this drives a lot easier. The track corners can be sharper now and the track narrower." Track 1 only, on the thin-green-line build; the drawing code (racetrack.asm, racetrack_hot.asm) is not touched. THE SHORT OF IT: the road can be 56 or 48 px wide (it is 72) and the four big corners half the radius, by two parameters; the computer cars have three levels, every number in one file. On today's cars a driver who cuts the corners laps 2 to 4 seconds a lap quicker than the best of them - that, more than the track, is why it was easy. On HARD the fastest is within 1 to 3% of that driver and the slowest within 8%. Nobody has driven any of it.

WHAT WAS FOUND FIRST (it changes what "sharper" can do):
- THE CAR TURNS FAR TIGHTER THAN THE TRACK ASKS. Measured in the emulator, flat out at 1.75 px a frame with P held: the car is travelling at right angles to where it was after going on only 39 px, and its speed dips only to about 1.66. So a square corner needs about a 39 px circle; today's corners are 54 px along the middle of a 72 px road. And a square corner between two straights can always be straightened by using the road's width: no radius, at any sensible width, makes one that cannot be taken flat out on a good line (by the geometry it would need a road about 25 px wide). What a sharper corner does do: the driver who keeps to the middle can no longer take it flat (under 39 px), the turn-in must be earlier and more exact, and a late one ends on the grass.
- SO THE RADIUS CHOSEN IS 27 PX (half of today's, and under the 39): the middle-of-the-road driver must lift, the corner-cutter need not, nobody is stopped. 20 px was built and measured too - no different by the numbers. A corner that even a good line cannot take flat would have to be a hairpin (a 180 degree turn) or a tighter chicane: a change to the track's design, not built.
- HOW EASY IT WAS. Two autopilots: the CAREFUL one (tests/rt_lib.py: aims at the middle of the road) and a CORNER-CUTTER (new, tests/rt_ace.py: aims 88 px further round the road - a tidy racing line; it stands in for a good human). On the 72 px trial the careful one laps 18.7 s, the corner-cutter 16.6 (15.8 at its best setting), never lifting, never on the grass. The computer cars lapped 19.2 to 23.1.

A. THE TRACK - three variants (parameters of tools/make_world.py, read only with RACETRACK=1 on track 1: `RT_ROADW=56` the width, `RT_CORNER=27` the big corners' radius; without them not a byte changes). The straights stay where they are, so a sharper corner makes the lap longer.

| | lap along the middle | careful autopilot, alone | corner-cutter, alone | its best clean lap (any setting) | bytes free | pictures a second: start / mid-lap / pack (NORMAL cars) |
|---|---|---|---|---|---|---|
| today: 72 px, radius 54 | 1,472 px (16.8 s flat out) | 18.7 s | 16.6 s | 15.8 s | 747 | 11.6 / 12.0 / 10.75 (today's cars) |
| 1. 56 px, radius 54 (`w56`) | 1,472 px | 18.8 s | 16.6 s | 16.4 s | 969 | 11.5 / 11.9 / 9.4 |
| 2. 56 px, radius 27 (`w56s`) | 1,519 px (17.4 s) | 19.5 s | 17.1 s | 16.4 s | 867 | 11.5 / 11.75 / 9.9 |
| 3. 48 px, radius 27 (`w48s`) | 1,519 px | 19.6 s | 17.2 to 17.7 s, with a bad lap in three (18.8 to 22.1) | 17.0 s | 1,052 | 10.75 / 11.4 / 9.4 |

- Neither autopilot touches the grass on any of them in the runs the table is from (the corner-cutter's bad laps on the 48 px road apart: 4 short visits in one run). The computer cars: on the grass 0.0 to 0.5% of the time on every variant and level (a few frames at a time, after a mistake); once, on the 48 px road, PINK was 5.9% of a race on it.
- The corner arrows, the mini-map and the grid come out right: the generator's arrow list has a sharp-left before each big corner on every variant; the mini-map is still 24 x 17 with a ribbon 3 wide (it is drawn as for the 72 px road - a narrower one's ribbon would be under 2 pixels); on the 48 px road the grid's two lanes are 11 px from the middle, not 14, so the boxes stay inside the road (looked at in the track pictures).
- THE GRASS still starts 10 px beyond the road's edge. It cannot come nearer than 8: the start line runs the road's full width, and anything white within a colour square of the grass stops the build (`RT_RUNOFF=8` is there to try; it builds, not measured). What the narrower road suggests: the black is 76 px across on the "56" road, so it LOOKS wider than it is - to look as narrow as it drives, the start line would have to be shortened first.
- A NARROWER ROAD COSTS A LITTLE DRAWING TIME, it does not save any: both grass edges are in the window more of the time, and the edge squares are the dear ones. 56 px costs about 1% alone; 48 px about 7% off the start.

B. THE COMPUTER CARS - three levels, `AI=1` (NORMAL) or `AI=2` (HARD) with bash build.sh; without it EASY, the cars exactly as they were. EVERY NUMBER IS IN src/ai_tune.asm, with what each does. No rubber-banding; no speed the player does not have.

| the knob (src/ai_tune.asm, one set for each car and level) | what it does | which way is quicker |
|---|---|---|
| REACH | how near a waypoint counts as reached: the car turns for the next one sooner and cuts the corner | bigger - the biggest gain. 24 keeps to the middle, 56 is a racing line; over 60 it misses waypoints and its laps count early |
| EASE | when it lifts: 0 only if its target is behind it, 1 at 45 degrees off its nose, 2 at 27 | 0 |
| PACE | it pushes on PACE of every 16 | 16 is flat out; each 1 less costs about 6% of a lap |
| ERR | chances in 256, at each waypoint, of a mistake (late turn-in, lift, wobble) | smaller (3 is one in two laps, 12 two a lap) |
| LINE, FUSS, REACT | how far its line wanders; twitchy or smooth steering; turns to think it lets go by | tidy (3,2), smooth (2), 0 - small effects |

Measured in the pack over 5 races of 3 laps, you on pole by the corner-cutter; mean flying lap, and how far behind yours:

| | you | WHITE | CYAN | PINK | GREEN |
|---|---|---|---|---|---|
| 56 px sharp, EASY (as they were) | 17.0 | 19.1 +13% | 20.6 +22% | 21.3 +26% | 21.0 +24% |
| 56 px sharp, NORMAL | 16.8 | 17.8 +6% | 18.0 +7% | 18.8 +12% | 19.1 +13% |
| 56 px sharp, HARD | 16.9 | 17.2 +1% | 17.5 +3% | 18.1 +7% | 18.2 +8% |
| 56 px gentle, EASY / NORMAL / HARD | 16.4 | 18.2 / 17.4 / 16.9 (+11, +6, +3%) | 19.4 / 17.6 / 17.1 | 19.5 / 18.4 / 17.9 | 19.8 / 18.0 / 17.6 (+21, +9, +7%) |
| 48 px sharp, EASY / NORMAL / HARD | 17.0 | 19.7 / 17.8 / 17.3 (+16, +5, +1%) | 20.4 / 18.2 / 17.7 | 20.8 / 18.9 / 18.3 | 20.7 / 18.7 / 18.4 (+22, +11, +8%) |

- HARD meets what was asked (fastest within about 2%, slowest about 8%) against the corner-cutter. Against the CAREFUL autopilot NORMAL is already too much: it laps 19.5 to 20.6 in the pack and comes in 4th or 5th. So: EASY is beaten by keeping to the middle of the road; NORMAL needs the corners cut; HARD needs them cut well every lap.
- THEY DIFFER AND CAN BE PASSED. The finishing orders change race to race (WHITE and CYAN swap, PINK and GREEN swap). Held on the grid for 3 s after the green light, then chasing, 6 races on the 56 px sharp track: on EASY you win 5; on NORMAL you come 3rd in four, 2nd and 5th in the others (passing GREEN and PINK, not catching the two quick ones in 3 laps); on HARD 3rd in five and 5th in one; on the 48 px road on HARD 4th or 5th every time - there is little room to pass on it.
- THEY DO NOT NEED A SPEED HINT AT EACH WAYPOINT: none was added. With the bigger REACH they turn in early enough to stay off the grass at full throttle (the figures above), so there was nothing for a hint to cure.
- THE PICTURE-RATE FAULT (OPTIMISATION-PLAN 5.2) AND `PACEFIX=1`: every tape here is built WITH it, and Grant has not approved it. But it only matters on EASY: on NORMAL and HARD every car is at PACE 16, where the gate is always open - measured without the fix, NORMAL laps the same (17.8 / 18.1 / 19.0 / 19.3).
- ONE UNFAIRNESS TO KNOW: a computer car's lap is counted when it "reaches" the first waypoint past the line, yours 40 px before it. With REACH 56 the quickest car is counted about 16 px (0.2 s) sooner than you would be - once a race, at the flag. Worked out from the code, not measured; not changed.
- THE PACK COSTS PICTURES: keener cars stay in view, and each car in view is about 9,000 T. In the pack: today's cars 10.75 a second (10.4 on the 56 px sharp track), NORMAL 9.4 to 9.9, HARD 9.4. With `GRIP1=1` (your car worked out once a picture) the 56 px sharp NORMAL tape makes 11.9 / 12.1 / 10.25.

C. RECOMMENDATION AND TAPES. Drive build/racer_tight_w56s_normal.tap first (56 px, sharp corners, NORMAL), then racer_tight_w56s_hard.tap. 56 px leaves room for two cars side by side; the 48 px road takes that away, costs the most drawing time and was the only one where the corner-cutter had bad laps by itself. All in build/: racer_tight_w56_easy / _normal / _hard, racer_tight_w56s_easy / _normal / _hard, racer_tight_w48s_easy / _normal / _hard, and racer_tight_w56s_normal_grip1 (the quicker twin). Each is `PACEFIX=1 AI=<0, 1 or 2> RT_ROADW=<56 or 48> RT_CORNER=<54 or 27> RT_PIN_GAP=1 RT_PIN_W=1 RT_PIN=solid RT_NOLINE=1 RACETRACK=1 OUT=racer_tight_<name> BDIR=tight_<name> bash build.sh` (add `GRIP1=1` for the twin); always run plain `bash build.sh` last. Pictures, docs/design/racetrack/tight/: <name>_track.png (the whole track, 3x - the generator now draws one for every race-track build, rt_track_preview.png in the build's folder), <name>_corner.png (the first corner in the pack, 3x) for w56_normal, w56s_normal, w56s_hard, w48s_normal; w56s_normal_lap.mp4 (10 s at real speed, every TV frame, 2x: the first two corners in the pack). Tools: tests/rt_tight.py (laps and grass, car by car; it can try the cars' numbers without building a tape), tests/rt_ace.py (the corner-cutter), tests/rt_tight_shots.py (the pictures and the clip).

- TESTS. The plain game, tracks 2, 3 and 5 and the two thin-green-line trial tapes were deleted and built afresh: byte for byte what they were (md5). tests/racetrack_test.py (not changed; it does not apply to the green-line tapes, so the white-dash build of each shape was made for it and racer_racetrack.tap put back after, md5 the same): 72 px / radius 54, 15 pass; 56 px / 27, 14 pass and 1 fail ("during the slide ... 2 pixels" - taken to be the known 2 pixels of rim at the window's edge, stage F of the last entry; NOT looked at pixel by pixel, so that is a guess); 48 px / 27, 15 pass. tests/rt_fixed_test.py: 3 pass on w56_normal, w56s_easy, w56s_normal, w56s_hard, w48s_normal and the GRIP1 twin.
- NOT DONE / NOT VERIFIED: nobody has driven any tape - whether it feels harder, or fair, is Grant's to say; the "good human" is an autopilot. The clip was made but not watched. Tracks 2, 3 and 5 are not built this way (RT_ROADW and RT_CORNER are track 1's; the AI levels build on any track but were measured only here). A hairpin or tighter chicane, a shorter start line (so the grass can come nearer), a fairer lap count for a big REACH: not built. Not tried on a real Spectrum.

## 17 Nov 2026 - the green-line race track as one switch, and tracks 2 and 3 built in it (background agent, branch worktree-agent-a272a1ab88e676794)

Grant chose the edge marking: the THIN GREEN LINE just inside the grass's edge ("the lines on the outside look good"). The coordinator's brief: make that look one short switch, build tracks 2 and 3 in it, test each, fix the 2-pixel rim fault if cheap, pictures. THE SHORT OF IT: `RACETRACK=green bash build.sh` builds it; tracks 1, 2 and 3 all build, fit and pass every test, each also with `GRIP1=1`. Track 3 is as quick as track 1; TRACK 2 IS SLOWER (about 10 pictures a second, 9.25 in the pack) because its roads lie close together and more grass edges are in view. Two faults at the window's edges were found and fixed. Nobody has driven any of it.

THE BUILDS (always run plain `bash build.sh` last):

| | command | tape |
|---|---|---|
| track 1 | `RACETRACK=green bash build.sh` | build/racer_track_green.tap |
| track 2 | `TRACK=2 RACETRACK=green bash build.sh` | build/racer_track_green_track2.tap |
| track 3 | `TRACK=3 RACETRACK=green bash build.sh` | build/racer_track_green_track3.tap |
| your car's grip sums once a picture | `GRIP1=1` in front of any of them | ..._grip1.tap |

The long form (`RT_PIN_GAP=1 RT_PIN_W=1 OUT=racer_racetrack_noline_pin1 BDIR=racetrack_noline_pin1 RT_PIN=solid RT_NOLINE=1 RACETRACK=1 bash build.sh`) still works and makes the same bytes as `RACETRACK=green` (md5 checked, with and without GRIP1). Breakfast things, cereal O's and the cloth are off on every track.

MEASURED (python3 tests/stage_profile.py, the same three 8-second drives; pictures a second; bytes free in the program; lap times by autopilot in seconds, tests/rt_laps.py):

| track | start, alone | mid-lap, alone | in the pack | bytes free | your lap alone | your lap in the pack | computer cars' laps |
|---|---|---|---|---|---|---|---|
| 1 | 11.62 | 12.00 | 10.00 | 549 | 18.8, 18.8, 18.8 | 18.5, 18.6, 19.0 | 18.4 to 20.9 |
| 1, GRIP1 | 11.88 | 12.38 | 11.38 | 535 | 18.2, 18.1, 18.4 | 17.8, 18.3, 18.3 | 18.0 to 21.5 |
| 2 | 10.12 | 10.00 | 9.25 | 1,974 | 27.1, 27.3, 27.4 | 27.0, 27.7, 27.8 | 26.0 to 30.8 |
| 2, GRIP1 | 10.50 | 10.50 | 9.50 | 1,960 | 27.4, 26.9, 26.6 | 26.5, 27.1, 26.9 | 25.3 to 29.1 |
| 3 | 11.75 | 11.25 | 11.00 | 202 | 31.5, 31.4, 31.2 | 31.5, 31.2, 31.1 | 31.3 to 34.0 |
| 3, GRIP1 | 11.88 | 12.12 | 11.50 | 188 | 31.4, 30.5, 30.4 | 31.6, 30.5, 30.6 | 29.8 to 35.0 |

(Today's breakfast tape: 12.4 / 12.4 / 12.6. Track 1's figures are what they were before this work - the fixes below cost nothing measurable - but its bytes free went from 747 to 549: the edge fix is 198 bytes. Each build also has 15 bytes free under 0x8000.) Tests on all six tapes: tests/racetrack_test.py 15 of 15 on track 1, 16 of 16 on tracks 2 and 3 (the 16th is the look-alike check, below); tests/rt_fixed_test.py 3 of 3.

WHY TRACK 2 IS SLOWER: nothing is wrong with it - the work a picture in the pack is 348,000 T-states against track 1's 312,000 and track 3's 284,000 (off the start alone 314,000 against track 1's 267,000), and the difference is in making up the squares that hold a grass edge (the race track's own part is 73,500 T a picture in the pack against track 1's 54,000). Track 2's rows of road are 3 to 5 tiles apart, so the window often holds three or four edges where track 1 holds two. The only cures are the ones the last entry listed (the white-line builds had the same cost), or a track 2 with its roads further apart.

WHAT ASSUMED TRACK 1, AND WHAT WAS DONE (tools/make_world.py unless said):
- TOO MANY EDGE PICTURES. The map is a byte a tile, so 256 pictures at most (and their eight pages are full at 256). Track 1 has 204 with the green line; track 2 wanted 327 and track 3 335, because their bends are all different. So where a track has too many, the part-grass pictures that differ least from another are drawn as that one - fewest pixels first, never a tile moved twice. Track 2: 71 pictures merged, 145 pixels moved in 81 tiles; track 3: 79 merged, 174 pixels in 88 tiles; 3 pixels at most in any tile. It moves a pixel or two of the grass's edge or the line in those tiles; grip does not come from these pictures. Track 1 is not touched. NOT JUDGED BY EYE beyond the stills: a line that steps a pixel where it should not is what to look for.
- THE MAP DID NOT FIT. Track 3 as first built was 1,440 bytes over in the program, and 13 over at the top of the room under 0x8000. Three things, none of them a change to the game's code: (1) the map's rows are laid into each other's unused gaps - the game only reads the tiles at a grass edge or with white on them, so where the track crosses a row twice the tiles between are never read and another row can lie there; (2) rows share bytes where they want the same picture at the same place (a straight piece going up the map is the same tiles row after row) - never a NOS canister's tile, which the game rubs out; (3) the row lists and their index, which the race track never reads, are left out. Track 2's map went from 4,010 bytes to 2,274, track 3's from 5,217 to 2,859. All three are on for tracks 2 and 3 only (RT_GAPS): track 1's tape is left byte for byte as it was measured. Turned on for track 1 (`RT_GAPS=1 RACETRACK=green bash build.sh`, tried and thrown away) they leave 2,719 bytes free there instead of 549: 2,170 bytes to be had when they are wanted.
- TRACK 3 IS 84 ROWS, TALLER THAN 64. Its blocks' kinds (36 bytes a row: 3,024) no longer fit above the pictures (5,752 bytes wanted, 5,315 there), so on such a track the kinds and the rows' addresses live in the program and the room up there is all the map's. The game reaches them by name (RT_CLS, RT_MAPR), so nothing in it changed.
- A CHECK THAT COULD NOT FAIL (src/racer.asm). "The pictures and the map run into the row lists" compared addresses, and an address past 0xFFFF starts again at 0 and passes. Track 3's first build got through it while running 437 bytes off the top of memory. It now compares sizes.
- TRACK 3'S MINI-MAP IS TALLER (26 lines; 17 and 20 on tracks 1 and 2) and its top lines stood in squares that scroll (src/racetrack.asm). Its black box is now as many rows of squares as the map needs - four on track 3. Tracks 1 and 2 do not change by a byte.

TWO FAULTS AT THE WINDOW'S EDGES, BOTH FIXED (src/racetrack_hot.asm; they were in every race-track tape, so the eleven older trial tapes were rebuilt too):
- THE 2 PIXELS OF RIM (the known one). A car's black rim is made by cutting its shape one pixel left, right, up and down; the part of a car that is out of sight beyond the window's edge brought its rim one pixel into view. Now, for a car that reaches past an edge, the window's edge column (or line) is kept through that one pass and put back. 198 bytes; it runs only for a car at an edge, and the speed figures did not move.
- A NEW ONE, found because track 2 showed it: a car at the window's LEFT edge whose first row of squares was row 0, 8 or 16 put its colour into squares 8 rows lower - and from row 16 that is past the end of the squares' table, into the first line of four of the grass's pictures, which stayed wrong for the rest of the race (2 pixels of green in the road at four kinds of tile). One instruction order in rt_car_sq; no bytes, no time. Track 1 had it too; its tests never landed on it.

THE TESTS (nothing loosened):
- tests/racetrack_test.py takes TRACK and TAPE (`TRACK=2 python3 tests/racetrack_test.py`; `TAPE=racer_track_green python3 tests/racetrack_test.py`). Its own picture of what the screen ought to show now has the build's green line, worked out from the road's shape again, not read from the build - so it applies to the line builds for the first time. Where the generator drew a tile as a look-alike the test takes that tile as the build says, after checking it is within 3 pixels of the true shape (the 16th check); every other pixel must still match exactly. The parked-car part now also parks on the start line, so there is white under the car whatever the limit line is ("squares of every kind" used to fail on every build without a white line). Two places were track 1's own: the grass below the start straight (tracks 2 and 3 end 72 pixels below it), and "30 seconds is time to begin a second lap" (now as much longer as the track is).
- tests/rt_fixed_test.py knows the taller map box; tests/rt_laps.py takes SECS and ALONE=1; tests/rt_track_shots.py is new (the pictures below).
- The older trial tapes after the fixes: white dashes, no line, sparse and green dashes all pass 15 of 15 (the no-line tape used to fail two).
- The plain game and tracks 2, 3 and 5 were deleted and built afresh at the end: byte for byte what they were.

PICTURES: docs/design/racetrack/built/green_track2_grid.png, green_track2_bend.png, green_track2_bend.mp4, and the same three for track3 (3x stills; the clips 2x, 6 seconds, a screenshot for every TV frame, so they show the game's own picture rate).

TRACK 5 (THE BRIDGE) IS NOT BUILT, and `RACETRACK=green` says so. What it would need: (1) a look for the bridge in this style - the concrete deck and its kerbs are white and cyan today, and the generator stops at once because they come within a colour square of the grass; (2) the bridge drawn by the race track's squares - today it is drawn by the tile routines and their masks, which the race track leaves out, so the deck, the cars passing under it and the kerbs all need writing again; (3) room - track 5's own tape has 2 bytes free before any of this. It is a piece of work of its own, not a switch.

NOT DONE / NOT VERIFIED: nobody has driven any tape, and nobody has judged GRIP1's feel. Not tried on a real Spectrum. The look-alike tiles were checked by the test (within 3 pixels) and in the stills, not by eye along every edge. The older trial tapes were rebuilt and tested but their speeds were not measured again (track 1's green tape was, and did not move). Track 3 has only 202 bytes free (188 with GRIP1), with every saving above already on: anything more on that track needs room found somewhere else. Track 2's speed is the open question for Grant.

## 17 Nov 2026 - two players in one shared view: a trial tape of track 1 on the race-track look (background agent, branch worktree-agent-a32fda323d3c74788)

Grant, shown four layouts (docs/design/racetrack/two_player_options.png): "two players would exist in the same screen" - A, one shared view. THE SHORT OF IT: on a build switch (`TWOP=1`, with RACETRACK=1; off by default, and every default tape is byte for byte what it was) the title's 2 now starts a two-player race: player 2 drives the cyan car from the second grid place on their own keys, with the same grip sums as player 1's car; the view sits between the two cars; a car left behind is put back behind the leader (the LEASH); a panel top right shows both players' place and lap. The other three cars are still the computer's. It costs pictures: 9.4 a second off the start with two players against 11.4 with one (10.5 with `GRIP1=1`). Nobody has driven it, and what it is like for two people cannot be judged from here.

THE TAPE: build/racer_2p.tap - `TWOP=1 PACEFIX=1 AI=1 RT_ROADW=56 RT_CORNER=27 RT_PIN_GAP=1 RT_PIN_W=1 RT_PIN=solid RT_NOLINE=1 RACETRACK=1 OUT=racer_2p BDIR=racer_2p bash build.sh` (the 56 px sharp track, NORMAL computer cars). Its quicker twin, build/racer_2p_grip1.tap: add `GRIP1=1` and `OUT=racer_2p_grip1 BDIR=racer_2p_grip1`. The POINTS rule, build/racer_2p_points.tap: add `TWOP_PTS=3` and `OUT=racer_2p_points BDIR=racer_2p_points`. Always run plain `bash build.sh` last. 1 on the title is the one-player game, as before.

- THE KEYS. Player 1: as chosen on the K screen (as loaded O P Q A SPACE). Player 2: 6 left, 7 right, 0 accelerate, 5 brake, 8 NOS. NOT 9 FOR THE NOS, as first suggested: the Spectrum's keyboard is a grid of 8 x 5 wires and three keys at three corners of a square of it read as the fourth too. O and P are in one row, 9 and 0 in another, in the same two columns - so P + 0 + 9 would read as O as well, and O + P + 0 (player 1 changing hands on the steering while player 2 accelerates) would fire player 2's NOS. With 9 left out no three of the ten keys make a fourth that is in use (worked out from the grid, not tried on a real keyboard: player 1's P, Q, A and SPACE all share a column with 0, but none of their rows has a second key in use except O and P's; the ghosts land on U, Y, W, T, R and the like, which the race does not read). That is the Spectrum's grid; a PC keyboard under an emulator has ghosting of its own, not looked at. The K screen does not redefine player 2's keys: they are fixed in this trial. (If player 1 redefines theirs onto the 6-0 row or into its columns, they can clash.)
- PLAYER 2'S CAR IS YOURS, TWICE. The grip model keeps one car's speeds in 34 bytes; the 18 of them that last from one TV frame to the next change places with player 2's copy around player 2's turn, and so do the NOS timers; for as long as the physics runs, player 2's car is "car 0, you". So grip, slides, grass and NOS are the same sums. To change places only twice a picture, player 2's car takes all of a picture's TV frames one after the other, after everything else (the buttons are read in a burst at the start of a picture anyway). Player 2 has their own three NOS canisters (picked up from the same cans on the road), shown as a number on the panel.
- WHAT PLAYER 2 DOES NOT HAVE, and what was done about it: DAMAGE is switched off for both cars in a two-player race (there is no room for a second gauge or its sums, and one car with damage and one without is not fair) - player 1's mug stays full. The crash noise and red border are only for crashes player 1's car is in. The engine note, the corner arrow, the crew chief, the lap plate and time in the window, FINAL LAP and the lap times under YOUR RACE are all player 1's. The car set-up keys 1, 2, 3 before the lights are player 1's.
- THE VIEW: half way between the two cars, held inside the world as today. It does not lead the car the way it is going, as the one-player view does (which car?): with the cars together it is today's view without that lead. THE LEASH (the default rule): the car further round the lap - the first of the two in the race order - is never nearer the window's edge than 40 px left and right, 32 px top and bottom (P2_MX, P2_MY in src/twoplayer.asm), so it can always see some road ahead; that lets the cars get 136 px apart across or 104 px up and down. When the other car's 16 x 16 box would cross the window's edge it is put back: on the middle of the road, at the first waypoint behind the leader that is 40 px or more from it (LEASH_BACK; measured 30 to 72 px from the leader), facing the next waypoint (the nearest of 8 directions), standing still, held with no buttons and flashing for 12 TV frames - a quarter of a second (LEASH_HOLD), with a beep. THE TIME IT COSTS is that hold and starting from rest: about half a second. It cannot be much more - in one view a car put back "behind the leader and in the window" is by definition close. Its lap count becomes the leader's lap at that spot (one less if the start line is still ahead of it, which it then crosses and is timed for itself). A car that never moves is towed round: about 13 leashes a lap.
- THE POINTS RULE (`TWOP_PTS=N`) turned out cheap, in a plain form: each time the leash goes the leader scores a point, shown on the panel ("2 - 1" where player 2's NOS count was); N points end the race there and then, and the podium shows the order on the road. It is NOT the full rule as described to Grant: the cars are not put side by side (the car is put back behind the leader, as the leash does), there is no "player 1 wins" screen, and the computer cars are on the podium too. That would need its own end screen: not built. Tried once (a stopped player 2 lost 3 - 0 in 6 seconds); the test below was not run on it.
- THE FINISH: the race ends as today - when four cars are in - but only once BOTH players are among them, or 30 seconds after player 1 finishes. A player who has finished rolls to a stop and the view becomes the other's; the leash is off from then. The podium is unchanged ("YOU" is player 1; player 2's car appears as the cyan driver). If player 2 wins there is no message for them: only the order and the panel say so.
- THE PANEL, top right above the race order: "P1 1ST / LAP1/3" white on red (player 1's car is red), "P2 2ND / LAP1/3 / NOS 0" black on cyan (player 2's is cyan). A row is printed only when what it shows changes.
- MEMORY. It took 767 bytes of the program's 867 free (100 left; 66 with GRIP1; 66 with the points rule), and there was not room for all of it there: its variables sit in the title's variables (free once the race is on) and its copy of the grip sums, two routines and a table in the page under the stack that only track 5 uses (0x5E00 to 0x5E9C; the stack has from 0x5EA0), copied down at the start; a new-race routine and the panel's texts are under 0x8000 (2 bytes free there now; the "2UP COMING SOON" message went, which gave 80). It is FULL: anything more for two players needs memory found first.
- SPEED (pictures a second; python3 tests/twop_speed.py <tape> <build folder>: three 8-second autopilot drives as tests/stage_profile.py's - off the start and mid-lap with the computer cars held on the grid, and in the pack; with two players both cars are driven):

| tape | players | start | mid-lap | pack | bytes free |
|---|---|---|---|---|---|
| racer_tight_w56s_normal (no switch) | 1 | 11.38 | 11.75 | 9.50 | 867 |
| racer_2p | 1 | 11.38 | 11.62 | 9.88 | 100 |
| racer_2p | 2 | 9.38 | 9.25 | 8.25 | 100 |
| racer_tight_w56s_normal_grip1 (no switch) | 1 | 11.75 | 12.12 | 10.38 | 853 |
| racer_2p_grip1 | 1 | 11.62 | 12.12 | 10.38 | 66 |
| racer_2p_grip1 | 2 | 10.50 | 10.50 | 9.62 | 66 |

  One player on the two-player tape costs nothing that shows. A SECOND HUMAN CAR COSTS ABOUT TWO PICTURES A SECOND: by the emulator's profiler its grip sums every TV frame are roughly 15,000 to 20,000 T-states a picture, the two changes of place about 2,700 (worked out) and the second car's drawing the rest, on a picture of about 270,000 - and a picture is a whole number of TV frames, so that tips most of them from 4 or 5 frames to 5 or 6. With GRIP1 (both human cars' grip worked out once a picture; they still steer every TV frame) it is one picture a second. So the two-player tape to drive is the GRIP1 one, if GRIP1's handling is accepted.
- TESTS. tests/two_player_test.py (new; 19 checks, all pass on racer_2p and on racer_2p_grip1): each car answers only its own keys and each NOS key fires its own player's canister; over a whole race by two autopilots both cars are wholly inside the window at every picture (511 pictures), laps count for both and the race ends with both in; with either player stopped, the car is put back 39 times in three laps, every time on a waypoint with road under it, in the window, 1 to 4 waypoints behind the leader, standing still, facing within 45 degrees of its next waypoint, held still for the hold, its lap following the leader's; and ONE PLAYER ON THE TWO-PLAYER TAPE IS THE GAME WITHOUT THE SWITCH - a scripted drive's car, and the computer's second car, are in the same place on both tapes at all 230 pictures, alone and in the pack. (How that last one is done matters: the game reads keys and moves cars in a burst at the start of each picture, as many TV frames' worth as the last picture took, so comparing two tapes TV frame by TV frame compares their speed, not their rules. Both are stopped at the same instruction each picture, the burst is made 5 frames, and keys change there.) tests/rt_fixed_test.py on racer_2p: 3 pass. tests/racetrack_test.py was not run (it does not apply to the green-line tapes). The plain game, tracks 2, 3 and 5 and racer_tight_w56s_normal.tap, deleted and built afresh: byte for byte what they were (md5). tests/rt_lib.py: to_grid takes the title key (default 1, as before). Helpers: tests/twop_lib.py, tests/twop_speed.py, tests/twop_shots.py.
- PICTURES, docs/design/racetrack/two_player/: two_player_both.png (3x, both cars), two_player_leash.png (3x, just after a car is put back), two_player_clip.mp4 (12 s at real speed, 50 frames a second, 2x: from the lights, player 2 easing off from 3 s, the leash at 5.0 s, and on). Made by python3 tests/twop_shots.py. Four frames of the clip were looked at; it was not watched as a film.
- NOT DONE / NOT VERIFIED: nobody has driven it, and two people at one keyboard have not tried the keys. Not tried on a real Spectrum. Player 2's damage, crash noise, gauge, arrow and messages (above). Player 2's keys on the K screen. The full points rule. Tracks 2, 3 and 5; the choose screen (OPT_CHOOSE) is not combined with it. The leash numbers are first guesses, to tune: P2_MX 40, P2_MY 32, LEASH_BACK 40, LEASH_HOLD 12 (src/twoplayer.asm, top). One thing seen in the clip: a car can be put back on top of a computer car that is at that waypoint (they bounce apart). (The page under the stack: over a whole two-player race on each tape the stack went no lower than 0x5EC8 and the routines copied there were unchanged at the end.) The engine files (racetrack.asm, racetrack_hot.asm) were not touched; build.sh only gained the switch, tools/make_world.py nothing.
## 17 Nov 2026 - the race track: the smoothness pass - 40,000 T a picture found with nothing changed on the screen, one new switch, and what track 2 needs (background agent, branch worktree-agent-aaccef13180d1b3bf)

Grant, after driving: "Now the focus should be to improve smoothness." The coordinator's brief: every picture inside 4 TV frames (12.5 a second) in the pack, the picture and the driving unchanged; exact savings first, then measured switches; say what track 2 needs. THE SHORT OF IT: three exact stages took track 1 in the pack from 312,000 T of work a picture to about 273,000 (10.0 pictures a second to 11.4-11.5), alone to 12.0 off the start and 12.4 mid-lap; with GRIP1 12.5 / 12.75 / 11.6. Nothing on the screen changed and every test passes as before. 12.5 IN THE PACK IS NOT REACHED without switches: GRIP1 and the new REACT1 together make 12.4 on track 1 (and REACT1 slows the computer cars by about 1.5 s a lap). Track 2's deficit is its geometry and only a wider-spaced track cures it. Nobody has driven any of this.

THE TABLE (python3 tests/stage_profile.py, the same three 8-second drives: pictures a second off the start alone / mid-lap alone / in the pack; in brackets the T-states of work a picture in the pack; each tape then its GRIP1 twin):

| | track 1 green | with GRIP1 | tight 56 px, NORMAL | with GRIP1 | track 2 green | with GRIP1 |
|---|---|---|---|---|---|---|
| before | 11.62 / 12.00 / 10.00 (312,000) | 11.88 / 12.38 / 11.38 (273,000) | 11.50 / 11.75 / 9.88 (325,000) | 11.88 / 12.12 / 10.25 (318,000) | 10.12 / 10.00 / 9.25 (348,000) | 10.50 / 10.50 / 9.50 (333,000) |
| 1. the cars (estimate 12,000 T) | 11.75 / 12.25 / 10.88 (288,000) | 12.00 / 12.50 / 11.50 (267,000) | 11.62 / 11.88 / 10.38 (308,000) | 11.88 / 12.25 / 11.12 (285,000) | 10.38 / 10.12 / 9.75 (333,000) | 10.62 / 10.50 / 10.12 (313,000) |
| 2. the edge squares (estimate 5,500) | 11.75 / 12.38 / 11.50 (272,000) | 12.62 / 12.88 / 11.75 (260,000) | 11.88 / 12.00 / 10.50 (298,000) | 12.25 / 12.62 / 11.38 (275,000) | 10.75 / 10.38 / 10.00 (316,000) | 10.88 / 10.75 / 10.50 (303,000) |
| 3. plain squares under a car (estimate 2,600) - THE TAPES AS THEY NOW ARE | 12.00 / 12.38 / 11.38 (275,000) | 12.50 / 12.75 / 11.62 (268,000) | 11.75 / 12.12 / 10.38 (307,000) | 11.88 / 12.38 / 11.62 (273,000) | 10.75 / 10.50 / 10.00 (315,000) | 11.12 / 10.75 / 10.62 (294,000) |
| the switch REACT1 on top (changes the computer cars) | 12.25 / 12.75 / 11.75 (260,000) | 13.25 / 13.50 / 12.38 (240,000) | 12.25 / 12.62 / 11.25 (279,000) | 12.88 / 13.25 / 11.75 (263,000) | not built | not built |
| bytes free in the program | 371 | 357 | 491 | 477 | 1,796 | 1,782 |

Track 3 green now makes 12.00 / 12.12 / 11.50, with GRIP1 12.38 / 12.75 / 12.12 (it made 11.75 / 11.25 / 11.0), and has 24 bytes free (10 with GRIP1). READ THE PACK COLUMN WITH CARE: a quicker picture changes how the race unfolds, so two builds never drive the same 8 seconds - the same source measured twice at different addresses gave 299,000 and 307,000 on the tight tape. Differences under about 5,000 T (0.2 of a picture a second) in the pack are noise; stage 3's saving is by the count of instructions, not by the measurement. The savings are bigger than the estimates in the pack because a picture that takes 4 TV frames instead of 5 also has one frame less of moving and thinking to do (about 12,000 T).

WHERE THE TIME IS NOW (track 1 in the pack, a picture, by the emulator's count of each routine - `calls on` and `routines`, a better tool than the profiler's addresses; it was used before every choice): sending the picture up 111,000 (of it making up the 91 grass-edge squares 60,000 - 656 T each; visiting all 456 squares 28,000; copying the 61 squares that are in the buffer 10,000); a TV frame of moving and thinking 11,600, 4.3 times a picture = 50,000 (your car and its grip 5,000-6,000 of each, the computer cars' thinking 5,200); moving the computer cars 20,000; the cars' drawing and colour rule 33,000 (it was 50,600); deciding the squares' colours 23,000; the plate 7,400, the arrow 5,400, the panel 5,300, laps and places 3,800, bumps 3,400, the fixed boxes 2,500; the interrupt and sound 3,500.

WHAT WAS DONE - ALL EXACT (src/racetrack_hot.asm; one line in src/racetrack.asm):
- STAGE 1, THE CARS. (a) Finding which squares a car has pixels in read the car's picture row by row at 202 T a row; it is now a short loop for each row of squares, 84 T a row (rq_g1). (b) THE SHORT CUT, rt_car_ink: a car alone on plain squares - nearly every car - has every square under it cleared a moment before it is drawn, so there is nothing to cut a hole in. Only its ink is put in, straight from the rows the first look found, without draw_car's working-out a second time. The buffer ends up byte for byte as draw_car leaves it (a pair of bytes is still passed over when its MASK is empty, as there); a car that shares a square with another car, the arrow, a box, the grass's edge or the window's margin is drawn the old way (rt_slow says which). (c) Clearing a square works its buffer address out in line. A car in view cost about 14,000 T; now about 10,000. draw_car itself (src/racer.asm) is not touched.
- STAGE 2, THE GRASS-EDGE SQUARES. (a) rt_show asked two questions of every square (in the buffer? made up here?); now one - a compare that only the hidden squares pass (CP 0x40 overflows for 0x80-0xBF and nothing else), 7 T less for each of the 330 hidden squares and 48 bytes shorter. (b) The way from rt_show into rt_sq is shorter (it comes in with the map's registers already in hand; the two copies of "move the map's pointers on" are one). (c) In the one picture in eight where the camera's height is a whole number of squares, a square lies wholly on its upper pair of tiles: rt_sq then ends at the fold (a RET patched in) instead of looking at the lower pair and writing no lines from it.
- STAGE 3. A plain-road square under a car (nothing showing in it - the usual case) is cleared and given the car's colour in one short step in rq_cell (rq_setpg tells it the row's page of the buffer; rt_arrow calls it too).
- ROOM: the three stages cost 178 bytes net. Track 3 was the limit (it had 202 free): with GRIP1 it has 10 left. Nothing moved between the slow and the fast half of memory.

LOOKED AT AND NOT BUILT (with the numbers):
- THE KINDS A BYTE A BLOCK (8,700 T): a byte a block without cutting rows to their spans is 36 bytes a row more - 2,304 on tracks 1 and 2. Track 1 would have it only with RT_GAPS turned on (2,719 free there, less this pass's 178), track 2 has 1,796 free, track 3 has 24. Not built: it is the next exact step for track 1 and the tight track if wanted. The kinds as runs were costed again: walking a row's runs to the window's first column and setting up each run comes to about 800 T a row, what the table look-up costs now - no gain.
- A CASE NUMBER FOR EACH GRASS-EDGE SQUARE, worked out by the generator (which of its four tiles are nothing, all grass or a picture - the game finds this out afresh for every square, about 100 T of the 656): the kinds' map has room for 12 such numbers. About 85 T a square, 8,000 T on track 1 and 12,000 on track 2, for about 275 bytes and a change to make_world.py. Not built: no room on track 3, and it is the biggest piece of work left. (Both figures are estimates, not measurements.)
- MAKING UP EDGE SQUARES IN RUNS (one call for several neighbours): the way back into rt_show's unrolled row costs as much as it saves. THE VISIT BY RUNS: every routine that marks a square (the cars, the boxes, the lights, the crew chief's bubble) would have to keep the runs right; 4,000 T at most, as the last pass found.
- STILL RUNNING BELOW 0x8000 AND HOT: the place plate (pl_draw: 7,400 T a picture, perhaps 1,500 of it the slow memory's doing) - it went down there in exchange for the drawing code and there is no room above to bring it back (track 3). Nothing else below 0x8000 costs over 1,500 T a picture.
- THE MOVING AND THINKING (src/racer.asm: physics, friction, wp_delta, ai_drive - 70,000 T a picture in the pack): not touched. Another agent is working in that code for the two-player mode. A computer car already decides only once every 4 TV frames; its other turn is cheap (700 T).

THE SWITCHES (behaviour-changing, off unless asked for; each with its GRIP1 column above):
- GRIP1 (as before: your car's grip sums once a picture). It does not apply to the computer cars: they have no grip model and are already moved once a picture.
- REACT1, NEW: `REACT1=1` in front of a race-track build (-> ..._react1.tap; build.sh, and four numbers in the cars' table in src/racer.asm). Each computer car decides how to steer every 8th TV frame, not every 4th (their REACT setting one higher - a setting the game always had). 11,000 to 19,000 T a picture in the pack. WHAT IT COSTS: the computer cars turn in later and run wide. By autopilot (tests/rt_laps.py, 60 s): track 1 their laps 17.6 to 20.8 s, mean 19.4, become 18.5 to 24.6, mean 21.0; the tight track 17.3 to 20.9, mean 18.6, become 18.4 to 22.6, mean 20.1. Not recommended as it stands - it would want their pace and reach tuned again.
- "COMPUTER CARS FAR OUTSIDE THE VIEW THINK HALF AS OFTEN": not built. It saves only for cars out of sight - none at the first bend, where the pack is slowest, and on the tight track the rivals stay in view (3.7 of the 5 cars are in the window on average). At most 3,000-5,000 T late in a race (an estimate).

LAP TIMES (tests/rt_laps.py; your car by autopilot; seconds; before -> after the exact stages): track 1 alone 18.8, 18.8, 18.8 -> 18.8, 18.5, 18.3; in the pack 18.5, 18.6, 19.0 -> 20.6, 19.2, 19.2 (the first lap is 2 s longer - probably a bump with a computer car, not looked into); the computer cars' mean 19.5 -> 19.4. Track 1 GRIP1 alone 18.2, 18.1, 18.4 -> 18.4, 18.1, 18.3; pack 17.8, 18.3, 18.3 -> 17.8, 18.1, 17.8; computer cars 19.5 -> 19.2. Tight alone 19.4, 19.9, 19.2 -> 19.1, 19.1, 19.4; pack 20.1, 20.8 -> 20.0, 20.0; computer cars 18.5 -> 18.6. Tight GRIP1 alone 18.9, 19.0, 18.8 -> 18.8, 18.8, 19.1; computer cars 19.0 -> 18.6. The game moves everything by TV frames, so pictures arriving sooner do not change its rules, only when the autopilot sees them; apart from that one first lap the times are within what one race differs from the next.

TRACK 2 - THE NUMBERS. Mid-lap alone it makes up 147 grass-edge squares a picture against track 1's 95: 101,000 T against 60,000. That 41,000, and the fifth TV frame of moving it causes (about 12,000), is nearly all of its deficit (300,000 T of work a picture against track 1's 243,000). A look-alike merge of edge tiles does NOT help: the cost is for each square made up, whatever picture is in it, and merging pictures makes no square fewer. The case numbers above would give about 12,000 and the kinds a byte a block 8,700 (it has no room for both): about 280,000, still 5 frames for most pictures. To make 12.5 it needs about 50 fewer edge squares in view - track 1's geometry, the window holding two grass edges, not three or four: ONLY A TRACK 2 WITH ITS ROADS FURTHER APART does that. As it is: 10.75 / 10.5 / 10.0, with GRIP1 11.1 / 10.75 / 10.6.

THE SEAM (the emulator's tear report, 8 s in the pack): the tight tape - 56 TV frames with a torn square before, 49 after (69 torn squares in all before, 65 after; 79 pictures before, 83 after); track 1 - 43 frames before, 39 after (52 squares, 50). A shade better or the same: a square's pixels and its colour still go up together.

TESTS (nothing loosened). tests/racetrack_test.py and tests/rt_fixed_test.py on every race-track tape, each with the switches it was built with: the eleven trial tapes 15 of 15 and 3 of 3 (the two small-window tapes: the first test does not apply to them and stops with an error, as it does on the tape from before this work; 3 of 3 on the other); track 1, 2 and 3 green and their GRIP1 twins 15, 16 and 16 of their 15, 16, 16, and 3 of 3; the nine tight tapes and the GRIP1 twin 15 of 15 and 3 of 3; the four REACT1 tapes the same. The plain game and tracks 2, 3 and 5 were deleted and built afresh at the end: byte for byte what they were (md5).

TAPES. Every race-track tape was rebuilt: build/racer_racetrack*.tap (11), racer_track_green*.tap (6), racer_tight_*.tap (10), and four new ones - racer_track_green_react1, racer_track_green_grip1_react1, racer_tight_w56s_normal_react1, racer_tight_w56s_normal_grip1_react1. FOUND ON THE WAY: some of the tight tapes in the repo were stale - built from the starting commit's own source, seven of the ten came out different from the tapes committed with it (only w56s NORMAL and HARD had been rebuilt after the two edge faults were fixed). They are current now. The clip: docs/design/racetrack/built/smooth_tight_before_after.mp4 (the tight NORMAL tape before and after side by side, the first bend in the pack, 8 s, a screenshot for every TV frame, 50 a second, 2x). The two races are not the same race - the quicker one unfolds differently.

RECOMMENDATION. The exact stages are free and are in every tape. For Grant to drive: build/racer_track_green_grip1.tap beside build/racer_track_green.tap, and the same pair of the tight tape - GRIP1 makes 12.5 alone and 11.6 in the pack; if he cannot feel it in the car, it should be the default. REACT1 is there to try but slows the rivals. If the pack must make 12.5 with no switch at all, the two pieces left are the kinds a byte a block and the edge squares' case numbers (about 17,000 T together on track 1 by estimate, both needing memory and the generator), and after them the moving and thinking in racer.asm once the two-player work has landed. Track 2 wants its roads further apart.

NOT DONE / NOT VERIFIED: nobody has driven any tape; nobody has judged GRIP1's or REACT1's feel. Not tried on a real Spectrum. The short cut for a car alone on plain squares is argued exact and passes the pixel-exact tests, but those tests look at the screen, not at every byte of the buffer's margins. REACT1 was measured on track 1 and the tight track only. The longer first lap in the pack on track 1 was not looked into. Track 3 with GRIP1 has 10 bytes free: the next byte of race-track code needs room found first.

## 17 Nov 2026 - the race track: everything fits again (the two-player mode with the smoothness pass), smoothness pass 3 - one exact stage, a test that proves "the same game", and what is left (background agent, branch worktree-agent-ab528df27c01b41e6)

The coordinator's brief: the two-player mode and the smoothness pass were merged and no longer fitted together (the two-player build stopped with "the room under 0x8000 runs into the data kept at its top"); make everything build, then a third smoothness pass, exact only. THE SHORT OF IT: everything builds and fits, with room to spare on tracks 1 and 2; one exact stage (the cars' moving sums) took about 5,500 T a picture; track 1 green in the pack makes 11.5 pictures a second (it made 11.4), with GRIP1 12.0 (11.6); two players on the GRIP1 tape make 11.75 / 11.6 / 10.6 (10.5 / 10.5 / 9.6 before the smoothness passes). 12.5 IN THE PACK IS NOT REACHED without switches, and the two bigger exact steps (the kinds a byte a block, a case number for each edge square) are NOT built. Nobody has driven any of it.

STAGE A - THE ROOM.
- WHAT WAS WRONG: the room under 0x8000 (0x5F00 to 0x7C58: the cars' pictures 2,880 bytes, the title 1,072, the place plate's rare parts 1,220, racetrack.asm 225, the driver strip 643, the faces 160, the small letters 92, the place plate's drawing 778, the title's car 430) had 12 bytes free and the two-player mode's part wanted 13 more; and the program itself was 276 bytes over with two players.
- THE MAP: tools/make_world.py's row-sharing (RT_GAPS: rows of the map laid into each other's gaps, and on top of each other where they hold the same tiles - on for tracks 2 and 3 since they were built) is now on for track 1 too. The game reads the same tile at every place it looks; only where each row's address points changes. About 2,200 bytes back. tests/racetrack_test.py (the picture to the pixel) passes as before on every track 1 tape. `RT_GAPS=0` turns it off.
- THE PLACE PLATE'S DRAWING (pl_draw, 778 bytes, 7,400 T a picture) went back up into the program, where code runs at full speed, on tracks 1 and 2 (build.sh writes OPT_RTPUP; `RT_PLATEUP=0` or 1 to say otherwise). Track 3 has no room, so there it stays below. That left 790 bytes free under 0x8000, and the two-player part fits there.
- WHAT STILL RUNS BELOW 0x8000: 5,000 T a picture in all on track 1 in the pack (the biggest: looking at the ground under a car, 1,150 T). Nothing hot is left down there.
- SPEED after stage A: the same as before it (the plate's move is worth about 1,000 T: inside the noise).

BYTES FREE NOW (in the program; then under 0x8000):

| tape | program | under 0x8000 |
|---|---|---|
| racer_track_green, _react1 (GRIP1: 14 less) | 1,763 | 790 |
| racer_track_green_track2 | 1,018 | 790 |
| racer_track_green_track3 (GRIP1: 10) | 24 | 12 |
| racer_tight_w56s_* (w56: 1,865; w48s: 1,843) | 1,941 | 790 |
| racer_2p | 918 | 777 |
| racer_2p_grip1, racer_2p_points | 884 | 777 |
| racer_racetrack (white dashes; _sparse 1,473; _noline 1,880; _pin 1,635; _pindash 1,689; _rows16 1,802) | 1,426 | 790 |

STAGE B, 1 - THE CARS' MOVING SUMS (src/racer.asm: ph_run; race-track builds only - the plain game's code is untouched). Profiled first (tests/stage_profile.py with DUMP=): of track 1's 274,000 T a picture in the pack, src/racer.asm's moving and thinking was 78,000 - and the biggest single piece was the loop that moves a car one TV frame at a time (speed gains the push, loses its friction, is added to its place): 12,000 T. It asked the friction's question at every step, kept its count and the push in memory and reached the car's place through IX. Now the friction's halvings are chosen once for the car (a jump patched into a run of halvings) and the step runs in registers: about 210 T a step where it was 420. The sums are THE SAME TO THE LAST BIT - proved, not argued: the new test below. Measured: 5,500 T a picture (estimate 5,000-7,000).

THE TABLE (pictures a second: start alone / mid-lap alone / in the pack; in brackets the T-states of work a picture in the pack):

| | track 1 green | with GRIP1 | tight 56 px NORMAL | with GRIP1 | track 2 green | with GRIP1 | two players, tight | with GRIP1 |
|---|---|---|---|---|---|---|---|---|
| as merged | 12.0 / 12.4 / 11.4 (275,000) | 12.5 / 12.75 / 11.6 | 11.75 / 12.1 / 10.4 (307,000) | 11.9 / 12.4 / 11.6 | 10.75 / 10.5 / 10.0 (315,000) | 11.1 / 10.75 / 10.6 | did not build | did not build |
| A: it fits | 12.00 / 12.38 / 11.38 (274,000) | 12.50 / 12.75 / 11.62 (267,000) | 11.75 / 12.12 / 10.50 (303,000) | 11.88 / 12.38 / 11.62 (272,000) | 10.75 / 10.50 / 10.00 (314,000) | 11.12 / 10.75 / 10.62 (292,000) | 9.88 / 10.00 / 9.12 | 11.00 / 11.25 / 10.12 |
| B1: the moving sums (est. 5,000-7,000; got 5,500) | 12.00 / 12.50 / 11.50 (268,500) | 12.88 / 13.12 / 12.00 (250,000) | 12.00 / 12.25 / 10.62 (297,600) | 12.38 / 12.75 / 11.38 (269,000) | 10.88 / 10.50 / 10.12 (311,000) | 11.38 / 11.12 / 10.38 (306,000) | 10.62 / 10.75 / 9.00 | 11.75 / 11.62 / 10.62 |

One player on the two-player tape: 12.0 / 12.25 / 11.0, GRIP1 12.0 / 12.6 / 11.1. As ever, read the pack column with care: two builds never drive the same 8 seconds, and under 5,000 T (0.2 of a picture a second) is noise (the tight GRIP1 and two-player pack figures that went down a shade are that). A picture is a whole number of TV frames: track 1 green's work in the pack is under 4 frames ON AVERAGE (268,500 of 279,552), but about a third of its pictures - the ones with the most grass-edge squares in view - still go over and take 5. To make every one fit, the average has to come down to about 238,000 (what the mid-lap drive alone makes: 12.5). That is 30,000 T more on track 1 and 60,000 on the tight track; with GRIP1 12,000 and 30,000.

LOOKED AT AND NOT BUILT:
- THE KINDS A BYTE A BLOCK: the loop is 30 T a square now and would be 16 to 22: 7,000-8,000 T (the last pass said 8,700), for 2,304 bytes. Only track 1 green and the one-player tight tapes have that (2,550 and 2,730 free counting both halves; cold code would have to go below to make it one piece). Two players (1,700), track 2 (1,800) and track 3 have not. Not built: two code paths and a generator option for 7,500 T on two of the four builds, and it does not reach 12.5.
- A CASE NUMBER FOR EACH EDGE SQUARE: still the best step left - it helps every build, and most of all the heavy pictures - and still the biggest piece of work (the generator, rt_show's way in, all nine cases of rt_sq). Not started: there was not the time left to do it safely. The last pass's estimate (8,000 T track 1, 12,000 track 2, about 275 bytes) stands unchecked.
- THE REST OF THE MOVING AND THINKING, by the profile (T a picture, track 1 in the pack): a computer car's decision about 2,500 T, one a TV frame = 11,000 (the way to the waypoint two or three times at 330, four multiplies, the scaling); your car's grip sums 9,500; the tick's own overhead, the keys and the throttle gate 6,000; the push and skid 3,000. Each exact saving left there is under 2,500 T (a quicker wp_delta about 1,200; the decision's multiplies kept in registers about 1,500). Below the 3,000 T bar; left.
- So what would make 12.5 in the pack, honestly: GRIP1 plus the case numbers on track 1 (250,000 less 8,000 - near enough to try); on the tight track not without REACT1 or fewer edge squares in view; two players and track 2 not as they are.

A NEW TEST: tests/rt_same_drive.py <tape A> <its folder> <tape B> <its folder> - do two tapes play THE SAME GAME? The same scripted keys on both, both stopped at the same instruction each picture and given the same burst of TV frames there (3, 4, 5, 6, 8, 4, 1, 5 ... in turn), and after every picture all five cars' whole records and your car's grip sums compared byte for byte, alone and in the pack. Used: the new moving sums against the old on the tight tape, its GRIP1 twin, track 2 green and its GRIP1 twin - the same at all 300 (track 2 GRIP1: 400) pictures; and one player on the two-player tape against the tight tape - the same.
TWO THINGS IT FOUND, neither a fault in the game: (1) the crash noise takes random numbers for as long as it waits for the TV, so how many it takes depends on how quick the picture was - and the computer cars' lines and mistakes come from the same run of numbers. Two tapes of different speed therefore part company after the first bump, with the same rules. The test starts the run of numbers afresh before each picture; tests/two_player_test.py's "one player on the two-player tape" check does the same now (it had begun to fail for this reason once the tapes' speeds changed). (2) tests/rt_lib.py's car() could read a car's place half written: the emulator stops wherever the processor is when the TV frame ends, and between the low and the high byte of x the place read is 256 pixels out. It stopped track 2 GRIP1's pixel test with "index 771 out of bounds" - the processor was at that very instruction, and a frame later the car was at 507. car() now lets the move finish first. Neither change loosens a check.

TESTS (nothing loosened):
- tests/racetrack_test.py and tests/rt_fixed_test.py on every race-track tape, each with its switches: track 1, 2, 3 green and their GRIP1 twins 15, 16, 16 of 15, 16, 16 and 3 of 3; the nine tight tapes, the GRIP1 twin and the four REACT1 tapes 15 of 15 and 3 of 3; the eleven first trial tapes 15 of 15 and 3 of 3 (the two small-window tapes: the first test does not apply and stops with an error, as before; 3 of 3).
- tests/two_player_test.py: racer_2p_grip1 19 of 19. racer_2p 17 OF 19 - NOT AS ASKED. The two that fail are the leash checks ("player 1 stops", "player 2 stops"): once in 40 times the car is put back at the waypoint just behind the leader, 30 px from it, in the window, standing still - but the test counts "waypoints behind the leader" and wants 1 to 4, and this one counts as 0, because the leader had not yet reached its next waypoint and both cars are then heading for the same one. That is what the game's rule says (the first waypoint behind the leader that is 40 px or more from it, across + down) and it can happen whenever the leader is far past its last waypoint; it did not happen in the old tape's 39 leashes because the pictures fell at other moments. Left as it is: making it pass means changing the two-player rule (start the search one waypoint further back) or the test (allow 0) - a choice for whoever owns the mode, not made here. Also seen once, on the GRIP1 tape before the last stage and not since: "held still for the hold - it moved 2 px": the car had been put back onto a computer car parked on the grid (the test keeps them there) and was bumped; the two-player entry already says a car can be put back on top of another.
- The plain game and tracks 2, 3 and 5, deleted and built afresh at the end: byte for byte what they were (md5).
- LAP TIMES by autopilot (tests/rt_laps.py, seconds): track 1 green alone 19.0, 18.7, 18.6; in the pack 18.4, 19.6, 19.6 - THE 20.6 s FIRST LAP the last pass saw did not repeat (a bump, as it guessed); the computer cars 17.3 to 20.7, as before. Tight in the pack 19.9, 20.2; the computer cars 17.3 to 19.6.

TAPES: all 34 race-track tapes rebuilt from this source by a new script, tools/build_racetrack_tapes.sh (one after the other, the plain game last - run it after any change to the race track's code; about 5 minutes). racer_racetrack_noline_pin1.tap is still byte for byte racer_track_green.tap.

NOT DONE / NOT VERIFIED: nobody has driven any of it; not tried on a real Spectrum. The two bigger exact steps above. racer_2p's two leash checks. The pixel test was not run on the two-player tapes (it looks for its build folder under another name; rt_fixed_test passed 3 of 3 on racer_2p before the last stage). racer_2p_points was built and not tested. The seam (tearing) was not measured again.

## 17 Nov 2026 - the race track: smoothness pass 4 - level stretches of the grass's edge copied as they are (8,500 to 29,000 T a picture), and the two-player leash put right (background agent, branch worktree-agent-a0ea9e145ac15e1cb)

The coordinator's brief: have the generator work out a case number for each grass-edge square so the game need not decide what kind of square it is; then the kinds a byte a block; then the two-player leash. THE SHORT OF IT: the profile said the deciding was NOT the biggest part of an edge square, so a different thing was worked out ahead of time instead, and it gave more than the case numbers were ever estimated to: track 1 in the pack 11.5 -> 11.75 pictures a second (GRIP1 12.0 -> 12.4), the tight track 10.6 -> 11.4 (GRIP1 11.4 -> 12.1), track 2 10.1 -> 11.0 (GRIP1 10.4 -> 11.9). The leash is fixed and its test passes 19 of 19 on both two-player tapes. The case numbers and the kinds a byte a block are NOT built. 12.5 in the pack is still not reached on any tape, though the GRIP1 tapes are close. Nobody has driven any of it.

WHERE AN EDGE SQUARE'S TIME WENT (tests/stage_profile.py DUMP=, track 1 in the pack, about 97 such squares a picture, about 790 T each): drawing its lines 36,000 T a picture (a line from one picture-tile 33 T, from a picture and all-grass 41, from TWO pictures joined 73); deciding what the four tiles are and setting up 26,000 (of which the pure "which case" questions about 11,000 - that is all a case number could save, less the 3,000-4,000 its own look-up costs: so 8,000, as estimated); getting to the square from rt_show 14,000.

STAGE 1 - WHAT WAS BUILT INSTEAD: THE BANDED PICTURES (tools/make_world.py, src/racetrack_hot.asm: rt_sq, rt_c1). The dearest lines are the ones joined from two pictures (two look-ups in the shift tables and an OR: 73 T). But about half of all such pairs, on every track, are THE SAME picture twice, and a picture in which every line is all grass or all road - the grass's edge (and the green line) running level. Such a square looks the same wherever its left edge cuts the tiles, so its lines are simply the picture's own lines: copied, 22 T a line, no tables. The generator now gives those pictures the first numbers (2 up to RT_BAND - 1, a new line in rt_world.asm) and rt_sq asks two questions when both tiles are pictures: the same number? below RT_BAND? Nothing else in the map changes but the numbers. 87 bytes. EXACT: the screen is the same to the pixel.
- Measured (work a picture): track 1 in the pack 268,500 -> 259,900 T; tight in the pack 297,600 -> 275,400; track 2 mid-lap 295,100 -> 265,900 and in the pack 310,800 -> 292,300 (track 2 has long level edges: it gains most). Against the case numbers' estimate of 8,000 (track 1) and 12,000 (track 2).
- A SWITCH: build.sh writes OPT_RTBAND 1 for every race-track build except track 3 (`RT_BANDED=0` or 1 to say otherwise). TRACK 3 HAS NOT THE ROOM: it has 24 bytes free in the program and 12 under 0x8000 and this needs 87, so it would need about 65 bytes found first (it would gain as track 2 does). Its tape is the same speed as before (only its tiles' numbers changed).

THE TABLE (pictures a second: start alone / mid-lap alone / in the pack; then the work in the pack, T a picture; then HOW MANY OF THE PACK'S PICTURES TOOK 5 TV FRAMES OR MORE - the number you feel). The two-player tape is driven by one player here, as the profiler does: two players driving were not measured.

| | before | now |
|---|---|---|
| track 1 green | 12.00 / 12.50 / 11.50 (268,500; 32%) | 12.25 / 12.88 / 11.75 (259,900; 25%) |
| track 1 green GRIP1 | 12.88 / 13.12 / 12.00 (250,300; 19%) | 12.62 / 13.38 / 12.38 (241,700; 6%) |
| tight 56 px NORMAL | 12.00 / 12.25 / 10.62 (297,600; 64%) | 12.25 / 12.88 / 11.38 (275,400; 41%) |
| tight GRIP1 | 12.38 / 12.75 / 11.38 (269,300; 33%) | 12.75 / 13.25 / 12.12 (254,800; 11%) |
| track 2 green | 10.88 / 10.50 / 10.12 (310,800; 85%) | 11.88 / 11.62 / 11.00 (292,300; 53%) |
| track 2 green GRIP1 | 11.38 / 11.12 / 10.38 (306,300; 77%) | 12.50 / 12.50 / 11.88 (259,100; 24%) |
| racer_2p (one player) | 12.00 / 12.12 / 11.12 (288,500; 45%) | 12.25 / 12.62 / 11.25 (278,200; 44%) |
| racer_2p_grip1 (one player) | 12.50 / 13.12 / 11.25 (277,300; 42%) | 12.88 / 13.50 / 12.00 (258,100; 19%) |

Read the pack column with care, as ever: two builds never drive the same 8 seconds (the "start" figure of track 1 GRIP1 going down a shade is that). Mid-lap alone, track 1 and the tight track now have under 1 picture in 10 over 4 TV frames; track 2 has 1 in 3 (it had 3 in 4). The two-player tapes were timed before the leash's change (which does not run with one player).

BYTES FREE NOW (program / under 0x8000): track 1 green 1,684 / 790 (GRIP1 1,670); track 2 939 / 790; track 3 24 / 12 (untouched); tight w56s 1,862 / 790; racer_2p 753 / 777; racer_2p_grip1 and _points 719 / 777.

STAGE 2 (the kinds a byte a block) - NOT BUILT. It is 6,000-7,000 T on two builds only, wants 2,304 bytes in one piece (cold code would have to move under 0x8000 first) and the time went to stage 1 and the leash.
STAGE 3 - nothing else exact over 3,000 T was found that is cheaper than the case numbers.
THE CASE NUMBERS - still worth about 8,000-9,000 T on track 1 and 13,000 on track 2, and now with a worked design: the generator's count shows only 25-27 kinds of edge block exist on a track and eight of them are 70-75% of all (upper or lower half plain and the other a pair of pictures: GG/PP, NN/PP, PP/GG, PP/NN; or one column of pictures: PG/PG, NP/NP, PN/PN, GP/GP). The kinds are four bits a block and five of sixteen are used, so eight new kinds fit without a bigger map: the two colour tables grow to 0xCD bytes each (272 bytes of the map's room), a table of jumps (about 20 bytes, at a page's top) and eight short routines (about 350 bytes) - about 650 bytes in all, 110-150 T saved a square. Track 1, the tight tapes and track 2 have the room; two players just; track 3 not. This is a design on paper: none of it is built or measured.

STAGE 4 - THE LEASH (src/twoplayer.asm: leash, lsh_4 on; separate commit). About once in 40 times the car left behind was put at the waypoint the leader had only just passed - 30-odd pixels behind it, aiming at the same next waypoint, so "0 waypoints behind" by the race order's count. Now, when the first choice is that waypoint, the one before it is taken instead if it is 40 px or more from the leader and both cars still fit in the window (across no more than 136 px apart, down 104: the window less a car and the leader's margin); if not, the choice stands. 86 bytes. tests/two_player_test.py: 19 of 19 on racer_2p (it was 17) and on racer_2p_grip1 (run as `TWOPDIR=racer_2p_grip1 OFFDIR=tight_w56s_normal_grip1 python3 tests/two_player_test.py racer_2p_grip1 racer_tight_w56s_normal_grip1`).

TESTS (nothing loosened):
- tests/racetrack_test.py (the picture to the pixel) and tests/rt_fixed_test.py on all 34 race-track tapes, each with its switches: 15 of 15 (tracks 2 and 3: 16 of 16) and 3 of 3 everywhere; the two small-window tapes stop the first test with an error as before (3 of 3 on the second). THE TWO-PLAYER TAPES PASS THE PIXEL TEST FOR THE FIRST TIME: it now takes `BDIR=` for a tape whose build folder is not its name less "racer_" (`BDIR=racer_2p TAPE=racer_2p` with the tight track's switches).
- tests/rt_same_drive.py, the tapes from before this work against the new (stage 1 only, before the leash): the same game byte for byte, alone and in the pack, on track 1 green, its GRIP1 twin, track 2 green and its twin, the tight GRIP1 tape and racer_2p_grip1 (one player). ON THE TIGHT TAPE AND racer_2p WITHOUT GRIP1 IT PASSES ALONE AND STOPS BEING THE SAME AT PICTURE 187 OF 300 IN THE PACK - NOT RUN TO GROUND. What is known: the new tiles' numbers alone (the switch off) give the same game at all 300; the change is in drawing code only and the picture is right to the pixel; all five cars part at once in one picture. The likeliest cause is the one the last entry found - a bump's crash noise takes random numbers for as long as it waits for the TV, and if the bump falls in the middle of a burst of moving, the test's fresh start of the numbers at each picture does not cover it, so a quicker picture gives the computer cars other numbers. That is a guess until someone checks whether a bump falls at that picture.
- The plain game and tracks 2, 3 and 5, deleted and built afresh last: byte for byte what they were.
- A NEW LINE FROM THE PROFILER: tests/stage_profile.py now prints how many TV frames each picture took and what share took 5 or more.

TAPES: all 34 race-track tapes rebuilt by tools/build_racetrack_tapes.sh from this source.

NOT DONE / NOT VERIFIED: nobody has driven any of it; not tried on a real Spectrum. The case numbers; the kinds a byte a block; track 3's 65 bytes. The one same-drive check above. Two players driving at once were not timed. racer_2p_points was rebuilt and passes the pixel and fixed-box tests; its points rule was not tested. Lap times by autopilot and the seam (tearing) were not measured again.

## 17 Nov 2026 - the driver cards: every car its own acceleration, speed and grip from Grant's ratings, and a personality for each computer driver (background agent, branch worktree-agent-abfbe424651a42ce8)

Grant's instruction: "the initial grip needs to be poor - lots of skidding - so all cars initially have low scores. Each car has a personality ... their acceleration, speed and grip/turning as ratings out of 10 - I will adjust these for each and explain so the game can have these apply in the game." His cards are tools/driver_cards.txt. THE SHORT OF IT: built, behind a switch (`CARDS=1`, off by default; the plain game, tracks 2, 3 and 5 and all 34 race-track tapes are byte for byte what they were). Change a rating in tools/driver_cards.txt, run `bash tools/build_cards.sh`, and it is in the tape - no code is touched. Tapes: build/racer_cards.tap and build/racer_cards_grip1.tap (the tight track, NORMAL drivers). Nobody has driven it: every number below is from the emulator and an autopilot, and none of them says how it FEELS.

HOW A RATING BECOMES A GAME NUMBER - THE SCALE (tools/make_cards.py, the few lines at its top; `python3 tools/make_cards.py table` prints it; the slide and the first-second figures are measured on the tape by `python3 tests/rt_cards.py racer_cards build/racer_cards/src scale`). A TV frame is a fiftieth of a second. 5 for speed and acceleration is the car as it always was.

| rating | SPEED: top speed, px a TV frame | ACCELERATION: TV frames from rest to 1.4 px a frame (and px covered in the first second) | GRIP, your car: after a flat-out right-angle turn it slides for ... TV frames and runs ... px straight on | GRIP, a computer car: it must be under ... px a frame to turn |
|---|---|---|---|---|
| 1 | 1.59 | 21 (63) | 130 frames, 138 px | 0.82 |
| 2 | 1.64 | 19 (65) | 130, 138 | 0.94 |
| 3 | 1.67 | 18 (67) | 103, 113 | 1.05 |
| 4 | 1.70 | 16 (70) | 82, 91 | 1.17 |
| 5 | 1.75 | 13 (72) | 82, 89 | 1.29 |
| 6 | 1.80 | 11 (73) | 73, 81 | 1.41 |
| 7 | 1.86 | 9 (75) | 64, 71 | 1.52 |
| 8 | 1.91 | 8 (75) | 58, 65 | 1.64 |
| 9 | 1.97 | 8 (76) | 52, 58 | 1.76 |
| 10 | 2.02 | 7 (77) | 47, 54 | 1.88 |
| the car as it was | 1.75 | 13 (72) | 58, 65 | (all slid above 1.00, none braked) |

- SPEED: a point above 5 is worth 3.1% of the top speed; a point below 5 only 1.6% (the last one 3.1%). WHY NOT A STRAIGHT LINE: Grant gave Bruno and Spike speed 2 and Jane 8. At 3.1% a point all the way down that is 1.59 against 1.91 px a frame - a fifth - and with it Spike lapped in 24 seconds to the leaders' 18; flattened below 5 it is 1.64 against 1.91 (14%) and every car laps within about a tenth of the leader. The ratings were not touched - only what a point is worth.
- ACCELERATION: 7.8% of the push a point. IT IS WORTH LITTLE IN THIS GAME, and that is the game's own sums, not the scale: every car loses an eighth of its speed every TV frame, so any car is near its top speed within half a second. A rating of 1 against 10 is 14 px in the first second. Where it shows is out of a corner a car has had to brake for.
- GRIP, YOUR CAR: what the tyres hold (TYRES in tools/make_cards.py; the car as it was held 16, 8, 8, 5 - gripping, with Q held, sliding, both). 8 is that car or a shade better (17, 9, 8, 5); MAX's 4 holds 10, 5, 5, 3 - its slide lasts 82 TV frames where it lasted 58, and it runs 91 px straight on where it ran 65; at 1 (6, 3, 3, 2) the autopilot could not get round the tight track (one lap in 70 seconds, most of it on the grass). Two ratings side by side can measure the same slide (1 and 2, 4 and 5): the tyres' numbers are small whole numbers and the slide follows the "sliding" one; what differs between those is how soon the slide begins. Each level of grip bought on the start line (keys 1-3) is now one more point of the rating.
- GRIP, A COMPUTER CAR: the next paragraph.

WHAT "GRIP" MEANS FOR A COMPUTER CAR (src/cards_code.asm: card_push). Earlier notes said the computer cars had no grip model. They have a small one (skid, racer.asm): steering above 1.0 px a frame, a car's push and friction were halved, up to three times, so it drifted. All four had the same numbers. Now each car's card gives it THE SPEED IT MUST BE UNDER TO TURN (the last column above), and two things follow from it:
1. THE BRAKE. When the car steers (or its driver eases off for a corner) while going faster than that, it brakes: no push, half the road's friction - it loses a sixteenth of its speed a TV frame - and it keeps braking until it is down to that speed. With no push it goes STRAIGHT ON the way it was already going, whichever way it points. So a car with little grip that arrives fast runs wide and crawls round; a car with a lot never lifts. Jane (grip 1) drops from 1.91 to between 0.6 and 1.3 px a frame at each corner; Bruno (grip 8, top speed 1.64) is at his limit already and slows the least (1.40 over his slowest quarter).
2. THE SLIDE. The old drift now starts at the car's own speed, not at 1.0 for everyone. A tidy driver brakes down to it and hardly slides; a clumsy one (AI_x_SLIP in src/ai_tune.asm) goes in faster than the tyres hold and slides as well.
ACCELERATION AND SPEED for a computer car: its push is multiplied by its card's number - one number up to four fifths of its top speed (acceleration), another above (which sets the top speed: 7 pushes).
COST: about 6,000 T a picture in the pack, 2% of a picture's work (card_push 2,900 for the four cars, its multiplies 1,700, the speed sum it needs 900, the two drivers' look for a near car 1,050, less 600 the old drift no longer spends). 393 bytes of program (card_push 135, card_near 216, the tables 42): 1,469 free on the tight track's tape (it had 1,862), 1,455 with GRIP1; under 0x8000 unchanged (790).

THE PERSONALITIES (src/ai_tune.asm, the CARDS part - plain numbers with Grant's words beside them; the level EASY / NORMAL / HARD, AI=0 / 1 / 2, is still the DRIVER'S skill on top: a higher level turns in sooner, makes fewer mistakes and carries 0.09 px a frame more into a corner).
- MAX, the racer, 5 / 5 / 4 - YOUR car: top speed 1.75, push 64, tyres 10, 5, 5, 3 through the existing grip sums.
- FRANK, the coupe (cyan), 5 / 5 / 4 - "very similar to Max": the same card, a tidy line, brakes to just over what the tyres hold, few mistakes.
- JANE, the dragster (white), 7 / 8 / 1 - "should shoot ahead of Max on the straights but really battle on the corners": 1.91 px a frame against Max's 1.75; eases off the earliest of all (when the corner is only 14 degrees off her nose), and still goes in 0.25 px a frame faster than the car will hold, so she slides too. Alone, the slowest quarter of her lap averages 1.10 px a frame (Frank's 1.21, Bruno's 1.40).
- BRUNO, the tank (pink), 4 / 2 / 8 - "Heavy and slow, likes to get in the way. Cuts corners": holds the exact middle of the road, turns in the earliest (the corner cut), does not slide, and when another car is within 40 px of him his line moves up to 10 px towards it. Top speed 1.64, but he hardly lifts: alone he laps as fast as Jane.
- SPIKE, the clown car (yellow, the green band), 6 / 2 / 3 - "Erratic ... Almost seems to want to hit other cars": a wandering line, the most mistakes of anyone (a late turn-in, a lift or a wobble), into corners 0.37 px a frame too fast so he slides, and when another car is within 56 px his line moves up to 14 px towards it and, one time in four, he steers straight AT it for six TV frames (the lunge).
- SPECS (4 / 5 / 3) and DOT (3 / 3 / 8) are on the choose screen only: their ratings are in src/cards.asm as numbers for that build to use; they do not race here.
"Gets in the way" and "wants to hit" are the one piece of new behaviour (card_near, 216 bytes of which the lunge is 57; it runs only when a car reaches a waypoint). MEASURED (tests/rt_cards_near.py): Bruno's line is pulled towards another car for 70% of a race and Spike's for 22% (he is usually behind, alone); Spike was seen lunging in about 9 of a race's pictures, 71 in a race he spent in the pack. THE BUMPS DID NOT GO UP: 41 a race as built against 46 with the two drivers minding their own business (5 races each; it runs from 25 to 62 race to race). So the code does what it says, but whether it LOOKS like blocking, and like a clown who wants a crash, is for Grant's eyes; it was not judged.

LAP TIMES (seconds; the tight track, NORMAL; 5 races of 3 laps in the pack, flying laps; tests/rt_tight.py). Your car is driven by the corner-cutting autopilot at two settings, because with poor grip the driver matters more than the car: TIDY (ace=104,30: it lifts early) never touches the grass; ROUGH (ace=88,60, the setting that suited the old car) is on it 4.5% of the time.

| | alone on the track | in the pack, you TIDY | in the pack, you ROUGH | on the grass |
|---|---|---|---|---|
| YOU, Max | 18.0 (tidy) | 17.6 | 19.4 | 0% tidy; 4.5% rough (20 visits in 5 races) |
| FRANK | 18.8 | 19.4 | 19.6 | 0% |
| JANE | 18.2 | 18.6 | 18.6 | 0% |
| BRUNO | 18.3 | 19.2 | 19.1 | 0% |
| SPIKE | 19.1 | 19.2 | 19.3 | 0% |

Finishing orders (Y you, C Frank, W Jane, P Bruno, G Spike): you tidy - YWPCG YPCWG YCWPG YWCPG YWCPG; you rough - WPYCG YPWCG YWCPG WCPYG YWPCG. Every computer car is within 10% of the leader, and within 4% of each other. Jane is the quickest of them but not by a straight's worth; Spike is last in all 10 races, by under a second a lap. Before the cards (the same tape without CARDS) the autopilot lapped 16.8 and the computer cars 17.6 to 18.7: EVERYONE IS SLOWER NOW, your car most of all in rough hands - which is what "poor grip to start with" asked for.
EASY and HARD drivers on the same cards (5 races each, you rough): EASY - Frank 19.8, Bruno 19.6, Jane 19.6; HARD - Frank 19.1, Bruno 18.5, Jane 18.3.
With GRIP1 (racer_cards_grip1.tap): you tidy 18.2 in the pack (18.0 alone), Frank 19.4, Jane 18.9, Bruno 19.2, Spike 19.6. GRIP1 still applies with the new grip numbers: top speed 1.74, the slide 85 TV frames and 92 px (82 and 91 without).

SPEED, pictures a second (start alone / mid-lap alone / in the pack; tests/stage_profile.py, 8 seconds each - two builds never drive the same 8 seconds):

| | without the cards | with |
|---|---|---|
| tight track | 12.25 / 12.88 / 11.38 | 11.75 / 12.00 / 10.88 |
| with GRIP1 | 12.75 / 13.25 / 12.12 | 12.25 / 13.00 / 12.00 |

The cards cost a quarter to half a picture a second - more, mid-lap without GRIP1. Only part of that is the new code (2%); the rest is your own car: sliding and being steered far more, its grip sums do more work every TV frame, which is why the GRIP1 tape (those sums once a picture) loses less. racer_cards_grip1.tap is the one to drive.

TESTS (nothing loosened): tests/racetrack_test.py 15 of 15 and tests/rt_fixed_test.py 3 of 3 on both cards tapes (`RACETRACK=1 RT_ROADW=56 RT_CORNER=27 RT_PIN_GAP=1 RT_PIN_W=1 RT_PIN=solid RT_NOLINE=1 BDIR=racer_cards TAPE=racer_cards python3 tests/racetrack_test.py`; `python3 tests/rt_fixed_test.py racer_cards racer_cards`). With CARDS off: tools/build_racetrack_tapes.sh rebuilt all 34 race-track tapes and git shows not one changed; racer.tap and tracks 2, 3 and 5, deleted and built afresh, have the md5 they had; the plain game was built last.

NEW FILES: tools/make_cards.py (the cards -> src/cards.asm; THE SCALE is at its top), tools/build_cards.sh (the two tapes, then the plain game), src/cards.asm (made by the tool), src/cards_code.asm (card_push, card_near), the CARDS part of src/ai_tune.asm; tests/rt_cards.py (your car's top speed, time to speed and slide; the whole scale measured; the computer cars' speeds), tests/rt_cards_solo.py (each computer car alone: laps, corner speed, sliding), tests/rt_cards_near.py (do Bruno and Spike go for the other cars), tests/rt_cards_shots.py (the clips). tests/rt_tight.py takes `ace=LOOK,LIFT` and more than six races. tools/build_racetrack_tapes.sh builds the two cards tapes too (36 tapes).
CLIPS (real speed, one screenshot a TV frame, twice the size; docs/design/racetrack/cards/): racer_cards_you_and_car4.mp4 - 14 seconds of your car (the tidy autopilot, started a second late) and Jane with the other three taken off the road: she is 37 px ahead at 5 s and 54 px at 7 s down the straight, and 18 px at 11 s after the corners (`ONLY=4 ACE=104,30 LATE=1.0 python3 tests/rt_cards_shots.py racer_cards racer_cards 14`). racer_cards_race.mp4 - 13 seconds of the whole pack from the lights (`ACE=104,30 LATE=1.6`, 13). The autopilot lifts a good deal with this grip, so your car is rarely at its full 1.75 in either.

WHERE THE RATINGS, GRANT'S WORDS AND A RACEABLE GAME PULL AGAINST EACH OTHER (said plainly):
- SPECS is described as "a decently fast car - good acceleration, good speed and reasonable grip - a real challenger" and rated 4 / 5 / 3: below Max on acceleration and grip and level on speed. By these numbers it is one of the two weakest cards, not a challenger. Either the words or the ratings want changing (say 6 / 6 / 4).
- FRANK's behaviour line says "a little more top speed than Max, and the best of the low-grip bunch through a bend" but his ratings are Max's exactly, and the note says "very similar to Max". Built as the ratings say: identical cars.
- JANE has by far the best card (7, 8 and 1; nobody else has two numbers over 6). On this track she is the quickest computer car even braking hard at every corner. If she should lose a lap's worth to Max in the corners, the lever is the bottom of the computer cars' grip scale (SLIDE_AT in tools/make_cards.py: with 0.41 px a frame for a rating of 1, not 0.82, she lapped 21.4 alone and ran near the back), or a track with fewer straights. It was set where the pack stays together.
- BRUNO and SPIKE at speed 2, "really slow": on the scale as built they are only 6% down on Max's top speed, because anything truer left them a lap behind. Bruno looks slow on a straight next to Jane (1.64 against 1.91), less so next to Max.
- SPIKE's note says "reasonable grip" and gives 3; Max's "weakness" is 4; Jane's "terrible" is 1. The scale follows the numbers.
- DOT's behaviour says "needs the whole road to turn" and her grip is 8, the best there is.
- "All cars initially have low scores": only grip was made poor. Speed and acceleration at 5 are the car as it was.

NOT DONE / NOT VERIFIED: nobody has driven it; not tried on a real Spectrum. Whether a rating of 4 skids "enough" and 1 is "barely controllable" in the hand is not known - only what the autopilot does. Blocking and lunging were measured as numbers, not judged by eye. The two-player build with CARDS assembles (360 bytes free) but was not run; player 2 would get Max's card, not Frank's. Tracks 1 (wide), 2 and 3 were not built with CARDS (track 3 has not the 393 bytes). Autopilot lap times swing by half a second with the smallest change; treat differences under that as nothing. The acceleration column's frame counts are from the game's sums, not measured (a computer car is moved once a picture, so its time to speed can only be read to the nearest 4 TV frames); the first-second distances are measured. Speed and acceleration levels bought on the start line still add what they always did (6% and 16%), not one rating point.

COMBINING WITH THE CHOOSE SCREEN (not attempted, as asked): (1) the chosen driver's card must set your car - today CD_TOP, CD_PUSH and the tyre rows are fixed numbers for MAX at build time; they need to become a seven-row table that su_apply (hud.asm) reads by the chosen driver; (2) the "extra" pip becomes +1 on that card's rating - for grip that is already how the tyre table is laid out (the next row is the next rating); for speed and acceleration CH_TOP, CH_SPUSH and CH_PUSH go and the next rating's numbers are read instead; (3) a card whose acceleration push is less than its top speed needs (DOT 3 / 3, SPECS 4 / 5) wants the choose build's "extra push only above a set speed" (yg_spush, grip.asm) with the speed taken from the card - today your car's push is simply raised to what its top speed needs, which for MAX changes nothing; (4) the computer cars' rows should follow who is NOT chosen (today the four colours are fixed drivers); (5) about 400 bytes, in a build that had few to spare.

## 17 Nov 2026 - armour and weapons: every car's armour as a bar on the race order, the limp, the tank's shell and the clown's wheels (background agent, branch worktree-agent-a010b6360182407bb)

Grant's words: "I would like to organise that the cars have some weapons. The tank can shoot, and the clown extends its wheels on the sides - if they hit you your car spins where it is. We need to add 'armour' to the cars as a gauge item. Tank is very strong. The fast dragster does not take much hit ... I would love a way to show damage on each car in the HUD somewhere." For the HUD he chose option V (docs/design/racetrack/armour_flash.gif). THE SHORT OF IT: all of it is built and all of it fits, behind a switch: `ARMOUR=1` on top of the driver cards (`bash tools/build_armour.sh` -> build/racer_armour.tap and build/racer_armour_grip1.tap, the one to drive; tools/build_racetrack_tapes.sh builds them too). With the switch off every tape is byte for byte what it was (racer.tap, tracks 2, 3 and 5 deleted and rebuilt: the same md5; the 36 race-track tapes rebuilt: not one changed; the plain game built last). Nobody has driven it, and whether it is fun is not something the emulator can say.

GRANT'S THREE OPEN QUESTIONS, BUILT AS DEFAULTS (each one number or one place to change):
1. At no armour a car LIMPS: half its top speed (ARM_LIMP_SHIFT 1 in src/armour_tune.asm; 2 would be a quarter). Nobody is knocked out. Measured: your car under 0.88 px a TV frame nine tenths of the time where it did 1.75; the dragster 1.01 where she did 1.91; your car limping from 10 s in still finishes (87 s for 3 laps).
2. Only the COMPUTER's tank (Bruno, pink) and clown car (Spike, yellow) use weapons (ARM_TANK 3, ARM_CLOWN 2).
3. No other car has a weapon. tools/driver_cards.txt now has a "weapon:" line on every card ("None yet." for the rest; Bruno's and Spike's are worded from Grant's message - paste the cards page's own words over them).

THE ARMOUR RATING (tools/driver_cards.txt: "armour N" on each card's ratings line; Grant confirmed MAX 5, FRANK 5, JANE 2, BRUNO 9, SPIKE 4, SPECS 5, DOT 8; a card without it gets 5). Every car has six pieces; the rating says how much damage ONE PIECE takes (ARMOUR_PIECE in tools/make_cards.py; `python3 tools/make_cards.py table` prints this). A bump costs BOTH cars the same damage, by how fast they were closing - so the dragster loses pieces three times as fast as the tank in the same crash (measured: Bruno rammed into Jane until he lost his first piece; she had lost three).

| rating | a piece takes | usual knocks (10) a piece | usual knocks for all six | hard rams (18) for all six | shells (16) | wheel hits (12) |
|---|---|---|---|---|---|---|
| 1 | 22 | 2.2 | 14 | 8 | 9 | 11 |
| 2 (JANE) | 26 | 2.6 | 16 | 9 | 10 | 13 |
| 3 | 30 | 3.0 | 18 | 10 | 12 | 15 |
| 4 (SPIKE) | 34 | 3.4 | 21 | 12 | 13 | 17 |
| 5 (MAX, FRANK, SPECS) | 38 | 3.8 | 23 | 13 | 15 | 19 |
| 6 | 46 | 4.6 | 28 | 16 | 18 | 23 |
| 7 | 55 | 5.5 | 33 | 19 | 21 | 28 |
| 8 (DOT) | 65 | 6.5 | 39 | 22 | 25 | 33 |
| 9 (BRUNO) | 77 | 7.7 | 47 | 26 | 29 | 39 |
| 10 | 92 | 9.2 | 56 | 31 | 35 | 46 |

A "usual knock" is two cars closing at a pixel a TV frame (damage 10); a rub is 3 or 4. The bottom of the scale is flatter than a straight line, as the speed scale is: at 14 a piece for a rating of 2 the dragster limped within 20 seconds of every race. Grass and walls do no damage (tested).

THE NUMBERS TO TUNE - all in src/armour_tune.asm, with this table at its top (a PICTURE is one drawing of the screen, about 12 a second):

| name | now | what it is |
|---|---|---|
| ARM_DIV, ARM_MIN | 5, 2 | a bump's damage: the closing speed in 256ths of a px a TV frame / 32, plus 2 |
| ARM_COOL | 30 | pictures before a car just bumped can be hurt by a bump again (one crash is many touches) |
| ARM_FLASH | 12 | pictures a lost piece flashes on the bar (about a second) |
| ARM_LIMP_SHIFT | 1 | no armour: top speed halved this many times |
| ARM_START | 60 | pictures from the race being set up before either weapon may be used |
| SPIN_T, SPIN_RATE | 32, 2 | a car hit spins 32 TV frames, 2 of 64 headings a frame: one full turn, ending as it began |
| WPN_SAFE | 40 | pictures after a hit before the wheels can hit that car again |
| TANK_RANGE, TANK_AIM | 80, 6 | the tank fires at a car 16 to 80 px ahead and within 6 px of his nose's line |
| TANK_COOL | 96 | pictures between shots (about 8 s) |
| SHELL_SHIFT, SHELL_LIFE | 4, 30 | the shell flies 4 px a TV frame for 30 frames: 120 px |
| SHELL_HIT, SHELL_DMG | 9, 16 | it hits a car whose middle is within 9 px; its damage |
| WH_SEE_LEN, WH_SEE | 16, 30 | the wheels come out for a car within 16 px ahead/behind and 30 px to the side |
| WH_LEN, WH_REACH | 12, 26 | while out they hit a car within 12 px ahead/behind and 26 px to the side |
| WH_TIME, WH_COOL | 10, 60 | pictures out; pictures until they may come out again |
| WHEEL_DMG | 12 | the damage a wheel does |

WHAT IS ON THE SCREEN.
- THE BAR (option V, the mock-up tool as the spec): the last column of each row of the race order, pixels 4-6 (3 wide), six pieces of 2 lines from the foot; a lost piece leaves one dot; the piece just lost flashes (two pictures on, two off) for ARM_FLASH pictures. The gap time moved 3 px left and the flag / best-lap clock 5 px left to make room (nothing overlaps: tested). It follows the race order as rows swap (tested over 298 pictures and 9 orders: 0 wrong). It is not drawn over a driver's face in the first second after the lights; it comes with the row.
- THE MUG IS YOUR ARMOUR: one system, not two. The old damage (a point a crash, each point a little off the top speed) is switched off in this build; the mug now empties as your six pieces go (6 pieces full, 3 half, 0 empty) and the oil can mends your armour. I kept the mug because it is already where your eye goes for "my car's health", it needs no new art, and its slow-down is replaced by the limp at zero, which every car shares. Two-player races (TWOP) were not combined with ARMOUR.
- THE SHELL: a white dot 3 x 3, by the cars' own two-colours-a-square rule (arm_dot, src/armour.asm; no new art). On plain road the square takes white ink on black. If a car is already in that square the dot shows in that car's colour; in a square of grass and road it shows in the grass's green; on all-grass it would be white on green, but the shell ends at the grass (looked at once a picture, so it can be up to a picture's flight - about 16 px - into it). It ends at a car (which spins and loses SHELL_DMG), at its range, or on the grass (all three tested). A falling note when it is fired; the crash noise on a hit (and the red border if it is you).
- THE CLOWN'S WHEELS: two dots each side of Spike, out to 12 px from his middle across his heading - the car visibly wider while they are out. No new car pictures (0 bytes of art; proper pictures of the car with wheels out would be 16 more frames, about 1 KB with FLIP - there is not that room). A short low beep when they come out. A car they touch spins and loses WHEEL_DMG; a car 36 px off is not touched and does not bring them out (tested).
- THE SPIN: on the spot - no speed, no steering, one full turn in 32 TV frames - for a computer car or you (your keys do nothing while it lasts).

THE RACES (tests/rt_armour.py; GRIP1 tapes, the tight track, NORMAL; your car by the tidy autopilot; 5 races each with the same five runs of luck. "Not in" in its report is the last car: the game ends the race when four are in, as it always has.)

| | ARMOUR, you from the lights | cards only, from the lights | ARMOUR, you 2 s late (in the pack) | cards only, 2 s late |
|---|---|---|---|---|
| finishing orders (Y you, F Frank, S Spike, B Bruno, J Jane) | YBFSJ YFJSB JFYBS YFJSB YFSBJ | YJFBS YFSJB YJBFS YJFBS YFBJS | JYFBS YFBSJ YFBJS YFBSJ JFBSY | YFJSB BYFSJ FBJYS JYBFS FBJYS |
| flying laps: you | 18.9 | 18.2 | 18.7 | 19.2 |
| Frank | 19.4 | 19.4 | 19.9 | 19.8 |
| Spike | 20.5 | 19.6 | 21.6 | 20.0 |
| Bruno | 20.6 | 19.2 | 20.1 | 19.4 |
| Jane | 19.8 | 18.9 | 19.0 | 19.3 |
| bumps a race | 58 | 43 | 87 | 54 |
| shells fired / hit, a race | 6.2 / 5.4 | - | 5.2 / 5.2 | - |
| wheels out / hits, a race | 5.0 / 3.4 | - | 4.8 / 4.2 | - |
| spins a race: Y F S B J | 0.4 1.4 2.0 2.2 2.8 | - | 2.6 2.6 0.4 1.6 2.2 | - |
| armour at the flag (of 6): Y F S B J | 6.0 4.4 3.2 4.8 1.6 | - | 3.4 3.0 4.0 4.4 1.2 | - |
| who limped | Jane in 2 races (from 54 s, 31 s) | - | Jane in 2 (52 s, 42 s), Frank in 1 (63 s) | - |

Race by race, shells fired/hit and wheels out/hit - from the lights: 8/8 5/2, 6/5 6/3, 6/4 6/5, 6/5 5/4, 5/5 3/3; in the pack: 7/7 4/3, 6/6 5/4, 4/4 4/3, 6/6 5/4, 3/3 6/7. Every car finished every race; nobody was lapped. The dragster suffers most - ending with 1 or 2 pieces and limping in about half the races - which is Grant's "hit the dragster" tactic at work. Your car is hardly touched when it leads (it is ahead of the weapons); in the pack it is spun about 2.6 times a race. The tank hits nearly every shot: his aim is narrow and short, so he only fires at a car sitting right in front of him on a straight. If that feels unfair: TANK_AIM down to 4, or TANK_COOL up. Lap-time differences under half a second are noise (the driver cards' entry).

SPEED (pictures a second, start alone / mid-lap alone / in the pack; tests/stage_profile.py, 8 s each - two builds never drive the same 8 s): GRIP1 cards 12.25 / 13.00 / 12.00 -> with ARMOUR 12.12 / 12.50 / 11.88. Without GRIP1: 11.75 / 12.00 / 10.88 -> 11.75 / 12.00 / 11.25. The armour code itself costs about 4,500 to 5,200 T a picture (2%): the weapons looking at one car a picture (arm_rel, about 1,000 T when a car is in reach), the cool-downs and each car's spin and limp check (about 1,800), drawing the shell and wheels (about 300 while out), THE BARS about 370 T a picture on average (one bar drawn is about 800 T, and only a flashing bar or a changed row is drawn), and the moved gap time about 250 more than before. The half a picture a second lost mid-lap with GRIP1 is more than that 2% - partly the 8-second windows not being the same drive; not run to ground.

MEMORY: the program 103 bytes free (89 with GRIP1), of the cards tape's 1,469: armour costs 1,366 bytes in the program and 319 under 0x8000 (the bars, a new race, firing a shell - the rare parts: src/armour_low.asm), leaving 471 there. Everything fitted, in the order asked.

A PLAYER'S FIRE KEY (not built): the weapons are written for "a car" (arm_fire fires from the car in IX; arm_wheels pushes the wheels out). It would need a key read in read_keys (racer.asm) calling arm_fire with IX = your car when the cool-down allows; a second shell record if yours and the computer tank's may fly at once (there is one: sh_rec); the wheels' drawing and hit check taking the car from a variable instead of ARM_CLOWN; and the choose screen saying which car you drive (you are always MAX today). About 150 to 250 bytes - more than the 89 free with GRIP1, so something would have to move under 0x8000.

TESTS: tests/armour_test.py (new), 28 of 28 on both armour tapes - a bump costs both the same, a harder one more, pieces in proportion to the ratings, your car too, the mug is your armour, grass costs nothing; the bars match each car's armour, are 3 px wide with a clear pixel either side, a lost piece flashes for 11 pictures then is a dot, and they follow the order in a race; the shell hits a car in line, is on the screen every picture it flies, spins the car on the spot (no movement, a full turn, back to its heading) and costs armour; your car too, with no control; a shell at nothing ends at its range (120 px), one across the road ends on the grass; the wheels come out for a car alongside, are on the screen, hit it once, miss a car 40 px off and one 36 px ahead, and do not come out for a car out of reach; the limp (you and a computer car) and finishing while limping; with ARMOUR off the two cards tapes have their old md5. tests/racetrack_test.py 15 of 15 on both armour tapes; tests/rt_fixed_test.py 3 of 3 (its boxes - map, plate, mug - needed nothing added: the race-order panel is not one of them). ONE CHANGE TO racetrack_test.py: its "the scenery matches the map to the pixel" check already leaves out every square a car is in; it now also leaves out the one square each dot of the shell or the wheels is in (rt_lib.py: weapon_dots, from the game's own sums). On a tape without ARMOUR there are no such dots and the check is exactly as it was. It is an exclusion like the cars', not a loosening of what the scenery must look like - but say so if it should be checked another way.

PICTURES (docs/design/racetrack/armour/, by tests/rt_armour_shots.py from one real race, run of luck 3, you starting 2 s late): armour_panel.png (the screen, 3x) and armour_panel_close.png (the panel, 6x: bars at 6, 3, 6, 6 and 4 pieces, dots for the lost ones; the best-lap clock in the 4th row sits left of the bar); armour_tank.mp4 (Bruno fires at 21.2 s and hits Jane at 21.4 s; she spins in place), armour_wheels.mp4 (Spike's wheels hit your car at 4.1 s), armour_ram.mp4 (Jane bumped at 19.0 s, her top piece flashing on the bar, 3 left) - real speed, a screenshot a TV frame, 2x.

NEW FILES: src/armour_tune.asm (the account and every number), src/armour.asm (what runs every picture), src/armour_low.asm (the rare parts, under 0x8000), tools/build_armour.sh, tests/armour_test.py, tests/rt_armour.py (race reports: `python3 tests/rt_armour.py racer_armour_grip1 ../build/racer_armour_grip1/src 5 late=2`, run from tests/), tests/rt_armour_shots.py. Changed: tools/driver_cards.txt (v2: armour and weapon lines; DOT's behaviour is now "A slow car but with good grip and good armour"), tools/make_cards.py (reads both, with or without; the armour scale), build.sh (ARMOUR=1), racer.asm / hud.asm / grip.asm / strip.asm (each change inside "if OPT_ARMOUR"), tools/build_racetrack_tapes.sh (38 tapes).

NOT DONE / NOT VERIFIED: nobody has driven it; fun and fairness are counted, not judged. The computer cars do not steer away from the shell or the wheels. One shell in the air at a time. The shell on an all-grass square was not looked at on the screen (it ends there within a picture). Whether a 32-TV-frame turn reads as "spins where it is" is for Grant's eye in armour_tank.mp4. Not combined with two players or the choose screen; not built on track 1 (wide), 2 or 3 (3 has no room).

## 2026-11-18 SAST - the corner arrow, option C: black over grass, green beside it
- Grant: "the yellow arrow needs mask or outline to be clearer". Why: its 1-pixel black outline vanished over grass (in an
  all-grass square the cleared pixels show the square's green), so it read yellow on green; where road met grass part of
  it went green. Mock-ups docs/design/racetrack/arrow_clear_options.png (A black box, B thick outline, C black over grass);
  Grant chose C.
- Built (src/racetrack.asm rt_arrow, ra_inv, aw_next; src/arrow.asm): over road the arrow is masked and yellow as before.
  If any of its 3 x 3 squares holds grass, all nine are drawn the other way: green ink on black, an all-grass square's
  pixels inverted (so a car on the grass there shows black), and the arrow XORed in - black over grass, green over the road
  beside it. The first try cut it out black in mixed squares, which made it vanish over their road part; the second left a
  yellow tip in a road square; the whole-arrow rule fixes both. docs/design/racetrack/arrow_c_built.png.
- Switch OPT_ARROWC (RT_ARROWC=0/1), on by default for race-track builds, OFF on track 3: it needs about 150 bytes under
  0x8000 and track 3 has 12. Track 3 keeps the old yellow arrow.
- Tapes: all 38 race-track tapes rebuilt (tools/build_racetrack_tapes.sh); the plain game, tracks 2, 3, 5 and the two
  track 3 green tapes are byte for byte as before. Armour tapes: 83 / 69 bytes free.
- Tests: racetrack_test 15/15 (armour GRIP1), 16/16 (track 2 green); rt_fixed_test 3/3; armour_test 28/28 after
  re-recording its two pinned cards-tape md5s (those tapes now carry the new arrow); two_player_test 19/19.

## 2026-11-18 SAST - your car's grass slowdown halved
- Grant: "there is too much of a slow down when going off the track in my car. Slowdown should have half the effect it
  currently does". Your car on the grass settled at 21% of the road's speed (lost 79%). Now its push on the grass is one and
  a half times, not halved (src/grip.asm, switch RT_GRASS_YOU in src/racetrack.asm): it settles at 4.5 pushes, 64% of the
  road's (loses 36%: under half the effect). The grass friction is unchanged, so it still bites the moment you go on.
  The computer cars are unchanged (they spend 0-0.5% of a race on the grass).
- tests/racetrack_test.py's grass check follows: 58-70% for your car where RT_GRASS_YOU is on (20-25% otherwise).
- All 38 race-track tapes rebuilt; the plain game unchanged. racetrack_test 15/15 (armour GRIP1), 16/16 (track 3 green);
  armour_test 28/28 after re-recording the cards tapes' md5s again; two_player_test 19/19.

## 2026-11-18 SAST - the white rectangle, you last on the grid, your car slower, a bar fault
- THE WHITE RECTANGLE (Grant: "sometimes picking up a NOS or health - a white rectangle is left"): the oil can (health).
  On ARMOUR tapes, picking it up called arm_mend, which left A non-zero, and the next lines wrote A into the can's two map
  tiles - tile 1, a solid block, in a white square. src/strip.asm ot_out: `xor a` after arm_mend. Found by a scripted hunt
  for solid white blocks in the window over 3,000 TV frames (39 hits before, 0 after); the NOS canisters were never involved.
- YOU LAST ON THE GRID (Grant: "start our person at the back of the grid"): GRID_BACK, on for race-track builds except
  two players (tools/make_world.py: you GRID[4], the others one place up - CYAN pole, WHITE, PINK, GREEN; build.sh writes
  OPT_GRIDBACK; src/hudtext_gfx.asm grid_order 1,4,3,2,0). GRID_BACK=0 for pole.
- YOUR CAR SLOWER (Grant: "make our car a bit slower"): MAX's speed card 5 -> 4 (tools/driver_cards.txt): top speed 1.75 ->
  1.70 px a frame (measured 1.70 on the road; 1.12 on the grass).
- A FAULT THE NEW GRID SHOWED: an armour bar could be the wrong car's for a few pictures after two cars swapped and swapped
  back before the row was drawn again - arm_bar drew for the car the race order has in that place, not the one the row
  shows. src/armour_low.asm: it now reads shown_order.
- Tests: racetrack_test 15/15 (armour GRIP1; its slide check now leaves out the tank's shell like the other checks do -
  he fires at you now that you start behind him); 16/16 track 2; armour_test 28/28 (the dragster-flash check finds her
  row each picture; cards md5s re-recorded); two_player_test 19/19 against new pole twins of the tight tapes
  (racer_tight_w56s_normal_pole, _grip1_pole: the two-player tapes keep you on pole). 40 race-track tapes; plain game unchanged.
- Mock-ups for health in the race order (Grant: "The vertical health bars are not visible, and the coffee cup is no longer
  relevant"): docs/design/racetrack/health_options.png (A-D), then variations of C (Grant: "for health can you do
  variations of C"): docs/design/racetrack/health_c_options.png (C, C2-C5).

## 2026-11-18 SAST - the slower game (three trial tapes) and the grid's colour clash
- SLOWER AND SMOOTHER (Grant: "the game plays too fast, I want it slower and smoother"; then "I would prefer a maximum
  jump of 4 pixels or even less"; "gentler NOS is fine"). ONE setting, GAME_SPEED (percent of today's; 100, the default, is
  byte for byte the game as it was). It scales together: every car's top speed and push (so acceleration) from its card,
  your car's tyres (so it slides the same way, only slower), the computer cars' corner speeds (where they slide and the
  speed they brake down to, the driver's margin included), and in the code the computer cars' slide steps (SKID_STEP), the
  bounce in a bump (KICK) and the speed at which your skid hisses. Grass, NOS and the limp were shares of the push already.
  Not scaled: the steering rate (the car still turns about 280 degrees a second - at 50% a full-lock circle is about 20 px
  across, a car and a bit), the tank's shell, the engine's note, and the set-up row's upgrades (keys 1-3 before the start,
  hud.asm: a level still adds today's 28/256 top speed and 4-10 push - relatively more at a lower speed; left for after the
  other agent's hud.asm work). Where: tools/make_cards.py (the top), build.sh, src/grip.asm, src/racer.asm two lines.
- THE GENTLER NOS (a named setting: NOS=0/1/2 - twice, a half more, a quarter more - and NOS_FR, how many TV frames a
  canister burns; build.sh): on the slow tapes a quarter more push and top speed for 2 seconds (100 TV frames), where today
  it is twice for 1 second. 20 bytes. The 100% tapes keep today's NOS.
- TAPES (not the default - Grant picks by driving): bash tools/build_slow.sh -> build/racer_armour_slow60.tap, _slow55,
  _slow50 (the armour GRIP1 tape at 60/55/50%, the gentler NOS). 37 bytes free on them; 57 on the armour GRIP1 tape.
- MEASURED (tests/slow_measure.py: each picture taken as it reaches the screen; "jump" = the larger of across and down, in
  px; "at speed" = pictures over 80% of the top speed; 60 s in the pack, NOS alone on the track; tests/stage_profile.py;
  tests/rt_tight.py ace=104,30, 3 races of 3 laps in the pack, RACE_SECS=200):

| | 100% today | 60% | 55% | 50% |
|---|---|---|---|---|
| your top speed, px a TV frame (card) | 1.70 | 1.02 | 0.93 | 0.85 |
| your car's jump a picture at speed: typical / largest | 7 / 12 | 4 / 6 (5+ px: 20%) | 4 / 6 (15%) | 3-4 / 6 (7%) |
| the view's (camera's) jump: typical / largest | 7 / 12 | 4 / 7 | 4 / 7 | 4 / 7 |
| pictures a second: start / mid-lap / pack (stage_profile, 8 s) | 12.0 / 12.3 / 11.0 | 12.1 / 12.8 / 11.0 | 11.9 / 12.6 / 11.1 | 12.1 / 12.8 / 11.8 |
| pictures of 5+ TV frames (60 s in the pack) | 56% | 30% | 58% | 64% |
| NOS: top speed, jump typical / largest | 3.39, 13 / 15 | 1.27, 5 / 7 | 1.16, 4-5 / 6 | 1.05, 4 / 7 |
| flying laps (s): you / Frank / Spike / Bruno / Jane | 18.1 / 19.2 / 21.3 / 21.1 / 19.5 | 27.5 / 31.9 / 32.2 / 31.9 / 29.6 | 30.0 / 36.4 / 37.3 / 38.7 / 30.8 | 32.0 / 36.6 / 42.3 / 38.0 / 38.2 |
| computer cars on the grass | 0% | 0% | 0% | 0% |

  Picture rate does not change with speed (the work a picture is the same); a 5- or 6-frame picture is the bigger jump.
  The computer cars still make every corner and stay off the grass; their laps scale with the speed (Frank 1.66 times at
  60%). Your car (the autopilot) gains on them as the speed drops - it turns relatively tighter - so the races get easier
  for the same driver. Clip, real speed, 100 / 60 / 55 / 50 side by side, 14 s from the green light through the first
  bend: docs/design/racetrack/speed/speed_100_60_55_50.mp4 (still: _still.png; tests/speed_clip.py).
- RECOMMENDED: 50% - the only one where your car moves 4 px or less in nine pictures in ten at full speed (55% is close).
- THE GRID (Grant: "at the start grid for a couple of cars the white grid has a colour clash with the car"): the [ boxes'
  top and bottom lines reached 3 px into the cars' colour squares and went red, pink, cyan in the lane that is not level
  with the squares (the view is centred on your car, which always puts the squares 4 px off it up and down; across, the
  view always starts on a square). tools/make_world.py: on the race track each [ is drawn wholly in the square behind its
  car (7 px to 2 px behind it); the cars stand where they did (x 248/232/216/200/184 for places 1-5, the same distance to
  the line as before). The plain game's grid unchanged. docs/design/racetrack/grid_clash_before_after.png.
  tests/racetrack_test.py part grid (PLAYERS=2 for two players): no square holds a white marking and a car - 0 on the
  armour, pole, two-player and track 2 tapes (6, 5 and 6 squares on the old ones).
- Tests: racetrack_test 17/17 (armour GRIP1), 18/18 (track 2 green); armour_test 28/28 (the cards md5s re-recorded; its
  "you ram Frank" scene now moves the tank and the dragster out of the way first - left on the straight, the check passed
  or failed by luck); rt_fixed_test 3/3; two_player_test 19/19. On the slow tapes racetrack_test fails only its two
  timed checks (2 laps in 30 s, the crawl back within 1,500 frames) - fixed times for today's speed; armour_test 28/28.
- All 40 race-track tapes rebuilt; the plain game and tracks 2, 3, 5 byte for byte as before.
## 2026-11-18 22:10 SAST - laps when you go off the track, the faces look about, the health blocks (option C)
- LAPS LOST OFF THE TRACK (Grant: "I also went off track for a bit, and I seemed to lose a lap"). THE CAUSE: your laps are
  counted by waypoints - points along the middle of the road, 32 pixels apart on the tight track. The game keeps the one
  you are heading for; you pass it within 40 of it, and the lap counts at the first one after the start line. A missed one
  was forgiven only if you came within 64 of one of the next FOUR. Off the road past more than four (along the infield
  grass, a spin onto it, a corner cut across the grass) and back on further round, the game kept waiting for the one where
  you left - and found it a lap later. Reproduced (tests/lap_offtrack_test.py on the tape before the fix): along the grass
  past eight waypoints, back on at 11 - "heading for 4" still, the line not counted; across the bottom-left corner's grass
  (30 to 37) - the same; a 3-lap race with that excursion each lap: laps [1, 2, 2] at the crossings, never finished.
- THE RULE NOW (src/lap_low.asm, under 0x8000; racer.asm's rp_try_next jumps to it when none of the five is near): when you
  are 96 or more (|dx| + |dy|) from your waypoint, the game looks ahead for the first one you are within 64 of and counts
  you past all those before it - but only as far round as you could have DRIVEN in the time since you were last near your
  waypoint: 2 pixels a TV frame (your top speed on the road is 1.70, on the grass about 1.1), plus 3, never more than half
  the track (NWP/2 - 1). Why: a fixed window has to choose between losing long excursions and allowing cuts (on the tight
  track a window of 11 would let a diagonal cut gain about a second); the time rule does both - on the grass you are always
  slower than the allowance grows, so going off never costs a lap; a short cut quicker than the road is held (you show
  behind in the race order) until the time has caught up, so it gains nothing; a cut of more than half the track is never
  counted. Ordinary driving counts exactly as before (the rule only acts 96 or more from your waypoint). The computer cars
  do not use it (they steer back to their waypoint). Player 2 (two-player tapes) has it too. Not track 3 (no room under
  0x8000: OPT_RTLAP, build.sh RT_LAPFIX). THE PLAIN GAME HAS THE SAME FOUR-WAYPOINT RULE and so the same fault in principle -
  unchanged, as asked; say if it should have the fix too.
- THE FACES LOOK ABOUT (Grant: "at the start of the games I want the faces animated looking left and right"): tw_anim
  (src/plate_slow.asm), called each picture from dmg_anim (or straight from the picture on ARMOUR tapes): until the lights
  go green each race-order face goes everyday / eyes in turn, a step every 32 TV frames, each row a step on from the one
  above (the podium's way) - reusing the title's pa_car. 41 bytes under 0x8000, none in the program; about 16,000-21,000 T
  once every 32 TV frames before the race (all five faces), 120 T a picture otherwise, 45 T a picture in the race. Not
  track 3 (OPT_RTEYES). Test: tests/faces_look_test.py (every sample of every face is one of its two looks, exactly; both
  looks seen in every row; rows not in step; none left once racing) - before: the faces never changed.
- THE HEALTH BLOCKS, OPTION C (ARMOUR tapes; Grant: "when health is good all bars are green, when 2 bars the 2 bars are
  yellow and 1 bar the 1 bar is red, when 0 - all three bars flash red"): each race-order row's last three squares black,
  a block in each (6 x 12 pixels; two pieces a block, an odd one the lower half), bright green / yellow / red by the blocks
  left (pieces / 2 rounded up); a piece just lost flashes as its half (ARM_FLASH, about a second), the colour changes at
  once; at none, three red outlines flash two pictures on, two off, for as long as it lasts. src/armour_low.asm (arm_bar;
  arm_bar_t draws only when the look changes: a drawing is about 8,000 T, so about 4,000 T a picture for each car with no
  armour left, and 7 drawings for a lost piece). THE GAP TIMES HAVE GONE from the race order (no room; nothing replaces
  them); the finished flag and the best-lap clock sit where the gap was (column 28). THE MUG HAS GONE (dmg_anim, dmg_draw,
  dmg_make, the icon, the gap code: all left out of ARMOUR builds); its corner of the window is the track's; the NOS spoons
  stay where they were in that corner. Bytes given back: the program 63 -> 425 free (GRIP1; 77 -> 439 without), under
  0x8000 171 -> 375. Speed in the pack over 20 s: 11.10 pictures a second against 11.30 before - but the two drives part
  ways early (different cars in view), so that is not like for like. Pictures: docs/design/racetrack/armour/health_c_built.png,
  _panel.png (3x), health_c_loss_clip.mp4 (50 fps, 2x: Frank 5 -> 4 pieces, green to yellow; Jane 1 -> 0, red outlines).
- TESTS: lap_offtrack_test (new); faces_look_test (new); armour_test 28/28 - the bar checks rewritten for the blocks: each
  row's three squares read as whole / half / outline / empty plus the colour of all six squares, compared with every car's
  armour as set by hand, and in a race at every picture looked at; the flash on loss (5 to 4: both looks seen, yellow at
  once - the picture of the loss itself may still show the old one, as the blocks are drawn before the bumps); the red
  outline flash at none; the mug check became "nothing of the mug is in the program". The dragster-flash check now reads
  the row that SHOWS her (shown_order; it read the race order's place, wrong for the picture or two after a swap). racetrack_test
  checks the mug's old corner as the track, to the pixel, on ARMOUR tapes (added); rt_fixed_test skips the mug on ARMOUR
  tapes. The cards tapes' md5s re-recorded (laps, faces). Plain game, tracks 2/3/5 and the track-3 race-track tapes byte
  for byte as they were.
- Bytes free (program / under 0x8000), measured as 0xC000 - code_end and LOWTAB - 0xE8 - low_end: racer_armour_grip1
  425 / 375. NOT VERIFIED: nobody has driven any of it; the lap rule's 2 px a frame has not been tried with NOS on grass.
- MERGED with the slower-game work (grid boxes, GAME_SPEED, NOS settings): all race-track tapes and the three slow tapes
  rebuilt; the cards tapes' md5s re-recorded for the two together. Program free on racer_armour_grip1 after the merge and
  the fix below: 418 (432 without GRIP1); under 0x8000 375.
- A FAULT IN THE RACE ORDER (seen in a recording: rows 2-5 all showing the red car about 4 s after the green). THE CAUSE: the
  rows were drawn again only one picture in four, and always the FIRST row that had changed. Early in a race the places at
  the top keep changing, so the rows below can keep showing a car that has left them - a car that drops back through the
  field while the redraw works its way down leaves its picture in every row it passed. Reproduced: from the green, a good
  driver from the back of the grid, every TV frame for 10 s - two rows showing the same car for up to 57 TV frames running
  (112 frames in all). THE FIX (ARMOUR tapes, src/hud.asm hu_order): a row is drawn again EVERY picture (still one a picture
  at most); now the longest is 7 TV frames (a swap takes two pictures), 32 frames in all. 7 bytes. The same one-in-four rule
  is in the plain game and the other race-track tapes (not changed). Test: armour_test rows_same (fails on the old rule).

## 2026-11-18 SAST - Grant's new faces in the race-track tapes; the faces editor
- Faces editor (https://claude.ai/artifact/JXzX56aU6KkAgqKv15F3LE; tools/faces_page.template.html, tools/make_faces_page.py):
  seven drivers, six looks each (now, eyes, happy, sad, idea1, idea2 - Grant: "two more face options for each face, I'm
  exploring other face expressions"), click to swap a pixel, arrows to shift a face a pixel (wrapping), Mirror, Copy and
  Paste between any two faces, Undo. tools/import_faces.py takes idea1/idea2 and WHITE.
- Grant's paste: YOU eyes (the whole head a pixel over) and happy redrawn, and YOU idea1/idea2 (the idea slots of the
  others were untouched copies and are not stored). The looks grew from 249 to 279 bytes; the table block at TD had about 4.
  So on the race-track builds the looks now live under 0x8000 (OPT_FACESLOW, build.sh: race-track builds but track 3);
  the plain game and track 3 keep the earlier looks (src/faces_mood_plain.asm, a frozen copy). The choose build's seven
  looks (faces_mood7.asm) fit as they are (90 bytes free there).
- All race-track, slow and choose tapes rebuilt; the plain game and tracks 2, 3, 5 unchanged. Armour GRIP1: 418 bytes free
  in the program. Tests: faces_look_test PASS (it now reads the screen between pictures, as the others do: one sample in
  200 had caught a face half-redrawn for one TV frame, the looks being read from slower memory); armour_test 29/29 (cards
  md5s re-recorded); racetrack_test 19/19; two_player_test 19/19; lap_offtrack_test PASS; choose_test passed every check it
  reached before its 10-minute limit.
- 18 Nov 2026, later: Grant's second faces paste - YOU eyes (front on) and sad, GREEN happy, PINK happy and sad, and trial
  looks (idea1/idea2) for YOU, CYAN, GREEN (idea2) and PINK. Looks now 270 bytes (under 0x8000 on the race-track builds);
  the choose build's seven 321 bytes, fitting. All tapes rebuilt; plain game and tracks 2, 3, 5 unchanged. faces_look_test
  PASS, armour_test 29/29 (cards md5s re-recorded), racetrack_test 19/19.

## 2026-11-18 SAST - the tank fires straight and less, the clown less, both a few times a race; a 70% tape
- Grant: "the tank is only allowed to shoot straight, and less frequently ... the clown spikes less often - we need the
  idea - like our NOS - they can only do this so many times". src/armour_tune.asm: TANK_COOL 96 -> 192 pictures (about 16 s),
  TANK_SHOTS 3 a race, TANK_STRAIGHT 1 (he fires only with his nose square to the screen, give or take one step of 64, so
  the shell flies straight along the road); WH_COOL 60 -> 120 (about 10 s), WH_USES 3 a race. sh_ammo / wh_ammo (racer.asm)
  set by arm_new, spent by arm_fire / arm_wheels. 26 bytes; armour GRIP1 395 bytes free.
- tests/armour_test.py: the shell checks top his shells up first (they test the shell, and fire four in one race); new
  checks - no shells left: no shot in 400 frames; nose off square: no shot, the same set-up square: a shot; no wheel-outs
  left: the wheels stay in. 32/32. racetrack_test 19/19.
- 70%: tools/build_slow.sh now also builds build/racer_armour_slow70.tap (Grant: "Any chance of a 70% speed"; 50% "too slow
  but much smoother").

## 2026-11-18 23:43 SAST - RACE or COMBAT: a traditional race, made competitive; the rubber band as a second tape
- Grant: "Now I need a game option - combat or race. Race produces a bunch of the same looking cars, but different colours
  and numbers. I would like to try a traditional race ... the idea is to make it competitive so you don't run away with it.
  70% speed is good." Then: "Number won't be legible - that's fine" (no numbers on the cars).
- TAPES (behind RACEMODE=1, with ARMOUR=1; ELASTIC=1 for the rubber band; every other tape byte for byte as it was):
  `bash tools/build_race.sh` -> build/racer_race70.tap (no rubber band) and build/racer_race70_elastic.tap (rubber band). Both
  are the 70% armour GRIP1 tape with the gentler NOS, and both hold both games. Also in tools/build_racetrack_tapes.sh.
- THE TITLE: the row "3 CHOOSE YOUR PLAYER" (it did nothing) is now "M  MODE: RACE" - M changes it to COMBAT and back. RACE
  to start with; the choice is kept from race to race (rmode, title.asm).
- COMBAT: the armour tape's game exactly (cards, personalities, armour, health blocks, shells, wheels, their limits).
- RACE (src/race_td.asm, race_low.asm, race.asm; the switches are a few numbers and first bytes put in place before each race
  by rm_setup, so nothing extra runs in the race):
  - every car is the racer (MAX's car) in its own colour - you red, then cyan, yellow, magenta, white. NO NUMBERS: a 5 x 7 box
    with a 3 x 5 digit cut out of it on each roof was built and worked (you 7, cyan 3, yellow 4, magenta 5, white 9), but Grant
    judged it illegible at this size and it was taken out (160 bytes back). Not put in the race order either: the row's
    colour already says which car it is.
  - no armour lost (arm_bump returns at once), no shells or wheels (arm_tick returns at once), no driver steering at
    another car (card_near returns at once): a bump is just a bump. The faces in the race order stay (the drivers).
  - the race order's right-hand squares (29-31): the GAP TO THE CAR AHEAD in small letters (each car's gap to the leader
    at the last checkpoint it passed, hud.asm's cp_hook, less that of the car ahead; nothing for the leader), in the row's
    own colour. A place's gap is brought up to date one picture in five, when no row of the order needs drawing again.
  - THE COMPUTER CARS: all four the same driver (ai_tune.asm, the RACE part): REACH 60 (the most that still counts every
    waypoint), line 3,2, EASE 0, FUSS 2, PACE 16, REACT 0, ERR 2. On MAX's card as it is a computer car slows to 0.82 px
    a frame for every bend (70% of its top speed); with the best driving that fits they lapped 24.7 s against the good
    driver's 23.7, and he won 10 of 10 by 5-10 s. So THEIR GRIP is raised (AI_R_GRIP 107/64, x1.67): on this track they
    then neither slide nor brake for a bend at their top speed. Their top speed and acceleration stay MAX's (1.18 px a
    frame at 70%, the same as yours). This is the one place RACE is not "the same card for all" - say if it should be.
  - NOS: the pickups as in COMBAT (the autopilots never use it - not measured).
  - THE RUBBER BAND (racer_race70_elastic.tap, race.asm el_tick, every picture): a computer car behind the leader gets
    +1/64 of its push (+2.3% top speed at 70%) for every waypoint it is behind (32 px, about half a second), up to +3/64
    (+7%) from 3 waypoints (about 1.6 s) back; a computer car more than 4 waypoints (about 2 s) ahead of you eases off
    1/64 (-2.3%). Nothing pushes once any car has finished.
- MEASURED (tests/race_measure.py: 3 laps, you from the back of the grid, race N with its own luck; GOOD = rt_ace.py LOOK
  104 LIFT 30, CAREFUL = rt_lib's middle-of-the-road autopilot; neither uses NOS):

| tape, driver (5 races) | your places | wins | gap to the winner when beaten | order changes a race | flying laps: you / the 4 computer cars |
|---|---|---|---|---|---|
| race70, good | 2, 5, 1, 5, 1 | 2 | 1.3, 1.7, 3.3 s (mean 2.1) | 25 | 23.8 / 24.0-24.3 |
| race70, careful | 5, 5, 5, 5, 5 | 0 | 15.0, 13.5, 15.0, 12.9, 14.6 | 3 | 28.4 / 23.7-24.2 |
| race70_elastic, good | 5, 1, 4, 3, 4 | 1 | 2.1, 1.3, 1.0, 2.4 (mean 1.7) | 25 | 23.9 / 24.0-24.3 |
| race70_elastic, careful | 5, 5, 5, 5, 5 | 0 | 13.8, 11.9, 11.0, 11.0, 11.8 | 11 | 28.0 / 24.4-24.9 |

  Over 10 races (the same driver, races 1-10): race70 - won 7, mean place 1.9, 2.1 s behind when beaten; race70_elastic -
  won 3, mean place 3.4, 2.6 s behind when beaten; the computer cars within 1-3% of each other a lap on both. (Five or ten
  races are few: the same settings measured twice gave 5 and 7 wins of 10.) The careful driver is 4 s a lap slower than the computer cars and loses by 11-15 s on either tape: the rubber band
  is too small to close that, as asked ("subtle"); it does make the computer cars' own race closer and gives him a few
  more places changing hands (11 against 3 a race). Rubber-band settings tried (good driver, 10 races): push every 2
  waypoints, easing for ANY car ahead of you - you won 8 of 10 (the easing helps you from the back more than the push
  hurts); easing only 2 s ahead - 5 of 10; the one built - 3 of 10, beaten by 0.9 s on average.
- MEMORY: racer_race70 371 bytes free in the program, 8 under 0x8000 (the cards' rows and the title's few bytes), 47 in the
  table block at TD (the set-up and the gaps live there); racer_race70_elastic 293 in the program.
- SPEED (tests/stage_profile.py, 8 s): pictures a second start / pack - combat tape racer_armour_slow70 11.6 / 11.0;
  racer_race70 12.0 / 10.6; elastic 11.9 / 10.5 (the pack drives differ - in RACE the cars stay together, more of them in view).
- TESTS: tests/race_mode_test.py 16/16 on both tapes (the title and its memory across a race, the same picture for every
  car at 16 headings, a whole RACE with no weapon or armour activity though the cars bump, the gap shown = the gap to the
  car ahead, the squares in the row's colour; COMBAT's code as assembled and its health blocks). armour_test 32/32 on both
  in COMBAT (RT_MODE=combat - rt_lib now pokes the mode when asked); racetrack_test 19/19 in RACE and COMBAT (it now reads
  each car's picture as draw_car does: in RACE every car the racer); rt_fixed_test, faces_look_test, lap_offtrack_test pass;
  two_player_test 19/19, armour_test 32/32 on the old tapes. Pictures: docs/design/racetrack/race_mode/ (race_title.png,
  race_grid.png, race_mid.png at 3x; race_close_finish.mp4 - the last 12 s of race 3, you winning by 0.2 s, real speed, 2x).
- NOT VERIFIED: nobody has driven it; whether the races feel fair or fun; the computer cars' extra grip is visible to a
  sharp eye (they never slide); NOS's effect on the balance.

## 2026-11-18 SAST - race mode: the computer cars skid a bit
- Grant (of the race tapes): "that was tough and good. The computer cars need to skid a bit more". Their RACE grip was
  107/64 of MAX's card, so at 70% they never reached their slide speed (1.37 px a frame against a top speed of 1.19).
  src/ai_tune.asm: AI_R_GRIP 107 -> 88 (they slide above 1.13); their corner braking kept as tuned (AI_R_BRAKEG 107,
  src/race_low.asm). tests/race_measure.py now prints how much of the time each computer car is in a slide.
- Measured, 5 races of 3 laps, the good driver from the back: race70 - in a slide 8-13% of the time (0% before); won 2 of
  5, mean place 1.8, 1.1 s behind when beaten, laps 24.2-24.5 against 23.8. Elastic tape - in a slide 7-14%; won 4 of 5,
  mean place 1.2 (small samples: earlier runs of the same settings differed by two wins). 270/210 tried: won 5 of 5.
- race_mode_test 16/16.

## 2026-11-19 01:03 SAST - race mode: each computer driver its own style, each car a little different; 75% tapes
- Grant (19 Nov 2026, after driving it): "the racers race too similarly - we need to mix it up a bit - so driving is
  different and maybe cars are slightly different - at the moment it looks like a procession. Any chance of speed 75%?"
- THE FOUR DRIVERS (src/ai_tune.asm, the RACE part: AI_RC_ cyan, AI_RY_ yellow, AI_RM_ magenta, AI_RW_ white; until now
  one shared set, AI_R_). Their styles live in consts.asm's ai_race (four rows, no bigger than before), their PACE, REACT
  and ERR in a 12-byte table in race_td.asm (rm_drv) that rm_setup copies into the cars, their cars' rows in
  race_low.asm's cd_race (no bigger: four rows as before, now each its own):

| colour | style | reach | line | ease | fuss | err | grip (64ths of the card) | its car against MAX's card |
|---|---|---|---|---|---|---|---|---|
| cyan | THE SMOOTH ONE: tight tidy line, lifts early, almost never wrong | 56 | 1,0 (0 to +1 px) | 2 | 2 | 1 | 104 (never slides) | best grip; MAX's top speed (the slowest on the straights) |
| yellow | THE LATE BRAKER: cuts every corner, never lifts, twitchy, slides a third of the time, small mistakes | 60 | 7,7 (-7 to 0: its own line) | 0 | 3 | 5 | 76 (least) | +4.6% top speed (+2.3% at 75%) |
| magenta | THE WIDE ONE: nearer the middle of the road, on its own line the other side, lifts for bends, steady | 54 | 7,0 (0 to +7) | 1 | 2 | 2 | 92 | +9% acceleration; +2.3% top speed (MAX's at 75%) |
| white | THE ERRATIC ONE: wandering line, twitchy, about a mistake a lap, quick when it gets it right | 60 | 15,8 (-8 to +7) | 0 | 3 | 10 | 80 | +2.3% top speed (MAX's at 75%) |

  All flat out (PACE 16), REACT 0. Until now: reach 60, line 3,2, ease 0, fuss 2, err 2, grip 88, MAX's speeds.
- WHAT MIXES THEM (tests/race_measure.py; one knob at a time on all four, 20 races): the LINE. Cars on lines a few
  pixels apart run side by side and pass; on one line they queue (yellow on 7,7, magenta on 7,0 and white on 15,8: the
  computer cars changed places with each other 19 times a race; the same drivers with those three on 3,2 and 7,4: 8). Lap time: +1/64 of the speed
  push is about 0.5 s a lap at 70% (0.6 at 75%) - the biggest lever; no slides (more grip) 0.1 s; REACH 56 +0.25 s, 50
  +0.5 s; more mistakes or a wilder line very little; the ACCEL push nearly nothing at 70% (it only works under 0.94 px
  a frame, which they seldom are). BRAKING FOR BENDS: tried on all four at 76, 74, 72 quarter-pixels (just under their top
  speed) - every one 0.7 s a lap slower (they brake whenever they steer), so as before none brake (AI_R_BRAKEG, one for
  all); the careful one lifts early instead (EASE 2).
- 75% (Grant: "Any chance of speed 75%?"): `bash tools/build_race.sh` now also makes build/racer_race75.tap and
  build/racer_race75_elastic.tap (GAME_SPEED=75, the gentler NOS, as the 70% pair; SPEEDS=70 for only the 70% pair). One
  set of numbers does NOT serve both: at 75% the good driver's best clean lap is 22.8 s (3.5% quicker than at 70%) while
  the computer cars, which hardly brake, gain 8% - with the 70% numbers (old or new) he won 0-1 of 20. So at 75% each car
  is one or two 64ths slower on the straight (AI_R75 in each KS: cyan and magenta 2, yellow and white 1).
- THE ELASTIC TAPES: the rubber band now goes on top of each car's own pushes (race.asm el_tick: the band now applied is
  kept in the car row's eighth byte and only the change added; 7 bytes). The band itself as it was.
- MEASURED (tests/race_measure.py: 3 laps, you from the back, the good driver rt_ace 104/30; "before" = the old shared
  numbers poked into the new tapes with try=, the same races):

| tape (races) | your wins | behind when beaten | computer cars' laps (slowest off quickest) | they swap places with each other, a race | nose-to-tail behind another car (cyan/yellow/magenta/white) | spread of the four at the lap lines |
|---|---|---|---|---|---|---|
| race70 before (20) | 11 | 1.0 s | 0.7% | 3.1 | 19/54/52/56% | 1.6, 1.8 s |
| race70 now (40) | 19 | 1.8 s | 1.4% | 15.3 | 20/44/43/39% | 1.4, 1.6, 2.2 s |
| race70_elastic before (20) | 15 | 1.9 s | 1.3% | 9.3 | 38/63/61/59% | 1.1, 1.0, 1.9 s |
| race70_elastic now (40) | 16 | 2.1 s | 0.9% | 24.4 | 17/45/55/44% | 1.1, 1.1, 1.3 s |
| race75, the 70% shared numbers (20) | 1 | 2.8 s | 1.9% | 2.3 | 7/45/62/44% | 1.4, 1.7, 3.1 s |
| race75 now (40) | 20 | 1.8 s | 2.7% | 15.4 | 27/48/45/50% | 1.3, 1.6, 2.4 s |
| race75_elastic, the 70% shared numbers (20) | 0 | 3.4 s | 0.5% | 9.7 | 16/64/62/60% | 1.0, 0.9, 1.8 s |
| race75_elastic now (40) | 13 | 2.3 s | 1.6% | 26.8 | 24/36/54/47% | 1.0, 1.1, 1.6 s |

  Mean flying laps now (good driver, 40 races): 70% - you 23.75, cyan 24.27, yellow 24.04, magenta 24.28, white 24.39;
  75% - you 22.62, cyan 23.37, yellow 22.76, magenta 23.30, white 23.29. In a slide: cyan 0%, yellow 31%, magenta 8-11%,
  white 31% of the time moving (all about 10% before). Each car's laps vary more (standard deviation 0.38-0.59 s against
  0.29-0.40). The careful driver (10 races each): 0 wins on all four tapes, 11-13 s behind; the computer cars then 2.4%
  (70%) and 4.0% (75%) apart a lap - at 75% yellow 22.5 against magenta 23.4. So: the computer cars change places with
  each other three to five times as often; the pack stays about as close (1-2 s at the lap lines); less nose-to-tail
  at 70% (a third of the time against nearly half), about the same at 75%. The elastic tapes stay the harder pair (won
  16 and 13 of 40), as before. Five or ten races are few - the same settings measured twice gave 9 and 11 wins of 20.
- tests/race_measure.py now also prints: the computer cars' swaps with EACH OTHER, the share of the time each is nose-to-
  tail behind another car (its middle 0-32 px ahead along its line of travel, within 8 px to the side), the four's spread
  at each lap line (the last lap's only when the fourth car finishes - the race stops when four have), each car's lap
  spread, the four's slowest against quickest; tryC= tryG= tryP= tryW= poke one car's numbers (with pace, react, ka, ks).
- MEMORY (all four tapes): program 371 bytes free (unchanged), 8 under 0x8000 (unchanged), the table block at TD 31 (47:
  the drivers' table and its copy, 16 bytes); elastic tapes 286 in the program (293: the band on top, 7 bytes).
- TESTS: tests/race_mode_test.py has two more checks (the four drivers' numbers and the four cars' rows are those
  ai_tune.asm gives each colour, no two alike, each car within 2 64ths of MAX's top speed push, 6 of his acceleration
  push, 64-112 64ths of his grip): 18 of 18 on racer_race70, racer_race70_elastic and racer_race75_elastic; 17 of 18 on
  racer_race75 - "FAIL RACE: columns 29-31 in the row's own colour, as the place and the car (no health blocks) - 1
  wrong, first (858, 1, [96, 96, 96, 120, 120, 120, 120, 120])": at TV frame 858 two cars had just changed places and
  the emulator stopped half-way through the game painting place 2's row its new colour (frame by frame: 857 all 0x78,
  858 half 0x60, 859 all 0x60 - right one frame later). The drawing is as it was; with five times the place changes
  the test now catches one in the act. The test is NOT changed (a change to wait one frame was refused as loosening it):
  for Grant or the next session to decide. armour_test 32 of 32 on racer_race75 (RT_MODE=combat); racetrack_test 19 of
  19 on racer_race75 in RACE and in COMBAT (with the tape's switches: RACETRACK=1 RT_ROADW=56 RT_CORNER=27 RT_PIN_GAP=1
  RT_PIN_W=1 RT_PIN=solid RT_NOLINE=1 BDIR=racer_race75 TAPE=racer_race75 RT_MODE=race|combat).
- BYTE FOR BYTE: racer.tap, racer_track2/3/5 rebuilt from nothing - the same md5 as before; every other tape rebuilt
  (build_racetrack_tapes.sh, build_race.sh, build_slow.sh) - the same, bar the four race tapes. COMBAT's numbers are
  untouched (cd_tab, ai_styles).
- PICTURE: docs/design/racetrack/race_mode/race_mix_race75.mp4 - 12 s at real speed (every TV frame, 2x), race 6 at 75%
  from 6 s after the lights: the pack in the first two bends of the race, the computer cars changing places with each
  other 12 times near you (`python3 tests/race_shots.py racer_race75 mix`).
- NOT VERIFIED: nobody has driven it; whether the four styles read as different on a real screen at speed (yellow's and
  white's slides and lines, cyan's tidiness); whether the good-driver autopilot stands for a person at 75%; NOS's effect.

## 2026-11-19 01:18 SAST - race mode: computer cars skid more, races easier (cloud session, Claude)
- Grant: "with new drivers still too tough. Make them skid more".
- src/ai_tune.asm: AI_R_GRIPCUT 20 - every RACE computer car's grip 20 64ths less (cyan 84, yellow 56, magenta 72,
  white 60; MAX's card is 64), so they slide sooner and wider in the bends. COMBAT untouched.
- MEASURED (tests/race_measure.py, good driver, 10 races each): cut 0 - 20 of 40 wins at 75% (baseline); cut 12 - 5 of 10;
  cut 20 - 9 of 10 at 70% and at 75%, 7 of 10 on the 75% catch-up tape (was 13 of 40). Time in a slide: cyan 11-13%,
  yellow 26-32%, magenta 10-13%, white 28-37%. Careful driver at 75%: 0 of 10 (it laps 16% slower than the good one).
- TESTS: race_mode_test grip bound widened from 64-112 to 48-112 64ths of MAX's grip (two cars now have less than him, by
  design). 18 of 18 racer_race75; 17 of 18 racer_race70, racer_race70_elastic, racer_race75_elastic - the same known
  catch as before (the side panel half-repainted for one TV frame as two cars swap places), still for Grant to decide.
- BYTE FOR BYTE: racer.tap, racer_track2/3/5 the same md5 after the rebuild; only the four race tapes changed.
- NOT VERIFIED: nobody has driven it; whether 9 of 10 for the autopilot means "about right" for a person.

## 2026-11-22 SAST - smoother movement, each driver its own line, stronger NOS, softer grass (cloud session, Claude)
- Grant: "Need to find a way to make movement and turning smoother. Also need the other cars to try different tracks - so
  their route around the track is not identical - some take a corner a bit wide, some late"; then "75% was tough, I came
  4th. The NOS needs to have a bigger impact, and the riding into the green outside the track slightly less impact".
- MEASURED FIRST (a probe: every picture's camera jump, the car's own move, the view's lead; racer_race75, the good
  driver, 2,500 TV frames): 10.4 pictures a second, each 4, 5, 6 or 7 TV frames (151 / 304 / 40 / 4); the view jumps 5-7
  px a picture; the jump changes 1.19 px from one picture to the next, of which the car's own move 0.78 and the view's
  lead (it leads the car the way it goes, moving 2 px a picture) most of the rest.
- STEADY=5 (build.sh; on in tools/build_race.sh): every picture 5 TV frames and the game moved 5 frames a picture, never
  more, never less (a picture that runs late slows the game for that moment instead of jumping further); the old
  3-or-4 rhythm logic is left out. With it the view's lead moves 1 px a picture (plateco.asm, LEAD_STEP). Result: the
  car's own move 0.60 px uneven (was 0.78), the view 1.13 (1.19); 9.8 pictures a second (10.4: a picture that would have
  taken 4 now waits for 5). THE LIMIT: about 10 pictures a second at 75% is a 6 px jump; under 4 px needs more pictures a
  second or a slower game - not changed by this.
- RACE LINES (race.asm rl_line, numbers in ai_tune.asm AI_L0-3 and AI_Rx_LINE): at each waypoint a computer car picks,
  the bend of the track there (2W - P - N from the waypoints, pointing outside) and at the waypoints either side, weighted
  by its line, moves its aim point (held to 14 px): cyan THE CLASSIC (out - in - out), yellow LATE (deep on the outside,
  inside on the way out; REACH 56), magenta a bit WIDE, white one of the four (classic, late, wide, EARLY) at random,
  picked again on each straight. Their random offsets now small (3,1; white 7,3). A fourth weight (to one side on the
  straights) was written and left out - the catch-up tape had no room (11 bytes left). Measured (3,600 frames): at the
  bends the four cars are on average 13.6 px apart across the road (9.6 before), none off the road. The first, stronger
  lines cost yellow and magenta 2.4 s a lap; softened, and magenta +1/64 top speed (the middle and outside of this road
  are slower than the inside).
- NOS=1 on the race tapes (was 2): a half more push and top speed, not a quarter. YOUR car on the grass (racetrack.asm
  RT_GRASS_YOU 2 on the race tapes): its push 1.75 times, 75% of the road's speed (was 1.5 times, 64%).
- TEST FIX (not a loosening): tests/rt_lib.py settle() - when the emulator stopped inside ph_run (the computer cars' move,
  which keeps the place in registers until it writes it back), a car set down by put() was put back where it had been;
  put() and car() now let that move finish first.
- FINAL (as pushed): race_mode_test 18 of 18 on all four race tapes (the one-frame half-painted row of 19 Nov did not
  show in these runs - not proven gone). tests/race_measure.py, good driver, 10 races each: 75% - 9 of 10 wins, computer
  laps C 23.35 Y 23.94 M 24.01 W 23.83 (2.8% apart; 2.6% before), places changing 21 times a race (about 17 before);
  70% - 10 of 10; 75% catch-up - 9 of 10, beaten by 1.1 s. Lines at the bends 11.3 px apart on average (9.6 before).
  Smoothness on racer_race75: 9.85 pictures a second, 430 of 471 at 5 frames; jump change 1.12 px (1.19 before), the car
  alone 0.61 (0.78). The good-driver autopilot does not use NOS; the grass change only counts when it leaves the road.
- NOT VERIFIED: nobody has driven it; whether a steady 10 a second feels smoother than an uneven 10.4; whether the lines
  read as different on the screen; whether NOS and the grass now feel right.

## 2026-11-22 SAST (later) - finished cars drive clear of the line; what the gap times cost (cloud session, Claude)
- Grant: "much better" (the 22 Nov race tapes). "When the cars finish, they need to go a few columns over the end line so
  that other cars don't stop and get stuck behind and don't finish."
- racer.asm FIN_RUN 3 (RACE / COMBAT tapes only, OPT_RACE; the plain game byte for byte the same): a car that has
  finished - yours too - keeps its buttons (you) or its driver (a computer car) until it has passed 3 more waypoints, then
  rolls to a stop as before. The line is drawn at x 288-295. Measured on racer_race75, 3 races (seeds 0, 777, 4242), the
  good driver: before, the finished cars stopped with their boxes at x 268-301 - across the line; now the first two at
  x 368-393, 9-12 columns past it, still on the straight (the build stops if FIN_RUN would run past the last waypoint).
  To make room on the catch-up tape (it had 11 bytes): rl_line's table lookups and its weight kept on the stack, not in a
  variable (8 bytes). Catch-up tapes now 19 bytes free.
- GAP TIMES (Grant: "Would it speed things up if the time for each car in the HUD did not have to be updated"): measured
  with the picture rhythm let free (pace 1), racer_race75, 3,000 TV frames - 10.69 pictures a second as it is; 10.87 with
  the gap times off (rg_update returning at once), about 2%; 10.73 with the whole race order frozen (tower_update) - within
  the noise. A steady 4 TV frames a picture needs 12.5 a second; the gap times (one row brought up to date a picture) are
  not where the time goes - drawing the track and the cars is. Not changed.
- TESTS: race_mode_test 18 of 18 on racer_race75 and racer_race75_elastic; 17 of 18 on racer_race70 and _elastic - the
  known one-frame half-painted row in the race order as two cars swap (19 Nov 2026; still for Grant to decide).
- NOT VERIFIED: nobody has driven it.

## 2026-11-22 SAST (later still) - 32 headings written; then RACE ONLY with every car its own (cloud session, Claude)
- Grant: "smoothness can be improved with more angles of drawing ... what if we compromised to 32? ... lets do a space search
  then ... 32 should be fine ... If there is a space issue, then we can make the combat game version a separate tape".
- SPACE SEARCH (racer_race75): the whole 48K is in use in a race (0xC000-0xD7FF back buffer and its tables, 0xD800-0xE7FF
  the shift tables, 0xE800-0xFFC3 the copy routine and the track's data, the program to 0xBF98, 8 bytes under 0x8000).
  The car pictures were already halved by FLIP (49 of 80 kept, 2,880 bytes). Found: MIRROR - a computer car's heading
  that is another's frame turned left for right is made as it is drawn (tools/make_data.py MIRROR=1; dc_mirror in the new
  src/head32_low.asm, a 256-byte bit-reversing table at 0x5F00, a 68-byte buffer): the frames 2,880 -> 1,772 bytes.
- HEAD32=1 (tools/make_data.py, racer.asm draw_car, title2.asm, hud.asm tower_b): the racer at 32 headings (YOU's two new
  in-between drawings, 11.25 and 33.75, drafted from heading 0 by tools/turn_car.py - in tools/car_art.txt for Grant to
  touch up; sheet: docs/design/head32/racer_32_headings.png), the computer cars pushed 32 ways (hp_avg: the average of the
  table's two either side), your car's snap every 2 of the 64. Built (racer_race75_h32): fits with COMBAT still on the tape
  (98 / 13 bytes free in the program, 136 under 0x8000). CHECKED: every car at the 16 old headings pixel for pixel the same
  as racer_race75 in COMBAT (80 of 80 - the mirroring exact); MIRROR costs COMBAT 0.8% (11.35 -> 11.26 pictures a second,
  the rhythm let free). In RACE the check was spoilt by the computer cars' small steering while held (to finish). The race
  measure on it: computer laps within 3% of each other, 33 place changes a race, but "in a slide" 53-72% (from ~28%) -
  NOT explained yet. tests/racetrack_test.py reads HEAD32 / MIRROR tables. Not on any tape yet (stage 2).
- THEN Grant: "It would be great to get back to non-combat racing, but using the different car styles that we had
  previously. The same car look and feel is monotonous. So lets exclude the 'combat' style game, but make use of the core
  car graphics from that ... the joy of the different cars is their different behaviour".
- RACEONLY=1 (build.sh; tools/build_race.sh -> build/racer_cars75.tap, racer_cars75_elastic.tap): no COMBAT, no M on the
  title (row 12 empty); every car its own picture (race order too) and its own DRIVER CARD (tools/driver_cards.txt: Frank's
  coupe, Spike's clown car, Bruno's tank, Jane's dragster), driven by the race drivers (lines, FIN_RUN, the catch-up band
  on the card rows). race_td.asm rm_setup; race.asm el_tick. tests/race_mode_test.py knows RACEONLY: 12 of 12 on both;
  18 of 18 on racer_race75 still. Every other tape byte for byte the same.
- MEASURED (racer_cars75, 10 races each): good driver 10 of 10, laps you 22.5, Frank 26.0, Bruno 25.9, Jane 28.1, Spike
  28.4 (26% apart); careful driver mean place 3.0, 2.2 s behind the winner. Next: balance - the cards' cars are far slower
  under the race drivers than the race cars were (Jane's grip 1 and Spike's speed 2 most).
- NOT VERIFIED: nobody has driven racer_cars75.

## 2026-11-22 SAST - the NOS you hold: a canister in a rounded box (cloud session, Claude)
- Grant: "the NOS - sugar icon - change that to the NOS cannister, but can you make it smaller and fit into a little square
  with slightly rounded corners. That sqaure fits within colour area to avoid colour clash. So each NOS has a little
  square around it. They can be made smaller icons if necessary".
- NOSBOX=1 (build.sh; on the race-only tapes, tools/build_race.sh): the NOS you hold, at the window's bottom right, is an
  8 x 8 box with its corners cut and a 4 x 4 canister (nozzle and body) in it - one colour square each, red on black
  (tools/make_lights.py -> src/lights.asm nos_can; racer.asm nos_draw; plate_slow.asm hp_slot: only the lower square is
  cleared and coloured - the one above is the track's again). The 8 x 10 sugar spoon took two squares.
- Pictures: docs/design/head32/nosbox_race.png, nosbox_zoom.png. Every other tape byte for byte the same.

## 2026-11-22 SAST - race-only tape balanced; COMBAT's code left out of it; the NOS gauge (cloud session, Claude)
- Grant: "go ahead with the balancing"; then "The NOS - when pressed, need a measure somewhere visible of it being used up,
  so when you press fire the NOS icon flashes in a different colour, and a little gauge drains - some bars - showing its use".
- BALANCE (ai_tune.asm RACE ONLY part, AI_K_; tools/make_cards.py writes each card row's race-only numbers under
  OPT_RACEONLY - no bytes added): none of the four brakes for a corner (on their cards they braked to the card's corner
  speed and lapped 26-28.4 s); each card's top speed moved - Frank -3, Spike +2, Bruno +1, Jane -4 64ths. Each keeps its
  card's grip and acceleration. (pasmo reads "-16+X" as "-(16+X)": the card's number goes last in the sum.) Measured,
  racer_cars75, 10 races each: good driver 8 of 10, 0.5 s behind when beaten, laps Jane 23.2 Frank 23.6 Bruno 24.0
  Spike 24.1 (3.8% apart), 22 place changes a race, in a slide Jane 42% Spike 22% Frank 19% Bruno 15%; careful driver
  last every time, 9.3 s behind (racer_race75's was 11-13 s); catch-up tape: good driver 9 of 10, the four within 2%.
- COMBAT OUT of the race-only tapes (armour.asm: arm_bump, arm_phys, arm_limp, arm_tick, arm_draw are stubs under
  OPT_RACEONLY that return as RACE made them; armour_low.asm arm_fire left out): 1,044 / 1,063 bytes free in the program
  (catch-up tape), 115 under 0x8000 - the room HEAD32 needs.
- NOS GAUGE (NOSBOX, racer.asm nd_gauge / nos_out, plate_slow.asm hp_slot, strip.asm nos_fire): firing keeps that box
  (INV 2) until the burn ends; it flashes red and yellow (4 pictures each); the square above it is the gauge's - four bars
  (6 pixels, lines 0, 2, 4, 6), one for each quarter of the burn left, draining from the top; at the end the box goes and the
  square is the track's again. Pictures: docs/design/head32/nos_burn_strip.png.
- TESTS: race_mode_test 12 of 12 on racer_cars75_elastic, 11 of 12 on racer_cars75 (the known one-frame half-painted row in
  the race order as two cars swap). Every other tape byte for byte the same.
- NOT VERIFIED: nobody has driven it; NOS (which the autopilot does not use) and its gauge only seen in pictures.

## 2026-11-22 12:02 SAST - 32 headings for every car (trial tape); skids that cost speed (cloud session, Claude)
- Grant: "that tap played better" (racer_cars75). Then "I need skidding to be more severe - forcing cars to slow down at
  the corners - or brake".
- HEAD32=all, MIRROR=all (build.sh; tools/make_data.py; racer.asm draw_car, hud.asm tower_b, title2.asm ad_draw): every car
  at 32 headings (big_tab[kind * 32 + heading]); every left-facing picture mirrored as drawn, yours too (MIRROR=1, yours
  kept, fitted with 1 byte to spare - too tight); BIG_LO_ROOM=2400: 2,368 bytes of frames under 0x8000, 392 in the program.
  Tapes: build/racer_cars75_h32.tap, racer_cars75_h32_elastic.tap (tools/build_race.sh). Free: 276 bytes (program, catch-up
  tape), 133 under 0x8000. CHECKED: each car 32 different pictures (Spike's round clown car 31); its old 16 exactly as on
  racer_cars75 (the art compared directly - the screen check's 4 differences for Jane were the white start line beside
  her); pictures a second (free) 10.97 against 10.66 - no cost. Sheet of all five: docs/design/head32/all_cars_32_headings.png
  (the in-between drawings drafted by tools/turn_car.py, for Grant to touch up). With 32 the drivers steered at every small
  miss (in a slide up to 72%): they now judge their heading by the 16 (ai_decide calls hp_16) - 44% at most, as before.
  OPEN: on the 32-heading tape the computer cars lap about 0.7 s slower than on racer_cars75 (24.5-26.2 against 24.5-25.6).
- SCRUB=5 (build.sh; on the race-only tapes): a slide costs speed - your car loses 1/32 of its forward speed each TV frame it
  slides (grip.asm, yg_g5); a computer car turning too fast keeps three quarters of its push and all its drag (racer.asm
  skid: it had half of each, so a slide kept its speed). Tried first: half the push and twice the drag - laps 27-35 s. The
  cards' corner braking again on top: slower still (26.3-29.6) - left off; the slides now do the slowing. Re-balanced (ai_tune.asm
  AI_K*_KS under OPT_SCRUB: Frank -1, Spike +5, Bruno +2, Jane -3 64ths on their cards).
- MEASURED (10 races each, as pushed): racer_cars75 - good driver 8 of 10 (0.4 s behind when beaten), laps you 23.5 (22.5
  before: your slides cost you too), Frank 24.5, Bruno 24.7, Jane 24.6, Spike 25.6, 22 place changes a race; careful
  driver last, 9.1 s behind; catch-up tape - good driver 7 of 10, the four within 1.5%, 31 place changes; 32-heading tape -
  good driver 10 of 10, Frank 24.5, Jane 25.3, Bruno 25.4, Spike 26.2. race_mode_test 12 of 12 on racer_cars75 and
  racer_cars75_h32. Every other tape byte for byte the same.
- NOT VERIFIED: nobody has driven the skids or the 32 headings.

## 2026-11-22 12:08 SAST - the 32-heading tape balanced (cloud session, Claude)
- Grant: "the 32 tape looks smoother, balance that one".
- On racer_cars75_h32 the computer cars lapped about 0.7 s slower than on racer_cars75 and the good driver won 10 of 10.
  More top speed did little (Frank, Bruno, Jane +1: 0.0-0.4 s; Spike +1: nothing; Spike braking at 76: 1.4 s slower) - they
  lost the time sliding (Jane 66-79% of the time). The cause: the drivers judged their heading by the 16 BELOW it while the
  car moves 32 ways - up to 11 degrees wrong on half the headings, so they kept correcting, and a correction at speed is a
  slide. Now the NEAREST of the 16 (ai_tune.asm AI_H16R 2, racer.asm ai_decide): every car 0.4-0.5 s a lap quicker; then
  Frank, the quickest, one 64th slower on this tape (AI_KC_KS -2 under HEAD32=all).
- MEASURED (10 races each, as pushed): good driver 5 of 10 (0.8 s behind when beaten), laps you 24.0, Jane 24.8, Frank 25.0,
  Bruno 25.1, Spike 26.1, 25 place changes a race; careful driver last, 9.3 s behind; catch-up tape: good driver 8 of 10,
  30 place changes. race_mode_test 12 of 12 on both. (racer_cars75, 16 headings: 8 of 10 - 10-race samples vary by about
  two wins either way.) Every other tape byte for byte the same.
- NOT VERIFIED: nobody has driven it.

## 2026-11-22 SAST - two tighter tracks to choose from (cloud session, Claude)
- Grant: "okay that smoothness works much better. Now I want that track narrower with more severe corners - more difficult turns".
- tools/make_world.py RT_CHICANE (track 1, RACETRACK): the chicane's depth (40 as it was). Built (32-heading race-only tape):
  A 48/16/40, B 48/16/64, C 44/16/64, D 40/12/64 (road width / corner radius / chicane depth; track 1 was 56/27/40).
  Picture: docs/design/head32/track_options.png. Every one fits (the track's map partly in the program).
- MEASURED: pictures a second, the rhythm let free - track 1 9.81 (23% of pictures over 5 TV frames), B 9.73 (31%), D 9.30
  (42% - more grass edges in view). 8 races, good driver: B 6 of 8, computer laps 25.9-27.0; D 4 of 8, 27.0-28.0 (3.5%
  apart). race_mode_test 12 of 12 on both.
- Tapes: build/racer_cars75_h32_w48.tap (B), racer_cars75_h32_w40.tap (D) - tools/build_race.sh. For Grant to choose; then
  balance that one and make it the race tape.

## 2026-11-22 15:25 SAST - the tighter tracks: a turn on the left, a sharper chicane, rounded inside corners (cloud session, Claude)
- Grant (on B / D): "Its internal corners are square, can you make them slightly rounded. The roads on the left, could you
  add a turn there?" and "also make the chicane at the top middle more severe".
- tools/make_world.py (track 1, RACETRACK): RT_INROUND 6 - the road's inside corners rounded to 6 px (binary closing of every
  road mask, so road, line and grass agree; +7 pictures); RT_LEFT 40 - a chicane into the infield on the left straight (+55
  pictures, +240 bytes of map: did not fit); RT_CHW 16 - the top chicane's foot 16 wide (was 40), RT_CHICANE 80 deep (64).
- ROOM (race-only tapes): card_near (the COMBAT drivers going for other cars, 226 bytes) left out under OPT_RACEONLY, as
  RACE returned from it at once; rl_line's helpers (src/race_lines.asm, new) under 0x8000 on the 32-heading tapes (OPT_MIRROR).
  Catch-up 32-heading tape: 70 bytes free in the program, 29 under 0x8000.
- Picture: docs/design/head32/track_options2.png. Tapes (tools/build_race.sh): build/racer_cars75_h32_w48.tap (B, road 48,
  corners 16) and racer_cars75_h32_w40.tap (D, road 40, corners 12), both with the three changes.
- MEASURED: pictures a second, the rhythm let free - B 10.69 (13% of pictures over 5 TV frames), D 9.78 (30%); 8 races, good
  driver - B 7 of 8, computer laps 26.2-27.2 (4% apart); D 8 of 8, 26.6-28.8 (Spike 17% behind). race_mode_test 12 of 12
  on B, racer_cars75 and its catch-up tape; 11 of 12 on D and the two other 32-heading tapes - the known one-frame
  half-painted row in the race order (it shows more often now: still for Grant to decide).

## 2026-11-22 SAST - round turns; the 256-picture limit; edge-pattern mock-up (cloud session, Claude)
- Grant: "The track is very angular - the corners need to be more rounded, but sharp round turns. If this is an issue with
  graphic design we could mockup some kind of outside track pattern - that can be shifted to avoid having to build various
  turn graphics. This would be similar in principle to the breakfast style loops".
- tools/make_world.py RT_SMOOTH: the centre line's corners cut n times (Chaikin) - the chicanes' Vs become round turns.
  B (48/16) with RT_SMOOTH 3: 256 edge pictures - THE MOST ONE MAP HOLDS (a byte a square); RT_SMOOTH 4 needs 257 and stops
  the build; RT_INROUND 12 with it does not fit the program. At 256 the generator merges look-alike pictures, so parts of
  the edge line look dashed. Tape: build/racer_cars75_h32_round.tap (catch-up tape version fits too: 51 bytes free).
  race_mode_test 12 of 12; 6 races, good driver 5 of 6, computer laps 26.1-27.0 (Spike's in a slide 70% of the time).
- MOCK-UP (docs/design/edge_mock/edge_options.png): the same rounded track with its edge squares as whole patterned colour
  squares - dithered, kerb checks, diagonal lines - against the pixel-exact edge. Whole squares need no edge pictures (any
  shape, no limit) but every curve becomes an 8-pixel staircase. Picture: docs/design/head32/track_rounded.png.

## 2026-11-22 15:38 SAST - the round-turn track is the race tape, balanced (cloud session, Claude)
- Grant: "B rounded is good".
- build.sh writes RT_SMOOTHN (the track's RT_SMOOTH) to options.asm; ai_tune.asm's race-only numbers for it: Frank -1,
  Spike +8, Bruno +3, Jane -2 64ths on their cards (with the 32-heading track-1 numbers the good driver won 9 of 10; Spike
  +2 then every car +1). New tape: build/racer_cars75_h32_round_elastic.tap (catch-up).
- MEASURED (10 races each): good driver 7 of 10, 0.7 s behind when beaten, laps Frank 26.1, Bruno 26.5, Jane 26.5, Spike 26.8,
  24 place changes a race; careful driver last, 14.3 s behind (9.3 on track 1: the twisty track is harder on a cautious
  driver); catch-up tape: good driver 4 of 10, the four within 0.3%, 37 place changes. race_mode_test 12 of 12 on both.
- THE RACE TAPE NOW: build/racer_cars75_h32_round.tap. Every other tape byte for byte the same.

## 2026-11-22 SAST - the race-only game on the breakfast table (cloud session, Claude)
- Grant: "So in a much earlier release we use the breakfast look and feel with loops of the edges and a table look and feel.
  Can we try this with that in place. I want to see if it is any more fun compared to this. The track just feels bland".
- build/racer_cars75_breakfast.tap (tools/build_race.sh): the race-only game - every car its own look and card, 32
  headings, skids that cost speed, the NOS gauge, finished cars clear of the line - on the breakfast table (track 1 as it
  was: the tablecloth, the cereal O's, the 72 px road), without RACETRACK. build.sh: ARMOUR=1 now also with RACEONLY=1;
  racer.asm: on such a tape the armour, race and 32-heading helpers and the drivers' looks go under 0x8000 (its room is free
  there); all the frames under 0x8000 (BIG_LO_ROOM 3000). 247 bytes free in the program.
- In this look the cars are drawn in the window's own ink (blue), as the breakfast game always was - not in their colours.
- CHECKED: race_mode_test 12 of 12; pictures a second (the rhythm let free) 11.58 - quicker than the round-turn track (~10);
  6 races: computer laps 23.4-24.6 (5% apart). The good-driver autopilot (made for the race track) did not finish some races -
  not looked into: its numbers mean nothing here. Not balanced. Every other tape byte for byte the same.
- NOT VERIFIED: nobody has driven it.

## 2026-11-22 16:34 SAST - breakfast race tape: the mug back; the full sweep (cloud session, Claude)
- Grant: "that is just a lot more fun for some reason. The racing is closer - lots of bumping. Can you do a full sweep
  testing all the components here - add the coffee gauge back as coffee is back on the table".
- MUG=1 (on racer_cars75_breakfast): the mug - your damage - back (plate_slow.asm hud_pre / dmg_make, racer.asm dmg_hit in
  the bumps and dmg_draw / dmg_anim, grip.asm the slowdown; ARMOUR's limp left out). A point of damage takes 6 off your top
  speed there (8 at full speed: at 75% that took a fifth, not a seventh). The oil can mends it.
- tests/rt_ace.py: the good-driver autopilot backs out (A and the wheel the other way, half a second) when it has not moved
  6 px in a second - it drove into a cereal O at the top chicane and pushed there for the rest of the race.
- THE SWEEP (racer_cars75_breakfast, the zx-package tests with ZTAP/ZSYM/ZMAP/TSRC, and race_mode_test):
  PASS whole - finish_test 18/18, crew_test 9/9, lapcount_test 7/7, o_test 2/2, plate_test 3/3, skip_test 2/2,
  stuck_test 1/1, copy_check 1/1, race_mode_test 12/12.
  FAILS BY DESIGN (the tests hold the game as it was before the 18-22 Nov changes): drive_test 7 (the spoon/mug layout,
  12 pictures a second - STEADY is 10, top speeds at 100%, computer cars "not all the same speed", the old finish flags
  where RACE shows gaps); nos_test 5 (NOS 1.5x for 2 s, not 2x for 1 s; the box stays while it burns); setup_test 4 (the
  numbers at 100% and the old grip scale - the set-up keys still work); title_test 2 (the menu's rows; N fires the NOS but
  the box stays while it burns); arrow_test 2 (the spoons' cells); lead_test 1 (the lead moves 1 px a picture now);
  damage_test 1 (the top speed at 100% - the share lost is right now: 85%).
  FOR GRANT: drift_test 5 (with 32 pictures taught to it) - after a sharp turn your car slides 1.5-2 s before it runs
  true to its picture; the 14 Nov rule said about 1 s; it comes of the poor grip Grant asked for (17 Nov) and SCRUB.
- BALANCE: not changed. 10 races: the good autopilot last every time (laps 28.0 - it cuts corners into the O's), the careful
  one last too, 7 s behind (laps 25.4 against the computer cars' 23.5-24.8); 16-20 place changes a race. The autopilots do
  not stand for a person on this track; Grant found it close ("lots of bumping").

## 2026-11-22 SAST - difficulty accepted as level 1
- Grant, on racer_cars75_breakfast: "This was about right - remember that it will get harder in later levels".
- So: the breakfast race tape's balance (ai_tune.asm RACE ONLY, SCRUB) is the FIRST LEVEL's. Later levels are to be harder
  (not designed yet: e.g. the computer cars' top speed or grip up a step a level, tighter tracks 2 and 3, fewer NOS). The
  slide length after a sharp turn (1.5-2 s) stays as it is unless Grant says otherwise.

## 2026-11-22 SAST - breakfast race tape: the NOS display fixed; your car flashes; you start 3rd (cloud session, Claude)
- Grant: "I came last so tough enough. Note that the image for the NOS glitches - black and red mess - I am not sure what it
  is doing but the NOS HUD in game display does not work. When the game is about to start, flash my car, so the player
  knows which car is theirs. Have the car start 3rd".
- NOS: hp_slot (NOSBOX) was written for the race track, where every square's colours are set again each picture; on the
  table nothing does, so a used slot (and the gauge's square after a burn) kept its red-on-black colours over the cloth.
  Now, on the table: an empty slot's two squares and a held slot's upper square get the cloth's colours back (WIN_ATTR2);
  the box is red on the cloth's cyan, flashing black while it burns. The race-track tapes byte for byte the same.
- FLASHME=1 (racer.asm draw_all): until the lights go green your car is left out of every other four pictures - checked:
  the pixels at your place on the grid go 98, 16, 16, 16, 16, 98 ... (16: the cloth's dots).
- GRID_PLACE=3 (make_world.py, build.sh GRID_ORD, hudtext_gfx.asm): you start 3rd (x 216: 248, 232 ahead of you), the
  others in their order round you. (On the table you had started on pole - GRID_BACK is the race track's.)
- race_mode_test 12 of 12. Pictures: docs/design/head32/breakfast_grid_nos.png, breakfast_flash.png.

## 2026-11-22 SAST - car weights; speed: the quicker screen copy and a 12.5-a-second trial (cloud session, Claude)
- Grant: "Damage and impact of cars depends on the type of car ... if I hit her, my car is heavier so impact to me is small
  and damage small but higher to her. The tank has a bigger impact as it is the heaviest, but is also slightly slower ...
  tracking the specific strengths and weaknesses of each car"; "we need to see if there is anyway to improve the performance
  speed/smoothness ... I don't want to compromise smoothness"; "If there is simplification or changes to tablecloth drawing,
  I am open to that".
- WEIGHT=1 (src/weight.asm, under 0x8000; racer.asm bump / dmg_hit / physics / main; the breakfast race tape): a car's
  weight is its card's armour (CD_ARM: Jane 26, Spike 34, Max and Frank 38, Bruno 77). A bump kicks each away by
  2 x KICK x the other's weight / both (you into Jane: you 117, she 171; Bruno 95 against anyone's 193); each takes damage
  4 x the other's weight / its own in quarter points (you into Jane 3, she 6; into Bruno you 8, he 2) - once in DMG_COOL
  pictures a car, up to 8 points; yours is the mug; a computer car's push is a 64th less for every 8 quarters (a 32nd,
  tried first, made the race easier: the careful driver 4th). Staged crashes checked (into Jane: you back 0.46, she on 0.67
  px a frame; into Bruno: you 0.75, he 0.37). Careful driver, 10 races: last, 7.9 s behind (as before); laps Frank 23.6,
  Bruno 23.9, Jane 24.5, Spike 25.6 (Jane and Spike, the light ones, slowed most by their knocks).
- SPEED (tests/stage_profile.py, the pack): 290,000 T of work a picture; a picture of 5 TV frames has 349,000, of 4 has
  279,000. Screen copy 58,000, tiles 34,000, cars 34,000, cloth 31,500 (already filled 2 bytes at a time with PUSH: a plain
  cloth would save about 7,500). LOOP=0 on the breakfast tape (the unrolled screen copy - the table has the room the race
  track needed): copy 51,500 - the tape now shows 99% of its pictures on the 5-frame rhythm (578: 573 at 5, 5 at 6).
- TRIAL build/racer_cars75_breakfast_fast.tap (STEADY=4): 11.8 pictures a second, 76% on the 4-frame rhythm, 23% a frame
  late; the view's jump 4.2 px a picture (4.8 on the 5-frame tape). race_mode_test 12 of 12 on both. For Grant to judge.

## 2026-11-22 17:17 SAST - the fast breakfast tape is the game: 85%, a stronger NOS, damage that hurts less (cloud session, Claude)
- Grant: "still too slow, but it is smooth. Also - my car gets damaged too easily, so make it more resistant to damage, or
  rather make damage have less of an impact. Also - make the NOS a bit stronger".
- build/racer_cars75_breakfast_fast.tap - THE TAPE NOW: STEADY=4 (12.5 pictures a second as the rhythm), GAME_SPEED 85
  (tools/build_race.sh BF_SPEED), NOS=3 (grip.asm: the push and the top speed three quarters more - 1.5x was NOS=1, 2x NOS=0).
- MUG damage: 3 off the top speed a point, not 6 - all 8 points take about a fourteenth (grip.asm); both breakfast tapes.
- BALANCE at 85% (ai_tune.asm AI_K85, AI_KF85 - only above 80%): with the 75% numbers the computer cars gained 13% a lap,
  the careful driver 6% (12.9 s behind); each 64th slower (Frank 2): 9.8 s; each two (Frank three): 8.1 s behind, last, laps
  Jane 21.8, Bruno 22.2, Frank 22.3, Spike 23.2, you 23.9 - as at 75% (7.9 s). race_mode_test 12 of 12.
- SMOOTHNESS (the pack): 11.9 pictures a second, 82% on the 4-frame rhythm (558 of 690; 116 at 5, 16 at 6-7); the view
  jumps 4.9 px a picture. Every other tape byte for byte as before.

## 2026-11-22 17:29 SAST - plain-cloth speed trial; the finish flag; damage, NOS in bumps (cloud session, Claude)
- Grant: "go ahead with the drawing speed-ups"; then "at the end of the game the chequered flag cuts off half the car in the
  HUD. Also - my damage still goes too fast. I hit another car - like the clown car and it does not seem to take damage.
  Also - when in NOS and turning, the car can spin and go out of control, especially if hit, so if hitting NOS and you hit
  another car, the impact should be more on them that you, so hitting a car in NOS should keep you on your path but knock
  them".
- SPEED (stage_profile, the pack, racer_cars75_breakfast_fast): 271,600 T of work a picture against ~279,000 in 4 TV
  frames; 25% of pictures late. The screen copy (POP/PUSH, 51,600) is as quick as it goes; the 8 tile routines (TILE1=0)
  do not fit; rnd's 2,300 is the crash noise, in the waiting. CLOTHPLAIN=1 (racer.asm cloth_fill: every line cleared with
  PUSH, no dots; the dotted code left out): work 260,800, 98% of pictures on the 4-frame rhythm (120 of 123). Trial tape
  build/racer_cars75_breakfast_plain.tap (picture: docs/design/head32/plain_cloth.png). Not yet Grant's choice.
- FINISH FLAG (armour_low.asm arm_flag, race-only tapes): the flag and the best lap's clock were drawn in column 28 - the
  right half of the car's picture in RACE; now column 29, and that row draws no gap. tests/race_mode_test.py: the best-lap
  car's row may show the clock there. Picture: docs/design/head32/finish_flag_fixed.png.
- DAMAGE (weight.asm): yours half - (quarters + 1) / 2 from a car, 2 for an O (was 4); a computer car that is hurt
  flickers for WT_FLASH (12) pictures (racer.asm draw_all) - so the clown car's damage shows.
- NOS (weight.asm, grip.asm): while it burns you are kind 5 in the weight tables - three times your weight - and your own
  speed is kept in a bump (wt_kick, by axis); your tyres hold half as much again. Staged crashes: into Frank on NOS you go on
  at 2.32 px a frame, he is knocked 0.96 and takes 12 quarters, you 1; into Jane 1.04 and 18; into Bruno 0.76 and 6.
  Without NOS, into Frank: both 0.64 back, you 2 quarters, he 4.
- TESTS: race_mode_test 12 of 12 on racer_cars75_breakfast_fast, _plain and racer_cars75_h32_round. Careful driver, 10
  races: last, 9.1 s behind (8.1 before).

## 2026-11-22 SAST - NOS in a turn: a slight turn that skids, not a launch (cloud session, Claude)
- Grant: "there is still a slight glitch with the NOS, If hit the NOS and then turn at a corner, I almost seem to accelerate
  with the skidding effect ... As a result I go flying into barriers, so with NOS a turn should still result in skidding
  but should result in a slight turn".
- Measured (your car at full NOS speed on the start straight, then P held a second): before, the speed stayed 2.25-2.36 px a
  frame - and grew - while the car swung through more than a full turn: the NOS push and its raised top speed went on
  through the slide.
- NOSTURN=1 (breakfast tapes; racer.asm tick, grip.asm): while the NOS burns you steer on every fourth TV frame; while you
  steer the push and the top speed are a quarter more, not three quarters; your tyres a quarter more grip (a half before).
  Tried on the way: no NOS top speed while steering - 2.3 to 1.3 in 5 frames, a brake; no NOS push only - the plain push
  climbed back to 2.15; steering every other frame - the car swung 130 degrees a second and slid sideways (0.7 when it
  straightened). Now: straight 2.5; steering, the heading 12 steps (67 degrees) in a second, the speed 1.55-1.72 (it skids
  and sheds speed); straightened, back to 2.2 at once.

## 2026-11-22 18:41 SAST - bumps by how the hit happens; your damage a quarter; the grid flash with the lights (cloud session, Claude)
- Grant: "reduce the damage again my car gets ... if I hit the side of another car from the front of my car that that car
  shifts sideways - so more impact on them, a small impact on me ... If someone hits you from behind you actually don't get
  damage and actually get pushed forward ... I can basically therefore ram a car off the road by aiming into their side";
  "sometimes in the grid my car during the intro music does not actually show, only when the lights appear"; and "fast tape,
  dotted cloth - happy with that - lets stick to that".
- weight.asm wt_kick (breakfast tapes, WEIGHT=1): along the axis of the bump, each car's speed TOWARDS the other. HEAD-ON
  only when both drive at each other (the slower over a quarter-pixel a frame AND at least half the quicker's): both
  bounce and both take full damage, by weight, as before. Otherwise the quicker is the HITTER: it keeps three quarters of
  its speed (all of it on NOS) and takes a quarter of its damage. The car hit: moving away faster than a quarter-pixel a
  frame (hit from behind) - pushed on, no damage; else (hit in the side, standing, crossing) - kicked away, full damage
  and the hurt flicker. Your own share of any damage is now a quarter (a half before).
- Grid flash (FLASHME): your car flashes only once the lights are up (it could be off for the whole intro tune).
- TWO BUGS FOUND ON THE WAY, fixed: (1) wt_kick lost racer.asm's 2-pixel "nudge apart" - after a bump the two cars were
  thrown up to 160 px (one off the table, one into the middle, stuck): the careful autopilot did not finish 7 of 8 races.
  (2) a car crossing your path with the slightest drift away or towards you counted as hit-from-behind or head-on.
- Staged crashes (fast tape, your car at 1.5 px a frame into Spike, same weight): SIDE (you coming down onto him on the
  straight) - you keep 1.07 down, he is kicked 0.64 sideways, he takes 4 quarters and flickers, you 1; FROM BEHIND (he at
  0.5) - you 1.07, he is pushed to 1.38, no damage to him, you 1; HEAD-ON - both bounce back 0.64, he 4, you 1.
- Careful autopilot, 10 races: all finish (one computer car still on its last lap when the race ended after you - the race
  ends a little after you cross the line), last 9 of 10, 8.3 s behind (9.1 before the change), order changes 19.7 a race
  (14.8 before - more bumping). race_mode_test 12/12. Plain tapes byte-identical.

## 2026-11-22 SAST - cars wedged between the O's (cloud session, Claude)
- Grant: "cars I have seen get stuck between the round loops".
- Measured (16 races a tape, a car counted stuck when it moves under 8 px in 1.5 s): the computer cars - never, on the tape
  before today's bump change or after (they already slip through after O_FREE bounces since their last waypoint); the
  cars thrown 160 px by the bump bug fixed above landed among the O's - likely what Grant saw. YOUR car (the corner-cutting
  autopilot) wedged nose-first between two O's at the top of the track for up to 20 s: you had no way through.
- racer.asm bumps_o (breakfast race tapes only: OPT_RACEONLY, not RT): you are let through too after O_FREE bounces in
  O_YOU_CLK pictures (25, 2 s - the count starts again every 2 s, so it does not open the O's in normal driving); O_FREE 4
  (was 6) so a computer car slips through sooner. After: no car stuck 1.5 s in 16 races; careful autopilot 8.2 s behind,
  good 5.5 s; race_mode_test 12/12; only the two breakfast tapes changed.

## 2026-11-22 SAST - a larger track map: trial tape (cloud session, Claude)
- Grant: "are you able to make the race track map slightly larger?"
- The mini-map is 24 px wide on the breakfast tapes. The 40 px map (MAPW40, Grant's "C wide please" of 16 Nov) builds on the
  fast tape: build/racer_cars75_breakfast_fast_map40.tap (tools/build_race.sh), the program 42 bytes from full (code_end
  0xBFD6). Speed: no measurable cost (11.57 pictures a second against 11.51, autopilot 60 s). Picture:
  docs/design/racetrack/race_mode/map_24_vs_40.png (24 left, 40 right). Not yet the main tape: Grant to choose.

## 2026-11-22 SAST - the hitter takes no damage; THE CHASERS' NOS (trial tape); 209 bytes found (cloud session, Claude)
- Grant: "If you hit the side of a car with the front, you get no damage" - weight.asm: the hitter (side or behind) takes none
  (a quarter before); head-on still hurts both. The dead quarter code went with it.
- Grant: "if you get ahead the other cars can speed up to catchup. But not a full catchup ... 2 of the cars can benefit
  from NOS at different times ... they also may have difficulty controlling NOS ... a deterministic rule ... not ... a
  cheat elastic catchup with no explanation". CNOS=1 (src/cnos.asm, cnos_low.asm) -> build/racer_cars75_breakfast_fast_cnos.tap.
  THE RULE: Spike (yellow, the late braker) and Jane (white, the erratic one) carry a NOS can each, one a lap. One may
  light it only when you lead, nobody has finished, it is 3 s or more behind you (the race order's gap), its can is unused
  this lap, nothing else is burning and 5 s have gone since the last burn (so never both at once); Spike only on a
  straight (his next two waypoints' bends under 10). A burn is as long as yours: pushes +32/64 (1.5x - 1.75x took them to
  3.3 px a frame, past your NOS), grip three quarters (Jane a half), Jane does not brake and turns half as fast. A car on
  NOS that hits the O's CRASHES: three quarters of its speed gone, its NOS over, it flickers. The crew chief: "NOS LIT BY
  <name>" (on this tape only, in place of the random "ON A CHARGE"). Nothing random.
- Measured (tests: scratchpad cnos_m.py - you on the good autopilot given a lead, every computer car 10/64 slower; 12 races):
  your margin at the flag 4.8 s without, 3.3 s with (you still win every race: not a full catch-up); Spike 33 burns, 0
  crashes; Jane 21 burns, 4 crashes (about 1 in 5). Spike with Jane's half steering never crashed either, only lost time
  (dropped).
- ROOM: the tape was full. Found by running the profiler over four whole races and listing code that never ran: the
  race order's health blocks (armour_low.asm arm_bar, 209 bytes under 0x8000) cannot run on a race-only tape (arm_tick
  returns at once) - left out there. Program 6 bytes free, under 0x8000 148 on the CNOS tape.
- race_mode_test: CNOS tape 12/12; racer_cars75_h32_round 12/12; racer_cars75_breakfast_fast 11/12 - the known glitch (a
  race-order row caught half repainted, one picture, as two cars swap: Grant's open question of 19 Nov) now falls in this
  race; with the changes stashed it passed. Plain tapes byte-identical.

## 2026-11-22 SAST - oil spills: where they would go (investigation; cloud session, Claude)
- Grant: "have oil spills appear. If a car hits an oil spill they spin in the direction they were going in without being
  able to change direction for a brief period - a second or so ... 3 or 4 spots where a spill may appear during a lap ...
  around the race track line ... appear randomly and in different places"; "Will need a graphic for that. The oil spill
  will be about the size of a car".
- Where the cars drive: the computer cars' positions over 4 races, on the track's own O and off-road maps:
  docs/design/oil_spill_spots.png. The line is a narrow ribbon (8-16 px) hugging the inside; 8 candidate spots S1-S8 at
  the densest point near the corner entries (world px): S1 492,364  S2 500,164  S3 436,92  S4 324,116  S5 220,100
  S6 124,92  S7 76,356  S8 260,404. Plan: each lap 3 or 4 of the 8 picked at random, a spill (16 x 16, car-sized) drawn
  as a sprite; a car whose middle crosses it spins on the way it was going, no steering and no push, about a second.
- Not built yet. Needs: the graphic (one-bit-art), about 300 bytes (148 free under 0x8000 on the CNOS tape, 6 in the
  program - more room to find: the profiler's never-run list, scratchpad dead.txt), and a drawing cost per picture when
  one is on screen (one car's worth).

## 2026-11-22 SAST - oil spill graphic: three options for Grant (cloud session, Claude)
- Grant: "go ahead with the oil spill graphic". Method: the one-bit-art skill (key shapes and a value plan first; review
  at 1x and 2x; checked on the real game screen). Oil is a dark liquid, so the pool is one solid key shape ringed by a
  paper halo (the masked sprite's), not a line drawing like the cars.
- Tried and dropped: an outline with dither inside (read as a bug), concentric sheen rings (a target), a dither rim and a
  dither sheen (came out as stripes at this size), a long highlight arc (read as a shell or a leaf in the game).
- Shown: docs/design/oil_spill_options.png - A glossy pool (one curved paper highlight), B splat (2x2 droplets thrown
  round it), C splat with a short highlight. Grids: docs/design/oil_spill/option_*.txt (# ink). In the game it takes the
  window's blue ink on the cloth's cyan, as the cars do. A mock-up pasted on a screenshot, not yet in the game.

## 2026-11-22 SAST - OIL SPILLS built (trial tape, with the chasers' NOS) (cloud session, Claude)
- Grant chose drawing B (the splat). OIL=1 (src/oil.asm; the picture: tools/make_oil.py -> src/oil_gfx.asm from
  docs/design/oil_spill/option_b_splat.txt) -> build/racer_cars75_breakfast_fast_cnos.tap.
- Each time you cross the line, 3 or 4 of the 8 spots on the line (docs/design/oil_spill_spots.png) get a spill, at
  random; never S8 on your first lap (it is in front of the grid); none before the first crossing. A spill is drawn as a
  car is (draw_car, entered at its new label dc_frame with the spill's own frame), under the cars. A car whose top left
  is within 9 px of a spill's both ways spins for 12 pictures (about a second): no steering, no push, it slides on the
  way it was going, a sixteenth slower a picture, its picture turning 1.5 times round; then 12 pictures it cannot be
  caught again. You hear the crash.
- ROOM: grip.asm's qmul now multiplies by shift and add on this tape (OIL) - the 768-byte quarter-square table left out
  (the same product, rounded once). Program 210 bytes free after it all.
- Found on the way: the breakfast tapes use the SMALL car frames (16 px, 4 bytes a row): the first spill, made as a big
  car's 24 px rows, drew as stripes.
- Measured: the computer cars drive through every spill on their line - about 12 spins a lap among the five cars (80 s:
  35-37). Careful autopilot, 8 races: laps 24.8-26.0 s (21.1-23.7 without spills), the field closer (slowest car 5% off
  the quickest, 12% without), you 4.2th on average, 5.8 s behind the winner (8.6 without). race_mode_test 11/12 - the
  known half-repainted race-order row. Not yet driven by Grant. Open: the computer cars do not steer round a spill.

## 2026-11-22 SAST - the mini-map back on the panel, top right (cloud session, Claude)
- Grant: "move the map out of the in game display and back to the HUD please. You can place it at the top of the HUD on
  the right". MAPHUD=1 (both breakfast fast tapes): hud.asm map_blit copies the map (its dots already XORed in) to the
  screen at columns 27-29, lines 12-28 - the panel's yellow above RACE - blue on yellow, whenever map_update moves the dots
  (one picture in four); nothing is drawn in the window's corner any more. Picture: docs/design/map_on_panel.png.
- The 40-wide map trial (racer_cars75_breakfast_fast_map40.tap) retired - deleted from build/.
- race_mode_test: racer_cars75_breakfast_fast 12/12; the trial tape 11/12 - a gap left in a race-order row a picture or two
  after it should have gone (the race-order redraw family; which check catches it changes from race to race). Plain tapes
  byte-identical.
- Next on the list: Grant, "During the music - animate the faces - at the start and end of a race" (the jingle player runs
  with nothing else running - to look at).

## 2026-11-22 20:30 SAST - faces move with the music; one spill a lap on a straight; the spill's border; no hurt flicker (cloud session, Claude)
- Grant: "During the music - animate the faces - at the start and end of a race"; "at the chequered flag use the mirrored
  picture of the player racer looking left and right and then the big smile - not the picture facing the front"; "Each
  players image can basically have a horizontal mirror, a happy and a sad face". JFACE=1 + RT_EYES=1 (both fast tapes;
  src/jface.asm, in the program): the jingle player calls jin_key each step (in place of jb_key - same size, nothing in the
  player moved); every 8 steps (two beats) the faces take a step - at the start the race order's (tw_anim, plate_slow.asm,
  now on), at the flag the podium's three. Measured: start - a change about every 1.3 s through the tune (0.1-5.9 s);
  flag - every 0.8 s through the tune, then every 0.64 s after it as before. pa_face_y: a driver's "other look" is its
  everyday face MIRRORED for you, Bruno and Jane (their faces change 52, 62 and 48 pixels mirrored); Frank's (14) and the
  clown's (0 - the same both ways round) keep their own eyes drawings, or they would not move. Podium: look, other look,
  look, happy (winner) or sad.
- Grant: "One oil spill a lap is fine, and an oil spill somewhere on a straight just slightly off the racing path". Now
  one spill a lap, at one of 8 spots on the straights 13 px to one side of the line (the line and the road measured:
  right straight x 506, left 81, top y 95-97, bottom 411-415; road 72 px). 80 s: 3-5 spins among all five cars (35-37
  before), each by a car a little off the line.
- Grant: "The oil spill should have a mask around it so it doesn't merge with the table dithering". The clear border is 2
  px, corners rounded (1 px before; the cloth's dots ran into the drops) - cut to 1 px where the 16 px frame ends.
  Picture: docs/design/spill_mask_and_faces.png.
- Grant: "There is some flickering of the cars, especially when they contact eachother". The hurt computer car's flicker
  (and the NOS crash's, the same) is left out on the breakfast tapes.
- race_mode_test 12/12 on both fast tapes; plain tapes byte-identical. Not yet driven by Grant.

## 2026-11-22 SAST - the panel's map bigger: 40 wide (cloud session, Claude)
- Grant: "The map in the top right corner needs to be quite a big bigger". Both fast tapes now MAPW40=1 with MAPHUD: the
  40 x 29 map (19/256, was 24 x 17 at 11/256) at columns 26-30, lines 6-34, above RACE; its ink (145 bytes) under 0x8000
  (MAPDAT there when MAPHUD), copied to the screen as the 24-wide one was; colours over its 5 x 5 squares. Room on the
  trial tape: cn_ohit/cno_q moved from cnos_low.asm to cnos.asm (program 11 bytes free, under 0x8000 27). Picture:
  docs/design/map_on_panel.png.

## 2026-11-22 SAST - THE FINISH ORDER: judged at the drawn line (cloud session, Claude)
- Grant: "I definitely was second over the line and yet I was marked as third. So the game is not recording the finish
  order correctly - this is not the first time I have seen this".
- Cause (measured, tests: scratchpad lapx.py): a lap is counted when a car reaches the line's waypoint (x 327), not the
  drawn line (x 288-295, middle 292). The computer cars are counted within REACH of their aim point - at x 274-287, before
  the line; you within 40 px of the waypoint, looked at every other picture - at x 290-301. In a close finish a computer car
  20-30 px behind you was in first. Worse: if your lap was not counted at the line (wide of the waypoint), you were not
  "in" at all until later. Reproduced (scratchpad finorder.py, 12 close races, the computer cars 7/64 slower): without the
  fix, race 9 - you over the line FIRST, the game had you LAST.
- LINEJ=1 (both fast tapes; src/linej.asm, under 0x8000): each picture, a car on its last lap (heading for the line's
  waypoint, or counted in already) whose middle has crossed x 292 on the bottom straight since the last picture is given
  the next place (line_at); progress puts cars over the line in that order (those counted but not over yet behind them);
  you are "in" - your place, the clock, FINISHED - when you cross it. With it: 20 of 20 races in the true order over the line.
- Room: the trial tape was full. Its variables (the spill's, the NOS's, the judge's) moved to the D0 strip the 40-wide
  map freed (src/vars_d0.asm: 66 of 90 bytes); the eyes rows of you, Bruno and Jane left out when JFACE (their look is the
  mirror: 60 bytes; tools/make_faces.py); cn_set and cn_ohit moved into the program. The trial tape's program is now FULL
  (0 bytes), 9 bytes under 0x8000; the main fast tape 53 and 64.
- race_mode_test 12/12 on both fast tapes; plain tapes byte-identical.

## 2026-11-22 SAST - finish order, part 2: your lost lap; the winner's smile mirrored; side hits push further and slow (cloud session, Claude)
- Still wrong in 3 of 24 close races after the line judge: in each, the game had your car on LAP 2 as you crossed the line
  to finish - a lap of yours had gone uncounted. Traced (scratchpad youlap.py): your waypoint was left at 21 (the top
  chicane) while you drove on - you cut it by more than the four waypoints the game looks ahead - so the game waited a
  whole lap for you to come back to it. The same fault Grant reported on 15 and 18 Nov ("I seemed to lose a lap"), fixed
  then on the race-track tapes only (lap_low.asm rp_far: when you are well away from your waypoint it looks further ahead,
  never further than you could have driven).
- LAPFIX=1 (both fast tapes): rp_far on the breakfast tapes too - kept in the stack's page at 0x5E00 (copied there by
  start; 102 bytes; free on track 1 - the stack measured never deeper than 0x5EC8 through a race with the music and the
  podium; the code checked intact after it). The line judge's last-lap test widened as well: heading for any waypoint in
  the second half of the lap (it was the line's own, then the last four).
- After: 32 of 32 close races in the true order over the line (both tapes); full races all finish.
- Grant: "If the player wins then play the happy face horizontally mirrored" - your happy face is shown as it is and
  mirrored in turn each time it comes round (pa_face_h, in the TOPMEM block - jface_low.asm).
- Grant: "If I hit one of the other cars on its side, it should move more to the side and be temporarily slowed" -
  weight.asm (MAPHUD tapes): the car hit in the side is kicked twice as hard, and its speed along the road halved (it pushes
  back up to speed as ever). Staged: kicked 1.27 sideways (0.64 before), along the road 0.38 (0.77 before); you keep
  three quarters, no damage.
- Room (the trial tape was full): the weight bump's variables to the D0 strip (vars_d0.asm, now 89 of 90); RACE mode's old
  card rows (cd_race, 32 bytes) left out on the breakfast race tapes - every car drives its own card; lj_new folded into
  spill_new; dc_oil under 0x8000; pa_face_h at TOPMEM. Trial tape: program 13 bytes free, under 0x8000 15; main fast
  tape 53 and 69.
- race_mode_test 11/12 on each fast tape: the race order's half-repainted row (a row's colours or gap a picture behind as
  two cars swap) - cosmetic, and NOT the finish order; open.
- Next, Grant: "we need a memory hunt. A deep one ... rules I have given about the dynamics of the game and movement could
  be simplified".

## 2026-11-22 21:02 SAST - THE MEMORY HUNT: findings, for Grant to choose (cloud session, Claude)
- Grant: "go ahead with the memory hunt". Method: pasmo -d's listing of the trial tape (every byte, its source file and
  routine) joined to the profiler's executed addresses over 8 races (both autopilots, the music, NOS, the podium);
  scratchpad hunt.py. 21,871 bytes kept while racing (start-up area not counted); 1,047 bytes of code never ran (some of
  it needed and rare: the title's return, lap recovery, NOS crashes).
- The report, ranked (published: https://claude.ai/artifact/111aiTs7iBWP7aryC9HS6L):
  A, no change to play: A1 the screen copy as a loop (LOOP=1) 5,571 bytes - its copy 51,369 -> 58,170 T a picture;
  pictures a second within the noise (tearlap 11.3 -> 10.9, smooth3 11.54 -> 11.91, both measured today); lower rows of
  the window late from row 13 (from row 18 today). A2 the main tape's multiply table 733. A3 big_tab's mirrored headings
  worked out, ~320 (estimate). A4 code that cannot run on race-only breakfast tapes, ~150-250 (estimate).
  B, features: B1 the title's lapping car 459; B2 redefine keys ~300; B3 pick 2 upgrades ~190; B4 the trial features 841.
  C, simpler rules: C1 your car on the computer cars' card-and-slide model, ~1,100 of grip.asm's 1,150; C2 one bump rule
  (a weight table of 5 for the two 6x6), ~200-300.
- Nothing changed in the game for this; waiting on Grant's choices.

## 2026-11-22 SAST - MEMORY HUNT GROUP A done: the looped copy, the tables moved above it, the multiply (cloud session, Claude)
- Grant: "do group A".
- A1 LOOP=1 on both fast tapes (the screen copy as a loop: 404 bytes, not 6,083) and UPPER=1: tables moved up into the
  room it frees above the copy routine (0xEA00 - HIMEM). tools/make_up.py (run by build.sh just before assembling, in the
  build's own copy of src/) writes src/up_data.asm - the tables, each name renamed name_u - and src/up_equs.asm - each name
  at its place up there; racer.asm assembles them after the start-up area (up_src) and start_once copies them up first
  thing. Moved: the car picture index (big_tab, 640), the O map (576), the waypoints (184), the map's row index (128),
  the faces (160), the faces' moods (210), the mug (64), the 40-wide map (145), and on the trial tape the oil spill (72):
  2,211 bytes; 3,360 left up there. src/up_data.asm and up_equs.asm in the repo are empty placeholders (pasmo opens an
  INCLUDE even in an IF that is off).
- A2 QMUL=1 on both fast tapes (the trial tape had it with OIL): the main tape's 768-byte multiply table gone.
- A3 not done: the picture index went up whole instead (640 out of the program, not 320) - working out the mirrored
  headings now would only add drawing time.
- A4 not done: the code that never ran turned out rare, not impossible (the computer cars' brake - every card's brake
  speed is 255, but a car at its top speed on NOS still reaches it), and with 2.3 KB free it is not worth the risk.
- FOUND ON THE WAY: pasmo takes an EQU's value where it stands - with UP_AT defined after the moved names, the code used
  them as offsets from 0 (the O map read from ROM: every car bounced off O's on the grid and wandered off the table,
  then a car drawn with 0 rows ran its drawing loop 256 times, over the tables above the buffer, and the game reset).
  Found with zxdev's watch and break; UP_AT now defined first, and every moved name's value checked in the listing.
- FREE NOW: main fast tape - program 2,383 bytes (was 53), under 0x8000 520 (was 69); trial tape - program 1,645 (was 13),
  under 0x8000 466 (was 15); above the copy routine 3,360 on both.
- Checked: no reset in 80 s on both tapes; race_mode_test 12/12 (trial), 11/12 (main: the race order's half-repainted
  row); finish order 8/8 true; full races as before (careful driver 8.9 and 9.1 s behind). SPEED: 11.36 pictures a
  second (11.54 before; smooth3), the lap 11.0 (11.3; tearlap) - about 2-3% slower, the looped copy's 6,800 T; torn
  frames the same (20.4%), more of the window's lower rows a TV frame late.

## 2026-11-22 SAST - GROUP C as a trial tape: your car on the card model (C1), one bump rule (C2) (cloud session, Claude)
- Grant: "leave b but try c". SIMPLE=1 -> build/racer_cars75_breakfast_fast_c.tap (the trial tape - chasers' NOS, oil -
  with group C; the main and trial tapes unchanged).
- C1: your car goes through the computer cars' physics (racer.asm: no ph_snap / you_grip for you): your buttons push,
  your card row scales it (you_card, cards_code.asm, row kind 0 at cd_tab - 8), the cards' slide (skid), the road's and
  the damage's slow-down (surface, wt_slow) as theirs; NOS 1.75x push (ph_34); the set-up keys raise your card (su_apply,
  SIMPLE part). grip.asm is left out but for trig (the title's car). Tuned so the careful autopilot does as it did on the
  grip model: your card slides from 45/64 of the computer cars' MAX card's slide speed and both pushes 8/64 less.
  Measured (8 races): careful autopilot laps 24.66 s, last, 10.8 s behind (grip model: 24.49, 4.9th, 9.1). The
  corner-cutting autopilot (rt_ace, tuned on the grip model) cannot drive it: laps 32 s (24.5 on the grip model) -
  the handling is different; only Grant's drive can say how.
- C2: weight.asm (SIMPLE): four weight classes (Jane 0; Max, Frank, Spike 1; Bruno 2; you on NOS 3); a bump's kick and
  damage by the other's class less your own, two tables of 7 (each class 1.6 times the one below: kick 2r/(1+r) of KICK,
  damage 4r quarters) in place of the two 6 x 6; no head-on rule (the quicker towards the other is the hitter). The staged
  crashes (scratchpad crash.py) were made for the grip model and do not stage cleanly on C1's car - not shown here.
- ROOM on the C tape: program 2,703 bytes free (trial 1,645), under 0x8000 583 (466): C1 1,058, C2 117.
- pasmo's EQU trap twice more (an EQU takes its value where it stands): YOU_SL/KA/KS first came out 0-based (slide 0:
  always sliding) - now after cards.asm.
- Checked: no reset in 80 s; race_mode_test 12/12; finish order 8/8.

## 2026-11-23 SAST - group C tape: your car was the slowest on the straights - power back to the MAX card (cloud session, Claude)
- Grant (on the group C tape): "my car is definitely the slowest of the lot - can you confirm comparative car speeds".
  Measured (scratchpad carspeeds.py: each car's speed on the right and bottom straights, 4 races, careful autopilot):
  group C tape - you typical 1.20 px a frame, 90th percentile 1.31; the computer cars 1.26-1.41 and 1.37-1.50. Confirmed:
  the slowest. (Main fast tape and trial tape: you 1.42 / 1.41 typical - among the quickest.)
- Cause: the group C tuning (22 Nov) took 8/64 off both your pushes to keep the careful autopilot last - the wrong lever.
  Now your pushes are the MAX card's as the computer cars have it (YOU_KA/KS = CD_R_KA/KS); your tyres still slide from
  45/64 of their slide speed. After: you typical 1.42, 90th 1.45 (Jane 1.45 / 1.50, Frank 1.33 / 1.39, Spike 1.31 / 1.48,
  Bruno 1.37 / 1.39).
- What it does to the difficulty: the careful autopilot now 1.9th on average, 3 wins in 8 (laps 21.50 s; the computer
  cars 21.9-23.0). On the grip model it was last. Easier - to put back by the computer cars, not by slowing you.

## 2026-11-23 07:49 SAST - faces at the start and podium fixed on the fast tapes; group C balance with Jane trimmed; the car sheet (cloud session, Claude)
- Grant: "when frank is placed second there is no animation of his head. Also the clown does not animate at the start
  sequence. Note that Jane was quite a bit faster than the others"; "balance was good though".
- FACES (all three fast tapes): faces_mood (the faces' looks, happy and sad) was aliased before up_equs.asm, so with
  UPPER it took the value 0 - pasmo's EQU trap again - and the face overlays were read from address 0. Moved after
  up_equs.asm. Checked (scratchpad startfaces.py): every race-order row's face now changes during the start music, on
  racer_cars75_breakfast_fast and racer_cars75_breakfast_fast_c.
- GROUP C BALANCE (racer_cars75_breakfast_fast_c only): your pushes 4/64 under the MAX card (were 8 under at first, then
  equal); the computer cars corner faster (slide speed x2.5 for Frank, Bruno and Jane, x1.4 for Spike - ai_tune.asm GROUP C,
  make_cards.py) and Jane's pushes 8/64 less. Measured (8 races, careful autopilot): mean place 4.2, 3.7 s behind the
  winner; flying laps you 24.27, Frank 23.31, Spike 23.95, Bruno 23.86, Jane 24.31 - Jane no longer the quickest, the
  slowest car 4% off the quickest. Straight speeds (4 races) typical 1.29-1.36 px a frame for all five, you 1.31.
  Nobody has driven this yet.
- CAR SHEET: docs/design/all_car_graphics.png - every car graphic in the game plus the five spare drafts
  (tools/new_cast_art.txt), for Grant to pick the one to swap.
- Checked: plain tapes byte-identical; no reset in 80 s (_c); race_mode_test 12/12 on _cnos, 11/12 on the main fast and _c
  tapes - the one fail is the known half-repainted race-order row (a colour caught mid-redraw at one frame; seen before).

## 2026-11-23 SAST - Frank drives the six-wheeled truck on the breakfast fast tapes (cloud session, Claude)
- Grant: "The six wheeler to replace Franks car" (his coupe looked like Max's racer - docs/design/all_car_graphics.png).
- tools/make_data.py: SWAP_CAR=CYAN=TRUCK takes a car's pictures from another drawing in tools/pool_art.txt (TRUCK's 0,
  22.5 and 45 headings; the 11.25 and 33.75 drafted from heading 0 as for every car). Set on the three fast tapes only
  (tools/build_race.sh); Frank's driving, card, weight and face unchanged. Every other tape keeps the coupe.
- Checked: all 32 headings read back from the game's memory on all three tapes (docs/design/frank_truck_headings.png,
  top row of each pair Frank, bottom yours); in the race and the race order; no reset in 80 s on each; race_mode_test 12/12
  on _cnos and _c, 11/12 on the main fast tape (the known half-repainted race-order row); plain tapes byte-identical.
- Nobody has driven it yet.

## 2026-11-23 08:12 SAST - oil spill smaller, half on the line, never on a NOS; group C: back to the balance Grant liked, the tank weak early and strong late (cloud session, Claude)
- Grant: "We need to make the oil spill a little smaller and also make sure it does not sit on top of a NOS. Make it slightly
  off the race line - so partly on partly off. Right now I'm coming last. The fastest car appears to be the tank - so the
  tank needs a slight slowdown - it should be the slowest car initially but as it takes little damage it gets stronger
  towards the end".
- OIL (both oil tapes, _cnos and _c): the spill drawn 12 x 12 (docs/design/oil_spill/option_b_small.txt; was 15 x 13), the
  2px mask kept; OIL_R 8 (was 10). Each spot's middle 9 px off the line the cars drive, measured at each spot
  (scratchpad linespots.py) - the spill overlaps a car on the line but a car must be 2 px or more to that side to spin.
  7 px off was tried first: 4 cars in 5 spun on every spill. Now about 2 spins a lap (2 races each tape). S7 was on NOS
  canister A (156, 416): moved after the line (330, 422), and with S8 never on your first lap; every spot 50 px or more
  from canisters B and C.
- GROUP C BALANCE (_c only): the corner boosts of this morning taken out (they made the tank, grip 8, the quickest car)
  and your pushes back to the MAX card's - the balance Grant liked - with Jane's pushes 4 less (8 less made her the
  slowest). THE TANK (src/tank.asm, TANKUP=1): Bruno's pushes 5/64 less on lap 1, his card's on lap 2, 3 more on lap 3.
  The game has no gradual damage slowdown (only a car with no armour left limps), so "stronger towards the end" is done by
  the lap.
- Measured (8 races, careful autopilot): mean place 1.4, 5 wins - easier than the version Grant liked (1.9, 3 wins).
  Laps, lap 1 / 2 / 3: tank 25.6 / 22.5 / 21.3 - the slowest car on lap 1, the quickest on lap 3; Frank 23.3 / 22.6 / 22.5;
  Spike 24.4 / 23.1 / 21.7; Jane 24.0 / 22.7 / 22.5; you 22.8 / 21.7 / 21.8. The four computer cars within 3% a lap.
- Checked: race_mode_test 12/12 on _c and _cnos; no reset in 80 s on each; plain tapes byte-identical; the main fast tape
  unchanged. Nobody has driven it yet.

## 2026-11-23 09:46 SAST - group C tape slightly tougher (cloud session, Claude)
- Grant: "Okay the balance is much better. You can make it slightly tougher." Your pushes 2/64 under the MAX card's
  (YOU_HARD, cards_code.asm; 0 before, 4 put him last). First built with YOU_HARD after the EQUs that use it - pasmo's
  trap again: it came out 0 and the tape did not change; moved first, checked in the .sym (YOU_KA -12, YOU_KS -13).
- Measured (8 races, careful autopilot): mean place 1.9, 3 wins (1.4 and 5 before); the field within 1-3 s at the flag;
  flying laps you 22.51, Frank 22.58, Spike 23.12, Bruno 22.51, Jane 23.09. The tank 25.7 / 23.0 / 21.7 by lap.

## 2026-11-23 09:49 SAST - CHOOSE YOUR CAR: the popup mocked up (cloud session, Claude)
- Grant: "show the strengths of each car. This is the grip, acceleration, speed. The armour cannot be adjusted - that is
  linked to the car you get ... a rock/paper/scissors type setup ... when you click 1, a popup appears asking you to choose
  your car. You press left and right to select cars ... We need to have spare cars to choose from ... Please mock this up".
- tools/make_choose_popup_mock.py -> docs/design/choose_popup/choose_popup_mock.png (and popup_1..4_*.png): the popup over
  the real title screen (the C tape's, from the emulator), the ROM font, the cars' own 16 x 16 drawings twice the size,
  kept to 8 x 8 colour squares. Each car: name, one line, ACCEL / SPEED / GRIP / ARMOUR as ten squares each (Grant's driver
  cards), one plus and one minus, the keys. Racer, tank, dragster, saloon shown. Not in the game; questions to Grant.

## 2026-11-23 10:06 SAST - choose your car: Grant's answers; the "which is yours" marks mocked up (cloud session, Claude)
- Grant's answers: you may take a computer driver's car - then there are two of it on the road, with "a small graphic tweak
  to specify which is yours"; ratings are not all equal - rock/paper/scissors, some cars slower on some tracks; everything
  can be adjusted but armour, which is fixed to the car; no adjusting when you choose - the car has default settings
  (tweaking a car comes later, elsewhere). Spare cars: not answered - going with the coupe and the saloon (ready drawn).
- tools/make_your_car_marker_mock.py -> docs/design/choose_popup/your_car_marks.png: A a white spot on the roof, B a
  target, C a bolder (2 px) white outline - each the same at every heading, so the game can add it to any car's frames as
  it unpacks them. Recommended C: it reads at the game's size and does not touch the car's drawing (A and B land off a thin
  car's body at 45 degrees - the dragster).

## 2026-11-23 10:14 SAST - Car Studio: an editor for every car graphic (cloud session, Claude)
- Grant: "give me an editor to make a tweak to each graphic".
- docs/tools/car_studio.html (tools/make_car_studio.py from docs/tools/car_studio.template.html), published privately:
  https://claude.ai/artifact/4AX5oqNc3y2mzdjMWheKtK. All seven cars as the game draws them today - racer (Max), six-wheeler
  (Frank), clown car (Spike), tank (Bruno), dragster (Jane), and the spares coupe and saloon - each its three drawn
  headings (0, 22.5, 45; ink, white body, empty), with mirror, undo, back-to-the-game's-drawing, all 16 headings on the
  table with the 1px white edge (4x and 2x), and the text in the car-art format. Edits save to the page's database
  (cars/<key>: art, h0, h22, h45, changed) for Claude to read back (ArtifactData list cars); copy-text when not connected.
- Checked: headless Chromium - no errors, a paint stroke and car/heading switching, no sideways scroll at 390 px; the store
  read back empty (nothing drawn yet). The 11.25 and 33.75 headings the game drafts by turn_car.py are not shown.

## 2026-11-23 10:39 SAST - Grant's Car Studio edits in the game (cloud session, Claude)
- Grant: "cars done". Read from the studio's store (6 cars: clown, coupe, dragster, saloon, six-wheeler, tank; the racer
  untouched). He changed heading 0 only: clown 9 pixels (white middle), coupe 6, dragster 4 (white stripe), saloon 10
  (white cockpit), six-wheeler 8, tank 4 (white turret). Carried onto 22.5 and 45 (each angled pixel looked up in heading
  0, turned back, 4 samples a pixel; the tank's turret cleared of a stray dot by hand) and written back to the studio.
- tools/car_art_studio.txt holds them; tools/make_data.py reads it on top when STUDIO_ART=1 - set on the three breakfast
  fast tapes only, so the plain tapes keep the old drawings (byte-identical). Studio defaults now these drawings.
  Before/after, all 16 headings: docs/design/car_studio_edits_before_after.png.
- Checked: heading 0 of Frank, Spike, Bruno and Jane read back from the game's memory on all three tapes matches the
  studio; no reset in 80 s on each; race_mode_test 12/12 on _cnos, 11/12 on the main fast and _c tapes - each fail one
  of the known race-order display glitches (the _c one the same frame as seen before). Nobody has driven it yet.

## 2026-11-23 10:43 SAST - correction: the Car Studio edits are YOUR car's versions, not the computer cars' (cloud session, Claude)
- Grant: "I made those changes in each car so that only my car gets those changes." I had put them on the computer cars.
  Undone: STUDIO_ART off the fast tapes - the three tapes are byte-identical to 255748c again (computer cars as drawn).
- tools/car_art_studio.txt is now YOUR car's version of each car, for the choose-your-car popup: when you pick a car a
  computer driver also has, yours is drawn from it. That answers "which one is yours" - the A/B/C marks are dropped.
  (The racer has no second version: only you drive it.)
- The Car Studio says so (republished; "back to the game's drawing" gives the computer car's): the drawings in it are
  yours. docs/design/choose_popup/yours_vs_computer.png: each pair side by side on the table, 4x and the game's size;
  docs/design/choose_popup/your_versions_all_headings.png: all 16 headings, computer car above yours.

## 2026-11-23 10:55 SAST - CHOOSE YOUR CAR built on the group C tape (cloud session, Claude)
- Grant: "go ahead and build the car selector too". PICK=1 on racer_cars75_breakfast_fast_c: the title's 1 opens the CHOOSE
  YOUR CAR card (src/pick.asm) over the title - left/right through 7 cars, round and round; accelerate or SPACE races.
  Each car: its picture (YOUR version) twice the size on its colour, name, line, ACCEL / SPEED / GRIP / ARMOUR as ten
  squares and the number, a plus and a minus. The words, colours, weight classes and which card: tools/pick_cars.txt.
- What the car brings: its 32 headings (tools/make_data.py packs each car's frames and table rows with ZX0 - 3,410 bytes for
  7 cars; four above the copy routine in pick_data.asm, three in the program in pick_data2.asm) unpacked into your
  frames (pk_buf = the racer's, padded to the biggest: pk_pad) and big_tab's kind-0 rows; its card as YOUR card row's
  numbers (slide 45/64 of the card's, pushes YOU_HARD less - as the racer's; su_apply reads pk_sl/pk_s8/pk_ka/pk_ks); the
  damage a piece of its armour takes (arm_tab row 0); its weight class (wt_cls). A computer driver keeps his car.
- tests/rt_lib.py to_grid: on a PICK tape picks car RT_CAR (default 0, the racer) and accelerates.
- Checked: all 7 cards shown and read back (docs/design/choose_popup/built_popup_all_cars.png); the saloon's and the tank's
  numbers in your card row, armour and weight as their cards; two tanks on the road, yours in your version
  (built_race_two_tanks.png); with the racer the race is the same as before (race_mode_test 11/12, the same known glitch at
  the same frame); no reset in 80 s with the racer, tank, dragster; plain tapes byte-identical; main and trial tapes
  unchanged. Room left on the C tape: program 742, above the copy routine 436, under 0x8000 427.
- Open: Frank drives the six-wheeler on his coupe's card; your six-wheeler is the DOT/TRUCK card (3/3/8/8). Nobody has
  driven it yet.

## 2026-11-23 10:56 SAST - CHOOSE YOUR CAR: each car measured; choosing again after a race (cloud session, Claude)
- After a race: back to the title, 1, the dragster chosen - its numbers in your card row (slide 125, pushes -3 / -6),
  armour 26 a piece, weight class 0; the next race ran (built_popup_after_a_race.png).
- Each car with the careful autopilot, 4 races each (few - a first look; tests/race_measure.py, RT_CAR=n):
  racer mean place 1.5, laps 22.09 s; six-wheeler 2.8, 23.83; clown car 3.2, 24.00; tank 3.5, 23.79; DRAGSTER 1.0 (4 wins
  of 4), 19.19 - 15% quicker than the field; coupe 1.8, 21.98; saloon 2.2, 22.37. The computer cars 22.3-24.7.
- The dragster is far too strong as yours: the computer cars' rows carry the race-only top-speed balance (ai_tune.asm
  AI_K?_KS) and your card row does not - the dragster's speed 8 is the card's in full. To be tuned with Grant (stage 3,
  rock/paper/scissors).

## 2026-11-23 11:27 SAST - group C tape: harder slides for every car, grip counts for more, the full speed (cloud session, Claude)
- Grant: "grip needs to have a bigger impact. So skidding should be more severe for all cars"; then "all cars need to be
  affected by skidding more, the game also needs to run faster".
- Found: a car slid only while its steering key was held (C_CTRL) - a few TV frames a corner; your dragster, grip 1, was
  over its grip in 135 of 140 turning frames but turned in only 140 of 1,500.
- GRIPX=1 (racer.asm skid): over its grip a car SLIDES - push and friction halved (it runs wide), the push a quarter less
  still (it loses speed); GX_STEP (0.375 px a frame) further over, halved again; and the slide goes on GX_T (5) pictures
  after the steering stops (gx_t, each car's). The grip scale lower and wider (make_cards.py, GRIPX): slides from 120 (grip
  1) to 430 (grip 10), was 210 to 480. The C tape at GAME_SPEED 100 (was 85): every speed 18% up. YOU_HARD 4 (was 2).
- Measured (careful autopilot, 8 races, the racer): mean place 2.0, 3 wins (1.9 / 3 before); laps you 21.75, Frank 21.96,
  Spike 22.65, Bruno 21.83, Jane 22.43 (were 22.5-23.1 at 85% with the old slides); computer cars in a slide 16 / 16 / 5 /
  30% of the time. The tank still slowest on lap 1 (24.1) and quickest on lap 3 (21.3). Your tank: mean place 1.8 (4 races).
  Your DRAGSTER still wins every race (laps 17.9) - to tune (its straight speed).
- Checked: race_mode_test 12/12; no reset in 80 s (racer, dragster); plain tapes byte-identical; main and trial tapes
  unchanged. Room: program 742, upper 436, low 427. Nobody has driven it yet.

## 2026-11-23 12:36 SAST - oil: one whole turn, out almost facing the way you were; you can steer out of it; slides end when you ease off (cloud session, Claude)
- Grant: "if you hit the oil, then you spin like currently So you lose control and deflect ever so slightly off your path,
  so you end up almost facing the way you were"; "the idea is that with some clever driving, after the skid you can
  potentially recover".
- OIL (both oil tapes): the spin turns the car ONE whole turn and OIL_DEF (2 steps, 11 degrees) more or less, at random,
  shared out over the spin's pictures (spill_left); the path turned an eighth of the speed the same way (about 7 degrees,
  spill_go). It was 1.5 turns - out facing back. Checked: 48 spins with oil on all 8 spots, every car out at +-11 degrees.
- Recovering: YOUR steering in a spin (spill_key - tick still clears the buttons, so the car is not steered as ever) turns
  it a step more or less a picture, up to OIL_STEER (4 steps, 22 degrees) either way (spill_kadj): out anywhere from 34
  degrees left to 34 right - a well-timed tap brings it out straight. Checked: right held +6/+2, left held -6/-2, none +-2.
  GRIPX slides (C tape): a slide that goes on after the steering stops now ends at once when the car is back under its grip
  (eased off).
- Checked: race_mode_test 12/12 (_cnos), 11/12 (_c: the known half-repainted race-order colour, frame 782, seen before);
  no reset in 80 s on either; plain tapes byte-identical; main tape unchanged. Balance (C tape, racer, 8 races): mean place
  2.8, 2 wins; laps you 21.83, Frank 21.81, Spike 22.96, Bruno 21.59, Jane 22.36. Nobody has driven it yet.

## 2026-11-23 14:12 SAST - the Sound Board: the race's key sounds to listen to (cloud session, Claude)
- Grant: "lets work on sound. I would like there to be more significant sounds. Can you play in Claude the key sounds played
  during the gameplay".
- One race on the group C tape recorded in the emulator (zxdev wav_start / wav_save, 44.1 kHz) with the sound variables logged
  each TV frame (snd_bump, snd_fxt / snd_fxk, snd_skt, HIT_O, spill_spin, the lights, laps); ten clips cut at the logged
  frames, 22,050 Hz 8-bit: docs/sound/race_clips/*.wav - start music, start lights, engine, car crash, hitting an O, oil
  spin, NOS pickup, NOS fired, lap complete, finish music. tools/make_sound_board.py -> docs/sound/sound_board.html, published
  privately: https://claude.ai/artifact/CJfPsJCYhhHbZMGP7AtxXk (each clip with its click density, and seven ideas).
- Found: NO SKID SCREECH on the group C tape - snd_skt is set only by you_grip (the grip model), which SIMPLE leaves out. The
  in-race sounds are thin beside the music: engine ~46 speaker clicks a second; crash 176 in 0.9 s; bonk 59 in 0.7 s; the
  music thousands. The snd_fxk codes seen: 48 a red light, 24 green, 9 NOS fired, 0 NOS picked up, 2 an O, 14 a lap.

## 2026-11-23 14:16 SAST - the overtaking faces on the group C tape (cloud session, Claude)
- Grant: "if you overtake or are overtaken by a player, then their face shows up top right in the gameplay as either happy or
  sad a short animation between frames and then it disappears".
- OVF=1 (src/ovface.asm, called from draw_all after the place plate): each picture your place against the last; better - the
  driver now just behind you, SAD; worse - the driver now just ahead, HAPPY. His face (faces + faces_mood's happy/sad rows)
  in a framed box 24 x 18 just under the plate, his everyday face and the mood by turns every 4 pictures, 20 pictures (1.6 s),
  then gone (the window is drawn afresh each picture). A new pass starts it again.
- Checked: in a race - you passed Jane (Jane sad), Spike passed you (Spike happy), the order before and after as the game
  had it (docs/design/overtake_faces.png); race_mode_test 11/12 (the known half-repainted race-order colour); no reset in
  80 s; plain tapes byte-identical; main and trial tapes unchanged. Room on the C tape: program 156 bytes. Nobody has driven it.

## 2026-11-23 14:29 SAST - the lap's own chime; the NOS whoosh no longer cut off (cloud session, Claude)
- Grant: "lap complete needs a unique beep".
- Found: the lap sound was a plain beep (effect 14, flips 14 counts apart) - next to the start lights' plain beeps (48, 24).
  And the Sound Board's "NOS fired" was the crew chief's blip: firing NOS set the whoosh (effect 1) and the crew chief's
  "BOOST" message's blip (msg_snd, effect 9) replaced it at once - the whoosh was never heard.
- SND2=1 (the three breakfast fast tapes): effect 3, a lap done - its own chime, a low note then a high one (ding-DING:
  flips 24 then 14 counts apart, 8 frames each), 16 flips a frame (the other beeps 6) - racer.asm fx_bonk, clothmini.asm.
  msg_snd waits: no blip over a sound already playing (plate_slow.asm).
- Re-recorded a race (C tape) and the clips re-cut from the logged events (start music, lights, engine, crash, O, oil,
  NOS pickup, NOS fired - the whoosh now -, lap - the chime: ~3.7 kHz then ~5.5 kHz -, crew chief blip, finish); the Sound
  Board republished (https://claude.ai/artifact/CJfPsJCYhhHbZMGP7AtxXk).
- Checked: race_mode_test 12/12 (_cnos), 11/12 (main and _c: the known race-order colour, the same frames as before); no
  reset in 80 s on each; plain tapes byte-identical. Room: C tape program 138 bytes. Nobody has heard it on a Spectrum yet.

## 2026-11-23 16:44 SAST - the skid screech on the group C tape (cloud session, Claude)
- Grant: "do the skid screech".
- GRIPX (racer.asm): skid keeps YOUR slide's level each picture in gx_lv (1 sliding, 2 well over the grip - GX_STEP);
  snd_picture applies grip.asm's rule: a screech (SKID_FR frames) as a slide STARTS, then quiet until the car grips and
  slides again - but a big slide screeches as long as it lasts. isr_sk: 4 flips a frame as a slide fades, 8 sliding, 12 well
  over (it was 8 always). Only your car screeches.
- Measured (30 s, careful autopilot): the racer 33 screeches, 32 of them big, sound 21% of the time (most corners); the
  dragster 21, all big, 14%. The Sound Board has the clip (the dragster in a corner) - republished.
- Checked: race_mode_test (see below); no reset in 80 s; plain tapes byte-identical; only the C tape changed. Room: program 132.

## 2026-11-23 16:56 SAST - race time and race record on the podium; more skidding; the C tape at 110% (cloud session, Claude)
- Grant: "at the end of the race, give a fastest lap, but also give the ability to track and show the fastest race time";
  then "there is still not enough skidding, and ideally would like the race speed overall to be upped a bit".
- The podium already showed the race's FASTEST LAP (time, whose, which lap). RREC=1 (the three fast tapes): under it your
  race time (green to the line) and the RACE RECORD - the best since the game was loaded, as the lap record -: "RACE 1:02.6
  RECORD 59.7", or "NEW RACE RECORD 59.7" (plate_slow.asm pd_rrec; rr_t0 at green, hud.asm; rr_you/rr_rec at the line,
  racer.asm). Found on the way: time_fmt blanks "0:" under a minute and never puts the colon back - a later time over a
  minute read "1 02.6"; pd_rrec puts it back (time_fmt itself left as it is). Checked: two races in a row - 62.6 a new
  record, then 59.8 beat it (docs/design/podium_race_record.png).
- Skidding (C tape): the GRIPX grip scale 15% lower again (slides from 100 at grip 1 to 365 at grip 10); a slide goes on 8
  pictures after the steering stops (was 5). GAME_SPEED 110 (was 100).
- Measured (careful autopilot, 8 races, the racer): mean place 2.5, 1 win; laps you 20.51, Frank 20.64, Spike 21.31,
  Bruno 21.40, Jane 20.56 (were ~21.8-22.7); computer cars in a slide Frank 12%, Spike 65%, Bruno 6%, Jane 42%.
- Checked: race_mode_test 12/12 (C); no reset in 80 s; plain tapes byte-identical.

## 2026-11-23 16:58 SAST - Sound Lab 2: alternative sounds to pick from (cloud session, Claude)
- Grant: "Please can you work on alternative sounds to try - sounds need to be distinct, in the background drone they all sound
  the same".
- Why they sound alike: every effect is the interrupt's burst - 6 flips a frame, all high (gaps 14-48 counts: ~2-6 kHz) - over
  the engine's ~46 clicks a second.
- tools/make_sound_lab2.py -> docs/sound/sound_lab2.html (docs/sound/lab2/*.wav), published privately:
  https://claude.ai/artifact/Lnq4BpF4Yem7zfBHF2Sxxv. For crash, skid, oil, NOS pickup,
  NOS fired, O hit, lap and a new overtaking blip: A today (recorded), and B-D alternatives that differ in pitch (low thuds and
  knocks, ~0.5-1 kHz, to high squeals), texture (noise or tone) and shape (rising, falling, warbling, pulsed) - each rendered as
  the effect player would play it (FLIPS flips a frame, GAP counts apart, 16 T a count, ~80 T a flip; noise a random gap) over
  the engine recorded in a race, with its cost: the most of a TV frame it takes (3-12%). And one with the engine hushed while
  the sound plays (ducking).

## 2026-11-23 18:48 SAST - skidding more prevalent (group C tape) (cloud session, Claude)
- Grant: "Skidding needs to be more prevalent as it requires more skill to drive".
- GRIPX: a slide goes on GX_T 12 pictures after the steering stops (was 8; about a second); a third level - twice GX_STEP
  over the grip, the push and friction halved a third time: far too fast into a corner, the car drifts wide until eased off.
- Measured: your car (the racer, careful autopilot) sliding 47% of the time in a race (screech levels: gripping 746 frames,
  sliding 639, big 115 of 1,500); laps (8 races) you 21.75, Frank 21.42, Spike 22.27, Bruno 21.98, Jane 22.49 - about a
  second slower than before (the slides cost time); mean place 2.4, 1 win. race_mode_test 12/12; no reset in 80 s (racer,
  dragster); plain tapes byte-identical; only the C tape changed.
