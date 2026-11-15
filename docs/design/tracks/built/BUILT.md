# Breakfast Run - tracks 2, 3 and 5 as built

Classification: Internal

One track a build: memory has no room for two tracks side by side. `build/racer.tap` is still track 1
and is byte for byte what it was before this work.

| Build command | Tape | Track |
|---|---|---|
| `bash build.sh` | `build/racer.tap` | 1, BREAKFAST AT TIFFANY'S (unchanged) |
| `TRACK=2 bash build.sh` | `build/racer_track2.tap` | 2, THE BREAKFAST CLUB (72 x 64) |
| `TRACK=3 bash build.sh` | `build/racer_track3.tap` | 3, BREAKFAST OF CHAMPIONS (72 x 84) |
| `TRACK=5 bash build.sh` | `build/racer_track5.tap` | 5, A FRIDGE TOO FAR (72 x 74), the bridge - see the end of this note |

Test: `TRACK=2 python3 tests/track2_test.py` and `TRACK=3 python3 tests/track2_test.py` (each about
10 minutes; `QUICK=1` leaves out the dropped-car part). Pictures: `TRACK=2 python3 tests/track_shots.py`.

## How it works

- `tools/make_world.py` takes `TRACK` (1, 2 or 3) and `WORLD_OUT` (a folder). The centre line of
  tracks 2 and 3 comes from `tools/make_track_designs.py`; everything else (road, cereal O's, grid,
  start line, waypoints, O map, mini-map, cans) is made the way track 1's is.
- `build.sh` builds a track other than 1 in a copy of `src/` under `build/trackN/src`, so the
  files in `src/` stay track 1's.
- The game's code is the same for tracks 1 and 2. Track 3 changes one routine, only in its own
  build: the mini-map's scale (14/256 instead of 21/256), so an 84-row map fits above RACE. (Since 15 Nov 2026 night the map is in the window's bottom left corner, 48 x 39 pixels: the same scales.)

## What differs from the designs

- **Waypoints: 61 on both** (the designs had 66 and 78). The game keeps a car's race progress in one
  byte, which over 3 laps allows 61 at most. They are 35 px apart on track 2 and 41 px on track 3
  (32 on track 1).
- **Fewer breakfast things, because of memory.** Track 2: ten (plate, four eggs, three toast, fork,
  knife) - no juice, bacon or spoon. Track 3: five (three eggs, two toast).
- Cans. Track 2: NOS behind the grid and in the middle of the third row; oil can half-way up the
  left-hand straight. Track 3: NOS behind the grid and at the foot of the middle fold; oil can on
  the left-hand straight.
- Track 2's mini-map sits one row lower than track 1's (its top edge would have been cut off).
- The track's name is not shown anywhere in the game (it is not on track 1 either).

## Measured (emulator, real 48K ROM)

| | Track 1 | Track 2 | Track 3 |
|---|---|---|---|
| Lap, pixels | 1473 | 2111 | 2497 |
| Computer cars' average lap, s (FRANK, SPIKE, BRUNO, JANE) | 19.2 19.6 19.4 18.1 | 26.8 28.6 27.5 25.5 | 30.6 31.8 30.9 29.7 |
| Time for all four to finish 3 laps, s | not measured | 87 | 97 |
| On the road (worst car) | 100% | 89% | 93% |
| Your car driven by script, laps, s | 16.5 16.8 16.9 (alone) | 25.8 25.5 25.3 (in the pack) | 29.3 29.6 26.4 (in the pack) |
| Dropped computer cars stuck | 0 (stuck_test) | 0 of 478 places | 0 of 614 places |
| Program bytes free | 5 | 35 | 23 |

Not verified: how either track feels to drive. Nobody has played them.

## Track 4 (THE DANISH GIRL, 72 x 91) - not built

It does not fit. Counted against track 1's memory, with no breakfast things at all:

- 27 more map rows at 20 bytes (road map 9, O map 9, row index 2): +540
- 118 more cereal O's in the row lists: +236
- waypoints: its lap is 2958 px, so 61 waypoints would be 48 px apart - further than the 40 px at
  which your car passes one. It needs about 92 (+184 bytes), and that needs race progress kept in
  two bytes (new code, about 40 bytes, an estimate)
- less track 1's things, which it would not have: -616 tiles, -148 row entries

That is about 240 bytes over with a bare table, where the program has 5 free and the top of memory
about 70. So room has to be found first (packing the O map and road map into one, or the row
lists), and the mini-map would be about 13/256.

## Track 5, A FRIDGE TOO FAR - the one with the bridge (15 Nov 2026, background agent; not playtested)

`TRACK=5 bash build.sh` -> `build/racer_track5.tap`, a one-track tape (72 x 74 tiles). Everything the bridge
needs is behind one switch, `OPT_BRIDGE` (set by build.sh for TRACK=5 only): `src/bridge.asm` and short
`if OPT_BRIDGE` blocks in racer.asm, hud.asm and grip.asm. With the switch off the tapes of tracks 1, 2 and 3
are byte for byte what they were (`cmp`). Test: `python3 tests/track5_test.py` (about 25 minutes; `QUICK=1`
leaves out the dropped cars, `BRIDGE=1` runs the bridge's checks only, about 5 minutes). Pictures:
`python3 tests/track5_shots.py` and `TRACK=5 python3 tests/track_shots.py`.

The lap: start line, round the bottom right, WEST along the lower road and UNDER the bridge, up the left
side, along the top, back along the second lane, then SOUTH up the ramp, OVER the deck, down the ramp and left
onto the start straight.

### How the bridge works

- **Levels.** Each car has a level: 0 on the table, 1 on the bridge. A car that comes onto the first 16 px of
  either ramp, between the kerbs, goes up to 1; it comes back to 0 when it leaves by either ramp's foot. Cars
  only bump cars on their own level: one on the deck and one under it pass through each other.
- **Walls.** On level 1 the car's x is kept between the kerb walls from ramp foot to ramp foot (a straight
  clamp and a kick back, with the bonk and damage of a cereal O for you). On level 0 the car is kept between
  the tunnel's walls while it is under the deck or between the concrete wings, and it cannot come in through
  the bridge's side beside the ramps. No cereal O's on or beside the bridge.
