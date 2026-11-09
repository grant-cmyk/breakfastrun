# Breakfast Run

A top-down micro-car racer for the ZX Spectrum 48K, written in Z80 assembler
(pasmo). Personal home project - Grant learning to code the Spectrum.
Inspired by the *genre* of Micro Machines / Super Off Road / Super Sprint:
tiny cars, momentum and drift, household tracks. Original game, original art.

## Stage 4 (this build) - five cars
- Keys: **O** left, **P** right, **Q** accelerate, **A** brake/reverse. The race starts on your first **Q**.
- You and four computer cars (a 3 + 2 grid). Each has its own mark: you a nose notch, A a roof
  stripe, B an open cockpit, C a grille slot, D a sunroof. Their laps: about 16.5, 20.2, 17.2 and
  19.2 s against your 13.5 s. They take turns to think, take different lines, make mistakes, and
  bounce off each other and you.
- 16.7 pictures a second on 32 of the lap's 34 stretches; 14-15 for the first two, while all five
  cars are bunched off the start.
- The screen-copy code (5.6 KB) is written by the program itself at start-up (make_copier).

Stage 3 (three cars) is commit e150334.
Stage 2 (scrolling, one car) is tag `stage2-verified` / commit 2ce33b7.
Stage 1 (one car, one single-screen track) is tag `stage1-verified` / commit 8501179.

## Build
    python3 tools/make_data.py                       # regenerates src/data.asm (car, thrust)
    python3 tools/make_world.py                      # regenerates src/world.asm (track, waypoints)
    python3 tools/make_code.py                       # regenerates src/gen_tiles.asm, src/gen_bumps.asm
    bash <retro plugin>/skills/zxspectrum/scripts/build.sh asm src/racer.asm build/racer.tap racer
    (cd src && pasmo racer.asm ../build/racer.bin ../build/racer.sym)
    python3 tests/drive_test.py                       # real 48K ROM test, 20 checks
    python3 tests/profile.py                          # T-states per stage of a picture
    python3 tests/lap_capture.py                      # autopilot lap: frame rate + build/stage3_lap.gif

## Files
- `src/racer.asm` - the game (commented for learning, BASIC equivalents given)
- `src/data.asm` - GENERATED: car pictures and masks, thrust table
- `src/gen_tiles.asm`, `src/gen_bumps.asm` - GENERATED: the 8 tile-draw routines and the car-pair checks
- `src/world.asm` - GENERATED: tiles, world map, surface map
- `tools/make_data.py`, `tools/make_world.py`, `tools/make_code.py` - the generators
- `tests/drive_test.py` - headless test on the genuine 48K ROM (zx package)
