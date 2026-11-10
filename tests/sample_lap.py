"""Where the time goes: an autopilot lap on the real ROM, the CPU's place sampled every
~0.2 ms of emulated time, each sample put to the label at or before it. Prints the
labels with the biggest share (a statistical profile of everything, not just the stages)."""
import os, math, bisect
from collections import Counter
from zx._spectrum import Spectrum
import zx._spectrum as zs
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SYM = {}
for line in open(os.path.join(ROOT, 'build', 'racer.sym')):
    p = line.split()
    if len(p) >= 3 and p[1] == 'EQU': SYM[p[0].lower()] = int(p[2].rstrip('H'), 16)
src = open(os.path.join(ROOT, 'src', 'racer.asm')).read()
labels = sorted((a, n) for n, a in SYM.items() if a >= 0x5F00 and not n.isupper())
addrs = [a for a, n in labels]
wps = [tuple(int(v) for v in l.split('dw')[1].split(',')) for l in open(os.path.join(ROOT, 'src', 'waypoints.asm')).read().split('waypoints:')[1].splitlines() if 'dw' in l]
held = set()
def key(sp, k, d):
    if d and k not in held: sp.devices.notify(zs.KeyStroke(zs.KEYS[k].ID, pressed=True)); held.add(k)
    if not d and k in held: sp.devices.notify(zs.KeyStroke(zs.KEYS[k].ID, pressed=False)); held.discard(k)
CARS = SYM['cars']; hits = Counter(); n = 0
with Spectrum(headless=True) as sp:
    sp.load_tape(os.path.join(ROOT, 'build', 'racer.tap'))
    while sp.read16(SYM['renders']) == 0: sp.run(duration=0.1, fast_forward=True)
    key(sp, 'Q', True)
    while sp.read8(SYM['race_on']) == 0: sp.run(duration=0.02, fast_forward=True)
    x0 = sp.read16(CARS + 1); wp = 0
    while wps[wp][0] < x0 + 30: wp += 1
    start_wp, laps, t = wp, 0, 0.0
    while laps < 1 and t < 30:
        x, y, ang = sp.read16(CARS + 1) + 8, sp.read16(CARS + 4) + 8, sp.read8(CARS + 10)
        tx, ty = wps[wp]
        if math.hypot(tx - x, ty - y) < 28:
            wp = (wp + 1) % len(wps); laps += wp == start_wp
        diff = (math.degrees(math.atan2(tx - x, -(ty - y))) % 360 - ang * 360 / 64 + 540) % 360 - 180
        key(sp, 'Q', abs(diff) < 70); key(sp, 'O', diff < -8); key(sp, 'P', diff > 8)
        for _ in range(100):
            sp.run(duration=0.0002, fast_forward=True)
            pc = sp.pc; i = bisect.bisect_right(addrs, pc) - 1
            hits[labels[i][1] if i >= 0 else '?'] += 1; n += 1
        t += 0.02
print('samples', n, 'lap %.1f s' % t)
for name, c in hits.most_common(40):
    print('%-22s %5.1f%%' % (name, 100 * c / n))
