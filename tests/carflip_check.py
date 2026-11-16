"""The cars drawn from frames read upside down (FLIP=1) against the ordinary build, pixel for pixel:
all five cars at every one of the 16 headings on the grid and part-way off the window's edges (the window's
lines 8-127 are compared: the moving HUD is below them). SHOT=name saves each build's title screen to look at.
Usage: python3 tests/carflip_check.py [flip tape] [flip sym]     (default build/racer_carflip.*; against build/racer.*)"""
import os, sys
from zx._spectrum import Spectrum
import zx._spectrum as zs
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = (os.environ.get('ATAP', os.path.join(ROOT, 'build', 'racer.tap')), os.environ.get('ASYM', os.path.join(ROOT, 'build', 'racer.sym')))
B = (sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'build', 'racer_carflip.tap'), sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'build', 'racer_carflip.sym'))
def syms(f):
    d = {}
    for line in open(f):
        p = line.split()
        if len(p) >= 3 and p[1] == 'EQU': d[p[0].lower()] = int(p[2].rstrip('H'), 16)
    return d
def press(sp, k, down): sp.devices.notify(zs.KeyStroke(zs.KEYS[k].ID, pressed=down))
def shots(tap, symf):
    SYM = syms(symf); out = []; CS = SYM['c_size']; CARS = SYM['cars']
    class R(Spectrum):
        armed = False
        def on_breakpoint(self):
            if self.armed and self.pc == SYM['copy_done']:
                self.armed = False; raise zs.EmulatorException('copy_done')
    with R(headless=True) as sp:
        sp.load_tape(tap); t = 0
        while sp.read8(0x5800 + 8 * 32 + 10) != 0x7A and t < 60: sp.run(duration=0.1, fast_forward=True); t += 0.1
        sp.run(duration=3.0, fast_forward=True)          # (the title's cars are not compared: they are paced by how long they take to draw - looked at by eye)
        if os.environ.get('SHOT'):
            from PIL import Image
            sp.render_screen(); import numpy as np
            px = np.array(sp.get_frame_pixels(), dtype=np.uint8).reshape(-1, 352, 4)[:, :, [2, 1, 0]]
            Image.fromarray(px).resize((704, px.shape[0] * 2), Image.NEAREST).save(os.environ['SHOT'] + ('_b.png' if tap == B[0] else '_a.png'))
        sp.write(SYM['jin_on'], bytes([0xFF]))
        press(sp, '1', True); sp.run(duration=0.2, fast_forward=True); press(sp, '1', False)
        sp.run(duration=2.0, fast_forward=True)
        sp.set_breakpoint(SYM['copy_done'])
        def stop():
            sp.armed = True
            try:
                for _ in range(80): sp.run(duration=0.02, fast_forward=True)
            except zs.EmulatorException: pass
        stop()
        x0 = sp.read16(CARS + 1); y0 = sp.read16(CARS + 4)
        for place, (dx, dy) in (('grid', (0, 0)), ('grid 2', (0, 0)), ('top edge', (0, -76)), ('left edge', (-92, 0)), ('right edge', (94, 0))):
            for h in range(16):
                stop()
                for n in range(5):                       # (before the lights nothing moves: the cars stay where they are put)
                    b = CARS + n * CS
                    x = x0 + (n - 3 if n < 3 else n - 2) * 22 * (dy != 0 or place.startswith('grid')) + dx + (0 if dx == 0 or n == 0 else 0)
                    y = y0 + (n - 3 if n < 3 else n - 2) * 22 * (dx != 0) + dy
                    if n == 0: x, y = x0, y0             # your car stays put (the camera follows it)
                    sp.write(b + 1, bytes([x & 255, (x >> 8) & 255])); sp.write(b + 4, bytes([y & 255, (y >> 8) & 255]))
                    sp.write(b + 6, bytes(4))
                    if n: sp.write(b + 10, bytes([h * 4]))       # (your own car keeps its heading: the view leads the way it points)
                    if n == 1: sp.write(b + 22, bytes([0 if place == 'grid 2' else 1]))   # ('grid 2': the second car wears YOUR car's pictures)
                for _ in range(3): stop()
                out.append(('%s, heading %d' % (place, h), bytes(sp.read(0x4000, 6144)), (sp.read16(SYM['camx']), sp.read16(SYM['camy']), sp.read16(SYM['renders']) & 3)))
    return out
a = shots(*A); b = shots(*B)
def win(p):                                      # the window's lines 8-127, columns 1-24, less the place plate top right (the HUD's moving parts are below)
    return bytes(p[((y & 0xC0) << 5) | ((y & 7) << 8) | ((y & 0x38) << 2) | x] for y in range(8, 128) for x in range(1, 25) if not (y < 32 and x > 18))
cams = [(x[2], y[2]) for x, y in zip(a, b)]
a = [(x[0], win(x[1])) for x in a]; b = [(x[0], win(x[1])) for x in b]
def box(p, q):
    d = [divmod(i, 24) for i in range(len(p)) if p[i] != q[i]]
    return 'lines %d-%d, columns %d-%d, cameras %s' % (8 + min(y for y, x in d), 8 + max(y for y, x in d), 1 + min(x for y, x in d), 1 + max(x for y, x in d), cams[[n for n, _ in a].index(NAME)])
def box_old(p, q):
    ys = [((i >> 5) & 0xC0 | (i >> 8 & 7) | (i >> 2 & 0x38), (i & 31)) for i in range(6144) if p[i] != q[i]]
    return 'lines %d-%d, columns %d-%d' % (min(y for y, x in ys), max(y for y, x in ys), min(x for y, x in ys), max(x for y, x in ys))
bad = []
for (n, p), (_, q) in zip(a, b):
    if p != q:
        NAME = n; bad.append((n, sum(bin(x ^ y).count('1') for x, y in zip(p, q)), box(p, q)))
ink = sum(1 for n, p in a if any(p))
print('%s the cars drawn from frames read upside down are the ordinary build\'s, pixel for pixel: %d screens compared (%d with ink), %d differ%s'
      % ('PASS' if not bad and len(a) == len(b) else 'FAIL', len(a), ink, len(bad), '' if not bad else ' - ' + ', '.join('%s (%d px, %s)' % x for x in bad[:12])))
sys.exit(1 if bad else 0)
