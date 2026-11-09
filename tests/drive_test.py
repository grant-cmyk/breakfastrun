"""Stage 2 headless test on the REAL 48K ROM (zx package).
Loads build/racer.tap through the real loader, drives with held keys, and checks:
  - the car starts on the start line, accelerates, steers, slows off-road
  - the camera keeps the car in the middle of the window
  - the window on screen matches the world map PIXEL FOR PIXEL (car area excluded)
  - how many pictures a second the scroller draws (printed, with a floor)"""
import sys, os, re
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

# rebuild the world picture from src/world.asm (independent of the Z80 renderer)
src = open(os.path.join(ROOT, 'src', 'world.asm')).read()
MAPW = int(re.search(r'MAPW\s+equ\s+(\d+)', src).group(1))
MAPH = int(re.search(r'MAPH\s+equ\s+(\d+)', src).group(1))
sect = lambda a, b: src[src.index(a):src.index(b)] if b else src[src.index(a):]
tiles = [[int(v, 16) for v in l.split('defb')[1].split(';')[0].split(',')]
         for l in sect('tiles:', 'world_map:').splitlines() if 'defb' in l]
wmap = [int(v) for l in sect('world_map:', 'surface_map:').splitlines() if 'defb' in l
        for v in l.split('defb')[1].split(',')]
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
        for c in range(32):
            b = scr[a + c]
            for i in range(8):
                out[y, c * 8 + i] = (b >> (7 - i)) & 1
    return out

def hold(sp, keys, secs):
    for k in keys: sp.devices.notify(zs.KeyStroke(zs.KEYS[k].ID, pressed=True))
    sp.run(duration=secs, fast_forward=True)
    for k in keys: sp.devices.notify(zs.KeyStroke(zs.KEYS[k].ID, pressed=False))

def st(sp):
    s = lambda v: v - 65536 if v > 32767 else v
    return dict(x=sp.read16(SYM['carx']), y=sp.read16(SYM['cary']),
                vx=s(sp.read16(SYM['vx'])) / 256, vy=s(sp.read16(SYM['vy'])) / 256,
                angle=sp.read8(SYM['angle']), camx=sp.read16(SYM['camx']),
                camy=sp.read16(SYM['camy']), renders=sp.read16(SYM['renders']))

def shot(sp, name):
    sp.render_screen()
    px = np.array(sp.get_frame_pixels(), dtype=np.uint8)
    img = px.reshape(-1, 352, 4)[:, :, [2, 1, 0]]
    Image.fromarray(img).resize((704, img.shape[0] * 2), Image.NEAREST).save(os.path.join(OUT, name))

fails = 0
def check(ok, msg):
    global fails
    print(('PASS ' if ok else 'FAIL ') + msg)
    fails += not ok

def window_matches(sp, s):
    bits = screen_bits(sp)[32:160, 32:224]
    want = world[s['camy']:s['camy'] + 128, s['camx']:s['camx'] + 192].copy()
    cx, cy = s['x'] - s['camx'], s['y'] - s['camy']
    mask = np.ones_like(want, dtype=bool)
    mask[max(cy, 0):cy + 16, max(cx, 0):cx + 16] = False      # the car sits here
    bad = int(((bits != want) & mask).sum())
    return bad

with Spectrum(headless=True) as sp:
    sp.load_tape(TAP)
    sp.run(duration=45, fast_forward=True)
    s0 = st(sp); print('start', s0)
    check(s0['angle'] == 16 and s0['vx'] == 0, 'car waiting on the start line, facing right')
    check((s0['x'] - s0['camx'], s0['y'] - s0['camy']) == (88, 56), 'car in the middle of the window')
    bad = window_matches(sp, s0)
    check(bad == 0, 'window matches the world map pixel for pixel at the start (%d wrong)' % bad)
    shot(sp, 'stage2_start.png')

    r0 = s0['renders']
    hold(sp, ['Q'], 2.0)
    s1 = st(sp); print('after 2s of Q', s1)
    fps = (s1['renders'] - r0) / 2.0
    print('pictures per second while driving: %.1f' % fps)
    check(fps >= 12, 'scroller draws at least 12 pictures a second (got %.1f)' % fps)
    check(s1['x'] > s0['x'] + 100, 'car drove right along the straight (x %d -> %d)' % (s0['x'], s1['x']))
    check((s1['x'] - s1['camx'], s1['y'] - s1['camy']) == (88, 56), 'camera followed: car still in the middle')
    check(1.6 < s1['vx'] <= 1.8, 'road top speed about 1.75 px/frame (got %.2f)' % s1['vx'])
    shot(sp, 'stage2_driving.png')

    hold(sp, ['Q', 'O'], 0.2)
    hold(sp, ['Q'], 0.8)
    s2 = st(sp); print('turned up', s2)
    check(0 < s2['angle'] < 16 and s2['vy'] < 0, 'O steered the car up the screen')
    shot(sp, 'stage2_turning.png')

    sp.run(duration=3.0, fast_forward=True)     # coast to a stop
    s3 = st(sp); print('stopped', s3)
    check(s3['vx'] == 0 and s3['vy'] == 0, 'car coasts to a stop')
    bad = window_matches(sp, s3)
    check(bad == 0, 'window matches the world map pixel for pixel after scrolling (%d wrong)' % bad)

    # off-road: put the car in the infield (blank table, off the road) and accelerate
    sp.write(SYM['carx'], bytes([232, 0])); sp.write(SYM['cary'], bytes([212, 0]))
    sp.write(SYM['angle'], bytes([16]))
    hold(sp, ['Q'], 0.6)
    s4 = st(sp); print('off-road', s4)
    check(0.6 < s4['vx'] < 0.8, 'off-road top speed about 0.75 px/frame (got %.2f)' % s4['vx'])
    sp.run(duration=3.0, fast_forward=True)
    s5 = st(sp)
    bad = window_matches(sp, s5)
    check(bad == 0, 'window matches the world after a jump across the map (%d wrong)' % bad)
    shot(sp, 'stage2_infield.png')

print('RESULT:', 'PASS' if fails == 0 else '%d FAIL' % fails)
sys.exit(1 if fails else 0)
