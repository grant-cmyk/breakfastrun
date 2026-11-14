"""The view leads the car (Grant, 14 Nov 2026: "have the car position in the screen adjust to allow
to see ahead more on the track"): centred at rest, sliding ahead with speed, back when it stops,
never a jump. Prints PASS/FAIL lines and RESULT."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'drive_test.py')).read()
src = src[:src.index('with Racer(headless=True)')].replace("os.path.dirname(os.path.abspath(__file__))", repr(HERE))
exec(src)
fails = 0
def ok(c, m):
    global fails
    print('PASS' if c else 'FAIL', m); fails += 0 if c else 1
s8 = lambda v: v - 256 if v > 127 else v
def lead(sp): return s8(sp.read8(SYM['lead_x'])), s8(sp.read8(SYM['lead_y']))
def onscreen(sp):
    c = car(sp, 0); return c['x'] - sp.read16(SYM['camx']), c['y'] - sp.read16(SYM['camy'])
with Racer(headless=True) as sp:
    sp.load_tape(TAP); t = 0
    while g(sp, 'renders') == 0 and t < 60: sp.run(duration=0.1, fast_forward=True); t += 0.1
    go_green(sp); press(sp, 'Q', False)
    for i in CPUS: put(sp, i, 4 + 40 * i, SY + 58); sp.write(CARS + i * CS + 19, bytes([0]))
    put(sp, 0, 120, SY - 8, 16); sp.run(duration=1.0, fast_forward=True)
    ok(lead(sp) == (0, 0) and onscreen(sp) == (WW // 2 - 8, WH // 2 - 8), 'at rest: no lead, the car in the window\'s middle %s' % (onscreen(sp),))
    press(sp, 'Q', True); seen = [lead(sp)[0]]
    for k in range(40): sp.run(duration=0.04, fast_forward=True); seen.append(lead(sp)[0])
    step = max(abs(b - a) for a, b in zip(seen, seen[1:]))
    lx, ly = lead(sp); x, y = onscreen(sp)
    ok(lx == 20 and abs(ly) <= 3 and abs(x - (WW // 2 - 8 - 20)) <= 8, 'at speed to the right: the view 20 pixels ahead, the car at x %d of %d in the window (lead %d, %d)' % (x, WW, lx, ly))
    ok(step <= 6, 'it slid there: never more than %d pixels between looks 2 TV frames apart' % step)
    shot(sp, 'lead_right.png')
    press(sp, 'Q', False); sp.run(duration=4.0, fast_forward=True)
    ok(lead(sp) == (0, 0), 'stopped: the car is back in the middle %s' % (lead(sp),))
print('RESULT:', 'PASS' if fails == 0 else '%d FAIL' % fails)
