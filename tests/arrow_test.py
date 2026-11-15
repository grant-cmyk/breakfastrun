"""The layout of 15 Nov 2026 and the corner arrows (Grant: "have the track map on the bottom left inside of
play. Move the damage to the right. Then, a couple of rows in front of my car, a flashing arrow pointing either
diagonally right or sharp right to indicate turns. A long straight stretch gets an early flashing straight in
the direction of the straight"). On the REAL 48K ROM (zx package), with tests/drive_test.py's own helpers.
  - the mini-map is in the window's bottom left corner, 24 pixels wide, a solid ribbon in the window's own colours
    laid over the picture (Grant: "c (2)4 is good, and the inside parts could be blue - so no masking inside
    required"), and the cars' dots move on it
  - the mug gauge is in the bottom right corner, the spoons beside it, the crew chief's bubble between; with
    three spoons, a message and full damage nothing overlaps and every colour is right
  - the arrows' table: the kind and side at known corners of this track, nothing on plain stretches
  - on the screen: the right arrow, pixel for pixel, always at the same spot (Grant: "always shows in the middle
    of the screen - so it doesn't jump around"); it flashes; it leaves no trail; it is clear of the map, the mug,
    the spoons and the bubble
TRACK=2 or 3 for another track's build (TRACK=n bash build.sh first). Prints PASS/FAIL lines and RESULT."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.environ.get('TRACK', '1')
ROOT_ = os.path.join(HERE, '..')
TSRC = os.path.join(ROOT_, 'src') if TRACK == '1' else os.path.join(ROOT_, 'build', 'track' + TRACK, 'src')
if TRACK != '1':
    os.environ.setdefault('ZTAP', os.path.join(ROOT_, 'build', 'racer_track%s.tap' % TRACK))
    os.environ.setdefault('ZSYM', os.path.join(ROOT_, 'build', 'racer_track%s.sym' % TRACK))
    if not (os.path.exists(os.environ['ZTAP']) and os.path.isdir(TSRC)):
        print('FAIL no track %s build: run  TRACK=%s bash build.sh  first' % (TRACK, TRACK)); print('RESULT: 1 FAIL'); sys.exit(1)
src = open(os.path.join(HERE, 'drive_test.py')).read()
src = src[:src.index('with Racer(headless=True)')].replace("os.path.dirname(os.path.abspath(__file__))", repr(HERE))
src = src.replace("os.path.join(ROOT, 'src',", "os.path.join(%r," % TSRC)
exec(src)
sys.path.insert(0, os.path.join(ROOT_, 'tools'))
import make_arrows                                                  # the eight arrows as drawn: (ink, mask), 16 x 11
FRAMES = make_arrows.FRAMES
_wsrc = open(os.path.join(TSRC, 'world.asm')).read()
CANS = [(int(re.search(r'NOS_%s_X equ (\d+)' % k, _wsrc).group(1)), int(re.search(r'NOS_%s_Y equ (\d+)' % k, _wsrc).group(1))) for k in 'ABC']
for cx_, cy_ in CANS: world[cy_ - 8:cy_ + 8, cx_ - 4:cx_ + 4] = 0     # (the NOS and oil cans come and go: their own cells are left out, as in tests/track2_test.py)
_wb = window_bad
def window_bad(sp, stop=False):                                     # (never stops for the next picture: at_copy_done first)
    for cx_, cy_ in CANS: wmask[cy_ - 8:cy_ + 8, cx_ - 4:cx_ + 4] = True
    camx, camy = g(sp, 'camx'), g(sp, 'camy'); keep = []                # (the picture the caller has stopped at: at_copy_done first)
    for cx_, cy_ in CANS:                                           # (whatever is in a can's cells on the screen is taken as right)
        x, y = cx_ - camx, cy_ - camy; ys = slice(max(y - 8, 0), max(min(y + 8, WH), 0)); xs = slice(max(x - 4, 0), max(min(x + 4, WW), 0))
        keep.append((cy_, cx_, world[cy_ - 8:cy_ + 8, cx_ - 4:cx_ + 4].copy()))
        got = screen_bits(sp)[WY:WY + WH, 8:8 + WW][ys, xs]
        world[camy + ys.start:camy + ys.stop, camx + xs.start:camx + xs.stop] = got
    bad = _wb(sp, False)
    for cy_, cx_, was in keep: world[cy_ - 8:cy_ + 8, cx_ - 4:cx_ + 4] = was
    return bad
fails = 0
def ok(c, m):
    global fails
    print('PASS' if c else 'FAIL', m); fails += 0 if c else 1
rd = lambda n: open(os.path.join(TSRC, n)).read()
WPS = [tuple(int(v) for v in l.split('dw')[1].split(',')) for l in rd('waypoints.asm').split('waypoints:')[1].splitlines() if 'dw' in l]
ATAB = [int(l.split('defb')[1].split(';')[0]) for l in rd('arrowtab.asm').splitlines() if 'defb' in l]
DIRS = ['up', 'up-right', 'right', 'down-right', 'down', 'down-left', 'left', 'up-left']
attr = lambda sp, r, c: sp.read8(0x5800 + r * 32 + c)
C_WP = 13
# What the track does at known places, written from its design (the road runs anticlockwise on the screen from the
# start line: east along the bottom, then north). (waypoint, kind, the way the arrow points) - None: any way.
KNOWN = {
 '1': [(0, 'sharp left', 'up'), (10, 'sharp left', 'left'), (14, 'gentle left', 'down-left'), (18, 'sharp right', 'up-left'),
       (25, 'sharp left', 'down'), (33, 'sharp left', 'right'), (37, 'straight', 'right'), (4, 'straight', 'up'), (28, 'straight', 'down')],
 '2': [(12, 'sharp left', 'up'), (18, 'straight', 'left'), (24, 'sharp right', 'up'), (29, 'straight', 'right'), (40, 'gentle left', None),
       (46, 'sharp right', 'up-left'), (52, 'sharp left', 'down'), (55, 'straight', 'down'), (1, 'sharp left', 'right'), (4, 'straight', 'right')],
 '3': [(10, 'gentle left', 'up-right'), (22, 'gentle left', 'up-left'), (26, 'sharp left', 'down'), (36, 'sharp right', 'left'),
       (41, 'straight', 'up'), (48, 'sharp left', 'left'), (4, 'straight', 'right'), (14, 'straight', 'up')],
 # track 5, the bridge: east past the line, north, WEST along the lower road and under the bridge, north up the left side, east
 # along the top, down and back west on the second lane, then SOUTH over the bridge and left onto the start straight
 '5': [(9, 'sharp left', 'up'), (13, 'sharp left', 'left'), (16, 'straight', 'left'), (24, 'sharp right', 'up'), (31, 'sharp right', 'right'),
       (34, 'straight', 'right'), (42, 'sharp right', 'down'), (53, 'sharp left', 'down'), (56, 'straight', 'down'), (1, 'sharp left', 'right')]}[TRACK]
PLAIN = {'1': [7, 30, 41, 42, 43], '2': [8, 9, 21, 32, 58], '3': [7, 17, 18, 31, 44, 55, 58], '5': [6, 20, 21, 38, 39, 51]}[TRACK]   # mid-straight (track 3's 55: the fast kink)

# ---------------------------------------------------------------- the table
ok(len(ATAB) == NWP and all(v == 0 or (1 <= v >> 3 <= 5) for v in ATAB), 'the arrows\' table has a byte for each of the %d waypoints: none, or a kind and a direction' % NWP)
bad = [(k, kind, d, ARROW_KINDS[ATAB[k] >> 3], DIRS[ATAB[k] & 7]) for k, kind, d in KNOWN if ARROW_KINDS[ATAB[k] >> 3] != kind or (d and DIRS[ATAB[k] & 7] != d)]
ok(not bad, 'at %d known places of track %s the table has the right kind of arrow, pointing the right way (%s)' % (len(KNOWN), TRACK, bad or ', '.join('%d %s' % (k, kind) for k, kind, d in KNOWN)))
ok(all(ATAB[k] == 0 for k in PLAIN), 'and nothing on the plain stretches (waypoints %s)' % PLAIN)
def car_place(k):
    """where your car typically is while it heads for waypoint k: 20 px before the waypoint before it; and the road's heading there (0-63)"""
    (x0, y0), (x1, y1) = WPS[(k - 2) % NWP], WPS[(k - 1) % NWP]; d = math.dist((x0, y0), (x1, y1))
    return x1 - 20 * (x1 - x0) / d, y1 - 20 * (y1 - y0) / d, round(math.atan2(x1 - x0, -(y1 - y0)) / (2 * math.pi) * 64) % 64
