# Breakfast Run

A top-down micro-car racer for the ZX Spectrum 48K, written in Z80 assembler
(pasmo). Personal home project - Grant learning to code the Spectrum.
Inspired by the *genre* of Micro Machines / Super Off Road / Super Sprint:
tiny cars, momentum and drift, household tracks. Original game, original art.

## Stage 3 (this build) - car art and two computer cars
- Keys: **O** left, **P** right, **Q** accelerate, **A** brake/reverse. The race starts on your first **Q**.
- Three cars, 16 headings each, in the one-bit-art house style (dithered tyres, white glass,
  solid roof ringed by paper, identifying mark cut into the car). Drawn with a mask and a 1px halo.
- Two computer cars drive at waypoints with a different line each time, think every 2 or 4
  frames, are slower than you (laps of about 17 s and 20 s; yours about 13.6 s), and make
  mistakes (late turn-in, lifting off, wobbling the wrong way). Cars that touch bounce apart.
- A steady 17 pictures a second (one every 3 TV frames), measured along a whole lap.

Stage 2 (scrolling, one car) is tag `stage2-verified` / commit 2ce33b7.
Stage 1 (one car, one single-screen track) is tag `stage1-verified` / commit 8501179.

## Build
    python3 tools/make_data.py                       # regenerates src/data.asm (car, thrust)
    python3 tools/make_world.py                      # regenerates src/world.asm (track, waypoints)
    python3 tools/make_code.py                       # regenerates src/gen_copy.asm, src/gen_tiles.asm
    bash <retro plugin>/skills/zxspectrum/scripts/build.sh asm src/racer.asm build/racer.tap racer
    (cd src && pasmo racer.asm ../build/racer.bin ../build/racer.sym)
    python3 tests/drive_test.py                       # real 48K ROM test, 22 checks
    python3 tests/profile.py                          # T-states per stage of a picture
    python3 tests/lap_capture.py                      # autopilot lap: frame rate + build/stage3_lap.gif

## Files
- `src/racer.asm` - the game (commented for learning, BASIC equivalents given)
- `src/data.asm` - GENERATED: car pictures and masks, thrust table
- `src/gen_copy.asm`, `src/gen_tiles.asm` - GENERATED: the POP/PUSH screen copy and the 8 tile-draw routines
- `src/world.asm` - GENERATED: tiles, world map, surface map
- `tools/make_data.py`, `tools/make_world.py`, `tools/make_code.py` - the generators
- `tests/drive_test.py` - headless test on the genuine 48K ROM (zx package)
