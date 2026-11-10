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
CS = SYM['c_size']; CARS = SYM['cars']; N = SYM['ncars']; CPUS = list(range(1, N))

src = open(os.path.join(ROOT, 'src', 'world.asm')).read() + open(os.path.join(ROOT, 'src', 'waypoints.asm')).read()
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
TM_FIRST = int(re.search(r'TM_FIRST\s+equ\s+(\d+)', src).group(1))
top = open(os.path.join(ROOT, 'src', 'topdata.asm')).read()
tsect = lambda a, b: [int(v, 0) for l in top[top.index(a):top.index(b)].splitlines() if 'defb' in l
                      for v in l.split('defb')[1].split(';')[0].split(',')]
midx = tsect('tmask_idx_src:', 'tmask_src:')
mbytes = tsect('tmask_src:', 'omap_src:')
world = np.zeros((MAPH * 8, MAPW * 8), dtype=np.uint8)
wmask = np.zeros((MAPH * 8, MAPW * 8), dtype=bool)    # breakfast things: cover the cloth
for ty in range(MAPH):
    for tx in range(MAPW):
        n = wmap[ty * MAPW + tx]
        t = tiles[n]
        m = mbytes[midx[n - TM_FIRST] * 8:midx[n - TM_FIRST] * 8 + 8] if n >= TM_FIRST else [0] * 8
        for j in range(8):
            for i in range(8):
                world[ty * 8 + j, tx * 8 + i] = (t[j] >> (7 - i)) & 1
                wmask[ty * 8 + j, tx * 8 + i] = (m[j] >> (7 - i)) & 1

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

def screen_text(sp, row, col, n):
    font = sp.read(0x3D00, 96 * 8)
    out = ''
    for c in range(col, col + n):
        a = 0x4000 | ((row & 0x18) << 8) | ((row & 7) << 5) | c
        cell = bytes(sp.read8(a + 256 * k) for k in range(8))
        ch = '?'
        for code in range(96):
            if bytes(font[code * 8:code * 8 + 8]) == cell: ch = chr(32 + code); break
        out += ch
    return out

def frame_ok(sp):
    bits = screen_bits(sp)
    top = bits[25:32, 5:187].all() and bits[152:159, 5:187].all()     # 7-px bands
    sides = bits[29:155, 1:8].all() and bits[29:155, 184:191].all()
    corners = not bits[25, 1:5].any() and not bits[158, 187:191].any() and bits[25, 5] and bits[28, 2]
    outside = not bits[24, 0:192].any() and not bits[159, 0:192].any() and not bits[25:159, 0].any() and not bits[25:159, 191].any()
    return bool(top and sides and corners and outside)

class Racer(Spectrum):
    armed = False                           # stop at copy_done only when asked
    def on_breakpoint(self):                # (the emulator calls this at its own
        if self.armed and self.pc == SYM['copy_done']:   # marks too: check where)
            self.armed = False
            raise zs.EmulatorException('at copy_done')

def at_copy_done(sp):
    # stop at the exact moment the copy has finished: the screen, the camera
    # and the car positions then all belong to the same picture
    sp.set_breakpoint(SYM['copy_done'])     # (set after loading: a reset clears it)
    sp.armed = True
    for _ in range(50):
        try:
            sp.run(duration=0.02, fast_forward=True)
        except zs.EmulatorException:
            break
    assert sp.pc == SYM['copy_done'], 'did not stop at copy_done (pc %04X)' % sp.pc

def cloth(camx, camy):
    # the tablecloth: 32-px checks, the dark ones 25% dots, locked to the table
    y, x = np.mgrid[camy:camy + 120, camx:camx + 176]
    return ((((x >> 5) + (y >> 5)) & 1) == 1) & ((x & 1) == 0) & ((y & 1) == 0)   # dark checks: 25% dots

def window_bad(sp):
    at_copy_done(sp)
    camx, camy = g(sp, 'camx'), g(sp, 'camy')
    bits = screen_bits(sp)[32:152, 8:184]            # the window: cells 1-22, rows 4-18
    want = world[camy:camy + 120, camx:camx + 176] | (cloth(camx, camy) & ~wmask[camy:camy + 120, camx:camx + 176])
    mask = np.ones_like(want, dtype=bool)
    for n in range(N):
        c = car(sp, n)
        cx, cy = c['x'] - camx, c['y'] - camy
        m = 1                                   # the car's 1px halo
        mask[max(cy - m, 0):max(cy + 16 + m, 0), max(cx - m, 0):max(cx + 16 + m, 0)] = False
    bad = int(((bits != want) & mask).sum())
    if bad:                                 # save what differs, to look at
        im = np.stack([want * 255, bits * 255, ((bits != want) & mask) * 255], axis=-1).astype(np.uint8)
        Image.fromarray(255 - im).resize((576, 384), Image.NEAREST).save(os.path.join(OUT, 'window_diff.png'))
        print('  cars (window x, y):', [(car(sp, n)['x'] - camx, car(sp, n)['y'] - camy) for n in range(N)], 'cam', camx, camy)
    return bad

