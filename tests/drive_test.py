"""Stage 3 headless test on the REAL 48K ROM (zx package).
Checks your car, the two computer cars, bumping, the frame rate, and that the
window matches the world map pixel for pixel (car areas excluded)."""
import sys, os, re, math
import numpy as np
from PIL import Image
from zx._spectrum import Spectrum
import zx._spectrum as zs
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
TAP = os.environ.get('ZTAP', os.path.join(ROOT, 'build', 'racer.tap'))
SYMF = os.environ.get('ZSYM', os.path.join(ROOT, 'build', 'racer.sym'))
OUT = os.path.join(ROOT, 'build')
SYM = {}
for line in open(SYMF):
    p = line.split()
    if len(p) >= 3 and p[1] == 'EQU':
        SYM[p[0].lower()] = int(p[2].rstrip('H'), 16)
CS = SYM['c_size']; CARS = SYM['cars']

src = open(os.path.join(ROOT, 'src', 'world.asm')).read()
MAPW = int(re.search(r'MAPW\s+equ\s+(\d+)', src).group(1))
MAPH = int(re.search(r'MAPH\s+equ\s+(\d+)', src).group(1))
NWP = int(re.search(r'NWP\s+equ\s+(\d+)', src).group(1))
CPU0X = int(re.search(r'CPU0X\s+equ\s+(\d+)', src).group(1))
sect = lambda a, b: src[src.index(a):src.index(b)]
tiles = [[int(v, 16) for v in l.split('defb')[1].split(';')[0].split(',')]
         for l in sect('tiles:', 'row_index:').splitlines() if 'defb' in l]
wmap = [0] * (MAPW * MAPH)                  # rebuilt from each row's list of tiles
for l in src.splitlines():
    m = re.match(r'row_(\d+):\s+defb\s+(.*)', l)
    if m:
        v = [int(x) for x in m.group(2).split(',')]
        for i in range(1, len(v), 2):
            wmap[int(m.group(1)) * MAPW + v[i]] = v[i + 1]
surf = []
for l in sect('surface_map:', 'waypoints').splitlines():
    if 'defb' in l:
        for b in l.split('defb')[1].split(','):
            surf += [int(c) for c in b.strip().lstrip('%')]
world = np.zeros((MAPH * 8, MAPW * 8), dtype=np.uint8)
for ty in range(MAPH):
    for tx in range(MAPW):
        t = tiles[wmap[ty * MAPW + tx]]
        for j in range(8):
            for i in range(8):
                world[ty * 8 + j, tx * 8 + i] = (t[j] >> (7 - i)) & 1

def screen_bits(sp):
    scr = sp.read(0x4000, 6144)
    out = np.zeros((192, 256), dtype=np.uint8)
    for y in range(192):
        a = ((y & 0xC0) << 5) | ((y & 7) << 8) | ((y & 0x38) << 2)
        row = np.unpackbits(np.frombuffer(bytes(scr[a:a + 32]), dtype=np.uint8))
        out[y] = row
    return out

def press(sp, k, down): sp.devices.notify(zs.KeyStroke(zs.KEYS[k].ID, pressed=down))
def hold(sp, keys, secs):
    for k in keys: press(sp, k, True)
    sp.run(duration=secs, fast_forward=True)
    for k in keys: press(sp, k, False)

s16 = lambda v: v - 65536 if v > 32767 else v
def car(sp, n):
    b = CARS + n * CS
    return dict(x=sp.read16(b + 1), y=sp.read16(b + 4), vx=s16(sp.read16(b + 6)) / 256,
                vy=s16(sp.read16(b + 8)) / 256, ang=sp.read8(b + 10), wp=sp.read8(b + 13))
def put(sp, n, x, y, ang=None):
    b = CARS + n * CS
    sp.write(b + 1, bytes([x & 255, x >> 8])); sp.write(b + 4, bytes([y & 255, y >> 8]))
    sp.write(b + 6, bytes(4))
    if ang is not None: sp.write(b + 10, bytes([ang]))
def g(sp, name): return sp.read16(SYM[name])

def shot(sp, name):
    sp.render_screen()
    px = np.array(sp.get_frame_pixels(), dtype=np.uint8).reshape(-1, 352, 4)[:, :, [2, 1, 0]]
    Image.fromarray(px).resize((704, px.shape[0] * 2), Image.NEAREST).save(os.path.join(OUT, name))

