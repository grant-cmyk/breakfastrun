# Breakfast Run - optimisation plan: several tracks and every listed feature in one 48K load

Classification: Internal

16 Nov 2026. Branch `worktree-agent-af7c58c90304a2ad1`, built on `claude/breakfast-run-layout-ik0vpe` at 70f731d.
Nothing here is pushed or merged. Every saving is a BUILD OPTION that is off by default: `bash build.sh` with no
option still makes a `build/racer.bin` byte-identical to 70f731d's (checked with `cmp` after every change).

"Measured" means counted from a real build or timed in the emulators (the `zx` package's 48K, or zxdev).
"Estimate" means worked out from measured counts and not built. Section 6 lists what is not verified.

## The answer in short

- **8.9 KB can be freed with four changes that are built and tested**: the screen copy as a loop (5,571 bytes),
  car pictures drawn upside down instead of stored twice (1,984), one tile routine instead of eight (975), the
  race order's cars drawn from the car pictures (226). Free while racing on track 1: 161 bytes today, 8,894 with
  all four.
- **Three tracks in one load is built**: `build/racer_3tracks.tap` holds tracks 1, 2 and 3; T at the title
  picks the next one, 1 starts the race. After a track is chosen, memory is byte for byte what that track's own
  build has (23,995 bytes compared on each). Choosing takes 0.07-0.08 s. 2,466 bytes are still free in it.
- **Track 5 (the bridge) in the same load is not built.** What stops it: its 904 bytes of bridge code are
  switched in when the game is assembled, at 17 places; one load needs them switched while it runs. On paper it
  fits once the tile pictures are shared between tracks (estimate).
- **Speed in the pack does not change** (12.4 pictures a second before and after, all four savings together).
  Racing alone it drops from 12.6 to 12.2, and at the bridge crossing from 10.2 to 10.0: the looped copy costs
  6,800 T-states a picture. I found no way to make the bridge faster than today at no cost.
- **The looped copy moves a tear that is already there.** Today the last two character rows of the window are
  shown a TV frame late on nearly every picture (the copy is overtaken by the TV beam). With the looped copy that
  line moves up to the window's row 13. An experiment that starts the copy just behind the beam shows no tear at
  all in the window (section 2.1). It needs the main loop re-ordered to be free; as built it wastes time.
- **The "latent fault" is in the test, not the game** (section 5). Found, shown and fixed. A second, real fault
  turned up on the way: the computer cars' speed depends on the picture rate (section 5.2), with a one-line fix
  built as an option.

## 1. Today's memory, measured (`python3 tools/memmap.py build/racer.sym ...`)

Size / free bytes, the four one-track tapes as built at 70f731d:

| Area | Track 1 | Track 2 | Track 3 | Track 5 |
|---|---|---|---|---|
| Title variables and tables 5B00-5DFF | 768 / 4 | 768 / 4 | 768 / 4 | 768 / 4 |
| Stack page 5E00-5EFF | 256 / - | 256 / - | 256 / - | 256 / - |
| Car pictures from 5F00 (80 frames) | 4,958 / 0 | same | same | same |
| Title, plate, podium code up to 7AD6 | 2,168 / 7 | 2,168 / 7 | 2,168 / 7 | 2,168 / 7 |
| Data at 7AD6 (masks, HUD text, row lists, grid) | 618 / 29 | 618 / 1 | 618 / 5 | 618 / 3 |
| Tables at 7D40 (messages, constants) | 704 / 49 | 704 / 49 | 704 / 49 | 704 / 49 |
| Program 8000-BFFF | 16,384 / 23 | 16,384 / 40 | 16,384 / 30 | 16,384 / 2 |
| Start-up area C000-D09F (used once) | 4,256 / 183 | 4,256 / 161 | 4,256 / 136 | 4,256 / 13 |
| Buffer strip D0: mini-map | 90 / 39 | 90 / 30 | 90 / 12 | 90 / 21 |
| Strips D1, D2: arrows' table, row lists | 122 / 0 | 122 / 3 | 122 / 3 | 122 / 3 |
| Strips D3-D7: the arrow's five pictures | 450 / 0 | same | same | same |
| 5B16 (the title's unused bytes): row lists | 54 / 10 | 54 / 4 | 54 / 2 | 54 / 0 |
| 5E46 (stack page): row lists, track 5 only | - | - | - | 90 / 1 |
| Shift tables D800-E7FF | 4,096 / 0 | same | same | same |
| Screen-copy routine E800-FFC2 | 6,083 / 0 | same | same | same |
| FFC3-FFF3: row lists | 49 / 0 | 49 / 1 | 49 / 2 | 49 / 0 |
| **Free while racing** | **161** | **139** | **114** | **90** |

RAM-SWEEP's "safe now" room (the buffer strips, the pocket above the copier, the title's unused bytes, part of the
stack page) is all in use now. Its bigger items were still there to take; this plan builds four of them.

Each track's own data today (`python3 tools/track_sizes.py`):

| | Track 1 | Track 2 | Track 3 | Track 5 |
|---|---|---|---|---|
| Map rows / waypoints | 64 / 46 | 64 / 61 | 84 / 61 | 74 / 61 |
| Tile pictures | 792 (99) | 640 (80) | 352 (44) | 632 (79) |
| Row lists | 646 | 708 | 674 | 676 |
| Row index | 128 | 128 | 168 | 148 |
| Surface map | 576 | 576 | 756 | 666 |
| O map | 576 | 576 | 756 | 0 (read from the row lists) |
| Waypoints | 184 | 244 | 244 | 244 |
| Masks and their index | 108 | 136 | 65 | 88 |
| Arrows' table, mini-map, grid | 46 + 51 + 140 | 61 + 60 + 140 | 61 + 78 + 140 | 61 + 69 + 140 |
| **Total** | **3,247** | **3,269** | **3,294** | **2,724** |

## 2. Every saving, ranked

| # | Saving | Bytes | Where | Speed cost | Risk | Status |
|---|---|---|---|---|---|---|
| 1 | Screen copy as a loop (`LOOP=1`) | 5,571 | EA00-FFC2, fast memory, one piece | +6,800 T a picture (51,370 -> 58,170). Pack 12.4 -> 12.4; alone 12.6 -> 12.2; crossing 10.2 -> 10.0. Tear line moves from row 18 to row 13 | Medium | BUILT. 29 suite runs on tracks 1, 2, 3, 5: all pass but two (below) |
| 2 | Car headings that are another upside down not kept (`FLIP=1`): 31 of 80 pictures | 1,984 (less 50 of code) | 5F00-7AD5, slow memory | about 600-2,000 T a picture (12 T a car line, 39 on a flipped one). Pack 12.4, alone 12.6: no change seen | Low-medium | BUILT. 80 screens pixel-identical; drive_test passes |
| 3 | One tile routine, patched once a picture (`TILE1=1`) | 975 | program | about 27 T a plain tile, about 1,000 T a picture. No change seen | Low-medium | BUILT. drive_test passes (window matches the map), same laps as today |
| 4 | Race order's cars from the car pictures (`TOWER=1`) | 226 | program | none in the race | Low | BUILT (track 5 had it). Same pictures a second, frame for frame |
| 5 | Tile pictures shared by all tracks | about 450 a waiting track | the packed tracks | none | Medium | Estimate (RAM-SWEEP 3.2: 101 pictures cover tracks 1-3; track 5 not counted) |
| 6 | O map out of the race on every track | 576 / 576 / 756 | program | +1,500-2,000 T a picture (estimate) | Medium | Track 5 has it. Others: O's must get the lowest tile numbers first (track 2 has two O's sharing a tile) |
| 7 | Cars mirrored left-right too | about 920 more | 5F00- | 2,000-6,000 T a picture, 256-byte table | Medium | Estimate (RAM-SWEEP). Not exact for every frame |
| 8 | Surface as spans | 320 / 300 / 192 | program | negligible | Low-medium | Estimate (RAM-SWEEP) |
| 9 | Waypoints in 2 bytes | 92 / 122 / 122 | program | about 30 T a look-up | Medium | Estimate. Changes the computer cars' lines slightly |
| 10 | Stack 256 -> 160 | 96 | 5E00 | none | Medium | Estimate (track 5 already uses 90 of it) |