side_bad = []
for k, v in enumerate(ATAB):                                        # every bend's arrow is off the road's line to its own side
    if v >> 3 >= 2:
        off = ((v & 7) * 8 - car_place(k)[2] + 32) % 64 - 32          # the arrow against the road, in 64ths of a turn: + is to the right
        want_right = (v >> 3) in (3, 5)
        if not (2 <= (off if want_right else -off) <= 22): side_bad.append((k, ARROW_KINDS[v >> 3], off))
ok(not side_bad, 'every bend\'s arrow (%d of them) points to its own side of the road\'s line there, by a sixteenth to a third of a turn (%s)' % (sum(v >> 3 >= 2 for v in ATAB), side_bad))
shown = sum(1 for v in ATAB if v)
ok(0.25 < shown / NWP < 0.85, 'an arrow is up for %d of the %d waypoints; the rest of the lap shows none' % (shown, NWP))

# ---------------------------------------------------------------- the layout, on the grid
sp = Racer(headless=True); sp.__enter__(); sp.load_tape(TAP); t = 0
while g(sp, 'renders') == 0 and t < 60: sp.run(duration=0.1, fast_forward=True); t += 0.1
sp.run(duration=0.6, fast_forward=True); at_copy_done(sp)
ok(bytes(sp.read(SYM['arrow_tab'], NWP)) == bytes(ATAB), 'the game holds that table (in the back buffer\'s unused bottom rows, at %04X)' % SYM['arrow_tab'])
md, dots, ink = minimap_diff(sp); sb = screen_bits(sp)
thin = min(min(len(run) for run in ''.join(map(str, r)).split('0') if run) for r in MM_ROWS)
ok(md == 0 and ink > 60 and MM_ROWS.shape[1] == 24 and thin >= 2 and not MM_ROWS[:, :2].any() and 2 <= WH - (MM_TOP + MM_H) <= 3,
   'the mini-map: 24 x %d, this track line for line (%d pixels of ribbon, %d wrong), the ribbon solid and never under 2 pixels across (%d at its thinnest along a line), 2 pixels clear of the window\'s left edge and %d of its foot' % (MM_H, ink, md, thin, WH - (MM_TOP + MM_H)))
