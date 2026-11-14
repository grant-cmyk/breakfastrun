"""Where does the time go?  Breakpoints on the main-loop stages, timed in
T-states (FRAMES * 69888 + ticks since the last interrupt), on the real ROM,
while you drive with all three cars in view. Prints the average per picture."""
import os, sys
from zx._spectrum import Spectrum
import zx._spectrum as zs
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SYM = {}
for line in open(os.environ.get('ZSYM', os.path.join(ROOT, 'build', 'racer.sym'))):
    p = line.split()
    if len(p) >= 3 and p[1] == 'EQU': SYM[p[0].lower()] = int(p[2].rstrip('H'), 16)
STAGES = ['main', 'tick_loop', 'race_progress', 'hud_update', 'camera', 'draw_tiles', 'draw_car', 'copy_to_screen', 'cloth_fill']
ADDR = {SYM[n]: n for n in STAGES}
log = []
class P(Spectrum):
    def on_breakpoint(self):
        t = self.read16(23672) * 69888 + self.ticks_since_int
        log.append((ADDR.get(self.pc), t))
with P(headless=True) as sp:
    sp.load_tape(os.environ.get('ZTAP', os.path.join(ROOT, 'build', 'racer.tap')))
    import title_skip; title_skip.leave(sp)   # the title screen first: 1 = 1UP
    while sp.read16(SYM['renders']) == 0:
        sp.run(duration=0.1, fast_forward=True)
    sp.run(duration=3.0, fast_forward=True)   # (the start: five cars bunched on the grid)
    for a in ADDR: sp.set_breakpoint(a)
    sp.devices.notify(zs.KeyStroke(zs.KEYS['Q'].ID, pressed=True))
    sp.run(duration=2.0, fast_forward=True)
# split the log into pictures (each starts at 'main' after a picture), sum time per stage
from collections import defaultdict
tot = defaultdict(int); pics = 0; ticks = 0
for (n, t), (n2, t2) in zip(log, log[1:]):
    if n == 'main' and n2 == 'tick_loop': n = 'wait for a frame'
    if n == 'tick_loop': n = 'ticks (keys, AI, physics, bumps)'
    if n == 'cloth_fill': pics += 1
    tot[n] += t2 - t
for n, t in sorted(tot.items(), key=lambda kv: -kv[1]):
    print('%-36s %7d T per picture' % (n, t // max(pics, 1)))
print('pictures: %d in 2 s; total per picture %d T = %.2f TV frames' %
      (pics, sum(tot.values()) // pics, sum(tot.values()) / pics / 69888))