Rows 1-4 together, track 1 (`build/racer_all.tap`): free while racing 161 -> **8,894** (5,571 above the copy
routine, 1,201 in the program, 1,991 below the program, 131 elsewhere). Pack 12.4 pictures a second, alone 12.2.

The car pictures, checked frame by frame (`python3 tools/car_flips.py`): headings 5-11 are headings 3, 2, 1, 0, 15,
14, 13 upside down, pixel for pixel, on all five cars - except GREEN's 6 and 10 (8 pixels differ from 2 and 14
upside down) and WHITE's and GREEN's heading 8 (the flip sits one pixel across). `FLIP=1` keeps those four stored,
so nothing on screen changes. RAM-SWEEP's note of 8 pixels on WHITE was about the left-right mirror (saving 7),
which I did not re-check.

The two failing checks with the looped copy, both understood:
- drive_test "the computer cars are not all the same speed": the fault of section 5.2, not the copy. With
  `PACEFIX=1` it passes.
- track5_test "10 a second is the floor": 10.0 measured, the check wants more than 10.0. A real cost.

### 2.1 The screen copy: size against speed, and the tear

| Version | Bytes | Copy, T a picture | Pack | Alone | TV frames with a torn cell | Where |
|---|---|---|---|---|---|---|
| Today: 152 lines written out | 6,083 | 51,370 | 12.4 | 12.6 | 23% | window row 18 torn, row 19 late |
| Loop of one character row, 8 lines written out (`LOOP=1`) | 404 (512 kept for it) | 58,170 | 12.4 | 12.2 | 22% | row 13 torn, rows 14-19 late |
| The same, started behind the beam (`LOOP=2`, experiment) | 419 | 58,170 + 16,000 waiting | 12.2 | 12.0 | 0.3-0.5% | nothing in the window; 3-5 frames with a panel cell |
| N character rows written out, the rest looped | 404 + 320 N | 58,170 - 358 N | - | - | - | estimate: the tear moves down about a row for every 4 rows written out |
| Plain LDI loop | about 70 | about 63,000 | - | - | - | estimate (16 T a byte); not built |