at_copy_done(sp); w = screen_bits(sp)[WY:WY + WH, 8:8 + WW].astype(bool); mnow = map_now(sp).astype(bool)
ok(all(attr(sp, r, c) == 0x29 for r in range(4, 20) for c in range(1, 7)) and w[MM_TOP:MM_TOP + MM_H, 0:24][mnow].all() and window_bad(sp, False) == 0,
   'it is in the window\'s own blue on cyan, no cells of its own; every pixel of the ribbon is ink on the screen, and everywhere else in its rectangle - outside the track and inside it - the scrolling picture shows, pixel for pixel against the world map')
ok(not sb[0:40, 208:256].any() and all(attr(sp, r, c) == 0x30 for r in range(5) for c in range(26, 32)), 'the panel\'s top right, where it was, is plain')
ok(all(attr(sp, r, c) == 0x78 for r in (17, 18) for c in range(7, 17)) and all(attr(sp, r, c) == 0x29 for r in (15, 16) for c in range(7, 25)) and all(attr(sp, 19, c) == 0x29 for c in range(7, 19)),
   'the crew chief\'s bubble is where it was (rows 17-18, columns 7-16), the cloth\'s colours round it')
at_copy_done(sp)
ok(arrow_state(sp) is None and window_bad(sp) == 0, 'no arrow on the grid, before green')
go_green(sp); press(sp, 'Q', False)
for i in CPUS: put(sp, i, 4 + 40 * i, SY + 58); sp.write(CARS + i * CS + 19, bytes([0]))      # the others parked, engines off

