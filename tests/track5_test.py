"""Track 5, A FRIDGE TOO FAR - the one with the BRIDGE - in its own build (TRACK=5 bash build.sh ->
build/racer_track5.tap). Modelled on tests/track2_test.py (the same checks of the grid, the window, the
mini-map, the computer cars' three laps, your laps counted, your car driven round by script), then the bridge:
  - LEVELS: a car on the deck and a car under it at the crossing do not bump (two on one level do)
  - WALLS: a car on the deck, driven hard at either kerb wall, cannot leave; a car on the table cannot
    get into the tunnel's walls nor in through the bridge's side
  - DRAWING: a car on the table under the deck is not in the window and the deck's pixels are whole;
    half under, only the part outside the cover shows; beyond, it is there again; a car on the deck shows
  - RAMPS: the speed up the ramp and down it, against the same run with the slope's pull taken out
  - SPEED: pictures a second near the crossing against the rest of the lap
Prints PASS/FAIL lines and RESULT. QUICK=1 leaves out the dropped cars (the slowest part); BRIDGE=1 runs
the bridge's part only."""
import os, sys, math, json
HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = '5'
ROOT_ = os.path.join(HERE, '..')
TSRC = os.path.join(ROOT_, 'build', 'track' + TRACK, 'src')            # that build's own copy of src/, with its world
os.environ.setdefault('ZTAP', os.path.join(ROOT_, 'build', 'racer_track%s.tap' % TRACK))
os.environ.setdefault('ZSYM', os.path.join(ROOT_, 'build', 'racer_track%s.sym' % TRACK))
if not (os.path.exists(os.environ['ZTAP']) and os.path.exists(os.environ['ZSYM']) and os.path.isdir(TSRC)):
    print('FAIL no track %s build: run  TRACK=%s bash build.sh  first' % (TRACK, TRACK)); print('RESULT: 1 FAIL'); sys.exit(1)
src = open(os.path.join(HERE, 'drive_test.py')).read()
src = src[:src.index('with Racer(headless=True)')].replace("os.path.dirname(os.path.abspath(__file__))", repr(HERE))
assert src.count("os.path.join(ROOT, 'src',") == 6
src = src.replace("os.path.join(ROOT, 'src',", "os.path.join(%r," % TSRC)    # the map, waypoints and masks the tape was built from
exec(src)
fails = 0
def ok(c, m):
    global fails
    print('PASS' if c else 'FAIL', m); fails += 0 if c else 1
rd = lambda n: open(os.path.join(TSRC, n)).read()
WPS = [tuple(int(v) for v in l.split('dw')[1].split(',')) for l in rd('waypoints.asm').split('waypoints:')[1].splitlines() if 'dw' in l]
WS, LAPS, C_LAPS, C_WP = SYM['ws'], SYM['laps'], 25, 13
OMAP = [[int(c) for b in l.split('defb')[1].split(',') for c in b.strip().lstrip('%')] for l in rd('omap.asm').splitlines() if 'defb' in l]
MM = [l for l in rd('minimap.txt').split()]                             # the mini-map as generated: '#' = ink
mm_ = rd('minimap.asm'); MSC = int(re.search(r'\* (\d+) / 256', mm_).group(1)); MMX0 = int(re.search(r'MMX0\s+equ\s+(-?\d+)', mm_).group(1)); MMY0 = int(re.search(r'MMY0\s+equ\s+(-?\d+)', mm_).group(1))
CANS = [(int(re.search(r'NOS_%s_X equ (\d+)' % k, src_w).group(1)), int(re.search(r'NOS_%s_Y equ (\d+)' % k, src_w).group(1))) for src_w in [rd('world.asm')] for k in 'ABC']
for cx_, cy_ in CANS:                                                   # the NOS and oil cans come and go (the game takes their tiles out of the
    world[cy_ - 8:cy_ + 8, cx_ - 4:cx_ + 4] = 0                         # row lists and puts them back): they are checked apart, below
def window_bad_t(sp):
    """drive_test's window_bad, the cans' own cells left out: (wrong pixels, cans in view and showing)"""
    at_copy_done(sp)
    camx, camy = g(sp, 'camx'), g(sp, 'camy')
    bits = screen_bits(sp)[WY:WY + WH, 8:8 + WW]
    want = world[camy:camy + WH, camx:camx + WW] | (cloth(camx, camy) & ~wmask[camy:camy + WH, camx:camx + WW])
    mask = np.ones_like(want, dtype=bool)
    mask[8 - WY:32 - WY, 56 - 8:136 - 8] = False; mask[WH - 16:WH, WW - 48:WW] = False
    want = want.copy(); want[MM_TOP:MM_TOP + MM_H, 0:24] |= map_now(sp)   # (the mini-map over the picture: as window_bad)
    mask[2:20, WW - 40:WW] = False; mask[136 - WY:152 - WY, 56 - 8:136 - 8] = False     # (the lights, spoons and mug, map, plate, bubble: as window_bad)
    ar = arrow_state(sp)
    if ar: mask[max(ar[2], 0):max(ar[2] + 11, 0), max(ar[1], 0):max(ar[1] + 16, 0)] = False   # (and the corner arrow, while it is on)
    for n in range(N):
        c = car(sp, n); cx, cy = c['x'] - camx, c['y'] - camy
        mask[max(cy - 6, 0):max(cy + 23, 0), max(cx - 3, 0):max(cx + 21, 0)] = False
    showing = 0
    for cx_, cy_ in CANS:
        x, y = cx_ - camx, cy_ - camy
        if 4 <= x < WW - 4 and 8 <= y < WH - 8:
            showing += bool((bits[y - 8:y + 8, x - 4:x + 4] & mask[y - 8:y + 8, x - 4:x + 4]).sum() > 20)
            mask[y - 8:y + 8, x - 4:x + 4] = False
        else: mask[max(y - 8, 0):max(y + 8, 0), max(x - 4, 0):max(x + 4, 0)] = False
    return int(((bits != want) & mask).sum()), showing
