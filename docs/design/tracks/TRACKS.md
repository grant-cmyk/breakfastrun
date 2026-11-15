# Breakfast Run - three longer track designs

Classification: Internal

These are **designs only**. Nothing here is in the game yet, and the game was not changed.
Made by `tools/make_track_designs.py` (run it again to redraw the pictures and this note).
Pictures: `track2.png`, `track3.png`, `track4.png`, and all four side by side in `tracks_overview.png`.

## The figures

| | Name | Map (tiles) | Lap (pixels) | Times track 1 | Waypoints | Distinct tiles | Cereal O's | Map data (bytes, estimate) |
|---|---|---|---|---|---|---|---|---|
| 1 | BREAKFAST AT TIFFANY'S | 72 x 64 | 1473 | 1.00 (in the game) | 46 | 99 | 128 | 2902 |
| 2 | THE BREAKFAST CLUB | 72 x 64 | 2125 | 1.44 | 66 | 104 | 176 | 3110 |
| 3 | BREAKFAST OF CHAMPIONS | 72 x 84 | 2510 | 1.70 | 78 | 107 | 207 | 3670 |
| 4 | THE DANISH GIRL | 72 x 91 | 2958 | 2.01 | 92 | 104 | 246 | 3937 |

- **Lap** is the length of the middle of the road, once round.
- **Waypoints** are the points the computer cars steer by, one every 32 pixels as on track 1.
- **Distinct tiles** is the number of different 8 x 8 pictures the map needs, counted the way `make_world.py` counts them ("tiles: N"). The game can hold 256. The count hardly changes with the length of the road, because the road itself is plain cloth: it is the breakfast things that use the tiles (each new design was given the same twelve things as track 1, wherever there was room: track 2 - 12, track 3 - 12, track 4 - 12 placed).
- **Map data** is an estimate of the bytes the map itself takes in memory: the row lists, the row index, the road/off-road and O maps, the waypoints and the tile pictures. It is there to compare the tracks with each other, not as an exact count.

## The tracks

### Track 2 - THE BREAKFAST CLUB

Twisty and technical: toast-rack switchbacks - three hairpins, then track 1's dip.

- Map: 72 x 64 tiles (576 x 512 pixels). Track 1 is 72 x 64.
- Lap: 2125 pixels, **1.44 times** track 1 (1473).
- Waypoints: 66 (track 1: 46). Cereal O's: 176 (track 1: 128).
- Distinct tiles: 104 (track 1: 99).
- Map data: about 3110 bytes (track 1: about 2902) - +208.
- Tightest corner: 55 pixel radius (track 1's arcs: 54; its dip is sharper). Start straight: 331 pixels (track 1: 326).
- Least cloth between two stretches of road: 3.3 tiles.

What would make it hard to put in the game:

- Fits the map the game has now (72 x 64 tiles) - no bigger map needed.
- The rows of road are close together (3 to 5 tiles of cloth between them), so there is little room for breakfast things between them, and a car that runs wide can reach the next row.

### Track 3 - BREAKFAST OF CHAMPIONS

Fast and flowing: four long straights, wide sweeping bends and one fast kink.

- Map: 72 x 84 tiles (576 x 672 pixels). Track 1 is 72 x 64.
- Lap: 2510 pixels, **1.70 times** track 1 (1473).
- Waypoints: 78 (track 1: 46). Cereal O's: 207 (track 1: 128).
- Distinct tiles: 107 (track 1: 99).
- Map data: about 3670 bytes (track 1: about 2902) - +768.
- Tightest corner: 56 pixel radius (track 1's arcs: 54; its dip is sharper). Start straight: 271 pixels (track 1: 326).
- Least cloth between two stretches of road: 4.8 tiles.

What would make it hard to put in the game:

- Needs a taller map: 84 rows instead of 64 (the same 72 wide). The game's row index, mini-map and camera limits are built for 64 rows and would need changing.
- The long straights run up and down the screen, where the window is shortest (152 px).

### Track 4 - THE DANISH GIRL

The pastry swirl: spiral in on big sweeping curves, hairpin in the middle, spiral out.

- Map: 72 x 91 tiles (576 x 728 pixels). Track 1 is 72 x 64.
- Lap: 2958 pixels, **2.01 times** track 1 (1473).
- Waypoints: 92 (track 1: 46). Cereal O's: 246 (track 1: 128).
- Distinct tiles: 104 (track 1: 99).
- Map data: about 3937 bytes (track 1: about 2902) - +1035.
- Tightest corner: 55 pixel radius (track 1's arcs: 54; its dip is sharper). Start straight: 222 pixels (track 1: 326).
- Least cloth between two stretches of road: 3.8 tiles.

What would make it hard to put in the game:

- Needs the tallest map: 91 rows instead of 64 (the same 72 wide), with the same changes as track 3.
- Two lanes run side by side in opposite directions all the way round (about 4 tiles of cloth between): the computer cars' waypoints and the wrong-way / lap-counting logic should be tested for a car that hops across to the other lane.
- The start straight is the shortest of the four: the grid fits, but the first bend comes sooner after the line than on track 1.

## For all three

- **Memory is the real obstacle.** The project notes say memory is full (well under 200 bytes free). A second track of any size needs room for its own map data (see the last column above), so room has to be found first - for example by loading one track at a time, or packing the map data.
- All three keep the map 72 tiles wide, because the game's road-surface code is written for exactly 72 (it stops the build otherwise). Only the height grows.
- All three use track 1's road width (72 pixels), start on a bottom straight heading right with the same five-car grid, and run the same way round (anticlockwise).
- The game today builds one track straight into the program: choosing between tracks, and each track's name on screen, are new work.
- The positions of the breakfast things and of the NOS and oil cans in the pictures are placeholders, put there by the script so the tile counts are fair. They are easy to move.

## Checks the script ran

For each new track: the middle line is closed and smooth; it never crosses itself; no two different stretches of road come closer than 3 tiles of cloth; no corner is tighter than track 1's; the road stays as far from the map's edge as track 1's does; the start straight holds the five-car grid; the lap is at least 1.4 times track 1.

| Check | Track 1 | Track 2 | Track 3 | Track 4 |
|---|---|---|---|---|
| closed | 53.1 (yardstick) | 5.0 - pass | 5.0 - pass | 5.0 - pass |
| centre line crosses itself | 0 (yardstick) | 0 - pass | 0 - pass | 0 - pass |
| least cloth between two sections of road | 46.9 (yardstick) | 26.0 - pass | 38.0 - pass | 30.0 - pass |
| tightest corner, 3-point radius | 26.8 (yardstick) | 54.9 - pass | 55.8 - pass | 54.9 - pass |
| smallest arc radius as drawn | 54.0 (yardstick) | 55 - pass | 56 - pass | 55 - pass |
| centre line to the map edge | 66.6 (yardstick) | 68.0 - pass | 68.0 - pass | 68.0 - pass |
| start straight | 326.0 (yardstick) | 331.0 - pass | 271.0 - pass | 222.0 - pass |
| five grid boxes all on the road | 1 (yardstick) | 1 - pass | 1 - pass | 1 - pass |
| lap at least 1.4 x track 1 | 1.0 (yardstick) | 1.4 - pass | 1.7 - pass | 2.0 - pass |
| distinct tiles within the game's 256 | 99 (yardstick) | 104 - pass | 107 - pass | 104 - pass |

Not checked: the tracks have not been driven - not built into the game, so nothing here says how they play, how fast a lap is, or whether the computer cars cope.