# three spoons, a message, full damage
sp.write(SYM['inv'], bytes([1, 1, 1])); sp.write(SYM['dmg'], bytes([SYM['dmg_max']]))
sp.run(duration=0.5, fast_forward=True); at_copy_done(sp); sb = screen_bits(sp).astype(bool)
A = lambda r, c: attr(sp, r, c)
spoons = all(A(r, c) == 0x2A for r in (18, 19) for c in (19, 20, 21)) and all(sb[WY + WH - 12:WY + WH - 2, c * 8:c * 8 + 8].any() for c in (19, 20, 21))
mug = all(A(r, c) == 0x2B for r in (18, 19) for c in (22, 23, 24)) and sb[144:160, 176:200].sum() > 40
bub = all(A(r, c) == 0x78 for r in (17, 18) for c in range(7, 17)) and sb[138:150, 72:136].sum() > 60
gap = all(A(r, c) == 0x29 for r in (17, 18, 19) for c in (17, 18)) and all(A(19, c) == 0x29 for c in range(7, 17)) and all(A(r, c) == 0x29 for r in (15, 16, 17) for c in range(19, 25))
mbx = all(A(r, c) == 0x29 for r in range(15, 20) for c in range(1, 7)) and minimap_diff(sp)[0] == 0 and MM_TOP * 0 + 24 <= 48
ok(spoons, 'three spoons held: red, each in its own cell column - screen columns 19, 20, 21, just left of the mug')
ok(mug, 'the mug gauge in the bottom right corner (columns 22-24), magenta, at full damage')
dm = bytes(sp.read(SYM['dmg_bmp'], 48)); on_scr = bytes(sp.read8(0x4000 | ((y & 0xC0) << 5) | ((y & 7) << 8) | ((y & 0x38) << 2) | (22 + i)) for y in range(144, 160) for i in range(3))
ok(dm == on_scr, 'its three columns hold the mug and nothing else (as composed, byte for byte)')
ok(bub and gap and mbx, 'a message up at the same time: the bubble white between them (columns 7-16), the map whole and its 24 pixels clear of the bubble (which starts at 48), and plain cloth colours in the cells between and above - nothing overlaps')
shot(sp, 'arrow_strip_t%s.png' % TRACK)
sp.write(SYM['inv'], bytes([1, 0, 1])); sp.run(duration=0.3, fast_forward=True); at_copy_done(sp)
ok([A(18, c) for c in (19, 20, 21)] == [0x2A, 0x29, 0x2A], 'a spoon used: its cell is the cloth\'s again, the others stay')
sp.write(SYM['inv'], bytes([0, 0, 0])); sp.write(SYM['dmg'], bytes([0]))

