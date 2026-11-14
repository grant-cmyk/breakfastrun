"""Damage on the real ROM (Grant, 14 Nov 2026): a hit adds a point (once a crash, not once a
touch), damage takes speed off your car, the gauge in the window's corner shows what is left, and
the oil can - put out on the road a while into the race - mends it all and goes away for about a
lap. Prints PASS/FAIL lines and RESULT."""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'drive_test.py')).read()
src = src[:src.index('with Racer(headless=True)')].replace("os.path.dirname(os.path.abspath(__file__))", repr(HERE))
exec(src)
top = open(os.path.join(ROOT, 'src', 'omap.asm')).read()
rows = [l.split('defb')[1] for l in top[top.index('omap_src:'):].splitlines()[1:] if 'defb' in l][:MAPH]
os_ = [(tx, ty) for ty in range(MAPH) for tx in range(MAPW) if [int(c) for b in rows[ty].split(',') for c in b.strip().lstrip('%')][tx]]
w = open(os.path.join(ROOT, 'src', 'world.asm')).read()
CX, CY = (int(re.search(r'NOS_C_%s equ (\d+)' % k, w).group(1)) for k in 'XY')
import sys; sys.path.insert(0, os.path.join(ROOT, 'tools')); import make_damage_icons as mdi
ROWS = mdi.game_rows(); bitsof = lambda v: np.array([(v >> (23 - x)) & 1 for x in range(24)], dtype=bool)
O_ = np.array([bitsof(o) for k, o, f in ROWS]); F_ = np.array([bitsof(f) for k, o, f in ROWS]); CLEAR = ~np.array([bitsof(k) for k, o, f in ROWS]) & ~O_ & ~F_
OUTLINE, FILL = int(O_.sum()), int(F_.sum())            # the gauge's icon, and the clear margin round it
fails = 0
def ok(c, m):
    global fails
    print('PASS' if c else 'FAIL', m); fails += 0 if c else 1
def patch(sp): return screen_bits(sp)[WY + WH - len(ROWS):WY + WH, 8:32].astype(bool)
def gauge(sp): return int((patch(sp) & (O_ | F_)).sum())   # the icon's pixels lit
with Racer(headless=True) as sp:
    sp.load_tape(TAP); t = 0
    while g(sp, 'renders') == 0 and t < 60: sp.run(duration=0.1, fast_forward=True); t += 0.1
    go_green(sp); press(sp, 'Q', False)
    for i in CPUS: put(sp, i, 4 + 40 * i, SY + 58); sp.write(CARS + i * CS + 19, bytes([0]))
    sp.run(duration=0.5, fast_forward=True)
    FULL = gauge(sp)
    ok(sp.read8(SYM['dmg']) == 0 and FULL == OUTLINE + FILL, 'at the start: no damage, the gauge\'s icon full (%d pixels lit: its outline and all its fill)' % FULL)
    tx, ty = os_[40]
    put(sp, 0, tx * 8 - 1, ty * 8 - 6, 16); sp.run(duration=0.15, fast_forward=True)
    d1 = sp.read8(SYM['dmg']); sp.run(duration=0.05, fast_forward=True)
    ok(d1 == 1, 'put on a cereal O: one point of damage (%d)' % d1)
    put(sp, 0, 200, 250, 16); sp.run(duration=1.0, fast_forward=True)
    ok(gauge(sp) < FULL, 'the icon has begun to empty (%d pixels lit)' % gauge(sp))
    for k in range(3):
        put(sp, 0, tx * 8 - 1, ty * 8 - 6, 16); sp.run(duration=0.15, fast_forward=True); put(sp, 0, 200, 250, 16); sp.run(duration=1.0, fast_forward=True)
    ok(sp.read8(SYM['dmg']) == 4, 'three more hits, a second apart: 4 points (%d)' % sp.read8(SYM['dmg']))
    def top_speed(d):
        sp.write(SYM['dmg'], bytes([d]))
        put(sp, 0, 120, SY - 8, 16); press(sp, 'Q', True); sp.run(duration=1.6, fast_forward=True)
        v = car(sp, 0)['vx']; press(sp, 'Q', False); sp.run(duration=0.6, fast_forward=True); return v
    v0, v8 = top_speed(0), top_speed(8)
    ok(1.6 < v0 < 1.9 and 0.80 < v8 / v0 < 0.90, 'top speed whole %.2f px a frame, fully damaged %.2f (%.0f%% of it)' % (v0, v8, 100 * v8 / v0))
    sp.write(SYM['dmg'], bytes([5])); sp.write(SYM['oil_t'], bytes([3])); put(sp, 0, 250, 250, 16); sp.run(duration=1.0, fast_forward=True)
    out = sp.read8(SYM['nos_c_t0']) == SYM['nos_c_v0'] and sp.read8(SYM['nos_c_t1']) == SYM['nos_c_v1']
    ok(out and sp.read8(SYM['dmg']) == 5, 'its time up, the oil can is put out on the road (at %d, %d)' % (CX, CY))
    put(sp, 0, CX - 8, CY - 8, 16); sp.run(duration=0.3, fast_forward=True)
    gone = sp.read8(SYM['nos_c_t0']) == 0 and sp.read8(SYM['nos_c_t1']) == 0
    ok(sp.read8(SYM['dmg']) == 0 and gone and sp.read8(SYM['oil_t']) >= 180, 'driven over: the damage is mended, the can gone, the next in %d pictures (about a lap)' % sp.read8(SYM['oil_t']))
    put(sp, 0, 200, 250, 16); sp.run(duration=0.5, fast_forward=True)
    ok(gauge(sp) == FULL, 'and the icon is full again (%d)' % gauge(sp))
    lit = []
    for d in range(9): sp.write(SYM['dmg'], bytes([d])); sp.run(duration=0.25, fast_forward=True); lit.append(gauge(sp))
    ok(all(a > b for a, b in zip(lit, lit[1:])) and lit[8] == OUTLINE and not (patch(sp) & CLEAR).any(),
       'damage 0 to 8: the icon empties a step at a time (%s pixels lit); fully damaged only its outline is left; the 2 pixels round it are clear' % lit)
    shot(sp, 'damage_gauge.png')
print('RESULT:', 'PASS' if fails == 0 else '%d FAIL' % fails)
