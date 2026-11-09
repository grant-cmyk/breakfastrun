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
