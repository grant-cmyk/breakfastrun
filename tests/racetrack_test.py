"""THE RACE-TRACK TRIAL (RACETRACK=1 bash build.sh -> build/racer_racetrack.tap), checked from the emulator's screen.
What the screen OUGHT to show is worked out here, apart from the game: the grass from tools/make_world.py's road shape (the
road and 10 pixels of run-off are black, the rest green), the white things from the build's own map (limit line, start
line, grid, canisters). Then:
  1. SCROLLING: a lap by autopilot, alone and in the pack - at every picture the window's rows 3-15 (the rows with no fixed
     thing in them) match that to the pixel, bar the squares a car is in: road black, grass green, line white, and the
     grass's edge exactly where the map says, with the view at every pixel offset.
  2. THE CLASH RULE (rule 4), your car parked on the road, on the limit line, across the grass's edge and on the grass:
     each square it is in has the colours the rule says, and the scenery beyond its 1-pixel rim is untouched.
  3. A SLIDE: straight on at the first bend into the grass, a crawl, and back - the rule holds at every picture; and the
     scorer's two numbers (tools/make_racetrack_clash_score.py) from the real tape: BACKGROUND = scenery pixels showing the
     wrong colour, CAR = pixels of the car's outline not in its colour.
  4. GRASS IS SLOW: top speed on the grass 20-25% of the road's; a car can drive onto the grass and back.
Usage: python3 tests/racetrack_test.py [part ...]     parts: scroll pack rule slide speed (default: all)
       TAPE=racer_track_green python3 tests/racetrack_test.py            another tape of track 1 (its build folder: the name less "racer_")
       BDIR=racer_2p TAPE=racer_2p python3 tests/racetrack_test.py       a tape whose build folder is not its name less "racer_"
       TRACK=2 python3 tests/racetrack_test.py                           track 2 or 3 in the green-line look (build/racer_track_green_track2.tap;
                                                                         TAPE=racer_track_green_track2_grip1 with it for that one)
THE GREEN LIMIT LINE (17 Nov 2026): a build that has one says so in its rt_world.asm ("; LIMIT green ..."), and the picture
worked out here then has it too - from the road's shape again, not from the build's map. And where tools/make_world.py had
to draw a tile as its nearest look-alike (tracks 2 and 3 have more edge pictures than the map can number: "; REDRAWN ..."),
that tile is taken as the build says it is - after checking it is within 3 pixels of the true shape; everything else in the
picture must still match to the pixel."""
import os, sys, re, math
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rt_lib import Game, ROOT
TRACK = int(os.environ.get('TRACK') or 1)
TAPE = os.environ.get('TAPE') or ('racer_racetrack' if TRACK == 1 else 'racer_track_green_track%d' % TRACK)
SRC = os.path.join(ROOT, 'build', os.environ.get('BDIR') or TAPE.replace('racer_', ''), 'src')    # (BDIR=racer_2p: a tape whose build folder has another name)
os.environ['TRACK'] = str(TRACK)                                          # (tools/make_world.py reads it: the road's shape for this track)
if TRACK != 1:
    import tempfile; os.environ['WORLD_OUT'] = tempfile.mkdtemp()         # (it insists on a folder for a later track; nothing is written by the part run here)
wsrc = open(os.path.join(ROOT, 'tools', 'make_world.py')).read()
wns = {'__file__': os.path.join(ROOT, 'tools', 'make_world.py')}
exec(wsrc[:wsrc.index('road = road_mask(ROAD)')], wns)
ROAD, road_mask, PW, PH = wns['ROAD'], wns['road_mask'], wns['PW'], wns['PH']
GRASS = ~np.array(road_mask(ROAD + 20), dtype=bool)                       # green: from 10 px beyond the road's edge
src = ''.join(open(os.path.join(SRC, f)).read() for f in ('world.asm', 'toprows.asm', 'hirows.asm'))
tiles = [[int(v, 16) for v in l.split('defb')[1].split(';')[0].split(',')] for l in src[src.index('tiles:'):src.index('; each list')].splitlines() if 'defb' in l]
WHITE = np.zeros((PH, PW), bool)
for m in re.finditer(r'row_(\d+):\s+defb\s+(.*)', src):
    v = [int(x) for x in m.group(2).split(',')]
    for i in range(1, len(v), 2):
        for j in range(8):
            for b in range(8):
                if tiles[v[i + 1]][j] & (0x80 >> b): WHITE[int(m.group(1)) * 8 + j, v[i] * 8 + b] = True
