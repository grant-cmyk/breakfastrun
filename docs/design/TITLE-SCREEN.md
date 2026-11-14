# Breakfast Run - title / attract screen (DESIGN, not built)

Design round of 14 Nov 2026, for Grant's ask: logo, 1UP / 2UP, K for keys, hi-score, and an attract
sequence that shows the drivers with a car skidding about; then choose a driver, then a car.
Nothing here is in the game. Every picture is made by `tools/make_title_mockups.py` as real
Spectrum pixels and colour cells (one ink + one paper per 8 x 8 cell), so it can be drawn as shown.

| Picture | What it is |
|---|---|
| `title_options.png` | three title layouts A, B, C side by side (singly: `title_option_a/b/c.png`) |
| `title_attract.gif` | layout A running: four drivers, about 11 seconds, 12.5 frames a second |
| `title_flow.png` | keys screen, choose driver, choose car, 2UP's turn, and the order of the screens (singly: `title_screen_*.png`) |

## Recommended: layout A, "the stage and the card"

- Same family as the race screen: yellow table and border, a blue-on-cyan cloth window in a slim blue frame.
- Logo at twice its size top left; LAP RECORD (time, and the driver who set it) top right.
- The cloth window is a stage. Each driver in turn: their car drives in, drifts (a circle, a figure of
  eight or a spin, nose pointing into the bend, two skid marks left behind), and drives off. Then the
  cloth is wiped and the next driver comes on. In the game each would stay about 5 seconds (the GIF is quicker).
- Beside the stage, that driver's card: face at twice the size on their colour, name, one-liner, the
  car they like best and its GRIP / SPEED / ACCEL as five pips each.
- Three big buttons along the bottom, each with its key as a key cap: `1` 1UP, `2` 2UP, `K` KEYS.
  PRESS 1 OR 2 TO START flashes (the Spectrum's own FLASH: costs nothing).
- The car is the only thing that moves, and only on the cloth (one colour pair), so there is no colour clash.

B (logo three times the size, cloth strip the full width) has the loudest logo but small choices and a
cramped card. C (all six faces in a row, the car spinning along bare table) shows the whole cast at once
but gives the skid less room.

## The order of the screens

1. TITLE + ATTRACT - loops until a key.
2. `K`: KEYS - press 1 or 2 to set that player's LEFT, RIGHT, ACCELERATE, BRAKE, NOS in turn (the row lights,
   its key cap flashes, a big line names the key wanted; a key already used is refused); ENTER goes back.
3. `1` or `2`: 1UP CHOOSES A DRIVER - six faces in a row, a red frame moves with left / right, accelerate picks.
4. 1UP CHOOSES A CAR - six cars on cloth tiles, each with its strengths in the race screen's little box;
   the card shows the chosen one bigger with big bars. It starts on the car that driver likes best.
5. Two players only: the header turns blue and 2UP picks driver, then car. 1UP's pick keeps its red frame.
   A driver can be picked once; both may drive the same car.
6. THE RACE - then back to the title with the lap record updated.

## The cast (all names, one-liners and numbers are PROPOSALS)

| # | Driver | | One-liner | Likes | Face art |
|---|---|---|---|---|---|
| 1 | EGGS BENNY | man | Cool head, sunny side up | Toaster | YOU - Grant's, in the game |
| 2 | HONEY BUN | lady | Sweet talker, rough driver | Bean Buggy | BUN - draft |
| 3 | OLD KIPPER | man | Slow to wake, hard to pass | Milk Float | CAP - draft |
| 4 | MISS MUESLI | lady | Has done the maths on you | Butty Truck | SPECS2 - draft |
| 5 | HARD BOILED | man | Never cracks. Never smiles. | Mud Muffin | SHADES - draft |
| 6 | LOOPY LOU | lady | Flat out or not at all | Espresso | CURLS - draft |

| Car | GRIP | SPEED | ACCEL | In a line | Art |
|---|---|---|---|---|---|
| TOASTER | 3 | 3 | 3 | Good at everything | YOU car - Grant's, in the game, 16 headings |
| MUD MUFFIN (the 4 x 4) | 5 | 2 | 2 | Sticks like jam | OFFROAD - draft |
| BUTTY TRUCK (the pickup) | 3 | 4 | 2 | Heavy, but it shifts | PICKUP - draft |
| BEAN BUGGY | 2 | 2 | 5 | Off like a shot | BUGGY - draft |
| ESPRESSO (the hot rod) | 2 | 5 | 2 | Fast. Slides a lot. | HOTROD - draft |
| MILK FLOAT | 4 | 1 | 4 | Steady. Never fast. | MILKFLOAT - draft |

