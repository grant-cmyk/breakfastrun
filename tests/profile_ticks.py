"""Like profile_lap.py, with the game tick split up: your physics, the computer cars' thinking
and physics, the bumps and the O checks (T-states per picture, over an autopilot lap).
(averaged over every picture of the lap), and how many TV frames pictures took."""
import os, math
from collections import defaultdict, Counter
from zx._spectrum import Spectrum
import zx._spectrum as zs
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SYM = {}
for line in open(os.path.join(ROOT, 'build', 'racer.sym')):
    p = line.split()
    if len(p) >= 3 and p[1] == 'EQU': SYM[p[0].lower()] = int(p[2].rstrip('H'), 16)
src = open(os.path.join(ROOT, 'src', 'world.asm')).read()
wps = [tuple(int(v) for v in l.split('dw')[1].split(',')) for l in open(os.path.join(ROOT, 'src', 'waypoints.asm')).read().split('waypoints:')[1].splitlines() if 'dw' in l]
STAGES = ['main', 'tick_loop', 'cpu_move', 'tick', 'tk_you', 'tk_ai', 'ai_drive', 'tk_rest', 'bump_all', 'tk_o', 'race_progress', 'hud_update', 'camera', 'cloth_fill', 'draw_tiles', 'draw_car', 'wait_show', 'copy_to_screen']
ADDR = {SYM[n]: n for n in STAGES}
log = []
class P(Spectrum):
    def on_breakpoint(self):
        if self.pc in ADDR: log.append((ADDR[self.pc], self.read16(23672) * 69888 + self.ticks_since_int))
held = set()
def key(sp, k, d):
    if d and k not in held: sp.devices.notify(zs.KeyStroke(zs.KEYS[k].ID, pressed=True)); held.add(k)
    if not d and k in held: sp.devices.notify(zs.KeyStroke(zs.KEYS[k].ID, pressed=False)); held.discard(k)
CARS = SYM['cars']
with P(headless=True) as sp:
    sp.load_tape(os.path.join(ROOT, 'build', 'racer.tap'))
    import title_skip; title_skip.leave(sp)   # the title screen first: 1 = 1UP
    while sp.read16(SYM['renders']) == 0: sp.run(duration=0.1, fast_forward=True)
    sp.devices.notify(zs.KeyStroke(zs.KEYS['Q'].ID, pressed=True))   # the start lights: to green first
    while sp.read8(SYM['race_on']) == 0: sp.run(duration=0.02, fast_forward=True)
    for a in ADDR: sp.set_breakpoint(a)
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
        sp.run(duration=0.02, fast_forward=True); t += 0.02
tot = defaultdict(int); pics = 0; frames = Counter(); last_copy = None
for (n, t0), (n2, t1) in zip(log, log[1:]):
    tot[n] += t1 - t0
    if n == 'copy_to_screen':
        pics += 1
        if last_copy is not None: frames[round((t0 - last_copy) / 69888)] += 1
        last_copy = t0
names = {'main': 'frames to step', 'tick_loop': 'tick loop', 'tick': 'tick: clock, keys', 'tk_you': 'your physics', 'tk_ai': 'cpu: loop', 'ai_drive': 'cpu: thinking', 'cpu_move': 'cpu: physics', 'tk_rest': 'cpu: next', 'bump_all': 'bumps', 'tk_o': 'O checks', 'wait_show': 'waiting for the 3rd frame'}
work = 0
for n, v in sorted(tot.items(), key=lambda kv: -kv[1]):
    print('%-30s %7d T' % (names.get(n, n), v // pics))
    if n != 'wait_show': work += v // pics
print('work per picture %d T (3 frames = 209,664)' % work)
print('TV frames per picture over the lap:', dict(sorted(frames.items())), ' lap %.1f s' % t)
