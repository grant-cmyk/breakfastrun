"""The cereal O's are solid on the real ROM: your car put on an O bounces off it (the
quick 4-tile test in o_check must never miss one), and a car on clear cloth does not.
Prints PASS/FAIL lines and RESULT."""
import os, re, random
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'drive_test.py')).read()
src = src[:src.index('with Racer(headless=True)')].replace("os.path.dirname(os.path.abspath(__file__))", repr(HERE))
exec(src)
top = open(os.path.join(ROOT, 'src', 'topdata.asm')).read()
rows = [l.split('defb')[1] for l in top[top.index('omap_src:'):].splitlines()[1:] if 'defb' in l][:MAPH]
obits = [[int(c) for b in r.split(',') for c in b.strip().lstrip('%')] for r in rows]
os_ = [(tx, ty) for ty in range(MAPH) for tx in range(MAPW) if obits[ty][tx]]
random.seed(3); pick = random.sample(os_, 30)
fails = 0
def ok(c, m):
    global fails
    print('PASS' if c else 'FAIL', m); fails += 0 if c else 1
with Racer(headless=True) as sp:
    sp.load_tape(TAP); t = 0
    while g(sp, 'renders') == 0 and t < 60: sp.run(duration=0.1, fast_forward=True); t += 0.1
    go_green(sp); press(sp, 'Q', False)
    for i in CPUS: put(sp, i, 4 + 40 * i, SY + 58)
    missed = []
    def bounces(tx, ty):
        sp.write(SYM['snd_bump'], bytes([0]))
        put(sp, 0, tx * 8 + 4 - 8 + 3, ty * 8 + 4 - 8 - 2, 16)       # its middle 3 px right, 2 up of the O's
        for k in range(8):                                            # (a frame at a time: the crunch is
            sp.run(duration=0.02, fast_forward=True)                  # set on the next game tick, and fades
            if sp.read8(SYM['snd_bump']): return True                 # a picture at a time)
        return False
    for tx, ty in pick:
        # (the test writes the car's place while the game runs: now and then the game is
        # half-way through moving the car and puts it back. A real miss is a matter of
        # where the car is, so it would miss again: try twice before calling it one)
        if not bounces(tx, ty) and not bounces(tx, ty): missed.append((tx, ty))
    ok(not missed, 'your car bounces off every O it is put on (%d of %d; missed %s)' % (len(pick) - len(missed), len(pick), missed[:5]))
    clear = []                                                        # clear cloth: no bounce
    for tx, ty in [(2, 2), (10, 3), (36, 30), (60, 4), (5, 60)]:
        if any(obits[ty + j][tx + i] for j in (-1, 0, 1, 2) for i in (-1, 0, 1, 2) if 0 <= ty + j < MAPH and 0 <= tx + i < MAPW): continue
        sp.write(SYM['snd_bump'], bytes([0])); put(sp, 0, tx * 8 - 4, ty * 8 - 4, 16); sp.run(duration=0.08, fast_forward=True)
        if sp.read8(SYM['snd_bump']): clear.append((tx, ty))
    ok(not clear, 'and not off clear cloth (%s)' % clear)
print('RESULT:', 'PASS' if fails == 0 else '%d FAIL' % fails)