Every car adds up to 9, so none is simply best. The four cars in the game today that are not yours (the
stripe car, the clown car, the tank, Slim Jane's) stay as computer rivals in this design.

## Draft or made up - needs Grant

- The five new faces (BUN, SPECS2, CURLS, CAP, SHADES) are first drafts to redraw.
- The five new cars are first drafts, 20 x 20, drawn facing up only. The game's cars are 16 x 16 with
  three drawn headings (0, 22.5, 45) from which the other 13 are made. In the GIF and the choose-car
  screens the new cars' turned pictures were made by the tool from the one drawing, so they are rough
  and a little bigger than TOASTER. Each needs redrawing at 16 x 16, three headings.
- Only TOASTER's skid in the GIF (the first driver) uses the game's real car frames.
- Made up: the lap record 0:41.2 and its holder; 2UP's keys 6 7 9 8 0 (chosen because they are also a
  Sinclair joystick); "accelerate picks" on the choosing screens.
- Tile colours: HARD BOILED's tile is grey because the card is white. When 1UP's and 2UP's frames are on
  neighbouring tiles they share a column of colour cells, so that side shows one colour.
- Open questions: what 2UP means in the race (taking turns, or both on the table at once); whether a
  driver changes anything but the face (today it would be looks only).

## BUILD PLAN (plain words; every number is an ESTIMATE, none measured)

The constraint is memory: the game's main area has about 1 KB free.

**How big the title is (estimates).** Code for title, attract, keys and the two choosing screens: 2 to
3 KB. Words, names and strength numbers: about 0.5 KB. Faces: 32 bytes each (six = about 0.2 KB). The
logo, font, cloth and the car-drawing routine are already in the game and can be shared.

**Where it can live.**
1. *In the start-up area the race frees (the back buffer region).* The title runs before the race, then
   the race draws over it. Costs the main area almost nothing: only the choices (players, drivers, cars,
   keys - about 16 bytes) are passed on. Catch: after a race the title is gone, so it has to be put back.
   Either keep a squeezed copy somewhere and unpack it each time (needs perhaps 1.5 to 2 KB that is not
   free today), or on 48K come back to a small "race again / change driver" screen and show the full
   title only after loading.
2. *A separate part loaded first from tape.* Simplest to write, but the title shows once per load;
   same catch as above.
3. *128K.* The title and all car pictures sit in the extra memory and are switched in when wanted. No
   squeeze at all, and the 48K version can stay simpler. Needs the 128K paging written and tested.

**The cars are the big cost.** One car's 16 headings is about 1.5 KB. Today five cars are in memory
(about 7.5 KB). Ten cars (five now + five new) would be about 15 KB: that does not fit a 48K game with
1 KB free. Options:
- *A pool, five loaded per race.* Only the chosen car (two in 2UP) and the computer cars for that race
  are unpacked into the room the five cars use now. The rest wait squeezed.
- *Store three headings, make the other thirteen in the Spectrum.* The build tool already makes 13 of the
  16 headings from three drawings by flipping and quarter-turning. Doing that in the game at race start
  would cut a car from about 1.5 KB to about 0.3 KB stored, so ten cars would be about 3 KB plus a small
  routine (perhaps 150 to 250 bytes) - likely the best 48K answer, but it must be proved to give the
  same pictures as the tool.
- *Fewer new cars at first.* Each extra car stored whole is 1.5 KB; with 1 KB free, not even one fits
  without one of the options above or freeing room elsewhere.
- *128K* holds all ten whole with room to spare.
- The attract sequence needs the featured car's headings in memory while it skids: fine with the
  three-headings method (make one car at a time), awkward with squeezed whole cars.

**Suggested order.** (1) Grant picks a layout and redraws the faces and cars. (2) Build the title with
attract using only the cars in the game today, in the start-up area, to prove the hand-over of choices.
(3) Keys screen (1UP only). (4) Choose driver / car with the three-headings method. (5) 2UP once the
race itself supports two players.

**Main risks.** Memory (above); getting back to the title after a race on 48K; the keyboard cannot
always read many keys held at once, so two players on one keyboard need care in which keys are
allowed (a joystick for 2UP avoids it); the new cars must read well at 16 x 16 at all headings.
