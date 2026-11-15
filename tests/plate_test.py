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
def plate(sp): return screen_bits(sp)[WY + 2:WY + 20, 8 + WW - 40:8 + WW].astype(bool)      # its 40 x 18 patch
def msg(sp): return screen_bits(sp)[WY + 21:WY + 34, 8 + WW - 48:8 + WW].astype(bool)
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
                solid = p[2:16, 5:34]                 # inside the plate: mostly lit, the letters cut out of it
                ok(not p[0].any() and not p[17].any() and not p[:, 0:5].any() and not p[:, 34:40].any() and p[2, 5:34].all() and p[1, 6:33].all() and not p[1, 5] and 0.55 < solid.mean() < 0.95,
                   'P2, lap 2: a solid plate 29 x 16 with rounded corners in the top right corner, clear table round it, its small letters cut out (%.0f%% of its inside lit)' % (100 * solid.mean()))
    laps = len({seen[(2, lap)] for lap in (1, 2, 3)}); places = len({seen[(pos, 1)] for pos in (1, 2, 3, 4, 5)})
    ok(laps == 3 and places >= 4, 'the plate changes with the lap (%d of 3 differ) and with the place (%d of 5 differ; the game works your place out afresh as the test writes it)' % (laps, places))
    # (FINAL LAP! is the crew chief's bubble at the foot of the window since 15 Nov 2026: tests/crew_test.py)
print('RESULT:', 'PASS' if fails == 0 else '%d FAIL' % fails)
