"""The layout of 15 Nov 2026 and the corner arrows (Grant: "have the track map on the bottom left inside of
play. Move the damage to the right. Then, a couple of rows in front of my car, a flashing arrow pointing either
diagonally right or sharp right to indicate turns. A long straight stretch gets an early flashing straight in
the direction of the straight"). On the REAL 48K ROM (zx package), with tests/drive_test.py's own helpers.
  - the mini-map is in the window's bottom left corner in cells of its own, and the cars' dots move on it
  - the mug gauge is in the bottom right corner, the spoons beside it, the crew chief's bubble between; with
    three spoons, a message and full damage nothing overlaps and every colour is right
  - the arrows' table: the kind and side at known corners of this track, nothing on plain stretches
  - on the screen: the right arrow, pixel for pixel, 32 px ahead of your car; it flashes; it leaves no trail;
    it is never drawn over the map, the mug, the spoons or the bubble
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
def window_bad(sp):
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
       (41, 'straight', 'up'), (48, 'sharp left', 'left'), (4, 'straight', 'right'), (14, 'straight', 'up')]}[TRACK]
PLAIN = {'1': [7, 30, 41, 42, 43], '2': [8, 9, 21, 32, 58], '3': [7, 17, 18, 31, 44, 55, 58]}[TRACK]   # mid-straight (track 3's 55: the fast kink)

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
ok(bytes(sp.read(SYM['arrow_tab'], NWP)) == bytes(ATAB), 'the game holds that table (above the screen-copy routine, at %04X)' % SYM['arrow_tab'])
md, dots, ink = minimap_diff(sp); sb = screen_bits(sp)
ok(md == 0 and ink > 120 and all(attr(sp, r, c) == 0x30 for r in range(15, 20) for c in range(1, 7)),
   'the mini-map is in the window\'s bottom left corner: 6 x 5 cells of its own, black on yellow, this track line for line (%d pixels, %d wrong)' % (ink, md))
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
mbx = all(A(r, c) == 0x30 for r in range(15, 20) for c in range(1, 7)) and minimap_diff(sp)[0] == 0
ok(spoons, 'three spoons held: red, each in its own cell column - screen columns 19, 20, 21, just left of the mug')
ok(mug, 'the mug gauge in the bottom right corner (columns 22-24), magenta, at full damage')
dm = bytes(sp.read(SYM['dmg_bmp'], 48)); on_scr = bytes(sp.read8(0x4000 | ((y & 0xC0) << 5) | ((y & 7) << 8) | ((y & 0x38) << 2) | (22 + i)) for y in range(144, 160) for i in range(3))
ok(dm == on_scr, 'its three columns hold the mug and nothing else (as composed, byte for byte)')
ok(bub and gap and mbx, 'a message up at the same time: the bubble white between them (columns 7-16), the map\'s box whole, and plain cloth colours in the cells between and above - nothing overlaps')
shot(sp, 'arrow_strip_t%s.png' % TRACK)
sp.write(SYM['inv'], bytes([1, 0, 1])); sp.run(duration=0.3, fast_forward=True); at_copy_done(sp)
ok([A(18, c) for c in (19, 20, 21)] == [0x2A, 0x29, 0x2A], 'a spoon used: its cell is the cloth\'s again, the others stay')
sp.write(SYM['inv'], bytes([0, 0, 0])); sp.write(SYM['dmg'], bytes([0]))

# ---------------------------------------------------------------- the map's dots
seen_on = seen_off = 0; mdbad = 0; moved = set()
for k in range(0, NWP, max(1, NWP // 12)):
    x, y = WPS[k]; put(sp, 0, x - 8, y - 8); sp.write(CARS + C_WP, bytes([(k + 1) % NWP]))
    for j in range(8):
        sp.run(duration=0.1, fast_forward=True); at_copy_done(sp)
        md, dots, _ = minimap_diff(sp); mdbad += md
        if dots[0] is None: seen_off += 1
        else:
            seen_on += 1
            if j >= 5 and dots[0] == map_dots(sp)[0]: moved.add(dots[0])
ok(mdbad == 0 and len(moved) >= 10 and seen_on > 10 and seen_off > 10, 'your dot follows your car round the map (at the right spot in %d places), 3 x 3 and blinking (on %d looks, off %d); the box is the map and the dots, pixel for pixel' % (len(moved), seen_on, seen_off))
ok(dots[1:] == map_dots(sp)[1:], 'the other cars\' dots are there too, 2 x 2, each where its car is')

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
bad = []; dist = []
for k, kind, d in KNOWN:
    stand(k); st, wb, w = look(True); c = car(sp, 0)
    if c['wp'] != k or st is None or st[0] != ATAB[k] or wb or not arrow_ok(st, w): bad.append((k, kind, c['wp'], st, wb)); continue
    ax, ay = st[1] + 8 - (c['x'] - g(sp, 'camx') + 8), st[2] + 5 - (c['y'] - g(sp, 'camy') + 8); dist.append(math.hypot(ax, ay))
    h = c['ang'] / 64 * 2 * math.pi
    if abs(ax - 32 * math.sin(h)) > 4 or abs(ay + 32 * math.cos(h)) > 4: bad.append((k, 'not ahead of the car', ax, ay))
    st2, wb2, w2 = look(False)
    if st2 is not None or wb2: bad.append((k, 'the off picture', st2, wb2))
    if k == KNOWN[0][0]: shot(sp, 'arrow_known_t%s.png' % TRACK)
ok(not bad and len(dist) == len(KNOWN), 'at each of those places the game draws that arrow, pixel for pixel with its clear edge, %.0f to %.0f px ahead of your car\'s middle along its heading; the rest of the window is the map; two pictures later it is off and nothing is left (%s)'
   % (min(dist or [0]), max(dist or [0]), bad))
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
    code = ATAB[KNOWN[0][0]]; c = car(sp, 0)
    t_ = SYM['thrust_tab'] + (c['ang'] & 0x3C); s8 = lambda v: v - 256 if v > 127 else v
    x = c['x'] - g(sp, 'camx') + (s8(sp.read8(t_)) >> 1); y = c['y'] - g(sp, 'camy') + (s8(sp.read8(t_ + 2)) >> 1) + 3
    ink, mask = FRAMES[code & 7]; seq.append(int((w[y:y + 11, x:x + 16][ink]).all()))
    sp.run(duration=0.02, fast_forward=True)
s = ''.join(map(str, seq))
ok(s in ('110011001100', '100110011001', '001100110011', '011001100110'), 'it flashes: on for two pictures, off for two (%s) - about three times a second at 12 to 14 pictures a second' % s)

# ---------------------------------------------------------------- never over the map, the mug, the spoons, the bubble
# (the arrow is drawn into the buffer before them, and the map's box is not copied from the buffer at all). Your car
# is stood at the foot of the world, where the camera stops and the car sits low in the window, pointing down.
sp.write(SYM['inv'], bytes([1, 1, 1])); sp.write(SYM['dmg'], bytes([SYM['dmg_max']]))
kk = next(k for k, v in enumerate(ATAB) if v)
kept = lambda: b''.join(bytes(sp.read(a_ + l * 0x100, 8)) for l in range(8) for a_ in (0x50D2, 0x50F2))   # (his words: rows 22-23, columns 18-25; his face moves)
FL_KEPT = 0x50C0                                                    # the bubble's picture as kept on the screen: rows 22-23 (fl_draw copies it in each picture)
hud = np.zeros((WH, WW), dtype=bool); hud[MBOX[0]:MBOX[1], MBOX[2]:MBOX[3]] = True; hud[WH - 16:WH, WW - 48:WW] = True; hud[136 - WY:152 - WY, 72 - 8:136 - 8] = True
hits = 0; diff = 0; tried = []
for wx in (30, 100, 160, 185):
    for ang in (32, 28, 36, 24, 40):
        put(sp, 0, 0, 0, ang); sp.run(duration=0.2, fast_forward=True)
        put(sp, 0, g(sp, 'camx') + wx - 8, MAPH * 8 - 44, ang); sp.write(CARS + C_WP, bytes([kk])); sp.write(SYM['msg_timer'], bytes([200]))
        sp.run(duration=0.6, fast_forward=True); sp.write(CARS + C_WP, bytes([kk]))
        for _ in range(10):                                         # a picture with the arrow on, numbered 2 of 8: the next but one is off, the steam and the dots the same
            at_copy_done(sp)
            if g(sp, 'renders') & 7 == 2: break
            sp.run(duration=0.02, fast_forward=True)
        st = arrow_state(sp); w1 = screen_bits(sp)[WY:WY + WH, 8:8 + WW].astype(bool); said = kept()
        sp.run(duration=0.02, fast_forward=True); at_copy_done(sp); sp.run(duration=0.02, fast_forward=True); at_copy_done(sp)
        w2 = screen_bits(sp)[WY:WY + WH, 8:8 + WW].astype(bool)
        if st is None or arrow_state(sp) is not None: tried.append((wx, ang, 'no arrow')); continue
        if said != kept(): tried.append((wx, ang, 'the chief said something new between the two')); continue
        box = np.zeros_like(hud); box[max(st[2], 0):max(st[2] + 11, 0), max(st[1], 0):max(st[1] + 16, 0)] = True
        if (box & hud).any():
            dd = (w1 != w2) & hud; hits += 1; diff += int(dd.sum())
            if dd.any(): ys_, xs_ = np.nonzero(dd); tried.append(('differs', int(dd.sum()), 'rows', int(ys_.min()), int(ys_.max()), 'columns', int(xs_.min()), int(xs_.max())))
            if hits == 1: shot(sp, 'arrow_hud_t%s.png' % TRACK)
        tried.append((wx, ang, st[1], st[2], int((box & hud).sum())))
ok(hits >= 3 and diff == 0, 'with the arrow\'s frame lying across the map\'s box, the bubble, the spoons or the mug (%d cases), not a pixel of them differs between the picture with the arrow and the one without (%d differ) %s' % (hits, diff, tried if hits < 3 or diff else ''))
sp.write(SYM['inv'], bytes([0, 0, 0])); sp.write(SYM['dmg'], bytes([0])); sp.write(SYM['msg_timer'], bytes([1]))
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
