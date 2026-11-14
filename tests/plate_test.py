"""Your place on its small plate inside the window, top right (Grant, 14 Nov 2026: "3 is good
build 3"): not there while the start lights hang; then a solid rounded plate with the table clear
round it, different for each place and each lap; and under it FINAL LAP! on a second plate while
the strip says so. Prints PASS/FAIL lines and RESULT."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'drive_test.py')).read()
src = src[:src.index('with Racer(headless=True)')].replace("os.path.dirname(os.path.abspath(__file__))", repr(HERE))
exec(src)
fails = 0
def ok(c, m):
    global fails
    print('PASS' if c else 'FAIL', m); fails += 0 if c else 1
def plate(sp): return screen_bits(sp)[WY + 8:WY + 32, 8 + 128:8 + 168].astype(bool)      # its 40 x 24 patch
def msg(sp): return screen_bits(sp)[WY + 33:WY + 46, 8 + 120:8 + 168].astype(bool)
with Racer(headless=True) as sp:
    sp.load_tape(TAP); t = 0
    while g(sp, 'renders') == 0 and t < 60: sp.run(duration=0.1, fast_forward=True); t += 0.1
    want0 = None
    go_green(sp); sp.run(duration=0.3, fast_forward=True)
    ok(sp.read8(SYM['lt_on']) != 0, 'at the green light the lights still hang: no plate yet')
    press(sp, 'Q', False)
    for i in CPUS: sp.write(CARS + i * CS + 19, bytes([0]))
    put(sp, 0, 300, 250, 16); sp.run(duration=3.0, fast_forward=True)
    seen = {}
    for pos in (1, 2, 3, 4, 5):
        for lap in (1, 2, 3):
            sp.write(SYM['position'], bytes([pos])); sp.write(CARS + SYM['c_laps'], bytes([lap])); sp.write(SYM['msg_timer'], bytes([0]))
            at_copy_done(sp); p = plate(sp); seen[(pos, lap)] = p.tobytes()
            if (pos, lap) == (2, 2):
                solid = p[3:22, 4:36]                 # inside the plate: mostly lit, the letters cut out of it
                ok(not p[0].any() and not p[23].any() and not p[:, 0:3].any() and not p[:, 37:40].any() and p[1, 5:35].all() and not p[1, 3:5].any() and 0.55 < solid.mean() < 0.95,
                   '2nd, lap 2: a solid plate 34 x 22 with rounded corners, 3 clear pixels each side and a clear line above and below, its letters cut out (%.0f%% of its inside lit)' % (100 * solid.mean()))
    laps = len({seen[(2, lap)] for lap in (1, 2, 3)}); places = len({seen[(pos, 1)] for pos in (1, 2, 3, 4, 5)})
    ok(laps == 3 and places >= 4, 'the plate changes with the lap (%d of 3 differ) and with the place (%d of 5 differ; the game works your place out afresh as the test writes it)' % (laps, places))
    sp.write(SYM['msg_timer'], bytes([0])); at_copy_done(sp); quiet = msg(sp).copy()
    sp.write(SYM['msg_timer'], bytes([120])); at_copy_done(sp); m = msg(sp)
    ok(m[1, 5:43].all() and not m[0].any() and not m[12].any() and 0.5 < m[3:10, 4:44].mean() < 0.95 and (m != quiet).any(), 'while the strip says FINAL LAP, a second plate under it with the words cut out')
    sp.write(SYM['msg_timer'], bytes([0])); sp.run(duration=0.3, fast_forward=True); at_copy_done(sp)
    ok((msg(sp) == quiet).all(), 'and it goes when the message does')
print('RESULT:', 'PASS' if fails == 0 else '%d FAIL' % fails)
