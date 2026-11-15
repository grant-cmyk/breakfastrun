"""Track 2, THE BREAKFAST CLUB, in its own build (TRACK=2 bash build.sh -> build/racer_track2.tap) - and
track 3, BREAKFAST OF CHAMPIONS, with TRACK=3 (TRACK=3 bash build.sh first).
On the REAL 48K ROM (zx package), with tests/drive_test.py's own helpers:
  - the five cars start on the grid, on the road, behind the line; nobody moves before green
  - the window matches the world map pixel for pixel, on the grid and at places all round the lap
  - the panel's mini-map is this track's, and the cars' dots are on it
  - the four computer cars each complete 3 laps, never stopping for long, on the road
  - your laps are counted: with your car placed along the waypoints, 3 laps round; a short cut
    across to the next row of road is not a lap; and DRIVEN round by script with the keys
    (O, P, Q) for 3 laps among the computer cars, to the podium
  - a computer car dropped anywhere near the road (the rows are close together) finds its way on
Prints PASS/FAIL lines and RESULT. TRACK=n for another track's build; QUICK=1 leaves out the
dropped cars (the slowest part)."""
import os, sys, math, json
HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.environ.get('TRACK', '2')
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
    want = want.copy(); want[MM_TOP:MM_TOP + MM_H, 0:24] |= map_now(sp)   # (the mini-map over the picture: as window_bad)
    mask = np.ones_like(want, dtype=bool)
    mask[8 - WY:32 - WY, 56 - 8:136 - 8] = False; mask[WH - 16:WH, WW - 48:WW] = False
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

# ---------------------------------------------------------------- the data the tape was built from
ok(MAPW == 72 and MAPH == {'2': 64, '3': 84}.get(TRACK), 'the map is the size of this track\'s design: %d x %d tiles (mini-map at %d/256)' % (MAPW, MAPH, MSC))
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
LINE_X = 288
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
ok(md == 0 and ink > 60 and MM_ROWS.shape[1] == 24 and all(sp.read8(0x5800 + r * 32 + c) == 0x29 for r in range(15, 20) for c in range(1, 7)), 'the mini-map in the window\'s bottom left corner is this track\'s road, line for line, 24 x %d in the window\'s own colours (%d pixels of ribbon, %d wrong outside the cars\' dots)' % (MM_H, ink, md))
ok(all(d is None or (0 <= d[1] <= MM_H - 1 and 0 <= d[0] <= 23) for d in dots) and sum(d is not None for d in dots) >= N - 1 and not sb[0:40, 208:256].any() and sp.read8(0x5800 + 5 * 32 + 26) == 0x4F,
   'the cars\' dots are inside the map; the panel\'s top right, where the map was, is plain above the RACE heading (dots at %s)' % dots)
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
    random.seed(5); random.shuffle(pts)
    sp = boot(); go_green(sp); press(sp, 'Q', False)
    you = car(sp, 0); pts = [p for p in pts if math.hypot(p[0] - you['x'], p[1] - you['y']) > 30]
    stuck = []; k = 0
    while k < len(pts):
        batch = pts[k:k + K]; k += K; start = {}
        for i, (x, y) in zip(CPUS, batch):
            near = min(range(NWP), key=lambda n: math.hypot(WPS[n][0] - x - 8, WPS[n][1] - y - 8))
            wp = (near + random.choice((-1, 0, 1, 2))) % NWP
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
