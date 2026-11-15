# Breakfast Run - four longer track designs (one with a crossover)

Classification: Internal

These are **designs only**. Nothing here is in the game yet, and the game was not changed.
Made by `tools/make_track_designs.py` (run it again to redraw the pictures and this note).
Pictures: `track2.png` to `track5.png`, all five side by side in `tracks_overview.png`, and the bridge close up in `crossover_closeup.png` (first ideas) and `crossover_walls.png` (with side walls).

## The figures

| | Name | Map (tiles) | Lap (pixels) | Times track 1 | Waypoints | Distinct tiles | Cereal O's | Map data (bytes, estimate) |
|---|---|---|---|---|---|---|---|---|
| 1 | BREAKFAST AT TIFFANY'S | 72 x 64 | 1473 | 1.00 (in the game) | 46 | 99 | 128 | 2902 |
| 2 | THE BREAKFAST CLUB | 72 x 64 | 2125 | 1.44 | 66 | 104 | 176 | 3110 |
| 3 | BREAKFAST OF CHAMPIONS | 72 x 84 | 2510 | 1.70 | 78 | 107 | 207 | 3670 |
| 4 | THE DANISH GIRL | 72 x 91 | 2958 | 2.01 | 92 | 104 | 246 | 3937 |
| 5 | A FRIDGE TOO FAR | 72 x 74 | 2236 | 1.52 | 70 | 150 | 158 | 4006 |

- **Lap** is the length of the middle of the road, once round.
- **Waypoints** are the points the computer cars steer by, one every 32 pixels as on track 1.
- **Distinct tiles** is the number of different 8 x 8 pictures the map needs, counted the way `make_world.py` counts them ("tiles: N"). The game can hold 256. The count hardly changes with the length of the road, because the road itself is plain cloth: it is the breakfast things that use the tiles (each new design was given the same twelve things as track 1, wherever there was room: track 2 - 12, track 3 - 12, track 4 - 12, track 5 - 12 placed).
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
- The start straight is short (222 pixels): the grid fits, but the first bend comes sooner after the line than on track 1.

### Track 5 - A FRIDGE TOO FAR

The crossover: a figure of eight - under the bridge first, then round, up a ramp and over it.

