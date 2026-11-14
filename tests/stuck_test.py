"""A computer car knocked off its line must find its way back (Grant, 14 Nov 2026: "the tank got
stuck in the top middle section of the game - in between the loops/circles and could not get out").
Each computer car is dropped, stopped, on a grid of places over the whole table - on the road, on
the cloth, in among the cereal O's - aiming at the waypoint it was near or the one before or after,
and must be passing waypoints again within 12 seconds. Prints PASS/FAIL lines and RESULT.
AREA=x0,y0,x1,y1 STEP=n to look at one part more closely."""
import os, re, random, math
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'drive_test.py')).read()
src = src[:src.index('with Racer(headless=True)')].replace("os.path.dirname(os.path.abspath(__file__))", repr(HERE))
exec(src)
wps = [tuple(int(v) for v in l.split('dw')[1].split(',')) for l in open(os.path.join(ROOT, 'src', 'waypoints.asm')).read().split('waypoints:')[1].splitlines() if 'dw' in l]
x0, y0, x1, y1 = [int(v) for v in os.environ.get('AREA', '8,8,%d,%d' % (MAPW * 8 - 24, MAPH * 8 - 24)).split(',')]
STEP = int(os.environ.get('STEP', 24)); SECS = float(os.environ.get('SECS', 12))
pts = [(x, y) for y in range(y0, y1 + 1, STEP) for x in range(x0, x1 + 1, STEP)]
random.seed(5); random.shuffle(pts)
pts = [p for p in pts if math.hypot(p[0] - 248, p[1] - 384) > 30]
fails = 0; stuck = []
with Racer(headless=True) as sp:
    sp.load_tape(TAP); t = 0
    while g(sp, 'renders') == 0 and t < 60: sp.run(duration=0.1, fast_forward=True); t += 0.1
    go_green(sp); press(sp, 'Q', False)
    YOU = (car(sp, 0)['x'], car(sp, 0)['y'])            # (you stay on the grid: places near you are left out)
    k = 0
    while k < len(pts):
        batch = pts[k:k + len(CPUS)]; k += len(CPUS); start = {}
        for i, (x, y) in zip(CPUS, batch):
            near = min(range(len(wps)), key=lambda n: math.hypot(wps[n][0] - x - 8, wps[n][1] - y - 8))
            wp = (near + random.choice((-1, 0, 1, 2))) % len(wps)
            put(sp, i, x, y, random.randrange(64)); sp.write(CARS + i * CS + 13, bytes([wp])); sp.write(CARS + i * CS + 25, bytes([1])); start[i] = (x, y, wp)
        sp.write(SYM['race_over'], bytes([0]))            # (dropped about, they cross the line early: the race never ends)
        sp.run(duration=SECS, fast_forward=True)
        for i in start:
            c = car(sp, i); x, y, wp = start[i]
            if (c['wp'] - wp) % len(wps) < 2: stuck.append((x, y, wp, c['x'], c['y'], c['wp']))
print('PASS' if not stuck else 'FAIL', 'every computer car dropped anywhere on the table is passing waypoints again within %d s (%d places; stuck: %d)' % (SECS, len(pts), len(stuck)))
for s in stuck[:40]: print('   dropped at %d,%d aiming at waypoint %d: after %d s at %d,%d, waypoint %d' % (s[:3] + (SECS,) + s[3:]))
print('RESULT:', 'PASS' if not stuck else '%d FAIL' % len(stuck))
