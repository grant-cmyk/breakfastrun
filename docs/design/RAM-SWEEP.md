# Breakfast Run - RAM sweep, 15 Nov 2026

Classification: Internal

Read-only sweep of branch `claude/breakfast-run-layout-ik0vpe` at e12fb0b. Nothing in the repo was
edited, built into or committed (`git status` clean at the end). All work is in scratch copies under
`/tmp/claude-0/-home-user/fffe8284-32d1-5fde-8a48-51a919ed51ce/scratchpad/sweep/` (scripts in `py/`,
proof build in `cp/`). The scratch builds of tracks 1, 2 and 3 are byte-identical to
`build/racer.bin`, `racer_track2.bin`, `racer_track3.bin` (`cmp`).

"Measured" below means counted from the real data or binary, or timed in zxdev (the project's own
emulator). "Estimate" means worked out from instruction counts and measured call counts; not built.

## 1. The answer in short

- **About 11.8 KB can be found** in a 48K machine: about 0.85 KB free today at no cost, about
  4.4 KB more for small code changes costing under 2% of a picture's time in total, and about
  6.6 KB more from two format changes (the screen-copy routine as a loop; cars mirrored both ways).
- **Two tracks in one 48K load is reachable**, and without touching the screen-copy routine: the
  "safe now" and "worth doing" packages together (about 5.2 KB) hold two tracks with a menu.
  With the looped copy routine as well, all three built tracks fit in one load, and on paper all
  five with the bridge (estimate).
- **The tracks share almost all their art.** Tracks 2 and 3 use 1 and 0 tile pictures that track 1
  does not have. A track's own data is 2.4 to 2.9 KB raw and packs to 0.7 to 1.2 KB.
- **Compression does not help a one-track tape.** Race data has to sit unpacked while the race
  runs. It helps only for tracks that are waiting their turn, and for tape time.
- **Moving the title and podium code into the back buffer is not worth it**: that code packs to
  82% only, a net gain near 500 bytes for a two-stage build.

## 2. Memory map as it stands (track 1, measured from racer.sym)

| Area | Addresses | Bytes | Holds | Free |
|---|---|---|---|---|
| Title variables TS | 5B00-5B4B | 76 | title's car and key variables | 54 (5B16-5B4B: `a_sav`, never referenced) |
| Table block TD | 5B4C-5DFF | 692 | title3 tables, pod_anim, jingles, mood faces (688) | 4 |
| Stack | 5E00-5EFF | 256 | deepest seen 56 bytes | about 96-160 (see 5.4) |
| Car frames | 5F00-71FF | 4,864 | 80 frames (5 cars x 16 headings) | 0 |
| Title, plate, podium code | 7200-7ACE | 2,255 | title.asm 1,072; plate_low/slow, dmgicon | about 8 |
| TOPMEM data | 7AD6-7D3F | 618 | masks, HUD text, 320 of row lists, cars_init (589 used) | 29 on track 1 (tracks 2 and 3 use 28 and 24 of them) |
| LOWTAB | 7D40-7FFF | 704 | 5 blocks of 128 + 64 (BUFC) | tail pockets about 49 (known) |
| Program | 8000-BFFA | 16,379 | code and data | 5 |
| Back buffer | C000-D7FF | 6,144 | laid out like the screen; start-up code loads here | 672 (see 4.4) |
| Shift tables | D800-E7FF | 4,096 | 16 pages, built at start-up | 0 |
| Screen-copy routine | E800-FFC2 | 6,083 | written at start-up: 152 rows x 40 bytes + jp | 0 |
| Top pocket | FFC3-FFF3, FFF7-FFFE | 57 | nothing (interrupt jump at FFF4, FFFF) | 57 |

The tape image is 5F00-CE10 (28,433 bytes). The start-up area after `code_end` runs to CE11 and may
grow to D7FF: 2,543 bytes free there, used once.

## 3. The world data of each track (measured: `py/tracks.py`, `py/an1.py`, `py/an2.py`)

### 3.1 Bytes per table