- Map: 72 x 74 tiles (576 x 592 pixels). Track 1 is 72 x 64.
- Lap: 2236 pixels, **1.52 times** track 1 (1473).
- Waypoints: 70 (track 1: 46). Cereal O's: 158 (track 1: 128).
- Distinct tiles: 150 (track 1: 99).
- Map data: about 4006 bytes (track 1: about 2902) - +1104.
- Tightest corner: 54 pixel radius (track 1's arcs: 54; its dip is sharper). Start straight: 211 pixels (track 1: 326).
- Least cloth between two stretches of road: 4.5 tiles.

What would make it hard to put in the game:

- **The game cannot do this today: it has no bridges.** Everything under 'What the crossover needs in the game' below is new work.
- Needs a taller map: 74 rows instead of 64 (the same 72 wide), with the same changes as track 3.
- The bridge's pictures add tiles (counted here with the double-rail walls, W3), and its deck needs a mask so it can be redrawn over a car underneath.
- The start straight is the shortest of all five: the grid fits, with as much room behind the line as it needs but less after it than track 1.

#### The crossover, as designed

- The crossing is at pixel (188, 336): tile column 23, row 42. The two roads meet at 90 degrees.
- **Upper road (the bridge):** the north-south road at x = 188, driven southwards (down the screen).
- **Lower road:** the east-west road at y = 336, driven westwards (right to left).
- **Ramp up:** y 240 to 288 (48 pixels). **Level deck:** y 288 to 384 (96 pixels). **Ramp down:** y 384 to 432 (48 pixels). These lengths are suggestions.
- **Hidden stretch of the lower road:** x 232 down to 144 (88 pixels): a car there is partly or wholly under the deck.
- 6 of the 70 waypoints are on the upper level (listed in `tracks_data.json`).
- The crossing is 184 pixels above the start straight and 200 pixels from the nearest grid box. A lap goes: start line, round the bottom loop, UNDER the bridge, round the top loop, then OVER the bridge and back to the start straight.
- `crossover_closeup.png` shows the first three ways the bridge could be drawn, in the game's two colours: A plain rails, B rails with posts and a shadow, C a planked deck.
- `crossover_walls.png` is the follow-up Grant asked for: A and B combined, with solid side walls and no cereal O's on the bridge. Three ways to draw the wall: W1 brick parapet, W2 thick rail with posts, W3 double rail.
- **Walls stop a car leaving the bridge.** They run down both sides from the foot of the ramp up to the foot of the ramp down (y 240 to 432, at x = 152 and x = 224). In the game that is a collision with a straight line - "on the upper level, between these two y values, x may not pass this value" - which should be simpler than the O collisions, as an estimate (not tried).
- **Fewer cereal O's.** With walls there instead, the O's beside the bridge and its ramps are gone: track 5 has 158 O's (it had 172 before the walls). The upper road's O's stop where the ramp walls start; the lower road's stop 56 pixels either side of the bridge's middle.

Crossover checks the script ran:

| Check | Result |
|---|---|
| crossing found where the design says (distance from it, px) | 0.0 - pass |
| angle between the two roads at the crossing (degrees; want 80 to 90) | 90.0 - pass |
| upper road dead straight from the foot of one ramp to the foot of the other (192 px) | 1 - pass |
| lower road dead straight where it is hidden (88 px) | 1 - pass |
| crossing to the start straight (px between the middles of the roads; want >= 150) | 184.0 - pass |
| crossing to the nearest grid box (px; want >= 150) | 200.0 - pass |
| cereal O's standing on either road at the crossing (count) | 0 - pass |
| cereal O's beside the bridge or its ramps, where the walls are (count) | 0 - pass |
| waypoints on the upper level (ramps and deck) | 6 - pass |

#### What the crossover needs in the game

The difficulty column is **an estimate** - a judgement from reading the game's code, not something measured or tried.

| What | Why | Difficulty (estimate) |
|---|---|---|
| A level for each car | Every car has to know whether it is on the upper or the lower road. It changes only at the foot of a ramp, so one bit per car is enough. | Small |
| Waypoints that carry a level | The computer cars steer by waypoints; the ones on the ramps and deck are marked "upper" (the data file lists them). A computer car's level can simply follow its next waypoint. Your own car needs its own rule: upper from the foot of the ramp up to the foot of the ramp down, if it came in along the upper road. | Small to medium |
| Collisions only on the same level | Two cars at the crossing, one above and one below, must pass through each other. One extra comparison in the car-to-car test. | Small |
| The O walls at the crossing | The O's of one road must not block the other. In this design no O stands on either road at the crossing or beside the bridge and ramps (the script checks it). Instead the bridge has side walls: a car on the upper level cannot pass them sideways, and a car on the lower level passes under them. A straight-line test by level - simpler than the O collisions. | Small to medium |
| Drawing order: the bridge over the car below | The hard one. After the cars are drawn, the deck's tiles must be drawn again over any car on the lower level (a mask, like the breakfast things have), while a car on the upper level is drawn over the deck. The picture is built to a tight time budget, and the redraw costs time whenever a car is under the bridge. | Large |
| Ramp speed | A little slower going up, a little faster going down: a small change to the speed while a car is on a ramp stretch - for the computer cars too. | Small |
| Mini-map | The mini-map draws the road's two edges; at the crossing the lower road's edges should stop at the bridge so it reads as "over". It also has to be taller for a 74-row map. | Small to medium |
| Lap counting | Laps are counted by waypoints in order, and the crossing is far from the start line, so it should carry on working. The risk is any "nearest waypoint" logic picking a waypoint of the other road at the crossing: it must only consider waypoints on the car's own level. | Small to medium (needs testing) |
| Memory | All of the above is new code and data, and there is essentially none free (0 to 10 bytes in each area at the last count). Room has to be found before any of it can go in. | Large |

Taken together this is the biggest of the five to put in. As an estimate: several sessions of work, most of it in the drawing order and in finding the memory.

## For all the new tracks

- **Memory is the real obstacle.** The game's memory is essentially full: at the last count 0 to 10 bytes free in each area. A second track of any size needs room for its own map data (see the last column above), so room has to be found first - for example by loading one track at a time, or packing the map data.
- All of them keep the map 72 tiles wide, because the game's road-surface code is written for exactly 72 (it stops the build otherwise). Only the height grows.
- All of them use track 1's road width (72 pixels), start on a bottom straight heading right with the same five-car grid, and run the same way round (anticlockwise).
- The game today builds one track straight into the program: choosing between tracks, and each track's name on screen, are new work.
- The positions of the breakfast things and of the NOS and oil cans in the pictures are placeholders, put there by the script so the tile counts are fair. They are easy to move.

## Checks the script ran

For each new track: the middle line is closed and smooth; it never crosses itself (track 5: it crosses itself exactly once, at the bridge); no two different stretches of road come closer than 3 tiles of cloth; (on track 5 the two roads that meet at the bridge are left out of that check within 120 pixels of the crossing); no corner is tighter than track 1's; the road stays as far from the map's edge as track 1's does; the start straight holds the five-car grid; the lap is at least 1.4 times track 1.

| Check | Track 1 | Track 2 | Track 3 | Track 4 | Track 5 |
|---|---|---|---|---|---|
| closed | 53.1 (yardstick) | 5.0 - pass | 5.0 - pass | 5.0 - pass | 5.3 - pass |
| centre line crosses itself | 0 (yardstick) | 0 - pass | 0 - pass | 0 - pass | 1 - pass |
| least cloth between two sections of road | 46.9 (yardstick) | 26.0 - pass | 38.0 - pass | 30.0 - pass | 35.7 - pass |
| tightest corner, 3-point radius | 26.8 (yardstick) | 54.9 - pass | 55.8 - pass | 54.9 - pass | 53.7 - pass |
| smallest arc radius as drawn | 54.0 (yardstick) | 55 - pass | 56 - pass | 55 - pass | 54 - pass |
| centre line to the map edge | 66.6 (yardstick) | 68.0 - pass | 68.0 - pass | 68.0 - pass | 68.0 - pass |
| start straight | 326.0 (yardstick) | 331.0 - pass | 271.0 - pass | 222.0 - pass | 211.0 - pass |
| five grid boxes all on the road | 1 (yardstick) | 1 - pass | 1 - pass | 1 - pass | 1 - pass |
| lap at least 1.4 x track 1 | 1.0 (yardstick) | 1.4 - pass | 1.7 - pass | 2.0 - pass | 1.5 - pass |
| distinct tiles within the game's 256 | 99 (yardstick) | 104 - pass | 107 - pass | 104 - pass | 150 - pass |

Not checked: the tracks have not been driven - not built into the game, so nothing here says how they play, how fast a lap is, or whether the computer cars cope.