- The loop copies 12 + 12 bytes a line with six register pairs; IX and IY walk the buffer, the other HL the
  screen. `tests/copy_check.py`: 6,080 lines compared with the buffer over 40 pictures, 0 differ, on each track.
  My first version was wrong in the way RAM-SWEEP's was (a flag byte carrying picture data): the check caught it.
- I found no version that is both small and as fast as today's. Sharing the code between lines needs pointers kept
  in registers, and that costs at least 28 T a line.
- **The tear.** The TV beam reaches the window 16,128 T after the interrupt and moves a line every 224 T. The
  copy takes about 340 T a line today, so the beam catches it near the bottom: zxdev's tear report shows row 18
  torn in 23% of TV frames, which is nearly every picture. The loop is slower, so it is caught sooner.
- **Starting behind the beam** (`LOOP=2`): the copy begins after the beam has passed the window's top and can
  never catch it, so the whole picture changes between two TV frames. Measured: no torn cell in the window over
  a lap. It runs over the next interrupt with interrupts off, so that interrupt is taken by hand afterwards
  (frame counter and engine sound; exactly one is missed every time, by arithmetic). As built it waits 16,000 T
  doing nothing. The real version would do the next picture's driving and sums in that time, which needs the main
  loop re-ordered and the tests told that the picture on screen is one step behind the cars. Not built.

## 3. The budget: the feature list against the memory

### 3.1 What each feature costs