with Racer(headless=True) as sp:
    sp.load_tape(TAP)
    t = 0                                   # the test loader is fast: start
    while g(sp, 'renders') == 0 and t < 60: # watching the moment the game runs
        sp.run(duration=0.1, fast_forward=True); t += 0.1
    sp.run(duration=3.0, fast_forward=True)
    p0 = car(sp, 0); cs0 = [car(sp, i) for i in CPUS]
    print('you', p0); [print('CPU', i, c) for i, c in zip(CPUS, cs0)]
    check(p0['vx'] == 0 and p0['ang'] == 16, 'your car waits on the start line')
    check(frame_ok(sp), 'a 7-pixel bezel with rounded corners surrounds the play window')
    logo = [[c == '#' for c in l.strip()] for l in open(os.path.join(ROOT, 'build', 'logo.txt'))]
    sb = screen_bits(sp)
    check((sb[8:24, 200:256] == np.array(logo)).all(), 'the BREAKFAST RUN logo is at the top of the panel')
    msg = screen_text(sp, 1, 12, 9) + '/' + screen_text(sp, 2, 12, 7)
    check(screen_text(sp, 0, 1, 22) == "BREAKFAST AT TIFFANY'S", 'the track is named along the top: %r' % screen_text(sp, 0, 1, 22))
    attr = lambda r, c: sp.read8(0x5800 + 32 * r + c)
    labels = screen_text(sp, 20, 1, 3) + '/' + screen_text(sp, 20, 12, 4) + '/' + screen_text(sp, 21, 1, 4)
    print('message bar %r  panel labels %r' % (msg, labels))
    check(msg == 'GET READY/PRESS Q', 'before the start: GET READY, PRESS Q in the message bar')
    check(labels == 'LAP/TIME/BEST', 'under the window: LAP, TIME and BEST')
    check(all(attr(5 + 2 * i, 26) == [0x57, 0x68, 0x78, 0x58, 0x60][i] for i in range(5)), 'the whole race order is drawn at the start in grid order (YOU, CYAN, WHITE, PINK, GREEN), each car on its colour')
    place = lambda: next(i + 1 for i in range(5) if attr(5 + 2 * i, 25) == 0x57)
    check(place() == 1 and sp.read8(SYM['position']) == 1, 'on the grid you are shown 1st (your row is red)')
    check(len(CPUS) == 4, 'there are four computer cars')
    check(all(c['vx'] == 0 and c['vy'] == 0 for c in cs0), 'computer cars wait on the grid until you press Q')
    bad = window_bad(sp)
    check(bad == 0, 'window matches the world map pixel for pixel, cars excluded (%d wrong)' % bad)
    shot(sp, 'stage3_start.png')

    # ---- you: accelerate, camera follows, top speed unchanged ----
    r0 = g(sp, 'renders')
    hold(sp, ['Q'], 2.0)
    p1 = car(sp, 0)
    fps = (g(sp, 'renders') - r0) / 2.0
    print('you after 2s of Q', p1, ' pictures/s %.1f' % fps)
    check(all(p1['x'] > car(sp, i)['x'] for i in CPUS), 'from the grid you pull away from all four')
    check(fps >= 13, 'at least 13 pictures a second off the start, five cars bunched (got %.1f)' % fps)
    check(all(car(sp, i)['x'] > CPU0X + 30 for i in CPUS), 'pressing Q started the race: all four computer cars set off')
    press(sp, 'Q', True); at_copy_done(sp); pc_ = car(sp, 0); press(sp, 'Q', False)
    cx, cy = pc_['x'] - g(sp, 'camx'), pc_['y'] - g(sp, 'camy')
    check((cx, cy) == (80, 52), 'camera keeps your car exactly in the middle of the 176 x 120 window (%d,%d)' % (cx, cy))

    # ---- park your car in the infield and watch the computer race 90 s ----
    put(sp, 0, 40, 40)                        # top-left corner, well off the track
    sp.run(duration=0.5, fast_forward=True)
    K = len(CPUS)
    laps = [0] * K; last_wp = [sp.read8(CARS + n * CS + 25) for n in CPUS]
    onroad = [0] * K; samples = 0; vmax = [0] * K; tracks = [[] for _ in CPUS]
    lap_t = [[] for _ in CPUS]; vs = [[] for _ in CPUS]; t = 0.0; m0 = g(sp, 'mistakes'); r0 = g(sp, 'renders')
    while t < 90:
        sp.run(duration=0.1, fast_forward=True); t += 0.1; samples += 1
        for i, n in enumerate(CPUS):
            c = car(sp, n)
            gl = sp.read8(CARS + n * CS + 25)   # the game's own lap count (C_LAPS):
            if gl != last_wp[i]:                 # the waypoint can't be sampled - the
                laps[i] += 1; lap_t[i].append(round(t, 1))   # AI moves it ahead
            last_wp[i] = gl                      # for a moment to look ahead
            tx, ty = (c['x'] + 8) // 8, (c['y'] + 8) // 8
            onroad[i] += surf[ty * MAPW + tx] == 0
            vs[i].append(math.hypot(c['vx'], c['vy']))
            vmax[i] = max(vmax[i], vs[i][-1])
            tracks[i].append((c['x'], c['y']))
    mistakes = g(sp, 'mistakes') - m0
    print('laps', laps, 'top speeds', ' '.join('%.2f' % v for v in vmax),
          'on road', ' '.join('%.0f%%' % (100 * o / samples) for o in onroad), 'mistakes', mistakes, 'bumps', g(sp, 'bumps'))
    check(min(laps) >= 3, 'all four computer cars lap the track (%s laps in 90 s)' % laps)
    fast = [sum(v > 1.80 for v in vv) / len(vv) for vv in vs]      # a bump's kick, or a slide, can add
    check(max(fast) < 0.02, 'computer cars are not faster than your top speed (over 1.80: %s of the time)' % ' '.join('%.1f%%' % (100 * f) for f in fast))  # a moment
    avg = [(lt[-1] - lt[0]) / (len(lt) - 1) for lt in lap_t]
    print('average laps (s):', ' '.join('%.1f' % a for a in avg))
    check(max(avg) - min(avg) > 1.0, 'the computer cars are not all the same speed (%s s a lap)' % ' '.join('%.1f' % a for a in avg))
    check(13.0 < min(avg) < 15.0, 'the fastest computer car is competitive: %.1f s a lap against your ~13.5 s' % min(avg))
    check(max(avg) < 17.5, 'even the slowest computer car is within 4 s a lap of you (%.1f s)' % max(avg))
    cl = [car(sp, i) for i in CPUS]
    claps = [sp.read8(CARS + i * CS + 25) for i in CPUS]
    print('computer cars past the line', claps, 'race time', g(sp, 'race_time'))
    check(min(claps) >= 3, 'the computer cars\' laps are counted (%s)' % claps)
    best = screen_text(sp, 21, 1, 23)
    print('best lap line %r' % best)
    check(best.startswith('BEST 1') and best[10:15].strip() in ('CYAN', 'GREEN', 'PINK', 'WHITE') and best[16:19] == 'LAP',
          'the best lap shows its time, the car that set it and the lap')
    check(place() == 5 and sp.read8(SYM['position']) == 5, 'parked while four cars race: your red row is 5th in the tower')
    # the four computer cars are in by now: the race order shows no faces while racing - a mini
    # chequered flag in column 30 for each car that is in, and the gaps to the leader in a small font
    def cellrows(row, col):
        return [sp.read8(0x4000 | ((row & 0x18) << 8) | ((row & 7) << 5) | col | (k << 8)) for k in range(8)]
    flagwant = [0, 0, 0, 0, 0xB3, 0xB3, 0x8C, 0x8C, 0xB3, 0xB3, 0x80, 0x80, 0, 0, 0, 0]
    ok_flags = all(cellrows(5 + 2 * i, 30) + cellrows(6 + 2 * i, 30) == flagwant for i in range(4))
    gap_ink = [sum(bin(b).count('1') for c in (28, 29) for b in cellrows(5 + 2 * i, c) + cellrows(6 + 2 * i, c)) for i in range(5)]
    check(ok_flags, 'finished cars: a mini chequered flag beside the car')
    check(gap_ink[0] == 0 and all(g > 0 for g in gap_ink[1:4]), 'the race order shows gaps to the leader (ink per place %s: none for the leader)' % gap_ink)
    check(g(sp, 'race_time') > 50 * 85, 'the race clock is running (%.1f s)' % (g(sp, 'race_time') / 50))
    check(min(o / samples for o in onroad) > 0.8, 'computer cars stay mostly on the road')
    check(mistakes >= 6, 'computer cars make mistakes (%d in 90 s)' % mistakes)
    d = [math.dist(a, b) for a, b in zip(tracks[0], tracks[1])]
    check(max(d) > 40, 'the computer cars drive differently (they spread out)')

    # ---- your top speed on a clear road (computer cars sent far away) ----
    for i in CPUS: put(sp, i, 20 + 25 * i, 420)
    put(sp, 0, 180, 344, 16)
    hold(sp, ['Q'], 1.5)
    pv = car(sp, 0)
    check(1.6 < math.hypot(pv['vx'], pv['vy']) <= 1.8, 'your top speed on a clear road is 1.75 px/frame (%.2f)' % math.hypot(pv['vx'], pv['vy']))

    # ---- bump: drop a computer car just in front of you, drive into it ----
    put(sp, 0, 200, 344, 16); put(sp, 1, 230, 344, 16)
    sp.write(CARS + CS + 16, bytes([60, 2]))      # CPU A: 60 frames of 'lift' so it sits still-ish
    b0n = g(sp, 'bumps')
    hold(sp, ['Q'], 1.0)
    p2, a2 = car(sp, 0), car(sp, 1)
    print('after ramming', p2, a2, 'bumps', g(sp, 'bumps') - b0n)
    check(g(sp, 'bumps') > b0n, 'driving into a computer car bumps it')
    check(abs(p2['x'] - a2['x']) >= 10 or abs(p2['y'] - a2['y']) >= 10, 'bumped cars do not end up inside each other')
    # head-on: you and a computer car coast at each other (no keys, so nothing
    # pushes back after the bump); just after they touch, each moves away
    for i in CPUS: put(sp, i, 20 + 25 * i, 420)
    put(sp, 0, 200, 344, 16); put(sp, 1, 222, 344, 48)   # 22 apart: they meet in a few frames
    sp.write(CARS + 6, bytes([0x80, 0x01]))        # you rolling right at 1.5 px/frame
    sp.write(CARS + CS + 6, bytes([0x80, 0xFE]))   # CPU A rolling left at 1.5 px/frame
    sp.write(CARS + CS + 16, bytes([40, 2]))       # ...and lifting (no throttle)
    b1 = g(sp, 'bumps'); seen = None
    for _ in range(40):
        sp.run(duration=0.02, fast_forward=True)
        if g(sp, 'bumps') > b1:
            seen = (car(sp, 0), car(sp, 1)); break
    print('just after the head-on bump', seen)
    check(seen is not None and seen[0]['vx'] < 0 < seen[1]['vx'],
          'cars that hit head-on bounce away from each other')

    # ---- finish: on your last lap, cross the line ----
    for i in CPUS: put(sp, i, 20 + 25 * i, 420)
    sp.write(CARS + 25, bytes([3]))                # past the line 3 times: on lap 3
    sp.write(CARS + 13, bytes([SYM['ws']]))        # heading for the first waypoint after it
    put(sp, 0, 250, 344, 16)
    hold(sp, ['Q'], 1.5)
    sp.run(duration=0.3, fast_forward=True)
    again = screen_text(sp, 20, 1, 22)
    print('after crossing the line on lap 3:', repr(again), 'race_over', sp.read8(SYM['race_over']))
    check(sp.read8(SYM['race_over']) == 1 and attr(1, 0) == 0x57, 'crossing the line on the last lap: FINISHED in the message bar')
    check(again == 'RACE FINISHED  PRESS Q', 'every car in: RACE FINISHED  PRESS Q under the window')
    sp.run(duration=0.3, fast_forward=True)
    hold(sp, ['Q'], 0.3)                           # let go, then press: a new race
    sp.run(duration=1.5, fast_forward=True)
    p5 = car(sp, 0)
    check(sp.read8(SYM['race_over']) == 0 and sp.read8(SYM['race_on']) == 0 and screen_text(sp, 1, 12, 9) == 'GET READY'
          and (p5['x'], p5['y']) == (car(sp, 0)['x'], car(sp, 0)['y']), 'Q after the finish starts a new race on the grid')
    hold(sp, ['Q'], 0.2)

    # ---- the picture: pixel check with cars masked out, after a stop ----
    sp.run(duration=3.0, fast_forward=True)
    bad = window_bad(sp)
    check(bad == 0, 'window matches the world map pixel for pixel, cars excluded (%d wrong)' % bad)
    shot(sp, 'stage3_bump.png')

print('RESULT:', 'PASS' if fails == 0 else '%d FAIL' % fails)
sys.exit(1 if fails else 0)
