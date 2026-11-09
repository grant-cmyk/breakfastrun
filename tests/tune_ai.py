"""Try computer-car settings on the real ROM: pokes PACE / REACT / ERR into the
four records (and the waypoint 'reached' distance into the code), races 90 s,
reports each car's average lap and time on the road. Used to tune, not a gate."""
import sys, os, re, math, json
from zx._spectrum import Spectrum
import zx._spectrum as zs
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SYM = {}
for line in open(os.path.join(ROOT, 'build', 'racer.sym')):
    p = line.split()
    if len(p) >= 3 and p[1] == 'EQU': SYM[p[0].lower()] = int(p[2].rstrip('H'), 16)
src = open(os.path.join(ROOT, 'src', 'world.asm')).read() + open(os.path.join(ROOT, 'src', 'waypoints.asm')).read()
NWP = int(re.search(r'NWP\s+equ\s+(\d+)', src).group(1))
surf = []
for l in src[src.index('surface_map:'):src.index('waypoints')].splitlines():
    if 'defb' in l:
        for b in l.split('defb')[1].split(','): surf += [int(c) for c in b.strip().lstrip('%')]
CARS, CS, N = SYM['cars'], SYM['c_size'], SYM['ncars']
cfg = json.loads(sys.argv[1])                 # {"pace":[..4], "react":[..], "err":[..]}
with Spectrum(headless=True) as sp:
    sp.load_tape(os.path.join(ROOT, 'build', 'racer.tap'))
    while sp.read16(SYM['renders']) == 0: sp.run(duration=0.1, fast_forward=True)
    for i in range(4):
        b = CARS + (i + 1) * CS
        sp.write(b + 19, bytes([cfg['pace'][i], cfg['react'][i], cfg['err'][i]]))
    sp.write(CARS + 1, bytes([40, 0])); sp.write(CARS + 4, bytes([40, 0]))   # park you in a corner
    sp.write(SYM['race_on'], bytes([1]))
    last = [sp.read8(CARS + (i + 1) * CS + 13) for i in range(4)]
    laps = [[] for _ in range(4)]; on = [0] * 4; n = 0; t = 0.0; m0 = sp.read16(SYM['mistakes'])
    while t < 90:
        sp.run(duration=0.1, fast_forward=True); t += 0.1; n += 1
        for i in range(4):
            b = CARS + (i + 1) * CS
            wp = sp.read8(b + 13)
            if wp < last[i] and last[i] - wp > NWP // 2: laps[i].append(t)
            last[i] = wp
            x, y = sp.read16(b + 1) + 8, sp.read16(b + 4) + 8
            on[i] += surf[(y // 8) * 72 + x // 8] == 0
    mis = sp.read16(SYM['mistakes']) - m0
avg = [(l[-1] - l[0]) / (len(l) - 1) if len(l) > 1 else 0 for l in laps]
print(json.dumps(cfg), '| laps', ' '.join('%.1f' % a for a in avg), '| on road', ' '.join('%.0f%%' % (100 * o / n) for o in on),
      '| mistakes', mis)