| | Feature | Code | Data a track | Speed | Status |
|---|---|---|---|---|---|
| a | Tracks chosen from one load | 172 (unpacker 68, T key, name) + about 200 for a real menu | waiting: 1,946 / 2,062 / 1,742 packed (tracks 1 / 2 / 3, measured, each with its own tile pictures); about 1,050-1,300 with shared pictures (estimate). Racing: the largest track's tables, 3,641 bytes for tracks 1-3 | none; 0.07-0.08 s to choose | BUILT for tracks 1-3, text only |
| a | Track 5 in that load | about 1,050 (904 of bridge.asm, 17 switched places) | about 1,900 packed with its own pictures; 90 more row-list bytes | about 200-400 T a picture on the other tracks (estimate) | Not built |
| a | Track 4 (72 x 91, 92 waypoints) | about 60 (2-byte race progress) | racing: about 350 more than track 3 (surface 819, O map 819, row index 182, waypoints 368); waiting: about 1,500-2,200 | negligible | Estimate |
| b | Breakfast things on every track | none | about 300 of row lists a track while racing, about 200 more packed; pictures 440 and masks 108 once if shared | what track 1 pays today (it has them all at 12.4) | Estimate |
| c | Bridge as built at 10.2 | - | - | 10.0 with the looped copy (measured). TILE1 and FLIP on track 5: not measured | See 3.3 |
| d | Arrows, mini-map, mug, spoons, crew chief, faces, jingles, key-skip | 0 | 0 | 0 | In every build here, tests pass |
| d | A different jingle pair a track ("Order Up") | about 20 | about 130 raw, about 100 packed, unpacked over the jingle table | none | Estimate |
| e | Choose your player | about 300-400, title only (can sit below the program) | 0 | none | Estimate |
| e | Sad face when overtaken | about 100-150 (the sad frames exist for the podium) | 0 | only when your place changes | Estimate |
| e | Set-up keys before the lights, shown | about 200-250 | 0 | none | Estimate |
| f | 128K | about 150 on the 48K side | none in the 48K's memory | none | Design only, section 7 |

### 3.2 What fits in one 48K load

| Combination | Needs | Have | Left | Pack / alone / crossing | Basis |
|---|---|---|---|---|---|
| Today, one track a tape | - | - | 161 / 139 / 114 / 90 | 12.4 / 12.6 / 10.2 | measured |
| One track, savings 1-4 | - | 8,894 | 8,894 | 12.4 / 12.2 / - | BUILT `racer_all.tap` |
| Tracks 1 + 2 | 4,125 + 60 | 5,571 + 226 | 1,446 above the copy routine, 189 program | 12.4 / 12.2 | BUILT `racer_2tracks.tap` (savings 1, 4) |
| Tracks 1 + 2 + 3 | 5,991 + 306 | 8,894 | **2,466** (1,322 high, 895 program, 249 low) | 12.4 / 12.2 | BUILT `racer_3tracks.tap` (savings 1-4) |
| + track 5 | about 3,050 | 2,466 | about -600 | - / - / 10.0 | estimate: does not fit as it stands |
| + track 5, pictures shared (saving 5) | about 3,050 - 1,800 | 2,466 | about +1,200 | 10.0 at the crossing | estimate |
| + things on all four (b) | about 900 | 1,200 | about +300 | as track 1 today | estimate: needs saving 6 or 8 to be safe |
| + savings 6, 7, 8, 9, 10 | - | about +2,900 | about 3,200 | -2,000 to -8,000 T a picture | estimate |
| + e (player, sad face, set-up) and per-track jingles | about 1,100 | 3,200 | about 2,100 | no change | estimate |
| + track 4 | about 1,900-2,600 | 2,100 | -500 to +200 | - | estimate: too close to promise |

Reading it: **tracks 1, 2, 3 and 5 with all their things and every feature in d and e fit one 48K load on
paper**, with about 2 KB over, but only after savings 5 and 6 are built, and both are estimates today. **Track 4
as a fifth track does not fit safely.** It is the natural first use of the 128K's extra memory, or it replaces a
track.

### 3.3 Frame rate

- In the pack: 4.02 TV frames a picture today, 4.03 with the loop, 4.04 with all four savings. All 12.4 a second.
- Alone: 3.95 -> 4.08 with the loop (12.6 -> 12.2). The pictures that made 3 TV frames mostly stop doing so.
- Bridge crossing: 10.2 -> 10.0 with the loop. Nothing found here gives time back at the crossing. The four
  efficiency options on `docs/design/tracks/bridge_efficiency_options.png` were not measured by me.
- So requirement c ("no worse than 10.2, same elsewhere") is **met in the pack, missed by 0.2 at the crossing and
  by 0.4 alone** if the loop is used. Without the loop, savings 2-4 give 3.2 KB at no measurable cost, which holds
  two tracks but not three.

## 4. Recommended order of work

Each step is one thing to approve. "You see" is what changes on screen.

