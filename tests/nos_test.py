"""NOS on the real ROM (Grant, 10 Nov 2026): you start with one canister; SPACE fires
it - about 1 s at twice the push (so up to twice the top speed); driving over
canister A (just behind the grid) puts it in your inventory and brings out B (the
top area); the crew chief says so. Prints PASS/FAIL lines and RESULT."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'drive_test.py')).read()
src = src[:src.index('with Racer(headless=True)')].replace("os.path.dirname(os.path.abspath(__file__))", repr(HERE))
exec(src)
INV, BOOST, SHOW = SYM['bufc'] + 139, SYM['bufc'] + 146, SYM['bufc'] + 145
fails = 0
def ok(c, m):
    global fails
    print('PASS' if c else 'FAIL', m); fails += 0 if c else 1
with Racer(headless=True) as sp:
    sp.load_tape(TAP); t = 0
    while g(sp, 'renders') == 0 and t < 60: sp.run(duration=0.1, fast_forward=True); t += 0.1
    sp.run(duration=1.0, fast_forward=True)
    ok(list(sp.read(INV, 3)) == [1, 0, 0], 'you start with one NOS canister (inventory %s)' % list(sp.read(INV, 3)))
    hold(sp, ['Q'], 0.3)                                  # racing; then the start straight's
    for i in CPUS: put(sp, i, 20 + 25 * i, SY + 58)           # (the computer cars out of the way)
    put(sp, 0, 175, SY - 8, 16)                              # left end, clear of canister A
    hold(sp, ['Q'], 1.2)                                  # up to top speed on the straight
    v0 = car(sp, 0)['vx']
    press(sp, 'Q', True); press(sp, 'SPACE', True)
    sp.run(duration=0.1, fast_forward=True); press(sp, 'SPACE', False)
    bt = sp.read8(BOOST)
    vmax = 0
    for _ in range(12):
        sp.run(duration=0.1, fast_forward=True); vmax = max(vmax, math.hypot(car(sp, 0)['vx'], car(sp, 0)['vy']))
    press(sp, 'Q', False)
    print('top speed before %.2f, with NOS %.2f px/frame; boost frames at the start %d' % (v0, vmax, bt))
    ok(bt > 40 and vmax > 1.9 * v0 * 0.9, 'SPACE fires it: up to about twice the top speed (%.2f -> %.2f)' % (v0, vmax))
    ok(sp.read8(BOOST) == 0, 'the burst is over after about a second')
    ok(list(sp.read(INV, 3)) == [0, 0, 0], 'the canister is used up')
    put(sp, 0, SYM['nos_a_x'] - 8, SYM['nos_a_y'] - 8, 16)   # over canister A
    sp.run(duration=0.5, fast_forward=True)
    ok(list(sp.read(INV, 3)) == [1, 0, 0] and sp.read8(SHOW) == 1,
       'driving over canister A: it is yours, and B comes out (inventory %s, showing %d)' % (list(sp.read(INV, 3)), sp.read8(SHOW)))
    ok(sp.read8(SYM['nos_a_t0']) == 0 and sp.read8(SYM['nos_b_t0']) == SYM['nos_b_v0'], 'A is off the map, B is on it')
    sp.run(duration=1.5, fast_forward=True)
    shot(sp, 'nos_pickup.png')
print('RESULT:', 'PASS' if fails == 0 else '%d FAIL' % fails)
