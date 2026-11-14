"""After a skid your car must end up going the way its PICTURE points (Grant, 14 Nov 2026: "once
the car is facing a direction, after a bit of drift it should stay true to the direction it is
facing"). On open ground (the O's and the off-road switched off in the emulator's memory), at top
speed: turn for a while, let go of the steering with Q held, and watch the angle between the way
the car moves and the way its picture points (one of 16). Prints PASS/FAIL lines and RESULT."""
import os, math
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'drive_test.py')).read()
src = src[:src.index('with Racer(headless=True)')].replace("os.path.dirname(os.path.abspath(__file__))", repr(HERE))
exec(src)
fails = 0
def ok(c, m):
    global fails
    print('PASS' if c else 'FAIL', m); fails += 0 if c else 1
def slip(sp):
    c = car(sp, 0); v = math.hypot(c['vx'], c['vy'])
    if v < 0.05: return 0.0
    return (math.degrees(math.atan2(c['vx'], -c['vy'])) % 360 - (c['ang'] >> 2) * 22.5 + 540) % 360 - 180
with Racer(headless=True) as sp:
    sp.load_tape(TAP); t = 0
    while g(sp, 'renders') == 0 and t < 60: sp.run(duration=0.1, fast_forward=True); t += 0.1
    go_green(sp); press(sp, 'Q', False)
    for i in CPUS: put(sp, i, 20 + 25 * i, 40)
    for n in ('omap', 'surface_map'):
        for i in range(MAPH * 9): sp.write(SYM[n] + i, bytes([0]), ram_page=0)   # no O's, road everywhere
    for key, name in (('P', 'right'), ('O', 'left')):
        for secs in (0.14, 0.3, 0.5):
            put(sp, 0, 60, 230, 16); sp.run(duration=0.3, fast_forward=True)
            press(sp, 'Q', True); sp.run(duration=1.5, fast_forward=True)
            press(sp, key, True); sp.run(duration=secs, fast_forward=True); press(sp, key, False)
            s = []
            for k in range(12):
                sp.run(duration=0.1, fast_forward=True); s.append(slip(sp))
            press(sp, 'Q', False); sp.run(duration=0.8, fast_forward=True)
            settle = next((k + 1 for k in range(12) if all(abs(v) <= 2 for v in s[k:])), None)
            ok(settle is not None and settle <= 6 and sp.read8(CARS + 10) % 4 == 0,
               'a %.2f s turn to the %s: runs true to its picture %s after the steering is let go (slip %s)' % (
                   secs, name, ('%.1f s' % (settle / 10)) if settle else 'NEVER', ' '.join('%d' % round(v) for v in s[:8])))
print('RESULT:', 'PASS' if fails == 0 else '%d FAIL' % fails)