# ---------------------------------------------------------------- the map's dots
seen_on = seen_off = 0; mdbad = 0; moved = set(); holes = 0
for k in range(0, NWP, max(1, NWP // 12)):
    x, y = WPS[k]; put(sp, 0, x - 8, y - 8); sp.write(CARS + C_WP, bytes([(k + 1) % NWP]))
    for j in range(8):
        sp.run(duration=0.1, fast_forward=True); at_copy_done(sp)
        md, dots, _ = minimap_diff(sp); mdbad += md
        if dots[0] is None: seen_off += 1
        else:
            seen_on += 1
            if j >= 5 and dots[0] == map_dots(sp)[0]:
                moved.add(dots[0]); dx, dy = dots[0]
                if MM_ROWS[dy:dy + 2, dx:dx + 2].all() and not map_now(sp)[dy:dy + 2, dx:dx + 2].any() and window_bad(sp, False) == 0: holes += 1
ok(mdbad == 0 and len(moved) >= 8 and seen_on > 10 and seen_off > 10 and holes >= 8, 'your dot follows your car round the map (at the right spot in %d places), 2 x 2 and blinking (on %d looks, off %d); on the road it is a hole in the ribbon, seen on the screen as the picture under it (%d places checked); the map is the ribbon and the dots, pixel for pixel' % (len(moved), seen_on, seen_off, holes))
ok(dots[1:] == map_dots(sp)[1:], 'the other cars\' dots are there too, a pixel each, where its car is')

# ---------------------------------------------------------------- the arrow on the screen, at the known places
def stand(k):
    x, y, h = car_place(k); put(sp, 0, int(round(x)) - 8, int(round(y)) - 8, h); sp.write(CARS + C_WP, bytes([k]))
    sp.run(duration=0.5, fast_forward=True)
def look(on):
    """the next picture with the arrow's turn on (or off): (arrow_state, wrong pixels outside the arrow's frame, the window)"""
    for _ in range(5):
        at_copy_done(sp)
        if bool(g(sp, 'renders') & 2) == on: break
        sp.run(duration=0.02, fast_forward=True)
    return arrow_state(sp), window_bad(sp), screen_bits(sp)[WY:WY + WH, 8:8 + WW].astype(bool)
def arrow_ok(st, w):
    code, x, y = st; ink, mask = FRAMES[code & 7]; box = w[y:y + 11, x:x + 16]
    return box.shape == (11, 16) and (box[mask] == ink[mask]).all()
bad = []; spots = set(); sides = set()
for k, kind, d in KNOWN:
    stand(k); st, wb, w = look(True); c = car(sp, 0)
    if c['wp'] != k or st is None or st[0] != ATAB[k] or wb or not arrow_ok(st, w): bad.append((k, kind, c['wp'], st, wb)); continue
    spots.add(st[1:]); sides.add(kind)
    cx, cy = c['x'] - g(sp, 'camx'), c['y'] - g(sp, 'camy')           # your car, standing: its 16 x 16 and the arrow's 16 x 11 apart
    if not (st[1] + 16 <= cx or cx + 16 <= st[1] or st[2] + 11 <= cy or cy + 16 <= st[2]): bad.append((k, 'on the car', st, cx, cy))
    st2, wb2, w2 = look(False)
    if st2 is not None or wb2: bad.append((k, 'the off picture', st2, wb2))
    if k == KNOWN[0][0]: shot(sp, 'arrow_known_t%s.png' % TRACK)
AX, AY = SYM['arrow_x'], SYM['arrow_y']
ok(not bad and len(spots) == 1 and spots == {(AX - 8, AY - 5)} and len(sides) >= 3,
   'at each of those places (%s) the game draws that arrow, pixel for pixel with its clear edge, and always at the same spot: its middle at (%d, %d) of the window - %d across from the middle, %d above it, clear of your car standing still; the rest of the window is the map; two pictures later it is off and nothing is left (%s)'
   % (', '.join(sorted(sides)), AX, AY, AX - WW // 2, WH // 2 - AY, bad))
bad = []
for k in PLAIN:
    stand(k)
    for on in (True, False):
        st, wb, w = look(on)
        if st is not None or wb or car(sp, 0)['wp'] != k: bad.append((k, st, wb))
ok(not bad, 'on the plain stretches: no arrow in either pair of pictures, the window is the map (%s)' % bad)
# it flashes
stand(KNOWN[0][0]); seq = []
for _ in range(12):
    at_copy_done(sp); st = arrow_state(sp); w = screen_bits(sp)[WY:WY + WH, 8:8 + WW].astype(bool)
    code = ATAB[KNOWN[0][0]]; x, y = AX - 8, AY - 5
    ink, mask = FRAMES[code & 7]; seq.append(int((w[y:y + 11, x:x + 16][ink]).all()))
    sp.run(duration=0.02, fast_forward=True)
s = ''.join(map(str, seq))
ok(s in ('110011001100', '100110011001', '001100110011', '011001100110'), 'it flashes: on for two pictures, off for two (%s) - about three times a second at 12 to 14 pictures a second' % s)

# ---------------------------------------------------------------- clear of the map, the mug, the spoons, the bubble, the plate, the lights
# (it has one fixed spot now, so this is a matter of where that is)
box = np.zeros((WH, WW), dtype=bool); box[AY - 5:AY + 6, AX - 8:AX + 8] = True
hud = np.zeros((WH, WW), dtype=bool); hud[MM_TOP:MM_TOP + MM_H, 0:24] = True; hud[WH - 16:WH, WW - 48:WW] = True; hud[136 - WY:152 - WY, 56 - 8:136 - 8] = True
hud[2:20, WW - 40:WW] = True; hud[8 - WY:32 - WY, 56 - 8:136 - 8] = True
ok(box.sum() == 176 and not (box & hud).any(), 'the arrow\'s spot is clear of the mini-map, the crew chief\'s bubble, the spoons, the mug, your place\'s plate and the start lights')
sp.__exit__(None, None, None)

# ---------------------------------------------------------------- no trails, driving
sp = Racer(headless=True); sp.__enter__(); sp.load_tape(TAP); t = 0
while g(sp, 'renders') == 0 and t < 60: sp.run(duration=0.1, fast_forward=True); t += 0.1
go_green(sp)
for i in CPUS: put(sp, i, 4 + 40 * i, SY + 58); sp.write(CARS + i * CS + 19, bytes([0]))
on = off_after = wrong = mapbad = 0; kinds = set(); pics = 0; r_last = -1
while pics < 110:                                                   # Q held: down the start straight to the first corner
    sp.run(duration=0.04, fast_forward=True); at_copy_done(sp)
    r = g(sp, 'renders')
    if r == r_last: continue
    r_last = r; pics += 1
    st = arrow_state(sp); wb = window_bad(sp); wrong += wb; mapbad += minimap_diff(sp)[0]
    if st: on += 1; kinds.add(ARROW_KINDS[st[0] >> 3])
    elif on: off_after += 1
    if wb and wrong == wb: shot(sp, 'arrow_trail_t%s.png' % TRACK)
press(sp, 'Q', False)
ok(on >= 8 and off_after >= 8 and wrong == 0 and mapbad == 0,
   'driven flat out from the line to the first corner, %d pictures looked at: the arrow (%s) on in %d, off in %d after it first showed - and in every one the window outside the arrow is the map, pixel for pixel, the mini-map whole (%d and %d wrong): no trail'
   % (pics, ', '.join(sorted(kinds)), on, off_after, wrong, mapbad))
sp.__exit__(None, None, None)
print('RESULT:', 'PASS' if fails == 0 else '%d FAIL' % fails)