| Step | What | You see | Gain | Risk |
|---|---|---|---|---|
| 1 | Test fixes of section 5 (done here) | nothing | the false alarm is gone | none |
| 2 | Computer cars' pace counted in pictures (`PACEFIX=1`) | the four computer cars differ in speed in the pack as they do when you are far away; lap times shift a few per cent | their speed stops depending on the picture rate, so later steps do not change the racing | changes the feel: wants your drive. Test thresholds for lap times need re-setting |
| 3 | Savings 3 and 4 on every track (`TILE1=1 TOWER=1`) | nothing | 1,201 bytes of program | low |
| 4 | Saving 2 (`FLIP=1`) | nothing (31 of the 80 pictures go; four stay stored because their flips are not exact: WHITE's heading 8 and GREEN's 6, 8 and 10) | 1,984 bytes below the program | low-medium; the title's cars were checked by eye only |
| 5 | Looped copy (`LOOP=1`) | racing alone a little slower; the late band at the window's foot grows from 2 rows to 6 | 5,571 bytes | medium |
| 6 | Copy started behind the beam, main loop re-ordered | no tearing at all in the window | undoes step 5's tear and today's | medium-high: every test that reads the screen needs adjusting |
| 7 | Track menu on the title, tracks 1-3 | T (or the menu) picks a track; its name shows | three tracks, one tape | low: it is `racer_3tracks.tap` with a proper menu |
| 8 | Tile pictures shared between tracks; O map out of the race everywhere | nothing | about 1,800 + 600-750 | medium |
| 9 | The bridge switched at run time; track 5 joins the load | four tracks, one tape | - | medium-high: 17 places in the hottest code |
| 10 | Things back on tracks 2, 3, 5 | the breakfast things on every track | - | low for memory; speed as track 1 |
| 11 | Choose your player, sad face, set-up keys, per-track jingles | as named | - | low each |
| 12 | 128K: track 4, more tunes | extra menu lines on a 128K | - | separate work, section 7 |

Steps 3 and 4 can go in now and by themselves put things back on tracks 2 and 3 (3.2 KB at no speed cost).

## 5. The latent fault

### 5.1 What it was

**Cause: `tests/drive_test.py` wrote a car's place into memory while the game was part-way through moving that
car, and the game wrote its old place back.** The game is not at fault.

- The ramming check parks the computer cars at y = SY + 58, later puts one at y = SY - 8 in front of you. The
  difference is 66 pixels: the "jump" was the car going back to where it had been parked.
- The test stops the emulator every 0.02 s wherever the program happens to be. Reproduced at commit 23ce62f with
  16 or more bytes added before `jb_end` (19 of 20 sizes tried fail the same way). In the failing build the stop
  before the write is at `ph_yp+10`, inside `physics`, with IX on that car: the car's y has been read into A and
  not yet stored. The test writes y; the next instruction stores the old value. One instruction decides it.
- Why extra bytes mattered: they shift the timing of the whole run by a few T-states, which moves where each
  0.02 s stop lands. HEAD passed with every size from 1 to 23 only by where its stops happened to fall.
- Shown directly: `python3 tests/put_race_probe.py` stops at `ph_yp+10` on purpose, writes the place, and the car
  is 62 pixels off a frame later.
- **Fix**: the test now writes places between pictures (at `copy_done`), as its head-on check already did. With
  that the 19 failing builds all pass. The head-on check had the mirror-image fault (it read the cars in the
  middle of `bump`: the count already up, the kick not yet given) and is fixed the same way.
- Not traced: which instruction's timing the added bytes change. It does not matter for the conclusion.
- Other tests that write places with the game running (o_test notes the same thing) were not changed.

**Restructuring memory is safe** as far as this fault goes. Four restructurings are built here and their suites
pass.

### 5.2 A real fault found on the way: the computer cars' speed depends on the picture rate

- `pace_gate` lets a computer car push on PACE of every 16 of its thinking frames, spread evenly by a
  bit-reversed count. But the cars are moved once a picture, with the buttons of their last think. At a steady
  4 TV frames a picture only the even counts are ever asked, and every car with PACE 8 or more is pushed every
  picture: they all run at top speed and their differences go.
