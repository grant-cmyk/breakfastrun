# Breakfast Run - tracks 2 and 3 as built

Classification: Internal

One track a build: memory has no room for two tracks side by side. `build/racer.tap` is still track 1
and is byte for byte what it was before this work.

| Build command | Tape | Track |
|---|---|---|
| `bash build.sh` | `build/racer.tap` | 1, BREAKFAST AT TIFFANY'S (unchanged) |
| `TRACK=2 bash build.sh` | `build/racer_track2.tap` | 2, THE BREAKFAST CLUB (72 x 64) |
| `TRACK=3 bash build.sh` | `build/racer_track3.tap` | 3, BREAKFAST OF CHAMPIONS (72 x 84) |

Test: `TRACK=2 python3 tests/track2_test.py` and `TRACK=3 python3 tests/track2_test.py` (each about
10 minutes; `QUICK=1` leaves out the dropped-car part). Pictures: `TRACK=2 python3 tests/track_shots.py`.

## How it works

- `tools/make_world.py` takes `TRACK` (1, 2 or 3) and `WORLD_OUT` (a folder). The centre line of
  tracks 2 and 3 comes from `tools/make_track_designs.py`; everything else (road, cereal O's, grid,
  start line, waypoints, O map, mini-map, cans) is made the way track 1's is.
- `build.sh` builds a track other than 1 in a copy of `src/` under `build/trackN/src`, so the
  files in `src/` stay track 1's.
- The game's code is the same for tracks 1 and 2. Track 3 changes one routine, only in its own
  build: the mini-map's scale (14/256 instead of 21/256), so an 84-row map fits above RACE.

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

Track 5 needs the bridge: not attempted.
