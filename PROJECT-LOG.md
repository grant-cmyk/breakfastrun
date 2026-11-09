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