- Measured, track 1, laps of the four cars: 19.4 19.0 21.6 18.6 s today in the test (3-frame pictures: the
  test parks you) against 19.0 19.1 19.1 18.7 with the looped copy (4-frame pictures). Track 2: FRANK 27.8 ->
  25.5 s, SPIKE 28.4 -> 32.1 s. In the pack the game runs at 4 frames today, so this is already how it races.
- `PACEFIX=1` counts the gate in pictures: 18.8 19.6 21.6 18.0 with today's copy, 18.9 19.5 21.6 18.4 with the
  loop. The same either way, and drive_test passes on both.
- It changes how the race feels in the pack, so it is step 2 above and yours to approve.

## 6. What is not verified

- Nothing has been driven by a person. All figures are from autopilot laps and the test suites.
- **Three checks fail on the multi-track tapes.** Results of `bash tests/multi_test.sh racer_3tracks`: track 1
  drive 52 of 53, arrow 23 of 23, copy exact; track 2 track test 35 of 36, arrow 23 of 23; track 3 track test 36
  of 36, arrow 23 of 23; memory after choosing exact on all three; unpacking round and back exact. The failures:
  (1) track 1, "the race order shows gaps to the leader": the leader's row shows a gap and the second row none.
  Two computer cars averaged the same 18.2 s a lap in that race, which suggests a dead heat at the line; not
  investigated, and it did not happen on the two-track tape. (2) Track 2, "no lap is much longer than another":
  21.1 to 29.2 s against a limit of 1.35 times. (3) On the two-track tape, "the fastest computer car is
  competitive": 17.4 s against a limit near 17.5. Memory is identical to each track's own build, so (2) and (3)
  are that build's racing with `PACEFIX` and the savings, not the track switching: thresholds set for today's
  pace. None of the three was run down to a cause.
- The full 15 suites were run on today's code and on `LOOP=1` (tracks 1, 2, 3, 5). On the multi-track tapes only
  the suites that take a tape from the environment were run: drive, arrow, copy on track 1; the track test and
  arrow on tracks 2 and 3. Finish, title, crew, damage, nos, plate, setup, skip, stuck were not run on them.
- `FLIP=1` and `TILE1=1` were tested on track 1 by themselves and on tracks 1-3 inside the three-track tape, not
  on track 5. The title's lapping cars with `FLIP=1` were looked at once, not compared pixel for pixel.
- `LOOP=2` (the copy behind the beam) is an experiment: only the tear report and a lap were run. The interrupt
  taken late shifts one engine-sound flip a picture by up to a frame: not listened to.
- How the multi-track tool finds a track's bytes: it compares the tracks' memory at the title screen and leaves
  out bytes that change by themselves. A byte that belongs to a track but is the same in every track compared, or
  one that only differs after a race, would be missed. The byte-for-byte check after choosing covers the first
  case at the title; a race on a track after racing on another was not run.
- Sizes for shared pictures, O map, spans, 2-byte waypoints, mirrored cars, track 4, the bridge at run time and
  every feature in e are estimates. Track 5's pictures were not checked against the other tracks' for sharing.
- Tear timing is the emulator's, within a few T-states of a real machine. On a 128K the beam timing differs.

## 7. 128K: design (no build)

**Rule: the 48K tape stays the whole game.** The first block is today's game with its tracks packed inside. A
48K never reads past it. A 128K reads further blocks into its extra pages.

- **Detecting**: at start-up, write to port 7FFD to bring page 1 in at C000, write a byte, bring page 0 back, see
  whether it changed. A 48K ignores the port. Keep bit 4 set always (the 48K ROM): the interrupt set-up relies on
  that ROM's bytes at 39xx.
- **Why pages suit this game**: the back buffer, shift tables and copy routine all sit at C000-FFFF, the part a
  128K swaps. So pages cannot change during a race, but at the menu they can.

| Page | Holds | Note |
|---|---|---|
| 0 | as the 48K: buffer, shift tables, copy routine, packed tracks | always in while racing |
| 1 | tracks 1-3 and 5, unpacked (about 3.7 KB each) | choosing is a plain copy, no unpacking |
| 3 | track 4 and later tracks; each track's jingle pair | the tracks a 48K cannot hold |
| 4 | the race tune for the AY chip, a tune a track | the AY build option exists (`AY=1`) |
| 6 | spare (bigger title art, more faces) | |
| 5, 2, 7 | screen, program, second screen | fixed |