- **Drawing order.** A car on level 0 wholly under the cover (x 136 to 240 on the lower road) is simply not
  drawn. Half under, at a tunnel mouth, it is drawn and the bytes under the cover are then put back as they
  were. So the deck, kerbs and mouth are never touched, and a hidden car costs less than a visible one. A car
  on level 1 is drawn as ever, on top.
- **Ramps.** On the ramp up a car's push and top speed are an eighth less, on the ramp down an eighth more
  (`RAMP_SHIFT` in bridge.asm: 3 = an eighth). The same routine serves you and the computer cars.
- **Look.** Grant's P4 with the tunnel mouths dithered (D1): concrete wings each side of both mouths, the
  concrete walls along the ramps (thin at the foot, 8 px by the deck), kerb walls, arrows on the ramps.
  Cyan only: no white paper anywhere (white cells would have to be coloured in the scrolling window every
  picture; not tried).
- **Mini-map.** The upper road's two edges run on over the crossing; the lower road's stop at it.
- **Corner arrows.** Worked out from the centre line as on the other tracks; `TRACK=5 python3
  tests/arrow_test.py` passes. The warning for the right-hander after the tunnel shows while your car is
  still under the deck (the arrow is drawn over everything).
- A computer car that misses the foot of the ramp and is beside the bridge heading for a waypoint on it is
  put onto the bridge (otherwise it pushed at the wall for ever).

### Simplified from the design

- **No breakfast things on this track** (no plate, eggs, toast): their memory went to the bridge.
- **Kerbs**: an 8 x 8 blue block every other cell with nothing between. The design's pale blocks had a line
  each side; drawing them made the pictures near the bridge take 5 TV frames against 4 elsewhere.
- **Ramp arrows**: 24 px wide, one every 16 px (the design: 26 wide every 12), so all six are the same six
  tiles.
- **The cloth's dots are not wiped off** the deck or the concrete: the bridge is drawn over the tablecloth
  like the cereal O's (wiping needs masked tiles, about 200 of them in view: far too slow).
- 61 waypoints (the design had 70), 36 px apart, as on tracks 2 and 3.
- Cans: NOS behind the grid and on the top lane; the oil can on the left-hand straight.

### Memory

The first assembly of track 5 with the bridge's pictures and no bridge code was 150 bytes over in the program
and 192 over in the start-up area. Found for it:

- **No O map on this track** (666 bytes): the O check reads the map's row lists instead (`o_at`). An O's tile
  holds the O alone, so the start line stops short of the two O's at its ends.
- **The race order's car pictures come from the cars' own frames** (`tower_b`, hud.asm) instead of a second
  copy (`tower_cars`, 320 bytes).
- The cheaper kerbs and arrows above (about 140 bytes of tiles and row lists).
- 88 bytes at the bottom of the stack's page (0x5E00: the levels, the ramp flags, the 72 bytes kept under a
  half-hidden car). The stack has been seen 56 bytes deep of its 256; 168 are left.

Now free on track 5: 246 bytes in the program, 92 at TOPMEM, 204 before the start-up area's limit. The bridge's
code is about 650 bytes in bridge.asm and 80 for tower_b.

### Measured (emulator, real 48K ROM, tests/track5_test.py: 60 checks pass)

| | Track 5 |
|---|---|
| Lap, pixels | 2223 |
| Computer cars' average lap, s (FRANK, SPIKE, BRUNO, JANE) | 27.7 28.6 29.1 27.8 |
| On the road (worst car) | 94% |
| Your car driven by script, laps, s (in the pack) | 26.3 25.8 24.9, finished 1st |
| Dropped computer cars stuck | 0 of 546 places |
| Deck car and car under it on the same spot for 1.5 s | 0 bumps (2 at once when both are put on one level) |
| Flat out with NOS at a kerb wall for 3 s | x stays 150 to 210 (walls at 152 and 224, car 16 wide) |
| Car under the deck | 0 pixels of it in the window; every pixel of the cover as the map has it |
| Half out of a mouth | 0 pixels changed inside the cover, 10 to 47 of car outside it |
| Top of the ramp up, against the same run with the ramps switched off | you 88%, FRANK 88% |
| Fastest on the ramp down, likewise | you 112%, FRANK 110% |
| Pictures a second, script driving in the pack | 11.7 near the crossing, 12.7 elsewhere, 11.1 while under the deck |

The slower pictures near the crossing are the bridge's tiles (about 125 of them, most in view at once, against about 40 cereal O's
elsewhere); hiding a car costs nothing. With no bridge pictures at all the same stretch ran at 15.9.

Not verified: how any of it feels to drive (nobody has played it); real hardware; the stack's worst case.
