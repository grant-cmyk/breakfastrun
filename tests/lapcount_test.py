"""Your laps are counted even when you leave the track and rejoin further round (Grant, 15 Nov 2026:
"sometimes I get off track, when I get back on and go over the finish line, it does not see that
as a lap and I need to do an extra lap"). Up to four waypoints may be missed; a real short cut
(ten of them) is still not a lap. Prints PASS/FAIL lines and RESULT."""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'drive_test.py')).read()
src = src[:src.index('with Racer(headless=True)')].replace("os.path.dirname(os.path.abspath(__file__))", repr(HERE))
exec(src)
fails = 0
def ok(c, m):
    global fails
    print('PASS' if c else 'FAIL', m); fails += 0 if c else 1
WPS = [tuple(int(v) for v in l.split('dw')[1].split(',')) for l in open(os.path.join(ROOT, 'src', 'waypoints.asm')).read().split('waypoints:')[1].splitlines() if 'dw' in l]
WS, NWP = SYM['ws'], SYM['nwp']
def at(sp, wp_next, stand_on, secs=2.5):               # your next waypoint, and where the car is put: (laps, next waypoint) after a while there
    sp.write(CARS + 13, bytes([wp_next % NWP])); sp.write(CARS + 25, bytes([1]))
    x, y = WPS[stand_on % NWP][:2]; put(sp, 0, x - 8, y - 8, 16); sp.run(duration=secs, fast_forward=True)
    return sp.read8(CARS + 25), sp.read8(CARS + 13)
with Racer(headless=True) as sp:
    sp.load_tape(TAP); t = 0
    while g(sp, 'renders') == 0 and t < 60: sp.run(duration=0.1, fast_forward=True); t += 0.1
    go_green(sp); press(sp, 'Q', False)
    for i in CPUS: put(sp, i, 4 + 40 * i, SY + 58); sp.write(CARS + i * CS + 19, bytes([0]))
    sp.run(duration=0.5, fast_forward=True)
    laps, wp = at(sp, WS, WS)
    near = lambda wp, on: (wp - on) % NWP in (1, 2, 3)        # (standing on a waypoint, the next one or two are within reach too)
    ok(laps == 2 and near(wp, WS), 'on the line with the line\'s waypoint next: a lap, as ever (lap %d, next %d)' % (laps, wp))
    for miss in (1, 2, 3, 4):
        laps, wp = at(sp, WS - miss, WS)
        ok(laps == 2 and near(wp, WS), 'over the line having missed the %d waypoint%s before it (off the track and back on): still a lap (lap %d, next %d)' % (miss, '' if miss == 1 else 's', laps, wp))
    laps, wp = at(sp, WS - 10, WS, 4.0)
    ok(laps == 1 and wp == (WS - 10) % NWP, 'ten missed - a real short cut: no lap (lap %d, next %d)' % (laps, wp))
    laps, wp = at(sp, WS + 6, WS + 9)
    ok(near(wp, WS + 9), 'the same out on the lap: three missed, and on from where you rejoined (next %d)' % wp)
print('RESULT:', 'PASS' if fails == 0 else '%d FAIL' % fails)