road_px = lambda x, y: 0 <= x < MAPW * 8 and 0 <= y < MAPH * 8 and surf[(y // 8) * MAPW + x // 8] == 0
laps_of = lambda sp, n: sp.read8(CARS + n * CS + C_LAPS)
def boot():
    sp = Racer(headless=True); sp.__enter__(); sp.load_tape(TAP); t = 0
    while g(sp, 'renders') == 0 and t < 60: sp.run(duration=0.1, fast_forward=True); t += 0.1
    return sp
def park_cpus(sp):                                                      # out of the way, engines off (pace 0)
    for i in CPUS: put(sp, i, 4 + 40 * i, SY + 58); sp.write(CARS + i * CS + 19, bytes([0]))
def heading(x0, y0, x1, y1): return round(math.atan2(x1 - x0, -(y1 - y0)) / (2 * math.pi) * 64) % 64   # 0 up, 16 right, 32 down
assert (np.array([[c == '#' for c in r] for r in MM], dtype=np.uint8) == MM_ROWS).all()     # (minimap_diff is drive_test's now: the map in the window's bottom left corner)

# ---------------------------------------------------------------- THE BRIDGE
_w = rd('world.asm')
BR = {k: int(re.search(r'BR_%s\s+equ\s+(\d+)' % k, _w).group(1)) for k in ('X0', 'X1', 'Y0', 'Y1', 'Y2', 'Y3', 'M0', 'M1', 'H0', 'H1')}
LVL = 0x5E00; RMP = LVL + 8                                           # the cars' levels (bridge.asm): 0 on the table, 1 on the bridge
XC, YC = (BR['X0'] + BR['X1']) // 2, (BR['M0'] + BR['M1']) // 2      # the crossing's middle
C_VY, C_PACE = 8, 19
lvl = lambda sp, n: sp.read8(LVL + n)
def setl(sp, n, v): sp.write(LVL + n, bytes([v]))
def fresh():
    sp = boot(); go_green(sp); press(sp, 'Q', False); park_cpus(sp); sp.run(duration=0.5, fast_forward=True); return sp
def place(sp, n, x, y, ang, level):
    put(sp, n, x, y, ang); setl(sp, n, level)
def view(sp):
    """the window as shown and as the map says it should be with no cars in it; the camera"""
    at_copy_done(sp)
    camx, camy = g(sp, 'camx'), g(sp, 'camy')
    bits = screen_bits(sp)[WY:WY + WH, 8:8 + WW]
    want = world[camy:camy + WH, camx:camx + WW] | (cloth(camx, camy) & ~wmask[camy:camy + WH, camx:camx + WW])
    return bits != want, camx, camy
def box_diff(sp, x, y, xa=None, xb=None):
    """pixels that differ from the bare map in the car's box at world (x, y) - within world columns xa..xb if given"""
    d, camx, camy = view(sp)
    x0, x1 = max(x - 2, xa if xa is not None else 0), min(x + 18, xb if xb is not None else 9999)
    wx0, wx1, wy0, wy1 = x0 - camx, x1 - camx, y - 6 - camy, y + 23 - camy
    assert 56 <= wx0 and wx1 <= WW - 48 and 26 <= wy0 and wy1 <= WH - 18, 'the car is not clear of the window\'s edge and its plates: %r' % ((wx0, wx1, wy0, wy1),)
    return int(d[wy0:wy1, wx0:wx1].sum())
print('the bridge: upper road x %(X0)d-%(X1)d, ramp up y %(Y0)d-%(Y1)d, deck to %(Y2)d, ramp down to %(Y3)d; the lower road y %(M0)d-%(M1)d, covered x %(H0)d-%(H1)d' % BR)
ok((XC, YC) == (188, 336) and BR['Y0'] == 240 and BR['Y3'] == 432 and BR['H0'] == 136 and BR['H1'] == 240, 'the bridge is where the design puts it: the crossing at (%d, %d)' % (XC, YC))
ok(not any(OMAP[ty][tx] for ty in range(BR['Y0'] // 8, BR['Y3'] // 8) for tx in range((BR['X0'] - 36) // 8, (BR['X1'] + 36) // 8 + 1)), 'no cereal O stands on or beside the bridge, its ramps or the tunnel')
UP_WPS = [k for k, (x, y) in enumerate(WPS) if x == XC and BR['Y0'] < y <= BR['Y3'] + 8]
# THE LOOK (Grant's picture, 16 Nov 2026). The kerb walls are not map tiles: the game draws them itself (kerb_draw) - 8 x 8 blocks, blue
# and cyan in turn, the cyan ones with a blue line down each side and clean paper between. Put into the map the tests compare with:
KERB_X = (BR['X0'] - 8, BR['X1'])
for xa in KERB_X:
    for y in range(BR['Y0'], BR['Y3']):
        if ((y - BR['Y0']) // 8) % 2 == 0: world[y, xa:xa + 8] = 1
        else: world[y, xa] = world[y, xa + 7] = 1
    wmask[BR['Y0']:BR['Y3'], xa:xa + 8] = True
ok(all(world[BR['Y0']:BR['Y3'], xa + i].all() for xa in KERB_X for i in (0, 7)) and world[BR['Y3'] - 1, KERB_X[0]:KERB_X[0] + 8].all(),
   'each kerb wall is one wall: an unbroken blue line down both its sides from ramp foot to ramp foot, closed at the foot')
ADDED_OS = [(104, 280), (272, 368), (272, 296), (104, 256), (224, 440), (144, 440)]
def seg_d(px_, py_, a_, b_):
    (x1, y1), (x2, y2) = a_, b_; dx, dy = x2 - x1, y2 - y1; t = max(0, min(1, ((px_ - x1) * dx + (py_ - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px_ - x1 - t * dx, py_ - y1 - t * dy)
road_d = lambda x, y: min(seg_d(x, y, WPS[i], WPS[(i + 1) % NWP]) for i in range(NWP))
conc = wmask.copy(); conc[BR['Y0']:BR['Y3'], BR['X0']:BR['X1']] = True          # the concrete, the kerbs and the deck
ok(sum(map(sum, OMAP)) == 156 and all(OMAP[oy // 8][ox // 8] for ox, oy in ADDED_OS), 'the six added cereal O\'s are in the map (156 in all)')
ok(all(road_d(ox + 4, oy + 4) >= 34 and not conc[max(oy - 2, 0):oy + 10, max(ox - 2, 0):ox + 10].any() for ox, oy in ADDED_OS),
   'none of the six is on a road (the nearest is %.0f px from the middle line; the road is 36 each side), nor within 2 px of a wing, a ramp wall, a kerb or the deck' % min(road_d(ox + 4, oy + 4) for ox, oy in ADDED_OS))
print('  waypoints a car heads for while it is on the bridge:', UP_WPS)

# ---- LEVELS
sp = fresh()
place(sp, 1, XC - 8, YC - 8, 32, 1); place(sp, 2, XC - 8, YC - 8, 48, 0)        # one on the deck, one under it: the same spot
b0 = g(sp, 'bumps'); sp.run(duration=1.5, fast_forward=True)
c1, c2 = car(sp, 1), car(sp, 2)
ok(g(sp, 'bumps') == b0 and (c1['x'], c1['y'], c2['x'], c2['y']) == (XC - 8, YC - 8, XC - 8, YC - 8) and (lvl(sp, 1), lvl(sp, 2)) == (1, 0),
   'a computer car on the deck and one under it at the crossing, on the very same spot for 1.5 s: no bump, neither moves, each keeps its level')
setl(sp, 1, 0); sp.run(duration=0.5, fast_forward=True)
c1, c2 = car(sp, 1), car(sp, 2)
ok(g(sp, 'bumps') > b0 and (c1['x'], c1['y']) != (c2['x'], c2['y']), 'the same two on one level do bump and are knocked apart (%d bumps)' % (g(sp, 'bumps') - b0))
park_cpus(sp); [setl(sp, n, 0) for n in CPUS]
place(sp, 0, XC - 8, YC - 8, 32, 1); place(sp, 1, XC - 8, YC - 6, 48, 0)        # you on the deck, a computer car under you
b0 = g(sp, 'bumps'); d0 = sp.read8(SYM['dmg']); sp.run(duration=1.5, fast_forward=True)
ok(g(sp, 'bumps') == b0 and sp.read8(SYM['dmg']) == d0 and (car(sp, 0)['x'], car(sp, 1)['x']) == (XC - 8, XC - 8), 'you on the deck with a computer car under you: no bump, no damage')
place(sp, 0, XC - 8, YC - 8, 48, 0); place(sp, 1, XC - 8, YC - 6, 32, 1)        # and the other way up
b0 = g(sp, 'bumps'); sp.run(duration=1.5, fast_forward=True)
ok(g(sp, 'bumps') == b0, 'you under the deck with a computer car on it: no bump')
sp.__exit__(None, None, None)

# the levels follow the cars round: 45 s of the four computer cars racing
sp = boot(); go_green(sp); press(sp, 'Q', False); sp.run(duration=0.3, fast_forward=True); put(sp, 0, 40, 40)
t = 0.0; on_deck = under = wrong = 0; ZSP = {'ramp up': [], 'deck': [], 'ramp down': []}; b0 = g(sp, 'bumps')
while t < 45:
    sp.run(duration=0.1, fast_forward=True); t += 0.1
    for n in CPUS:
        c = car(sp, n); cx, cy = c['x'] + 8, c['y'] + 8; L = lvl(sp, n)
        if BR['X0'] <= cx < BR['X1'] and BR['Y0'] + 20 <= cy < BR['Y3'] - 28:
            up = c['wp'] in UP_WPS
            on_deck += up; under += not up; wrong += (L != up)
            if up: ZSP['ramp up' if cy < BR['Y1'] else 'deck' if cy < BR['Y2'] else 'ramp down'].append(math.hypot(c['vx'], c['vy']))
        elif not (BR['X0'] - 40 <= cx < BR['X1'] + 40 and BR['Y0'] - 8 <= cy < BR['Y3'] + 8): wrong += (L != 0)
ok(on_deck > 20 and under > 10 and wrong == 0, 'racing, every computer car is on level 1 over the bridge (%d sightings), level 0 under it (%d) and everywhere else (wrong: %d)' % (on_deck, under, wrong))
print('  the computer cars\' speed, px a frame: ' + ', '.join('%s %.2f' % (k, sum(v) / max(len(v), 1)) for k, v in ZSP.items()))
sp.__exit__(None, None, None)

# ---- WALLS
def shove(sp, n, x, y, ang, level, secs=3.0, nos=True):
    """your car (or you pushing car n) driven flat out: the places it was seen at"""
    place(sp, 0, x, y, ang, level); press(sp, 'Q', True); seen = []; t = 0.0
    while t < secs:
        if nos: sp.write(SYM['boost_t'], bytes([200]))
        sp.run(duration=0.04, fast_forward=True); t += 0.04
        at_copy_done(sp)                               # (as each picture goes up: between pictures your car moves a TV frame at a time and is put back before it is drawn)
        c = car(sp, n); seen.append((c['x'], c['y'], lvl(sp, n)))
    press(sp, 'Q', False); return seen
sp = fresh()
s = shove(sp, 0, XC - 8, YC - 8, 16, 1)
ok(max(p[0] for p in s) <= BR['X1'] - 12 and all(p[2] == 1 for p in s), 'on the deck, driven flat out with NOS at the right-hand wall for 3 s: your car stays on (furthest x %d; the wall is at %d, the car 16 wide)' % (max(p[0] for p in s), BR['X1']))
s = shove(sp, 0, XC - 8, YC - 8, 48, 1)
ok(min(p[0] for p in s) >= BR['X0'] - 4 and all(p[2] == 1 for p in s), '... and at the left-hand wall (least x %d; the wall is at %d)' % (min(p[0] for p in s), BR['X0']))
s = [p for p in shove(sp, 0, XC - 8, BR['Y0'] + 16, 16, 1) + shove(sp, 0, XC - 8, BR['Y3'] - 36, 48, 1) + shove(sp, 0, XC - 8, BR['Y0'] + 16, 44, 1, secs=1.5) + shove(sp, 0, XC - 8, BR['Y3'] - 36, 20, 1, secs=1.5) if p[2]]
ok(len(s) > 100 and BR['X0'] - 4 <= min(p[0] for p in s) and max(p[0] for p in s) <= BR['X1'] - 12, 'the ramps\' walls hold too: on either ramp, for as long as the car is on the bridge (x %d to %d over %d sightings)' % (min(p[0] for p in s), max(p[0] for p in s), len(s)))
place(sp, 1, BR['X1'] - 20, YC - 8, 32, 1)
s = shove(sp, 1, XC - 8, YC - 8, 16, 1)
ok(max(p[0] for p in s) <= BR['X1'] - 12 and all(p[2] == 1 for p in s), 'a computer car on the deck, pushed at the wall by your car: it cannot be pushed through (furthest x %d)' % max(p[0] for p in s))
park_cpus(sp); [setl(sp, n, 0) for n in CPUS]
s = shove(sp, 0, XC - 8, YC - 8, 0, 0) + shove(sp, 0, XC - 8, YC - 8, 32, 0)
ok(BR['M0'] - 6 <= min(p[1] for p in s) and max(p[1] for p in s) <= BR['M1'] - 10 and all(p[2] == 0 for p in s), 'under the deck, driven at the tunnel\'s walls: your car stays in the lower road (y %d to %d; the walls at %d and %d)' % (min(p[1] for p in s), max(p[1] for p in s), BR['M0'], BR['M1']))
s = shove(sp, 0, BR['X0'] - 60, BR['Y0'] + 30 - 8, 16, 0)
s2 = shove(sp, 0, BR['X1'] + 44, BR['Y3'] - 30 - 8, 48, 0)
ok(max(p[0] for p in s) <= BR['X0'] - 14 and min(p[0] for p in s2) >= BR['X1'] - 2 and all(p[2] == 0 for p in s + s2), 'from the table, driven at the bridge\'s side: your car cannot get in (stopped at x %d from the left, %d from the right)' % (max(p[0] for p in s), min(p[0] for p in s2)))
s = shove(sp, 0, XC - 8, BR['Y0'] - 60, 32, 0, secs=4.0, nos=False)
ls = [p[2] for p in s]
ok(ls[0] == 0 and 1 in ls and ls[-1] == 0 and max(p[1] for p in s) > BR['Y3'] and BR['X0'] - 4 <= min(p[0] for p in s if p[2]) and all(p[2] == (BR['Y0'] - 8 <= p[1] + 8 < BR['Y3'] + 8) or abs(p[1] + 8 - BR['Y0']) < 12 or abs(p[1] + 8 - BR['Y3']) < 12 for p in s),
   'driven straight down the upper road: level 0, up at the foot of the ramp, 1 all the way over, 0 again off the far ramp (y reached %d)' % max(p[1] for p in s))
sp.__exit__(None, None, None)

# ---- DRAWING ORDER
sp = fresh()
place(sp, 0, XC - 8, YC - 8, 48, 0); sp.run(duration=2.5, fast_forward=True)
d, camx, camy = view(sp)
cov = d[max(BR['Y0'] - camy, 20):BR['Y3'] - camy, BR['H0'] - camx:BR['H1'] - camx][:WH - 60]
bits = screen_bits(sp)[WY:WY + WH, 8:8 + WW]; clo = cloth(camx, camy); wm = wmask[camy:camy + WH, camx:camx + WW]
ys, xs = slice(20, WH - 44), slice(BR['H0'] - 28 - camx, BR['H1'] + 28 - camx)   # the bridge and its wings, clear of the plates at the window's top and foot
hidden = int((clo & wm & ~world[camy:camy + WH, camx:camx + WW].astype(bool))[ys, xs].sum())
ok(hidden > 40 and not (bits.astype(bool) & clo & wm & ~world[camy:camy + WH, camx:camx + WW].astype(bool))[ys, xs].any(),
   'the concrete is clean: %d of the cloth\'s dots fall inside the wings, the ramp walls and the kerbs\' cyan blocks in this view, and none is on the screen' % hidden)
kb = [bits[20:WH - 44, xa - camx:xa - camx + 8] for xa in KERB_X]
ok(all(k[:, 0].all() and k[:, 7].all() for k in kb) and all(((k[:, 1:7].sum(axis=1) == 0) | (k[:, 1:7].sum(axis=1) == 6)).all() for k in kb),
   'on the screen both kerb walls are solid: a blue line down each side on every line, and between them all blue or all clean')
ok(box_diff(sp, XC - 8, YC - 8) == 0 and cov.sum() == 0, 'your car on the table under the deck: nothing of it in the window, and every pixel of the deck, kerbs and tunnel mouths is as the map has it')
shot(sp, 'track5_under.png')
place(sp, 0, BR['H1'] + 40, YC - 8, 48, 0); sp.run(duration=2.5, fast_forward=True)
n_out = box_diff(sp, BR['H1'] + 40, YC - 8)
ok(n_out > 40, 'beyond the cover it is in the window again (%d pixels of car)' % n_out)
res = []
for x, edge, name in ((BR['H0'] - 8, BR['H0'], 'left'), (BR['H1'] - 8, BR['H1'], 'right'), (BR['H0'] - 3, BR['H0'], 'left'), (BR['H1'] - 12, BR['H1'], 'right')):
    place(sp, 0, x, YC - 8, 48, 0); sp.run(duration=2.5, fast_forward=True)
    inside = box_diff(sp, x, YC - 8, xa=edge) if name == 'left' else box_diff(sp, x, YC - 8, xb=edge)
    outside = box_diff(sp, x, YC - 8, xb=edge) if name == 'left' else box_diff(sp, x, YC - 8, xa=edge)
    res.append((x, inside, outside))
    if x == BR['H0'] - 8: shot(sp, 'track5_half_under.png')
ok(all(i == 0 and o > 5 for x, i, o in res), 'half under, at either mouth: the part outside the cover shows and not a pixel inside it is touched (x, pixels inside, outside: %s)' % res)
place(sp, 0, XC - 8, YC - 28, 32, 1); sp.run(duration=2.5, fast_forward=True)
n_on = box_diff(sp, XC - 8, YC - 28)
ok(n_on > 40, 'on the deck your car is drawn over it (%d pixels of car)' % n_on)
place(sp, 1, XC - 8, YC + 12, 48, 0); sp.run(duration=1.0, fast_forward=True)
ok(box_diff(sp, XC - 8, YC + 12) == 0 and box_diff(sp, XC - 8, YC - 28) > 40, 'a computer car under the deck beside you is hidden while you, on the deck, show')
place(sp, 1, XC - 8, YC + 12, 32, 1); sp.run(duration=1.0, fast_forward=True)
ok(box_diff(sp, XC - 8, YC + 12) > 40, 'and with that car on the deck too, both show')
shot(sp, 'track5_deck.png')
sp.__exit__(None, None, None)

# ---- RAMPS: the same run with the slope's pull, and with it taken out of the code (the control)
def over(sp, n, v0):
    """car n from just above the ramp up, going down the screen at v0 px a frame, driven on: speed at each place"""
    for m in CPUS: put(sp, m, 4 + 40 * m, SY + 58); sp.write(CARS + m * CS + C_PACE, bytes([0])); setl(sp, m, 0)
    b = CARS + n * CS
    place(sp, n, XC - 8, BR['Y0'] - 12, 32, 0); v = int(v0 * 256); sp.write(b + C_VY, bytes([v & 255, v >> 8]))
    if n: sp.write(b + C_WP, bytes([UP_WPS[1]])); sp.write(b + C_PACE, bytes([15]))
    else: press(sp, 'Q', True)
    at = {}; t = 0.0; t0 = None
    while t < 5 and car(sp, n)['y'] + 8 < BR['Y3'] + 4:
        sp.run(duration=0.02, fast_forward=True); t += 0.02; c = car(sp, n); cy = c['y'] + 8
        if t0 is None and cy >= BR['Y0']: t0 = t
        for k in ('Y1', 'Y2', 'Y3'):
            if k not in at and cy >= BR[k] - 2: at[k] = (math.hypot(c['vx'], c['vy']), t - (t0 or 0))
        if BR['Y2'] + 8 <= cy < BR['Y3']: at['down'] = max(at.get('down', 0), math.hypot(c['vx'], c['vy']))     # (the fastest it went on the ramp down:
    press(sp, 'Q', False)
    return at
def flat_top(sp, n):                                   # its top speed along the start straight
    b = CARS + n * CS
    place(sp, n, 250, SY - 8, 16, 0)
    if n: sp.write(b + C_WP, bytes([SYM['ws'] + 2])); sp.write(b + C_PACE, bytes([15]))
    else: press(sp, 'Q', True)
    v = 0
    for _ in range(30): sp.run(duration=0.1, fast_forward=True); v = max(v, math.hypot(car(sp, n)['vx'], car(sp, n)['vy']))
    press(sp, 'Q', False); return v
rows = []
for n, name in ((0, 'you'), (1, 'a computer car (FRANK)')):
    res = {}
    for pull in (True, False):
        sp = fresh()
        if not pull:                                   # the control: ramp_adj's "ret z" made "ret" - no ramp changes anything
            a = SYM['ramp_adj']; code = bytes(sp.read8(a + i) for i in range(12)); assert code.count(0xC8) == 1
            sp.write(a + code.index(0xC8), bytes([0xC9]))
        v0 = flat_top(sp, n); res[pull] = (v0, over(sp, n, v0)); sp.__exit__(None, None, None)
    (v0, a), (_, b) = res[True], res[False]
    upr, dnr = a['Y1'][0] / b['Y1'][0], a['down'] / b['down']
    rows.append((name, v0, a, b, upr, dnr))
    print('  %s: top speed on the flat %.2f px a frame. At the top of the ramp up %.2f (no ramp: %.2f) = %.0f%%; at the end of the deck %.2f (%.2f); fastest on the ramp down %.2f (%.2f) = %.0f%%; ramp foot to ramp foot in %.2f s (%.2f s)'
          % (name, v0, a['Y1'][0], b['Y1'][0], 100 * upr, a['Y2'][0], b['Y2'][0], a['down'], b['down'], 100 * dnr, a['Y3'][1], b['Y3'][1]))
ok(all(0.80 <= r[4] <= 0.95 for r in rows), 'up the ramp a car is a little slower than on the flat: %s of the speed it would have had' % ' and '.join('%s %.0f%%' % (r[0], 100 * r[4]) for r in rows))
ok(all(1.03 <= r[5] <= 1.20 for r in rows), 'down the ramp a little faster: %s' % ' and '.join('%s %.0f%%' % (r[0], 100 * r[5]) for r in rows))

# ---- SPEED: pictures a second near the crossing against the rest of the lap (your car driven by script, in the pack)
def drive(sp, secs, dt=0.06):
    t = 0.0; keys = set(); out = []
    while t < secs:
        c = car(sp, 0); wx, wy = WPS[(c['wp'] + 1) % NWP]
        e = (heading(c['x'] + 8, c['y'] + 8, wx, wy) - c['ang'] + 32) % 64 - 32
        k = set()
        if e > 1: k.add('P')
        if e < -1: k.add('O')
        if abs(e) < 12 or math.hypot(c['vx'], c['vy']) < 0.9: k.add('Q')
        for q in list(keys - k): press(sp, q, False); keys.discard(q)
        for q in k - keys: press(sp, q, True); keys.add(q)
        r0 = g(sp, 'renders'); sp.run(duration=dt, fast_forward=True); t += dt
        out.append((c['x'] + 8, c['y'] + 8, (g(sp, 'renders') - r0) & 0xFFFF, lvl(sp, 0)))
    for q in keys: press(sp, q, False)
    return out
sp = boot(); go_green(sp); press(sp, 'Q', False)
tr = drive(sp, 62.0)[20:]
near = [p for p in tr if abs(p[0] - XC) < 96 and abs(p[1] - YC) < 110]
far = [p for p in tr if not (abs(p[0] - XC) < 150 and abs(p[1] - YC) < 170)]
pps = lambda v: sum(p[2] for p in v) / (0.06 * len(v))
under_ = [p for p in tr if BR['H0'] <= p[0] < BR['H1'] and BR['M0'] <= p[1] < BR['M1'] and p[3] == 0]
print('  pictures a second, your car driven by script in the pack for 62 s: near the crossing %.1f (%d samples), elsewhere %.1f (%d), under the deck itself %.1f (%d)' % (pps(near), len(near), pps(far), len(far), pps(under_) if under_ else 0, len(under_)))
ok(len(near) > 60 and len(under_) > 5 and pps(near) >= 10.0, 'near the crossing the game runs at %.1f pictures a second against %.1f elsewhere (the whole bridge in view takes 5 TV frames a picture; 10 a second is the floor asked of it here)' % (pps(near), pps(far)))
sp.__exit__(None, None, None)

if not os.environ.get('BRIDGE'):
    # ---------------------------------------------------------------- the data the tape was built from
    ok(MAPW == 72 and MAPH == 74, 'the map is the size of this track\'s design: %d x %d tiles (mini-map at %d/256)' % (MAPW, MAPH, MSC))
    ok(46 < NWP <= 61 and (LAPS + 1) * NWP - 1 < 246, 'its %d waypoints fit the game\'s one-byte progress over %d laps (%d at most, under the 246 kept for finished cars)' % (NWP, LAPS, (LAPS + 1) * NWP - 1))
    gaps = [math.dist(WPS[i], WPS[(i + 1) % NWP]) for i in range(NWP)]
    lap_px = sum(gaps)
    ok(max(gaps) <= 42.5 and all(road_px(x, y) for x, y in WPS) and not any(OMAP[y // 8][x // 8] for x, y in WPS),
       'the waypoints are on the road, clear of the cereal O\'s, %.1f to %.1f px apart (your car passes one when within 40 of it); once round is %d px' % (min(gaps), max(gaps), lap_px))
    ok(sum(map(sum, OMAP)) > 128 and not any(OMAP[ty][tx] and surf[ty * MAPW + tx] == 0 and all(road_px(tx * 8 + i, ty * 8 + j) for i in (-16, 23) for j in (-16, 23)) for ty in range(MAPH) for tx in range(MAPW)),
       'the cereal O\'s (%d) stand along the road\'s edges, none out in the road' % sum(map(sum, OMAP)))

    # ---------------------------------------------------------------- the grid, the window, the mini-map
    sp = boot()
    sp.run(duration=3.0, fast_forward=True)
    cs = [car(sp, n) for n in range(N)]
    print('grid:', [(c['x'], c['y'], c['wp']) for c in cs])
    ok(all(c['vx'] == 0 and c['vy'] == 0 and c['ang'] == 16 for c in cs), 'five cars wait on the grid, facing right')
    ok(all(road_px(c['x'] + i, c['y'] + j) for c in cs for i in (0, 15) for j in (0, 15)), 'every car is wholly on the road')
    ok(all(not OMAP[(c['y'] + j) // 8][(c['x'] + i) // 8] for c in cs for i in (0, 15) for j in (0, 15)), 'no car starts on a cereal O')
    LINE_X = 384
    ok(all(c['x'] + 16 <= LINE_X for c in cs) and all(abs(c['y'] + 8 - SY) < 36 for c in cs) and cs[0]['x'] == max(c['x'] for c in cs),
       'they are on the start straight (y %d) behind the line (x %d), you on pole' % (SY, LINE_X))
    ok(len({(c['x'], c['y']) for c in cs}) == N and all(abs(a['x'] - b['x']) >= 16 or abs(a['y'] - b['y']) >= 16 for i, a in enumerate(cs) for b in cs[i + 1:]), 'no two cars share a place')
    line = world[SY - 30:SY + 30, LINE_X:LINE_X + 8]
    ok(line.sum() > 150 and (WPS[WS][0] > LINE_X + 8 and abs(WPS[WS][1] - SY) < 4 and WPS[(WS - 1) % NWP][0] <= LINE_X + 8),
       'the chequered start line crosses the road at x %d; waypoint %d is the first one past it (x %d)' % (LINE_X, WS, WPS[WS][0]))
    ok(all(0 < (WPS[c['wp']][0] - c['x'] - 8) < 80 and abs(WPS[c['wp']][1] - SY) < 4 for c in cs), 'each car\'s first waypoint is just ahead of it on the straight')
    bad, _ = window_bad_t(sp)
    ok(bad == 0, 'on the grid the window matches the world map pixel for pixel, cars excluded (%d wrong)' % bad)
    md, dots, ink = minimap_diff(sp)
    sb = screen_bits(sp)
    ok(md == 0 and ink > 60 and all(sp.read8(0x5800 + r * 32 + c) == 0x29 for r in range(15, 20) for c in range(1, 7)), 'the mini-map in the window\'s bottom left corner is this track\'s road, line for line, black on yellow (%d ink pixels, %d wrong outside the cars\' dots)' % (ink, md))
    ok(all(d is None or (0 <= d[1] <= 36 and 0 <= d[0] <= 45) for d in dots) and sum(d is not None for d in dots) >= N - 1 and not sb[0:40, 208:256].any() and sp.read8(0x5800 + 5 * 32 + 26) == 0x4F,
       'the cars\' dots are inside the map\'s box; the panel\'s top right, where the map was, is plain above the RACE heading (dots at %s)' % dots)
    shot(sp, 'track%s_grid.png' % TRACK)
    x0 = [c['x'] for c in cs]
    press(sp, 'Q', True); sp.run(duration=1.5, fast_forward=True)
    ok([car(sp, n)['x'] for n in range(N)] == x0 and sp.read8(SYM['race_on']) == 0, 'on the red lights nobody moves')
    go_green(sp); press(sp, 'Q', False)
    ok(sp.read8(SYM['race_on']) == 1, 'green: the race is on')

    # ---------------------------------------------------------------- the four computer cars: 3 laps each
    sp.run(duration=0.3, fast_forward=True)
    put(sp, 0, 40, 40)                                    # you: parked in the top-left corner, off the track
    K = len(CPUS); last = [laps_of(sp, n) for n in CPUS]; lt = [[] for _ in CPUS]; onroad = [0] * K; samples = 0
    still = [0.0] * K; worst = [0.0] * K; prev = [None] * K; t = 0.0; m0 = g(sp, 'mistakes'); offmap = 0
    while t < 150 and min(last) < LAPS + 1:
        sp.run(duration=0.1, fast_forward=True); t += 0.1; samples += 1
        for i, n in enumerate(CPUS):
            c = car(sp, n); l = laps_of(sp, n)
            if l != last[i]: last[i] = l; lt[i].append(round(t, 1))
            if l > LAPS: continue                         # (in: it may do as it likes)
            tx, ty = (c['x'] + 8) // 8, (c['y'] + 8) // 8
            inmap = 0 <= tx < MAPW and 0 <= ty < MAPH; offmap += not inmap
            onroad[i] += inmap and surf[ty * MAPW + tx] == 0
            if prev[i] and math.dist(prev[i], (c['x'], c['y'])) < 2: still[i] += 0.1; worst[i] = max(worst[i], still[i])
            else: still[i] = 0.0
            prev[i] = (c['x'], c['y'])
    names = ['CYAN (FRANK)', 'GREEN (SPIKE)', 'PINK (BRUNO)', 'WHITE (JANE)']
    lapt = [[round(b - a, 1) for a, b in zip(x, x[1:])] for x in lt]
    for i in range(K): print('  %-14s crossed the line at %s s: laps of %s s; longest stop %.1f s' % (names[i], lt[i], lapt[i], worst[i]))
    ok(min(last) >= LAPS + 1, 'all four computer cars complete %d laps (line crossings %s, in %.0f s)' % (LAPS, last, t))
    ok(all(len(x) == LAPS for x in lapt) and offmap == 0, 'each has %d timed laps, and none left the map' % LAPS)
    flat = [v for x in lapt for v in x] or [0]
    avg = [sum(x) / len(x) if x else 0 for x in lapt]
    print('  average laps (s):', ' '.join('%.1f' % a for a in avg), ' - fastest lap %.1f, slowest %.1f' % (min(flat), max(flat)))
    ok(max(flat) < 1.35 * min(flat), 'no lap is much longer than another - nobody stuck, no line missed or counted twice (%.1f to %.1f s)' % (min(flat), max(flat)))
    ok(max(worst) < 2.0, 'no computer car stands still for 2 s (longest %.1f s)' % max(worst))
    ok(min(o / samples for o in onroad) > 0.8, 'the computer cars stay on the road (%s of the time)' % ' '.join('%.0f%%' % (100 * o / samples) for o in onroad))
    REF = 18.1 * lap_px / 1473                            # track 1's fastest computer car (tests/drive_test.py: 18.1 s a lap of 1473 px)
    ok(0.8 * REF < min(avg) < 1.2 * REF, 'the fastest laps in %.1f s: in step with track 1\'s 18.1 s for the length (%.1f s expected)' % (min(avg), REF))
    ok(sp.read8(SYM['position']) == 5 and sp.read8(SYM['race_over']) == 0, 'parked, you are 5th, and the race waits for you')
    print('  mistakes', g(sp, 'mistakes') - m0, 'bumps', g(sp, 'bumps'))
    sp.__exit__(None, None, None)

    # ---------------------------------------------------------------- your laps, the car placed along the waypoints
    sp = boot(); go_green(sp); press(sp, 'Q', False); park_cpus(sp); sp.run(duration=0.5, fast_forward=True)
    def stand(sp, k, secs=0.3):                           # your car on waypoint k, pointing at the next
        x, y = WPS[k % NWP]; nx, ny = WPS[(k + 1) % NWP]
        put(sp, 0, x - 8, y - 8, heading(x, y, nx, ny)); sp.run(duration=secs, fast_forward=True)
    k0 = car(sp, 0)['wp']; l0 = laps_of(sp, 0); seen = []; missed = []; wbad = []; cans_seen = 0; shots = {NWP // 3: 'a', 2 * NWP // 3: 'b'}
    for step in range(LAPS * NWP + 2):
        k = (k0 + step) % NWP
        before = laps_of(sp, 0); stand(sp, k); after = laps_of(sp, 0)
        if after != before: seen.append((step, k, after))
        if (car(sp, 0)['wp'] - k) % NWP not in (1, 2, 3): missed.append(k)
        if step < NWP and step % 4 == 0:                  # the first time round: the window against the map, every 4th waypoint
            sp.run(duration=0.4, fast_forward=True)       # (the view settles on the car)
            b, sh = window_bad_t(sp); wbad.append((k, b)); cans_seen += sh
        if step in shots: sp.run(duration=0.5, fast_forward=True); shot(sp, 'track%s_lap_%s.png' % (TRACK, shots[step]))
    print('  line crossings (step, waypoint, laps):', seen)
    ok(not missed, 'placed on each waypoint in turn, your next waypoint moves on every time (%d places; missed %s)' % (LAPS * NWP + 2, missed))
    # (standing on the waypoint before the line, the line's own is within reach too - 34 px on: so the lap may show one place early)
    ok(all(s[1] in (WS, (WS - 1) % NWP) for s in seen) and [s[2] for s in seen] == list(range(l0 + 1, l0 + 1 + len(seen))) and len(seen) == LAPS + 1 and laps_of(sp, 0) == LAPS + 1,
       'a lap is counted each time you pass waypoint %d, the first past the line, and nowhere else: %d crossings in %d times round, lap count %d' % (WS, len(seen), LAPS, laps_of(sp, 0)))
    ok(all(b == 0 for k, b in wbad), 'all round the lap the window matches the world map pixel for pixel (%d places; wrong: %s)' % (len(wbad), [x for x in wbad if x[1]]))
    ok(cans_seen >= 1 and all(road_px(x, y) and not OMAP[y // 8][x // 8] for x, y in CANS), 'the three cans stand on the road, and one was seen in the window on the way round (%d times; at %s)' % (cans_seen, CANS))
    yl = [sp.read16(SYM['you_laps'] + 2 * i) for i in range(LAPS)]
    ok(all(v > 0 for v in yl) and sp.read8(SYM['fin_at']) == 1, 'your %d lap times are kept (%s frames) and you are first in' % (LAPS, yl))
    md, dots, ink = minimap_diff(sp)
    ok(md == 0, 'the mini-map is still whole after three laps of dots (%d wrong)' % md)
    sp.__exit__(None, None, None)

    # a short cut: from the start straight across the cloth to the row of road above it (the rows are
    # 110 px apart), or on round to the row above that - more than four waypoints on: not counted
    sp = boot(); go_green(sp); press(sp, 'Q', False); park_cpus(sp); sp.run(duration=0.5, fast_forward=True)
    def cut(sp, next_wp, on_wp, secs=2.5):
        sp.write(CARS + C_WP, bytes([next_wp % NWP])); sp.write(CARS + C_LAPS, bytes([1]))
        x, y = WPS[on_wp % NWP]; put(sp, 0, x - 8, y - 8, 16); sp.run(duration=secs, fast_forward=True)
        return laps_of(sp, 0), sp.read8(CARS + C_WP)
    above = min((n for n in range(NWP) if 8 <= (n - WS) % NWP <= NWP - 8), key=lambda n: math.dist(WPS[n], WPS[WS]))    # the nearest waypoint of another stretch of road: on track 2, straight above the line on the next row
    l, w = cut(sp, WS + 2, above)
    ok((above - WS) % NWP > 6 and l == 1 and w == (WS + 2) % NWP, 'across the cloth to the nearest other stretch of road (waypoint %d, %d on, %d px away): your waypoint stays %d, no lap' % (above, (above - WS) % NWP, math.dist(WPS[above], WPS[WS]), w))
    l, w = cut(sp, above - 3, WS, 4.0)
    ok(l == 1 and w == (above - 3) % NWP, 'and back from there to the line, missing %d waypoints: no lap (lap count %d)' % ((WS - above + 3) % NWP, l))
    l, w = cut(sp, WS - 3, WS)
    ok(l == 2, 'off the track and back on over the line having missed 3: still a lap, as on track 1 (lap count %d)' % l)
    sp.__exit__(None, None, None)

    # ---------------------------------------------------------------- your car DRIVEN round by script, in the race
    def autopilot(sp, laps_want, limit=240.0, look=1, dt=0.06):
        """The keys only: O / P towards the waypoint after your next one, Q unless well off line."""
        t = 0.0; cross = []; laps = laps_of(sp, 0); keys = set(); trace = []
        def setk(want):
            for k in list(keys - want): press(sp, k, False); keys.discard(k)
            for k in want - keys: press(sp, k, True); keys.add(k)
        while t < limit and laps_of(sp, 0) < laps_want and sp.read8(SYM['race_over']) == 0:
            c = car(sp, 0); wx, wy = WPS[(c['wp'] + look) % NWP]
            e = (heading(c['x'] + 8, c['y'] + 8, wx, wy) - c['ang'] + 32) % 64 - 32
            k = set()
            if e > 1: k.add('P')
            if e < -1: k.add('O')
            if abs(e) < 12 or math.hypot(c['vx'], c['vy']) < 0.9: k.add('Q')
            setk(k); sp.run(duration=dt, fast_forward=True); t += dt; trace.append((c['x'], c['y']))
            if laps_of(sp, 0) != laps: laps = laps_of(sp, 0); cross.append(round(t, 1))
        setk(set())
        return cross, trace
    sp = boot(); go_green(sp); press(sp, 'Q', False)
    cross, trace = autopilot(sp, LAPS + 1)
    mine = [round(b - a, 1) for a, b in zip(cross, cross[1:])]
    on = sum(road_px(x + 8, y + 8) for x, y in trace) / len(trace)
    print('  driven by script: line at %s s, laps %s s, on the road %.0f%%, bumps %d, place %d' % (cross, mine, 100 * on, g(sp, 'bumps'), sp.read8(SYM['position'])))
    ok(len(cross) == LAPS + 1 and laps_of(sp, 0) == LAPS + 1, 'driven with the keys among the four computer cars: %d laps counted (%s s each)' % (LAPS, mine))
    ok(on > 0.9 and mine and max(mine) < 1.4 * min(mine), 'the script keeps to the road (%.0f%%) and its laps are alike - the track can be driven clean' % (100 * on))
    sp.run(duration=0.2, fast_forward=True)
    ok(sp.read8(SYM['fin_at']) in (1, 2, 3, 4, 5), 'you are given a finishing place (%d)' % sp.read8(SYM['fin_at']))
    t = 0.0
    while sp.read8(SYM['race_over']) == 0 and t < 90: sp.run(duration=0.5, fast_forward=True); t += 0.5
    sp.run(duration=0.5, fast_forward=True)
    card = [sp.read8(0x5800 + r * 32 + c) for r, c in ((5, 5), (6, 5), (18, 20), (17, 20))]
    ok(sp.read8(SYM['race_over']) != 0 and card == [0x4F, 0x70, 0x4F, 0x70], 'four cars in: the race ends and the podium card comes up (%.0f s after you finished)' % t)
    shot(sp, 'track%s_podium.png' % TRACK)
    sp.__exit__(None, None, None)

# ---------------------------------------------------------------- a computer car dropped off its line finds the way on
# (tests/stuck_test.py's rule, on this track's close rows: passing waypoints again within 12 s)
if not os.environ.get('QUICK'):
    import random
    STEP = int(os.environ.get('STEP', 24)); SECS = 12
    pts = [(x, y) for y in range(8, MAPH * 8 - 23, STEP) for x in range(8, MAPW * 8 - 23, STEP)]
    # (not UNDER the deck heading for a waypoint ON it: a car cannot come to be there - see below, where the drop sets the level)
    under_cover = lambda x, y: BR['H0'] - 16 <= x < BR['H1'] and BR['M0'] - 12 <= y + 8 < BR['M1'] + 12
    random.seed(5); random.shuffle(pts)
    sp = boot(); go_green(sp); press(sp, 'Q', False)
    you = car(sp, 0); pts = [p for p in pts if math.hypot(p[0] - you['x'], p[1] - you['y']) > 30]
    stuck = []; k = 0
    while k < len(pts):
        batch = pts[k:k + K]; k += K; start = {}
        for i, (x, y) in zip(CPUS, batch):
            near = min(range(NWP), key=lambda n: math.hypot(WPS[n][0] - x - 8, WPS[n][1] - y - 8))
            wp = (near + random.choice((-1, 0, 1, 2))) % NWP
            if under_cover(x, y) and not (BR['X0'] <= x + 8 < BR['X1']): wp = min((n for n in range(NWP) if n not in UP_WPS and (n - 1) % NWP not in UP_WPS), key=lambda n: math.hypot(WPS[n][0] - x - 8, WPS[n][1] - y - 8))
            setl(sp, i, int(wp in UP_WPS and BR['X0'] <= x + 8 < BR['X1'] and BR['Y0'] <= y + 8 < BR['Y3']))     # (its level: on the bridge if it is dropped on the upper road heading for one of its waypoints)
            put(sp, i, x, y, random.randrange(64)); sp.write(CARS + i * CS + C_WP, bytes([wp])); sp.write(CARS + i * CS + C_LAPS, bytes([1])); start[i] = (x, y, wp)
        sp.write(SYM['race_over'], bytes([0]))
        sp.run(duration=SECS, fast_forward=True)
        for i in start:
            c = car(sp, i); x, y, wp = start[i]; gone = (c['wp'] - wp) % NWP
            if gone < 1 or (gone < 2 and math.hypot(c['x'] - x, c['y'] - y) < 60): stuck.append((x, y, wp, c['x'], c['y'], c['wp']))
    ok(not stuck, 'every computer car dropped anywhere on the table is passing waypoints again within %d s (%d places; stuck: %d)' % (SECS, len(pts), len(stuck)))
    for s in stuck[:40]: print('   dropped at %d,%d aiming at waypoint %d: after %d s at %d,%d, waypoint %d' % (s[:3] + (SECS,) + s[3:]))
    sp.__exit__(None, None, None)

print('RESULT:', 'PASS' if fails == 0 else '%d FAIL' % fails)
sys.exit(1 if fails else 0)
