"""The driver cards' measurements (17 Nov 2026): what a car's three numbers make it do, on a race-track tape.
Usage: python3 tests/rt_cards.py <tape name in build/> <its src folder> [what ...]
  car                 YOUR car on an open stretch (the whole world made road for the test): its top speed, how long it
                      takes to reach 90% of it from rest, and THE SLIDE - flat out, the steering held for a right-angle
                      turn (16 TV frames), then let go: how many TV frames until the car again goes where it points
                      (within 10 degrees), and how far it ran on in its old direction from the turn-in (a car on rails: 18 px)
  car=top,push,g,q,s,b  the same with trial numbers poked in (no tape need be built): top speed and push (256 = 1 px a
                      frame), and the tyres' four holds - gripping, with Q, sliding, both
  cpu                 each COMPUTER car alone on the open stretch: top speed, time to 90% of it, px in its first second
  scale               THE SCALE, MEASURED: for each rating 1 to 10 - the top speed and the TV frames from rest to 90% of it
                      (a computer car with that rating for speed and for acceleration, the other at 5), and your car's
                      slide with that rating for grip (speed and acceleration 5). Takes a minute.
  ace [LOOK ...]      your car alone, 3 laps by the corner-cutting autopilot (rt_ace.py): laps and TV frames on the grass
The lap times in the pack are tests/rt_tight.py's (it reads the cards' tape like any other)."""
import sys, math
from rt_lib import *
import rt_ace
def open_road(g):
    S = g.sym
    g.poke(S['surface_map'], [0] * (9 * S['maph']))
def set_car(g, nums):
    S = g.sym; top, push, a, b, c, d = nums
    g.poke(S['yg_topv'], [top & 255, top >> 8]); g.poke(S['yg_pushv'], [push & 255, push >> 8]); g.poke(S['yg_gtab'], [a, b, c, d])
def vel(g, i=0):
    c = g.mem(g.sym['cars'] + i * g.sym['c_size'], 12)
    s = lambda lo, hi: (lo + 256 * hi + 32768) % 65536 - 32768
    return s(c[6], c[7]), s(c[8], c[9]), c[10]
def car(name, src, nums=None):
    g = Game(name, src); g.to_grid(); g.go(alone=True); open_road(g)
    if nums: set_car(g, nums)
    g.put(40, 250, 16); g.key('O', False); g.key('P', False); g.key('Q', True)
    sp = []
    for f in range(120):
        g.run(1); vx, vy, a = vel(g); sp.append(math.hypot(vx, vy))
    top = max(sp); t90 = next(i for i, v in enumerate(sp) if v >= 0.9 * top) + 1
    x0, y0, _ = g.car()
    g.key('P', True); g.run(16); g.key('P', False)
    n = None; wide = 0; still = 0
    for f in range(400):
        g.run(1); vx, vy, a = vel(g); x, y, _ = g.car(); wide = max(wide, x - x0)
        off = abs((math.degrees(math.atan2(vx, -vy)) - a * 5.625 + 540) % 360 - 180)
        still = still + 1 if off < 10 else 0
        if still >= 5: n = f + 16 - 4; break
    g.close()
    return top / 256, t90, n, wide
def cpu(name, src, rows=None):
    g = Game(name, src); g.to_grid(); g.go(alone=False); open_road(g)
    S = g.sym; CS = S['c_size']; out = []
    for i, r in enumerate(rows or []):       # (trial cards: each row is (ACCEL push number, SPEED push number, top speed))
        g.poke(S['cd_tab'] + 8 * i + 3, [min(r[2] * 4 // 5, 7 * (64 + r[0]) * 85 // 100) // 4, r[0] & 255, r[1] & 255])
    for i in range(1, 5):
        g.put(40, 100 + 60 * i, 16, i=i)
    g.put(40, 30, 16)
    g.key('Q', False)
    sp = [[] for _ in range(5)]; x1 = [0] * 5
    for f in range(160):
        for i in range(1, 5):            # (held pointing along the stretch, with the throttle down: the car only, no driver)
            a = S['cars'] + i * CS
            g.poke(a + 10, [16]); g.poke(a + 23, [0]); g.poke(a + 24, [0]); g.poke(a + 16, [0]); g.poke(a + 18, [9])
        g.run(1)
        for i in range(1, 5): vx, vy, a = vel(g, i); sp[i].append(math.hypot(vx, vy))
        if f == 49: x1 = [g.car(i)[0] - 40 for i in range(5)]
    for i in range(1, 5):
        top = max(sp[i]); out.append((top / 256, next(k for k, v in enumerate(sp[i]) if v >= 0.9 * top) + 1, x1[i]))
    g.close()
    return out
def scale(name, src):
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    import make_cards as mc
    sp = []; ac = []
    for lo in (1, 5, 9):
        r = list(range(lo, min(lo + 4, 11)))
        sp += cpu(name, src, [(0, mc.k_speed(v), mc.top(v)) for v in r]); ac += cpu(name, src, [(mc.k_accel(v), 0, 448) for v in r])
    print('THE SCALE, MEASURED on %s (a TV frame is a fiftieth of a second; "as it was" is the car before the cards)' % name)
    print('rating   SPEED: top speed      ACCELERATION: how far it gets     GRIP (your car): after a flat-out right-angle turn it')
    print('         px a TV frame         in the first second, px           slides for ... TV frames and runs ... px straight on')
    for v in range(1, 11):
        t = mc.tyres(v); top, t90, n, wide = car(name, src, [448, 64] + list(t))
        print('  %2d        %.2f                       %2d                              %3s              %3d       (tyres hold %d)' % (v, sp[v - 1][0], ac[v - 1][2], n, wide, t[0]))
    top, t90, n, wide = car(name, src, [448, 64, 16, 8, 8, 5])
    print('  as it was  1.75                       %2d                              %3s              %3d       (tyres hold 16)' % (ac[4][2], n, wide))
if __name__ == '__main__':
    name, src = sys.argv[1], sys.argv[2]
    if 'scale' in sys.argv[3:]: scale(name, src); sys.exit()
    for w in sys.argv[3:] or ['car']:
        if w.startswith('car'):
            nums = [int(v) for v in w[4:].split(',')] if '=' in w else None
            top, t90, n, wide = car(name, src, nums)
            print('%s your car%s: top speed %.2f px a TV frame, %d TV frames from rest to 90%% of it; after a flat-out right-angle turn it slides for %s TV frames and runs %d px on in its old direction' % (name, ' with ' + w[4:] if nums else '', top, t90, n, wide))
        elif w == 'cpu':
            for k, (top, t90, x1) in zip(['CYAN', 'GREEN', 'PINK', 'WHITE'], cpu(name, src)):
                print('%s %-6s top speed %.2f px a TV frame, %d TV frames from rest to 90%% of it (it is moved once a picture: to the nearest 4), %d px in its first second' % (name, k, top, t90, x1))
        elif w == 'ace':
            for look in ([int(v) for v in sys.argv[sys.argv.index('ace') + 1:] if v.isdigit()] or [88]):
                l, on = rt_ace.laps(name, src, look, 60)
                print('%s your car alone, the corner-cutting autopilot LOOK %d: laps %s (the first from the grid), %d TV frames on the grass' % (name, look, l, on))
            break