- **Choosing a track**: one entry point, "put track N in its working places", with two sources behind it: the
  packed store (48K) or a page (128K). The 128K path is about 60 bytes kept below C000: page in, copy, page out.
  Working places that are themselves above C000 (the buffer strips, the pocket at FFC3: about 230 bytes today)
  must go through a small buffer below C000, or better be moved below C000 when the multi-track layout is made
  final.
- **Loading**: the extra blocks follow the game on the same tape. The 128K start-up calls the ROM's tape routine
  for each (with the 48K ROM in). A 48K has already started the game and the tape can be stopped.
- **The menu**: a 48K shows tracks 1, 2, 3, 5. A 128K shows those and track 4 onwards, and a line for the AY tune.
- **Watch**: the 128K's frame is 70,908 T and its lines 228 T, so the copy-behind-the-beam start time needs its
  own constant; pages 1, 3, 5, 7 are slow memory on a 128K, which is fine for data read at the menu.

## How to build each proof

| Tape | Command | What it shows |
|---|---|---|
| `build/racer_looped.tap` | `LOOP=1 OUT=racer_looped bash build.sh` | the looped copy, track 1 |
| `build/racer_looped_late.tap` | `LOOP=2 OUT=racer_looped_late bash build.sh` | the copy started behind the beam (experiment) |
| `build/racer_tower.tap` | `TOWER=1 OUT=racer_tower bash build.sh` | race order's cars from the car pictures |
| `build/racer_tile1.tap` | `TILE1=1 BDIR=tile1 OUT=racer_tile1 bash build.sh` | one tile routine |
| `build/racer_carflip.tap` | `FLIP=1 TOWER=1 BDIR=flip OUT=racer_carflip bash build.sh` | cars drawn upside down |
| `build/racer_all.tap` | `LOOP=1 TOWER=1 FLIP=1 TILE1=1 BDIR=all OUT=racer_all bash build.sh` | all four, track 1 |
| `build/racer_looped_pace.tap`, `racer_pace.tap` | `PACEFIX=1` with and without `LOOP=1` | the pace fix |
| `build/racer_2tracks.tap` | `MULTI_ENV="PACEFIX=1" python3 tools/make_multi.py` | tracks 1 and 2; T at the title, then 1 |
| `build/racer_3tracks.tap` | `MULTI_ENV="PACEFIX=1 TILE1=1 FLIP=1 TOP_ROWS=292" OUT=racer_3tracks python3 tools/make_multi.py "1 2 3"` | tracks 1, 2 and 3 |

`tools/make_multi.py` needs the `zx0` program (github.com/einar-saukas/ZX0, built with gcc; `ZX0=path`). After a
build with options, run plain `bash build.sh` again: it rewrites `src/options.asm`, `src/data.asm` and
`src/bigcars.asm` to the defaults.

Tests added: `tests/run_all.sh <name> [OPTION=1 ...]` (every suite, every track, in a scratch copy),
`tests/multi_test.sh [tape]`, `tests/multi_mem_check.py`, `tests/unpack_time.py`, `tests/copy_check.py`,
`tests/carflip_check.py`, `tests/tearlap.py`, `tests/speed_table.sh`, `tests/put_race_probe.py`.
Tools added: `tools/make_multi.py`, `tools/memmap.py`, `tools/track_sizes.py`, `tools/car_flips.py`.

### How the multi-track build works

Each track is built by itself with the same options and with every block of track data padded to the longest,
so that every routine and table sits at the same address whichever track it is. Each build is run to its title
and its memory read. A byte that is steady in each build and not the same in all of them belongs to a track: its
tiles, row lists, surface, O map, waypoints, masks, arrows' table, mini-map, grid, and the numbers the assembler
built into the code (map height, waypoint count, the start, the cans' places: 31 short stretches). Long stretches
are packed with ZX0, short ones kept as they are. `src/hp.asm` (172 bytes: ZX0's own 68-byte unpacker, the T key,
the name) unpacks one track straight onto its working places. What must sit unpacked during a race is exactly
today's tables, at today's places, sized for the largest track: nothing new is read packed while racing.