assert not (WHITE & GRASS).any()
# GREEN: what shows green - the grass, and the build's thin green limit line if it has one (GRASS stays the real grass:
# "is the car on the grass" is asked of that)
GREEN = GRASS.copy()
rtw = open(os.path.join(SRC, 'rt_world.asm')).read()
_m = re.search(r'; LIMIT green (\w+) gap (\d+) wide (\d+)', rtw)
if _m:
    _gap, _wide = int(_m.group(2)), int(_m.group(3))
    _pin = np.array(road_mask(ROAD + 2 * (10 - _gap)), dtype=bool) & ~np.array(road_mask(ROAD + 2 * (10 - _gap - _wide)), dtype=bool)
    if _m.group(1) == 'dash': _yy, _xx = np.mgrid[0:PH, 0:PW]; _pin &= ((_xx // 8) + (_yy // 8)) % 2 == 0
    _near = np.zeros_like(WHITE); _wp = np.pad(WHITE, 7)                  # (left out within a colour square of anything white)
    for _dy in range(15):
        for _dx in range(15): _near |= _wp[_dy:_dy + PH, _dx:_dx + PW]
    GREEN |= _pin & ~_near
REDRAWN = [(int(m.group(1)), int(m.group(2)), bytes.fromhex(m.group(3))) for m in re.finditer(r'; REDRAWN tile (\d+),(\d+) as ([0-9a-f]{16})', rtw)]
_far = 0
for _tx, _ty, _b in REDRAWN:
    _t = np.unpackbits(np.frombuffer(_b, np.uint8)).reshape(8, 8).astype(bool)
    _far = max(_far, int((GREEN[_ty * 8:_ty * 8 + 8, _tx * 8:_tx * 8 + 8] != _t).sum()))
    GREEN[_ty * 8:_ty * 8 + 8, _tx * 8:_tx * 8 + 8] = _t
assert not (WHITE & GREEN).any()
CANS = [(int(m.group(1)), int(m.group(2))) for m in re.finditer(r'NOS_\w_X equ (\d+)\nNOS_\w_Y equ (\d+)', src)]
SY = int(re.search(r'TRACK_SY\s+equ\s+(\d+)', src).group(1)); LX = 288
MAP_R0 = (int(re.search(r'^MAP_ROW\s+EQU\s+0([0-9A-F]+)H', open(os.path.join(ROOT, 'build', TAPE + '.sym')).read(), re.M | re.I).group(1), 16) - 8) // 8   # the window's row of squares the mini-map starts in (16; track 3: 15)
INKS = [2, 5, 6, 3, 7]                                                    # you red; cyan, yellow, magenta, white
fails = []; passes = 0
def check(ok, msg):
    global passes
    print(('PASS  ' if ok else 'FAIL  ') + msg)
    if ok: passes += 1
    else: fails.append(msg)

def ideal(cx, cy):
    """the scenery the window ought to show for a camera at (cx, cy): 0 black, 4 green, 7 white"""
    g = GREEN[cy:cy + 152, cx:cx + 192]; w = WHITE[cy:cy + 152, cx:cx + 192]
    out = np.zeros((152, 192), np.uint8); out[g] = 4; out[w] = 7
    for x, y in CANS:                                                     # (a canister goes when it is picked up: not compared)
        out[max(0, y - cy - 12):max(0, y - cy + 12), max(0, x - cx - 12):max(0, x - cx + 12)] = 255
    return out
def car_masks(g, cx, cy):
    """each car's picture where it falls in the window: (body, ink) - read from the game's own frames, as draw_car reads them"""
    S = g.sym; out = []
    if not hasattr(g, 'frames'): g.frames = g.mem(0x5F00, 0x2000); g.tab = g.mem(S['big_tab'], 320)   # (the cars' pictures do not change)
    allc = g.mem(S['cars'], 5 * S['c_size'])
    for i in range(5):
        c = allc[i * S['c_size']:(i + 1) * S['c_size']]
        x, y, ang, kind = c[1] + 256 * c[2], c[4] + 256 * c[5], c[10], c[22]
        e = g.tab[4 * (kind * 16 + ((ang >> 2) & 15)):][:4]
        addr, first, n = e[0] + 256 * e[1], e[2], e[3] & 0x7F; flip = e[3] & 0x80
        body = np.zeros((152, 192), bool); ink = np.zeros((152, 192), bool)
        for r in range(n):
            o = (addr - 4 * r if flip else addr + 4 * r) - 0x5F00; d = g.frames[o:o + 4]
            wy = y - cy - 6 + first + r
            for b in range(16):
                wx = x - cx + b
                if 0 <= wy < 152 and 0 <= wx < 192:
                    if d[2 * (b // 8)] & (0x80 >> (b % 8)): body[wy, wx] = True
                    if d[2 * (b // 8) + 1] & (0x80 >> (b % 8)): ink[wy, wx] = True
        out.append((body | ink, ink))
    return out
def grow(m, n=1):
    for _ in range(n):
        p = np.pad(m, 1); m = p[1:-1, 1:-1] | p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
    return m
def squares(m): return m.reshape(19, 8, 24, 8).any(axis=(1, 3))
def spread(sq): return np.repeat(np.repeat(sq, 8, axis=0), 8, axis=1)
def at_picture(g):
    g.rpc('run', until_pc=g.sym['snd_picture'], max_frames=40)            # (the picture and its colours are on the screen)
    return g.cam()
ROWS = slice(3 * 8, 16 * 8)                                               # the window's rows with nothing fixed in them ...
def free_area():
    a = np.zeros((152, 192), bool); a[ROWS] = True
    a[13 * 8:16 * 8, 10 * 8:13 * 8] = False                               # ... but for the corner arrow's 3 x 3 squares
    if MAP_R0 < 16: a[MAP_R0 * 8:16 * 8, 0:24] = False                    # ... and the mini-map's box where it is taller than 3 rows of squares (track 3: from row 15)
    return a

def scroll(alone):
    g = Game(TAPE, SRC); g.to_grid(); g.go(alone=alone)
    bad = pics = offs = 0; seen = set(); worst = None; edge = 0
    start = g.wp; lapped = False; f = 0
    while f < 2600 and not lapped:
        g.steer(); f += 3
        for _ in range(3): g.steer(); g.run(1)
        cx, cy = at_picture(g)
        px, at = g.window(); want = ideal(cx, cy)
        cars = np.zeros((152, 192), bool)
        for body, ink in car_masks(g, cx, cy): cars |= body
        ok = free_area() & ~spread(squares(grow(cars, 1))) & (want != 255)
        for wx, wy, _ in g.weapon_dots():                                  # (ARMOUR tapes: the tank's shell and the clown's wheels are not scenery either -
            wx -= cx; wy -= cy                                             #  the one square each of their dots is in is left out, as the cars' squares are)
            if 0 <= wx < 192 and 0 <= wy < 152: ok[wy & ~7:(wy & ~7) + 8, wx & ~7:(wx & ~7) + 8] = False
        d = int(((px != want) & ok).sum())
        gsq = squares(want == 4) & squares(want != 4)
        edge += int((gsq & squares(ok)).sum())
        pics += 1; seen.add((cx & 7, cy & 7)); bad += d
        if d and worst is None: worst = (cx, cy, d); g.shot(os.path.join(ROOT, 'build', 'racetrack_test_fail.png'))
        if d and os.environ.get('WHERE'):                                  # WHERE=1: each wrong picture's pixels (window x, y, shown, wanted) and the cars' places in the window
            ys, xs = np.nonzero((px != want) & ok); print('   wrong at camera %d,%d:' % (cx, cy), [(int(x), int(y), int(px[y, x]), int(want[y, x])) for y, x in list(zip(ys, xs))[:8]], 'cars', [(g.car(i)[0] - cx, g.car(i)[1] - cy) for i in range(5)])
        if g.wp == (start - 2) % len(g.wps): lapped = True
    g.close()
    who = 'alone' if alone else 'in the pack'
    check(pics > 100 and lapped, '%s: a lap by autopilot, %d pictures looked at' % (who, pics))
    check(bad == 0, '%s: rows 3-15 of every picture match the map to the pixel - road black, grass green, line white - outside the cars\' squares (%d wrong pixels%s)' % (who, bad, '' if worst is None else '; first at camera %d,%d: %d' % worst))
    check(len(seen) >= 32 and edge > 1000, '%s: with the view at %d of the 64 pixel offsets, and %d squares that held both grass and road checked' % (who, len(seen), edge))

def rule_squares(g, label, tally):
    """the clash rule for your car as it stands: returns (wrong, background score, car score)"""
    cx, cy = at_picture(g)
    px, at = g.window(); want = ideal(cx, cy)
    masks = car_masks(g, cx, cy); body, ink = masks[0]
    others = np.zeros_like(body)
    for b, i in masks[1:]: others |= spread(squares(grow(b, 1)))
    rim = grow(body, 1); wrong = []
    for r, c in zip(*np.nonzero(squares(body))):
        s = (slice(r * 8, r * 8 + 8), slice(c * 8, c * 8 + 8))
        if others[s].any() or (want[s] == 255).any() or not (3 <= r <= 15) or c in (0, 23): continue   # (not at the window's edge: the car is cut off there)
        hasg = (want[s] == 4).any(); hasr = (want[s] != 4).any(); a = int(at[r, c]); p = px[s]; w = want[s]; b = body[s]; i = ink[s]
        if not hasg:                                                      # no grass: the car's colour on black; white there takes it
            kind = 'line' if (w == 7).any() else 'road'
            ok = a & 0x3F == INKS[0] and (p[i] == INKS[0]).all() and (p[b & ~i] == 0).all() and np.isin(p[~b & (w == 0)], [0]).all() and np.isin(p[~b & (w == 7)], [INKS[0], 0]).all()
        elif not hasr:                                                    # all grass: the car's colour on green
            kind = 'grass'
            ok = a & 0x3F == 0x20 | INKS[0] and (p[i] == INKS[0]).all() and (p[~i] == 4).all()
        else:                                                             # both: the scenery stays, the car in green with a black rim
            kind = 'mixed'
            ok = a & 0x3F == 0x04 and (p[~rim[s]] == w[~rim[s]]).all() and (p[i] == 4).all() and (p[b & ~i] == 0).all() and (p[rim[s] & ~b] == 0).all()
        tally[kind] = tally.get(kind, 0) + 1
        if not ok: wrong.append('%s: %s square row %d col %d, attribute %02X' % (label, kind, r, c, a))
    # the scorer's numbers, over the whole window but the fixed things' rows
    area = free_area() & (want != 255) & ~others
    back = int(((px != want) & ~body & area).sum()); carsc = int(((px != INKS[0]) & ink & area).sum())
    far = int(((px != want) & ~rim & area & ~((want == 7) & spread(squares(body)))).sum())   # ... and what the rule never allows
    wred = int(((px != want) & ~body & area & (want == 7) & (px == INKS[0])).sum())            # (of the background score: white shown in the car's colour)
    return wrong, back, carsc, far, wred

def rule():
    g = Game(TAPE, SRC); g.to_grid(); g.go(alone=True); g.key('Q', False)
    tally = {}; wrong = []; far = 0
    for name, y in (('on the road', SY - 8), ('on the limit line', SY - 44), ('on the limit line, lower', SY - 41), ('across the grass edge', SY - 56),
                    ('across the grass edge, higher', SY - 60), ('on the grass', SY - 84), ('on the grass, deeper', SY - 99),
                    ('on the start line', SY - 8), ('on the start line, higher', SY - 20)):   # (17 Nov 2026: white under the car whatever the limit line is)
        for dx in (0, 3, 5):                                              # (three pixel offsets across)
            g.put((LX - 8 if 'start line' in name else LX + 60) + dx, y, 16); g.run(12)
            w, b, c, f, wr = rule_squares(g, '%s (+%d)' % (name, dx), tally); wrong += w; far += f
            if name in ('on the limit line', 'across the grass edge', 'on the grass') and dx == 0 and os.environ.get('SHOTS'):
                g.shot(os.path.join(os.environ['SHOTS'], 'car_%s.png' % name.replace(' ', '_')))
    g.close()
    check(all(tally.get(k, 0) >= 6 for k in ('road', 'line', 'mixed', 'grass')), 'your car parked in 27 places: squares of every kind were under it (%s)' % ', '.join('%s %d' % kv for kv in sorted(tally.items())))
    check(not wrong, 'each square has the colours rule 4 says: road and line - red on black; all grass - red on green; grass and road - left alone, the car green with a black rim (%d wrong%s)' % (len(wrong), ': ' + '; '.join(wrong[:3]) if wrong else ''))
    check(far == 0, 'the scenery beyond the car\'s 1-pixel rim is unchanged by the car - bar white that shares a road square with it (%d pixels changed)' % far)

def slide():
    g = Game(TAPE, SRC); g.to_grid(); g.go(alone=True)
    S = g.sym; tally = {}; wrong = []; B = []; C = []; WR = []; farsum = 0; phase = 0; deep = 0; back = 0; n = 0; offgrass = 0
    gif = os.environ.get('SLIDE_GIF')
    while n < 1500:
        x, y, ang = g.car(); on = GRASS[y + 8, x + 8]
        if phase == 0:                                                    # straight on at the first bend: no steering
            g.key('Q', True); g.key('O', False); g.key('P', False)
            deep += on
            if deep > 60: phase = 1
        else:                                                             # then back to the road
            g.steer(); back = 0 if on else back + 1
            if back > 80: break
        g.run(1); n += 1
        if n % 3 == 0:
            w, b, c, f, wr = rule_squares(g, 'slide frame %d' % n, tally); wrong += w; B.append(b); C.append(c); farsum += f; offgrass += bool(on); WR.append(wr)
    g.close()
    check(phase == 1 and back > 80, 'your car goes straight on at the first bend into the grass, crawls, and drives back onto the road (%d frames)' % n)
    check(not wrong and all(tally.get(k, 0) for k in ('road', 'line', 'mixed')), 'the clash rule holds at every one of the %d pictures looked at (squares: %s; %d wrong%s) - deep in this bend\'s grass the car is at the window\'s edge, where its squares are not judged: part 2 has the all-grass squares' % (len(B), ', '.join('%s %d' % kv for kv in sorted(tally.items())), len(wrong), ': ' + '; '.join(wrong[:3]) if wrong else ''))
    check(farsum == 0, 'during the slide the road never turns green and the grass never black beyond the car\'s rim (%d pixels)' % farsum)
    print('      clash scores from the real tape, %d pictures (%d with the car\'s middle on the grass): BACKGROUND total %d, worst picture %d; CAR total %d, worst picture %d'
          % (len(B), offgrass, sum(B), max(B), sum(C), max(C)))
    print('      (of the background total, %d are white shown in the car\'s red where the car shares a road square with it - the grid\'s bracket as it pulls away, the limit line - and %d the 1-pixel black rim; nothing else)' % (sum(WR), sum(B) - sum(WR)))
    print('      (the mock-up\'s rule 4, PLAIN=1 python3 tools/make_racetrack_clash_score.py: 367 pictures, background 1129, worst 34; car 2025, worst 61 - another drive, and a smaller drawing of the car: the game\'s has 92 pixels of outline)')

def speed():
    g = Game(TAPE, SRC); g.to_grid(); g.go(alone=True)
    S = g.sym
    def v():
        c = g.mem(S['cars'], 10); return math.hypot(int.from_bytes(c[6:8], 'little', signed=True), int.from_bytes(c[8:10], 'little', signed=True)) / 256
    top = [0]
    def each(f): top[0] = max(top[0], v())
    g.drive(frames=600, each=each)
    for k in 'OP': g.key(k, False)
    GY = SY + 72 if TRACK == 1 else SY + 52                               # (tracks 2 and 3: the world ends 72 pixels below their start straight's middle - the car goes nearer the road, still wholly on the grass)
    g.key('Q', True); g.put(LX - 88, GY, 16)                         # on the grass below the start straight, pointing along it
    for _ in range(250): g.run(1)
    vg = v(); x, y, a = g.car()
    check(GRASS[y + 8, x + 8] and 0.20 <= vg / top[0] <= 0.25, 'grass is slow: flat out on the grass %.2f pixels a frame, %.0f%% of the road\'s %.2f (20-25%% asked)' % (vg, 100 * vg / top[0], top[0]))
    g.put(LX - 40, GY, 0)                                            # ... then pointing at the road
    for _ in range(400):
        g.run(1); x, y, a = g.car()
        if not GRASS[y + 8, x + 8] and y < SY + 20: break
    g.key('Q', False); g.run(5)
    x, y, a = g.car()
    check(not GRASS[y + 8, x + 8] and g.mem(S['cars'] + 12, 1)[0] == 3, 'and it drives off the grass back onto the road (now at %d, %d)' % (x, y))
    # the computer cars: a lap in the pack, how much of it on the grass
    g.close()
    g = Game(TAPE, SRC); g.to_grid(); g.go(); on = [0] * 4; tot = 0
    # (30 seconds on track 1 - time to begin a second lap; a longer track gets as much longer as its centre line is: track 1's is 1,472 pixels)
    FR = 1500 if TRACK == 1 else int(1500 * sum(math.dist(g.wps[k], g.wps[(k + 1) % len(g.wps)]) for k in range(len(g.wps))) / 1472)
    for f in range(FR):
        g.steer(); g.run(1)
        if f % 5 == 0:
            tot += 1
            for i in range(1, 5):
                x, y, a = g.car(i); on[i - 1] += bool(GRASS[min(PH - 1, y + 8), min(PW - 1, x + 8)])
    laps = [g.mem(S['cars'] + i * S['c_size'] + 25, 1)[0] for i in range(1, 5)]
    g.close()
    check(max(on) / tot < 0.05 and min(laps) >= 2, 'the computer cars stay on the road: in %d s each has its middle on the grass %s of the time (laps begun: %s)' % (FR // 50, ' '.join('%.1f%%' % (100 * o / tot) for o in on), laps))

if REDRAWN: check(_far <= 3, 'this build draws %d tiles as their nearest look-alike: each is within 3 pixels of the true shape (the most: %d)' % (len(REDRAWN), _far))
PARTS = {'scroll': lambda: scroll(True), 'pack': lambda: scroll(False), 'rule': rule, 'slide': slide, 'speed': speed}
for p in (sys.argv[1:] or list(PARTS)): PARTS[p]()
print('%d passed, %d failed' % (passes, len(fails)))
sys.exit(1 if fails else 0)
