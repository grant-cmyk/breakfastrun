"""How smoothly the computer cars move: their distance moved from one picture to
the next, on the opening straight. Jerky = big swings between pictures.
Prints, for each car, the moves and their spread (standard deviation / mean)."""
import os, math, statistics
from zx._spectrum import Spectrum
import zx._spectrum as zs
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SYM = {}
for line in open(os.path.join(ROOT, 'build', 'racer.sym')):
    p = line.split()
    if len(p) >= 3 and p[1] == 'EQU': SYM[p[0].lower()] = int(p[2].rstrip('H'), 16)
CARS, CS = SYM['cars'], SYM['c_size']
class P(Spectrum):
    armed = False
    def on_breakpoint(self):
        if self.armed and self.pc == SYM['copy_done']:
            self.armed = False
            raise zs.EmulatorException('copy')
with P(headless=True) as sp:
    sp.load_tape(os.path.join(ROOT, 'build', 'racer.tap'))
    import title_skip; title_skip.leave(sp)   # the title screen first: 1 = 1UP
    while sp.read16(SYM['renders']) < 3: sp.run(duration=0.1, fast_forward=True)
    sp.devices.notify(zs.KeyStroke(zs.KEYS['Q'].ID, pressed=True)); sp.run(duration=0.2, fast_forward=True)
    sp.devices.notify(zs.KeyStroke(zs.KEYS['Q'].ID, pressed=False))
    sp.run(duration=1.0, fast_forward=True)                  # up to speed
    sp.set_breakpoint(SYM['copy_done'])
    pos = []
    for n in range(40):
        sp.armed = True
        while True:
            try: sp.run(duration=0.02, fast_forward=True)
            except zs.EmulatorException: break
        pos.append([(sp.read16(CARS + k * CS + 1) + sp.read8(CARS + k * CS) / 256, sp.read16(CARS + k * CS + 4) + sp.read8(CARS + k * CS + 3) / 256) for k in range(5)])
for k in range(1, 5):
    mv = [math.hypot(b[k][0] - a[k][0], b[k][1] - a[k][1]) for a, b in zip(pos, pos[1:])]
    print('car %d moves per picture: %s  spread %.0f%%' % (k, ' '.join('%.1f' % m for m in mv[:16]), 100 * statistics.pstdev(mv) / statistics.mean(mv)))
