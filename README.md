# Breakfast Run

A top-down micro-car racer for the ZX Spectrum 48K, written in Z80 assembler
(pasmo). Personal home project - Grant learning to code the Spectrum.
Inspired by the *genre* of Micro Machines / Super Off Road / Super Sprint:
tiny cars, momentum and drift, household tracks. Original game, original art.

## Current build - the race screen
- Keys: **O** left, **P** right, **Q** accelerate (and start, and race again), **A** brake/reverse.
- 3 laps, you and four computer cars. Window 23 x 16 cells on the left; panel: logo, race order
  (each car on its colour, you on red), mini-map (a dot per car, yours blinking). Above the window:
  start lights, GO!, FINAL LAP!, FINISHED nTH. Below: LAP, TIME, BEST lap (time, car, lap).
- Track: chequered kerbs; a breakfast table round it (plate, eggs, toast, juice, bacon, cutlery).
- 16.7 pictures a second where the screen is clear, a steady 12.5 where it is busy.

Stage 3 (three cars) is commit e150334.
Stage 2 (scrolling, one car) is tag `stage2-verified` / commit 2ce33b7.
Stage 1 (one car, one single-screen track) is tag `stage1-verified` / commit 8501179.

## Build
    python3 tools/make_data.py                       # regenerates src/data.asm (car, thrust)
    python3 tools/make_world.py                      # regenerates src/world.asm (track, waypoints)
    python3 tools/make_code.py                       # regenerates src/gen_tiles.asm, src/gen_bumps.asm
    bash <retro plugin>/skills/zxspectrum/scripts/build.sh asm src/racer.asm build/racer.tap racer
    (cd src && pasmo racer.asm ../build/racer.bin ../build/racer.sym)
    python3 tests/drive_test.py                       # real 48K ROM test, 38 checks
    python3 tests/profile_lap.py                      # T-states per stage over a whole lap
    python3 tests/profile.py                          # T-states per stage of a picture
    python3 tests/lap_capture.py                      # autopilot lap: frame rate + build/stage3_lap.gif

## Files
- `src/racer.asm` - the game (commented for learning, BASIC equivalents given)
- `src/data.asm` - GENERATED: car pictures and masks, thrust table
- `src/gen_tiles.asm`, `src/gen_bumps.asm` - GENERATED: the 8 tile-draw routines and the car-pair checks
- `src/world.asm` - GENERATED: tiles, world map, surface map
- `tools/make_data.py`, `tools/make_world.py`, `tools/make_code.py` - the generators
- `tests/drive_test.py` - headless test on the genuine 48K ROM (zx package)