fails = 0
def check(ok, msg):
    global fails
    print(('PASS ' if ok else 'FAIL ') + msg); fails += not ok

def window_bad(sp):
    camx, camy = g(sp, 'camx'), g(sp, 'camy')
    bits = screen_bits(sp)[32:160, 32:224]
    want = world[camy:camy + 128, camx:camx + 192]
    mask = np.ones_like(want, dtype=bool)
    for n in range(3):
        c = car(sp, n)
        cx, cy = c['x'] - camx, c['y'] - camy
        m = 6                                   # cars can move a few pixels between drawn and read
        mask[max(cy - m, 0):max(cy + 16 + m, 0), max(cx - m, 0):max(cx + 16 + m, 0)] = False
    return int(((bits != want) & mask).sum())

with Spectrum(headless=True) as sp:
    sp.load_tape(TAP)
    t = 0                                   # the test loader is fast: start
    while g(sp, 'renders') == 0 and t < 60: # watching the moment the game runs
        sp.run(duration=0.1, fast_forward=True); t += 0.1
    sp.run(duration=3.0, fast_forward=True)
    p0 = car(sp, 0); a0 = car(sp, 1); b0 = car(sp, 2)
    print('you', p0, '\nA', a0, '\nB', b0)
    check(p0['vx'] == 0 and p0['ang'] == 16, 'your car waits on the start line')
    check((a0['x'], b0['x'], a0['vx'], b0['vx']) == (CPU0X, CPU0X, 0, 0), 'computer cars wait on the grid until you press Q')
    bad = window_bad(sp)
    check(bad == 0, 'window matches the world map pixel for pixel, cars excluded (%d wrong)' % bad)
    shot(sp, 'stage3_start.png')

    # ---- you: accelerate, camera follows, top speed unchanged ----
    r0 = g(sp, 'renders')
    hold(sp, ['Q'], 2.0)
    p1 = car(sp, 0)
    fps = (g(sp, 'renders') - r0) / 2.0
    print('you after 2s of Q', p1, ' pictures/s %.1f' % fps)
    check(p1['x'] > car(sp, 1)['x'] and p1['x'] > car(sp, 2)['x'], 'from a side-by-side start you pull away from both')
    check(fps >= 16, 'at least 16 pictures a second with three cars (got %.1f)' % fps)
    a1 = car(sp, 1)
    check(a1['x'] > CPU0X + 40, 'pressing Q started the race: computer cars set off')
    cx, cy = p1['x'] - g(sp, 'camx'), p1['y'] - g(sp, 'camy')
    check(abs(cx - 88) <= 6 and abs(cy - 56) <= 6, 'camera keeps your car in the middle (%d,%d)' % (cx, cy))

    # ---- park your car in the infield and watch the computer race 90 s ----
    put(sp, 0, 40, 40)                        # top-left corner, well off the track
    sp.run(duration=0.5, fast_forward=True)
    laps = [0, 0]; last_wp = [car(sp, 1)['wp'], car(sp, 2)['wp']]
    onroad = [0, 0]; samples = 0; vmax = [0, 0]; tracks = [[], []]
    lap_t = [[], []]; t = 0.0; m0 = g(sp, 'mistakes')
    while t < 90:
        sp.run(duration=0.1, fast_forward=True); t += 0.1; samples += 1
        for i in (0, 1):
            c = car(sp, i + 1)
            if c['wp'] < last_wp[i] and last_wp[i] - c['wp'] > NWP // 2:
                laps[i] += 1; lap_t[i].append(round(t, 1))
            last_wp[i] = c['wp']
            tx, ty = (c['x'] + 8) // 8, (c['y'] + 8) // 8
            onroad[i] += surf[ty * MAPW + tx] == 0
            v = math.hypot(c['vx'], c['vy'])
            if v > 1.75: print('  fast: car %s at %.1f s v=%.2f %s bumps=%d' % ('AB'[i], t, v, c, g(sp, 'bumps')))
            vmax[i] = max(vmax[i], v)
            tracks[i].append((c['x'], c['y']))
    mistakes = g(sp, 'mistakes') - m0
    print('laps', laps, 'lap times', lap_t, 'top speeds %.2f %.2f' % tuple(vmax),
          'on road %.0f%% %.0f%%' % (100 * onroad[0] / samples, 100 * onroad[1] / samples),
          'mistakes', mistakes, 'bumps', g(sp, 'bumps'))
    check(laps[0] >= 3 and laps[1] >= 3, 'both computer cars lap the track (A %d, B %d laps in 90 s)' % tuple(laps))
    check(vmax[0] < 1.75 and vmax[1] < 1.75, 'computer cars never reach your top speed (top %.2f, %.2f vs 1.75)' % tuple(vmax))
    lapA = (lap_t[0][-1] - lap_t[0][0]) / (len(lap_t[0]) - 1)
    lapB = (lap_t[1][-1] - lap_t[1][0]) / (len(lap_t[1]) - 1)
    print('average lap: A %.1f s, B %.1f s' % (lapA, lapB))
    check(lapB > lapA, 'CPU B is the slower of the two (A %.1f s, B %.1f s a lap)' % (lapA, lapB))
    lapsA = [round(b - a, 1) for a, b in zip(lap_t[0], lap_t[0][1:])]
    print('A lap times', lapsA)
    check(max(lapsA) - min(lapsA) >= 0.5, 'lap times vary from lap to lap (A: %s)' % lapsA)

    # ---- your top speed on a clear road (computer cars sent far away) ----
    put(sp, 1, 40, 420); put(sp, 2, 70, 420); put(sp, 0, 180, 344, 16)
    hold(sp, ['Q'], 1.5)
    pv = car(sp, 0)
    check(1.6 < math.hypot(pv['vx'], pv['vy']) <= 1.8, 'your top speed on a clear road is 1.75 px/frame (%.2f)' % math.hypot(pv['vx'], pv['vy']))
    check(onroad[0] / samples > 0.8 and onroad[1] / samples > 0.8, 'computer cars stay mostly on the road')
    check(mistakes >= 3, 'computer cars make mistakes (%d in 90 s)' % mistakes)
    d = [math.dist(a, b) for a, b in zip(tracks[0], tracks[1])]
    check(max(d) > 40, 'the two computer cars drive differently (they spread out)')

    # ---- bump: drop a computer car just in front of you, drive into it ----
    put(sp, 0, 200, 344, 16); put(sp, 1, 230, 344, 16)
    sp.write(CARS + CS + 16, bytes([60, 2]))      # CPU A: 60 frames of 'lift' so it sits still-ish
    b0n = g(sp, 'bumps')
    hold(sp, ['Q'], 1.0)
    p2, a2 = car(sp, 0), car(sp, 1)
    print('after ramming', p2, a2, 'bumps', g(sp, 'bumps') - b0n)
    check(g(sp, 'bumps') > b0n, 'driving into a computer car bumps it')
    check(abs(p2['x'] - a2['x']) >= 10 or abs(p2['y'] - a2['y']) >= 10, 'bumped cars do not end up inside each other')
    # head-on: drive at a computer car coming the other way; watch the frame they touch
    put(sp, 0, 200, 344, 16); put(sp, 1, 236, 344, 48)
    sp.write(CARS + CS + 6, bytes([0x80, 0xFE]))   # CPU A rolling left at 1.5 px/frame
    sp.write(CARS + CS + 16, bytes([40, 2]))       # ...and lifting (no throttle) for 40 frames
    b1 = g(sp, 'bumps'); press(sp, 'Q', True); seen = None
    for _ in range(40):
        sp.run(duration=0.02, fast_forward=True)
        if g(sp, 'bumps') > b1 and seen is None:
            press(sp, 'Q', False)
            sp.run(duration=0.06, fast_forward=True)
            seen = (car(sp, 0), car(sp, 1)); break
    press(sp, 'Q', False)
    print('just after the head-on bump', seen)
    check(seen is not None and seen[0]['vx'] < 0 < seen[1]['vx'],
          'cars that hit head-on bounce away from each other')

    # ---- the picture: pixel check with cars masked out, after a stop ----
    sp.run(duration=3.0, fast_forward=True)
    bad = window_bad(sp)
    check(bad == 0, 'window matches the world map pixel for pixel, cars excluded (%d wrong)' % bad)
    shot(sp, 'stage3_bump.png')

print('RESULT:', 'PASS' if fails == 0 else '%d FAIL' % fails)
sys.exit(1 if fails else 0)