| Table | Track 1 | Track 2 | Track 3 | Where it lives |
|---|---|---|---|---|
| Map rows | 64 | 64 | 84 | |
| Tile pictures (8 bytes each) | 792 (99) | 640 (80) | 352 (44) | program, page-aligned |
| Row lists (count + column, tile pairs) | 646 | 708 | 674 | 320-388 at TOPMEM, rest in program |
| Row index (2 a row) | 128 | 128 | 168 | program |
| Surface map (1 bit a tile) | 576 | 576 | 756 | program |
| O map (1 bit a tile) | 576 | 576 | 756 | program |
| Waypoints (4 bytes each) | 184 (46) | 244 (61) | 244 (61) | program |
| Mask index | 20 | 24 | 9 | TOPMEM |
| Masks (8 bytes each) | 88 (11) | 112 (14) | 56 (7) | TOPMEM |
| cars_init (grid) | 140 | 140 | 140 | TOPMEM |
| **Run-time total** | **3,150** | **3,148** | **3,155** | |
| Mini-map picture | 264 | 264 | 264 | start-up area only (drawn once) |

The three totals are within 7 bytes of each other because each track was trimmed to the same ceiling.

### 3.2 What is the same across tracks

- **Tile pictures**: 99, 80 and 44 on the tracks; 101 different pictures in all. 34 are on all
  three. Track 2 has 1 picture track 1 lacks; track 3 has none.
- **Masks**: 24 different masks in all (11, 14, 7 a track).
- The cereal O, the grid boxes, the start line, the cans and every breakfast thing are the same
  drawings. A thing placed on another track cuts into the same tiles, because things sit on the
  8-pixel grid.
- One shared art block for all three tracks: 91 plain + 41 masked tile slots = 1,056 bytes of
  pictures, 192 of masks, 41 of mask index: **1,289 bytes**, against 900, 776 and 417 a track
  today. (A tile that is plain on one track and masked on another needs two slots.)
- **A track's own data** (rows, index, surface, O map, waypoints, mini-map): 2,374 / 2,496 / 2,862
  bytes raw, plus about 60 bytes of numbers (start, grid, cans, mini-map origin).
- Track numbers are built into the code as fixed values today (MAPH, NWP, WS, the cans' places,
  MMX0/MMY0, the grid): about 40 places. A second track in memory needs a table that sets them.

### 3.3 Encodings tried on the real data

Sizes are from my own sizer using ZX0's bit costs (`py/lz.py`). The real `zx0` program was not run
(see section 9); its output should be the same size or slightly smaller.

| Encoding | Track 1 | Track 2 | Track 3 | Note |
|---|---|---|---|---|
| Whole world block, raw | 3,146 | 3,144 | 3,111 | without the row index (rebuilt on unpacking) |
| Whole block, ZX0 | **1,450** | **1,594** | **1,196** | 46%, 51%, 38% |
| All three blocks as one ZX0 stream | 3,833 | | | 9,401 raw |
| Own data only (art shared), ZX0 | 928 | 1,178 | 985 | rows, surface, O map, waypoints, mini-map |
| Own data, O map and mini-map derived, waypoints as steps, ZX0 | 685 | 822 | 672 | 1,316 / 1,408 / 1,554 raw |
| Same with the surface as spans, ZX0 | 665 | 797 | 663 | spans gain almost nothing once packed |

By table (raw to ZX0, track 1): tiles 792 to 466; rows 646 to 510; surface 576 to 115; O map 576 to
114; waypoints 184 to 120; mini-map 264 to 82.

Single ideas, each measured:

- **O map from the row lists**: exact. Every O bit has a row-list entry and every O-tile entry has
  its bit (128 / 176 / 207 O's). On track 2 two O's share a tile with other pixels, so the O tiles
  need the lowest tile numbers for a one-compare test. The O map (576 / 576 / 756 bytes) can go
  from the race altogether if the bump check walks the row list: see 5.5 below.
- **Surface from the row lists**: not possible. The road is not in the row lists (it is white
  cloth); they hold O's, things, grid, line and cans only.
- **Surface as road spans** (count + start, end; at most 3-4 spans a row): 256 / 276 / 564 bytes
  against 576 / 576 / 756. Kept inside each row's record there is no second index.
- **O map and surface merged**: no gain found. Only 31 / 34 / 34 of the O's sit on road tiles and
  they are not at the ends of the road spans, so the O's cannot ride on the span data.
- **Waypoints**: two bytes each as x/4, y/4: 92 / 122 / 122. As a start and one-byte steps:
  96 / 126 / 126 (steps are at most 42).
- **Mini-map made at start-up**: it is already start-up-only data, so this saves no race memory.
  It matters for tracks waiting in memory (264 bytes each, 82-132 packed). A mini-map drawn from
  the surface map would not be pixel-identical to today's (8-pixel tiles against a 12-pixel scale);
  not tried.
- **Rows trimmed top and bottom** (rows with no road at all): 126 / 72 / 72 bytes of surface and
  about the same of O map.
- **Tile pictures that are flips of each other**: 99 to 68 on track 1. Not recommended: the tile
  drawer is the hottest code in the game.

What must stay unpacked because the race reads it in place: tile pictures (page-aligned), row lists
(the cans are switched on and off by writing into them), row index, surface, O map (if kept),
waypoints, masks, cars_init. Only the mini-map and the fixed screen pictures are read once.

## 4. Big fixed blocks

### 4.1 Car frames, 4,864 bytes at 5F00 (measured: `py/cars.py`)

- 80 frames, all used: 5 cars x 16 headings, 4 bytes a row, 9 to 17 rows.
- **Headings 9-15 are exact left-right mirrors of 7-1, and 5-8 are exact top-bottom flips of 3-0**,
  pixel for pixel, on all five cars. One exception: WHITE has 8 pixels (2 of mask, 6 of ink) that
  differ at one angle (headings 2/14, 6/10), and its heading 0 and car 2's sit one pixel across
  from their flips.
- So 5 stored headings (0-4) carry everything: **1,484 bytes instead of 4,864**.
- Making the other frames at start-up saves nothing (all 80 are needed while racing). The saving
  comes from flipping as the car is drawn:
  - Top-bottom flip: read the frame's rows from the last upward. Store 9 headings (0-4, 12-15):
    about 2,660 bytes. **Saves about 2,200**, less about 100 of code. Cost about 20 T a row:
    under 1,000 T a picture (51 car rows a picture, measured).
  - Left-right flip as well: needs a 256-byte bit-reversal table and about 19 T a byte. Store 5
    headings. **Saves about 3,120 in all** (after the table). Cost about 2,000 T a picture
    typically, 6,000 worst case (five mirrored cars in view). Estimates.
- The title's own car drawer (title2.asm) reads the same frames and needs the same change.
- **`tower_cars` (data.asm, 320 bytes) is a second copy of each car's heading-4 frame**, padded to
  16 rows: checked row for row, all five cars. Drawing the race order's cars from the frames
  saves about 280 bytes net (estimate); that code runs only when the order changes.

### 4.2 Shift tables, 4,096 bytes at D800

- 16 pages: for each shift 0-7, one page for the left byte and one for the right. Used by
  draw_car, the tile drawers, hud.asm, strip.asm and title2.asm.
- All 16 are needed. The access map shows every page read across its range (only 14 entries a page
  never read in three sessions).
- Halving to 8 pages means doing the other four shifts in code: about 16 T more per look-up, four
  look-ups a car byte, roughly 10,000 T a picture with the pack in view. Not recommended.
- The only cheap cut is shift 0 (one page of zeros, one of the byte itself): 512 bytes, for a
  special case in the car and tile drawers costing about 150 bytes. Net about 350. Low value.

### 4.3 The screen-copy routine, 6,083 bytes at E800 - built and measured

- Today: 152 rows x 40 bytes of POP/PUSH code. Measured 51,648 T a picture.
- **Looped version built in scratch** (`cp/src/racer.asm`, `lc_src`): 16 unrolled half-rows and a
  loop over the 19 character rows; 6 + 6 register pairs a row; IX walks the buffer, HL the screen.
  **386 bytes**. Copy checked against the buffer on 40 pictures: 6,080 rows, 0 differences.
- **Frees 5,697 bytes** (E982-FFC2), in fast memory, in one piece.
- **Cost, measured with tests/zxlap.py: 58,114 T a picture, +6,466 T (2.6% of a picture).**

| One lap, autopilot | Today | Looped copier |
|---|---|---|
| In the pack: pictures at 3 / 4 / 5 TV frames | 9 / 237 / 17 | 9 / 247 / 19 |
| In the pack: average TV frames a picture | 4.03 | 4.04 |
| Alone: pictures at 3 / 4 / 5 / 6 | 41 / 224 / 8 / 1 | 1 / 245 / 15 / 1 |
| Alone: average TV frames a picture | 3.89 | 4.06 |

- In the pack nothing changes. Racing alone, the pictures that made 3 TV frames (15% of them)
  drop to 4: about 4.5% slower there.
- A plain LDI loop would cost about 17,000 T a picture; a stack copy with patched addresses about
  the same as the version built. The built one is the cheapest I found.
- First attempt was wrong (a flag register carried picture data and was changed by `inc h`); the
  check caught it. The fixed order pushes AF first.

### 4.4 Back buffer margins and rows 160-191

- The buffer is laid out like the screen, so its rows 160-191 are eight strips of 128 bytes
  (pages D0-D7, low byte 80-FF).
- Rows 160-167 (low byte 80-9A) are used: tiles overflow below the window.
- **Rows 168-191 (low byte A0-F9) are never read or written**, in three full sessions (title, keys
  screen, 3-lap race, podium, title again) on tracks 1, 2 and 3. Exceptions: D2C0-D2EF holds
  `cloth_pat` and `PNUM`; the last 6 bytes of a strip (FA-FF) can take an interrupt's pushes.
- **672 bytes free**: seven strips of 90 (D0, D1, D3-D7) and 42 in D2. The tables that were there
  moved to LOWTAB when the window grew a row, but only row 160-167 was needed by the window.
- The left and right margins of rows 0-159 are all written by the cloth fill: nothing there.
- Best use: the map's row lists. Each is a separate record of at most 39 bytes reached through the
  row index, so they pack into 90-byte strips with little waste, and all 646-708 bytes fit. That
  empties `toprows` at TOPMEM (320-388) and the rest from the program (about 330).

### 4.5 Unrolled tile and cloth drawers

- `gen_tiles.asm`: 1,158 bytes, eight routines (`tdraw_0`..`7`) that are the same eight row bodies
  with the character-row step in a different place. The block packs to 72 bytes, which shows how
  repetitive it is.
- One routine of eight bodies does the same if a tile is drawn in two calls, entering part-way
  (rows before the step, the step, rows after). **Saves about 990 bytes** (estimate: about 170
  stay). Cost one more call a tile, about 45 T; 35 plain tiles a picture (measured) = about
  1,400 T a picture, 0.6%.
- Cloth fill (37,900 T a picture, about 250 bytes): leave. It is small and the second hottest code.

### 4.6 Fonts, title data, faces, jingles, strings

| Item | Bytes | Finding |
|---|---|---|
| ROM font | 0 | already used by print_at and hud.asm (0x3C00) |
| `sfont` (digits 3 x 5) | 50 | tight already |
| `LFONT` (letters, 15 bits each) | 60 | tight already |
| `faces` | 160 | 5 x 32, needed in the race |
| `faces_mood` | 249 | stored as differences already; packs to about 90% |
| Jingles | 131 | two parts; in the table block |
| Title script and tables (TD block) | 688 | packs to 603 |
| Messages (strip_a/e/f/g/h) | about 500 | 5-bit letters would save about 150 for about 60 of code; low value |
| `strip_img`, `logo`, `minimap` | 648 + 126 + 264 | start-up area only: no race memory |
| `sqtab`, `sq4` | 768 + 256 | the range used is 0..383 by the code's own limits; leave |

## 5. Code

### 5.1 Dead or duplicate code

- Label-level check of the whole source against the symbol file and an emulator access map: the
  only labels nothing refers to are the known unused variables (`mu_wait`, `mu_ph`, `mu_off`,
  `mu_ptr`, `mu_va`, `mu_vb`, `mu_vn`, `mu_beat`, `isr_bc`: 11 bytes flagged; about 22 with the
  `yg_`, `bar_next`, `MSG_T` ones of the earlier audit).
- No dead routine of any size is left. Code not run in my sessions (`su_k1` 42 bytes, `nt_1` 36,
  `ph_xout`/`ph_yout` 50, `trg_rand` 21) is live code for things the script did not trigger.
- Duplicate data found: `tower_cars` (4.1). `a_sav` (title.asm, 54 bytes at 5B16) is declared and
  never used.

### 5.2 Title-only and podium-only code

The buffer is free while no race runs, apart from the 2.4 KB race picture the title keeps there, so
about 3 KB is available. What qualifies, with its size and what it packs to (ZX0 sizer):

| Code or data | Bytes | Packed |
|---|---|---|
| title.asm (title, keys screen, script, egg) | 1,072 | 921 |
| `t_anim` (plate_slow.asm) | 231 | 129 |
| `podium` and `tc_tab` (plate_slow.asm) | 443 | 363 |
| title2.asm (the title's car) | 407 | 365 |
| `t_run` (clothmini.asm, the RUN logo) | 176 | 159 |
| Podium words `pd_t*` (clothmini.asm) | 128 | 122 |
| TD block (title3 tables, pod_anim, jingles, mood faces) | 688 | 603 |
| **All, one stream** | **3,145** | **2,573** |

- The title comes back after every race, so this code cannot be thrown away after the first show;
  a packed copy has to stay. Net gain: 3,145 - 2,573 - about 70 (unpacker) = **about 500 bytes**.
- It would need a two-stage build (that code assembled to run at buffer addresses) and care with
  the start jingle, which plays over the grid picture while the buffer is in use.
- Verdict: not worth doing on a 48K. On a multi-load tape it changes: see 6.

### 5.3 Start-up-only code still in the main program

None found. `start_once`, `screen_once`, `make_tables`, `make_copier`, `im2_on`, `draw_frame` and
the fixed pictures are all in the start-up area already. Note for a track menu: `screen_once` draws
the mini-map once and is then gone; choosing a track later needs about 60 bytes of that kept.

### 5.4 to 5.7 Smaller items

- **5.4 Stack**: 256 bytes are kept (5E00-5EFF). Deepest seen: 54-56 bytes on all three tracks
  (zxdev stack_watch). Keeping 160 frees 96 bytes next to the table block; keeping 96 frees 160.
- **5.5 O map out of the race**: bump check walks the two row lists instead (rows have 3.5-5
  entries on average, 19 at most). Saves 576 / 576 / 756 bytes (819 on track 4), less about 40 of
  code. The check runs 5 times a picture (measured, 1,702 T today); estimate +1,500-2,000 T a
  picture.
- **5.6 Surface as spans** in each row's record: saves 320 / 300 / 192. `surface` runs about once
  a picture for you plus the cars' friction; cost negligible. Generator and one routine change.
- **5.7 Waypoints in two bytes** (x/4, y/4): saves 92 / 122 / 122. Positions move by up to 3
  pixels, so the computer cars' laps change slightly and the lap tests need re-running.

## 6. Platform

### 6.1 A 48K multi-load

- The game loads once as now. The menu picks a track; the game calls the ROM's tape routine
  (LD-BYTES, 0x0556) to load one block straight into the track's working area, or packed into the
  back buffer and unpacked from there (no extra memory: the buffer is idle at the menu).
- Resident cost: about 40 bytes for the load call and error handling, about 70 more for an
  unpacker, plus the table that sets the track's numbers (about 120). About 110-230 bytes.
- Track block: 3.2-3.4 KB raw with the mini-map and numbers; 1.2-1.6 KB packed.
- **Tape time at the ROM's speed (1,500 baud nominal, about 170 bytes a second on mixed data)**:
  raw about 20 s of data plus a 5 s lead tone, about 25-27 s with a header block; packed about
  8-10 s of data, about 13-15 s in all. The whole game today is 28,433 bytes: about 2 min 50 s.
- On a real tape the tracks are in order, so an earlier track means rewinding; loading by name
  (about 40 bytes more) lets the player leave the tape running.
- This gives goal (d) for almost no memory. It does not make a track bigger than the working area
  fit: track 4 still needs its 240 bytes found first.

### 6.2 128K as an option

Worth offering, after the 48K scheme and built on it. The engine's back buffer, shift tables and
copy routine all sit at C000-FFFF, which is exactly the part a 128K swaps, so pages cannot be
switched during a race; but at the menu they can. A 128K loader would put each track, unpacked, in
a spare page (five are free), and choosing a track would run about 60 bytes of code kept below C000:
switch the page in, copy 3.4 KB into the same working area, switch back. The 48K sees none of this
and uses its packed store or the tape. No speed cost, no change to the race code, and the AY tune
already has its build switch. The one design rule to keep is a single "put track N in the working
area" entry point with three sources behind it (packed store, tape, page).

## 7. Ranked table

| # | Candidate | Bytes | Area freed | Cost | Risk | Verified how |
|---|---|---|---|---|---|---|
| 1 | Screen copy as a loop | 5,697 | E982-FFC2, fast, one piece | +6,466 T a picture (2.6%); alone, 3-frame pictures go | Medium | Built; 6,080 rows compared, 0 wrong; zxlap both modes |
| 2 | Cars flipped top-bottom when drawn | about 2,100 | 5F00-71FF | under 1,000 T a picture; about 100 of code | Medium | Frames compared: exact. Drawer not built |
| 3 | Gen_tiles as one routine | about 990 | program (A7CD) | about 1,400 T a picture | Low-medium | Sizes and tile count measured. Not built |
| 4 | Cars flipped left-right too | about 920 more | 5F00-71FF | about 2,000 T typical, 6,000 worst; 256-byte table | Medium | Frames compared: exact but 8 pixels on WHITE. Not built |
| 5 | O map out of the race | 540-780 | program | +1,500-2,000 T a picture | Medium | Exact match with row lists proved. Not built |
| 6 | Buffer rows 168-191 for row lists | 672 | TOPMEM 320-388, program about 330 | none (faster memory) | Low-medium | Access map, 3 tracks, full sessions. Not built |
| 7 | Surface as spans | 190-320 | program | negligible | Low-medium | Encoded on real data. Not built |
| 8 | `tower_cars` duplicate | about 280 | program (before sq4) | none in the race | Low | Row-for-row match. Not built |
| 9 | Stack 256 to 160 | 96 | next to table block | none | Medium | Depth 54-56 measured, 3 tracks |
| 10 | Waypoints in 2 bytes | 92-122 | program | about 30 T a look-up | Medium | Sizes measured. Behaviour not tested |
| 11 | Top pocket FFC3-FFF3 | 57 | top of memory | none | Low | Access map, 3 tracks |
| 12 | `a_sav` at 5B16 | 54 | before table block | none | Low | Never referenced; untouched |
| 13 | LOWTAB tail pockets (known) | about 49 | under 8000 | none | Low | Block sizes from the symbol file |
| 14 | Unused variables (known) | about 22 | the gap before sq4 | none | Low | Label check |
| - | Title/podium code into the buffer | about 500 net | 7200-, program | two-stage build | High | Packed sizes measured. Not recommended |
| - | Shift tables | 0 (350 at most) | | 10,000 T a picture to halve | | Not recommended |

## 8. Three packages

Needs, for comparison (from BUILT.md and make_world.py's own notes, plus the things' sizes measured
in `py/things.py`): track 4 bare about 240 bytes; track 2 with all twelve things 232, with track 1's
full set about 390 (estimate); track 3 with the full set about 880 (estimate); track 4 with the full
set about 1,300 (estimate). The bridge code is not designed: I have assumed 0.5 to 1 KB.

### Safe now - no speed cost - about 850 bytes

Items 6, 11, 12, 13, 14. 672 + 57 + 54 + 49 + 22 = 854.

- (a) Track 4 fits bare. Track 2 gets all its breakfast things. Track 3 gets most of them.
- (b), (c): no. (d) multi-load: yes, its 110-230 bytes fit.

### Worth doing - small speed cost - about 4,400 bytes more

Items 2, 3, 5, 7, 8, 9, 10 (track 1 figures): 2,100 + 990 + 540 + 320 + 280 + 96 + 92 = 4,418.
Speed: about +4,000-5,000 T a picture in all (under 2%), estimate.

- With "safe now": about 5.2 KB.
- (a) in full, track 4 with things included (1.3 KB).
- (b) the bridge code (0.5-1 KB assumed).
- (c) **two tracks in one load**: two packed tracks (about 3.0 KB) and about 0.6 KB of code
  (unpacker, numbers table, menu, names). 3.6 KB. This fits, but not together with all of (a) and
  (b): choose, or store the tracks with shared art (0.7-1.2 KB each) to have both.

### Big moves - format changes - about 6,600 bytes more

Items 1 and 4: 5,697 + 920.

- The looped copier alone holds **all three built tracks packed (4,240 bytes) and the 0.6 KB of
  code**, with about 0.85 KB over.
- All three packages: about 11.8 KB. Five tracks packed (about 7.5 KB), a working area grown for
  track 4 (about 0.75 KB), menu code (0.6) and the bridge (0.8 assumed) come to about 9.7 KB. So
  all five in one load fits on paper. This is an estimate resting on two tracks not yet built.

## 9. Not verified

- **The real ZX0 program was not run.** I fetched its source and the session's permission rules
  stopped me compiling it; I deleted the copy. Packed sizes come from my own sizer using ZX0's
  published bit costs, with no decoder built, so no round trip and no unpacking time measured.
- Items 2-5, 7, 8, 10 are not built. Their bytes and T-states are estimates from instruction
  counts and measured call counts (35 plain tiles, 51 car rows, 5 bump checks a picture).
- Item 6: no build puts data in the strips. The access map covers the default build only, not
  PIT=1, OBJECTS=1, MUSIC=1, AY=1 or the big cars. Bytes FA-FF of each strip are left out because
  interrupt pushes landed there in some sessions.
- Item 1: built and timed on track 1 only, one autopilot lap each way. The test suites were not
  run on it. Tearing on a real television was not judged. Not run on real hardware.
- Stack depth is the deepest seen in three sessions, not a proven worst case.
- Code "not run" in my sessions is not proof it is dead; only the label check is static.
- Needs for tracks 4 and 5, for the full sets of things, and for the bridge are arithmetic or
  assumptions; none was built.
- WHITE's 8 pixels that break the mirror: I do not know whether they are a deliberate touch-up.
- Tape times are worked out from the ROM's timings, not recorded.
- No test suite was run on any scratch build other than zxlap and my own copy check.

## 10. Files

- This report: `/tmp/claude-0/-home-user/fffe8284-32d1-5fde-8a48-51a919ed51ce/scratchpad/sweep/RAM-SWEEP.md`
  (scratch space: it can be cleared; copy it into the repo's `docs/` if it is to be kept).
- Scripts: `/tmp/claude-0/-home-user/fffe8284-32d1-5fde-8a48-51a919ed51ce/scratchpad/sweep/py/`
  (`map.py` memory map; `tracks.py`, `an1.py`, `an2.py` track data and encodings; `lz.py` the
  sizer; `cars.py` frame mirrors; `cover.py`, `cov2.py`, `dead.py` access map and label check;
  `cpcheck.py` copier check; `things.py`).
- Looped copier proof: `/tmp/claude-0/-home-user/fffe8284-32d1-5fde-8a48-51a919ed51ce/scratchpad/sweep/cp/src/racer.asm`
  (`lc_src` to `lc_end`), tape `/tmp/claude-0/-home-user/fffe8284-32d1-5fde-8a48-51a919ed51ce/scratchpad/sweep/cp.tap`.
