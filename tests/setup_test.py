"""Your car's set-up on the real ROM (Grant, 13 Nov 2026): three parts - GRIP, SPEED, ACCEL - at
levels 1..5; every car starts at 1, 1, 1 and you have 2 points to add before the start with keys
1, 2, 3 (0 takes them back). Checks the keys and what each part does to the car (the set-up is
not shown on the race screen - Grant, 14 Nov 2026):
the top speed, the frames to reach 1.5 px a frame from rest, and the tyres' grip.
Prints PASS/FAIL lines and RESULT."""
import os, math
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'drive_test.py')).read()
src = src[:src.index('with Racer(headless=True)')].replace("os.path.dirname(os.path.abspath(__file__))", repr(HERE))
exec(src)
fails = 0
def ok(c, m):
    global fails
    print('PASS' if c else 'FAIL', m); fails += 0 if c else 1
LV = SYM['su_lv']
def tap(sp, k):
    press(sp, k, True); sp.run(duration=0.2, fast_forward=True); press(sp, k, False); sp.run(duration=0.2, fast_forward=True)
def pips(sp, part):                      # filled pips shown for a part (0 GRIP, 1 SPEED, 2 ACCEL)
    sb = screen_bits(sp)
    return sum(1 for j in range(5) if sb[23 * 8 + 3, (8 * part + 2 + j) * 8 + 3])
def run_setup(keys):
    """A fresh game, the keys pressed before the start; returns what was measured."""
    with Racer(headless=True) as sp:
        sp.load_tape(TAP); t = 0
        while g(sp, 'renders') == 0 and t < 60: sp.run(duration=0.1, fast_forward=True); t += 0.1
        sp.run(duration=0.5, fast_forward=True)
        r = {'row0': screen_text(sp, 23, 0, 2) + screen_text(sp, 23, 8, 2) + screen_text(sp, 23, 16, 2)}
        for k in keys: tap(sp, k)
        r['lv'] = list(sp.read(LV, 4)); r['pips'] = [pips(sp, i) for i in range(3)]
        go_green(sp); press(sp, 'Q', False)
        sp.run(duration=0.3, fast_forward=True)
        r['row1'] = screen_text(sp, 23, 0, 2) + screen_text(sp, 23, 8, 2) + screen_text(sp, 23, 16, 2)
        for i in CPUS: put(sp, i, 20 + 25 * i, SY + 58)       # the computer cars out of the way
        put(sp, 0, 60, SY - 8, 16)                            # the bottom straight's left end, facing right
        sp.run(duration=0.3, fast_forward=True)
        press(sp, 'Q', True); n = 0; r['t15'] = None; vmax = 0
        while n < 150:                                        # 3 s of Q: the frames to 1.5, the top speed
            sp.run(duration=0.02, fast_forward=True); n += 1
            v = car(sp, 0)['vx']; vmax = max(vmax, v)
            if r['t15'] is None and v >= 1.5: r['t15'] = n
        r['top'] = vmax
        press(sp, 'P', True); sp.run(duration=0.3, fast_forward=True); press(sp, 'P', False)   # a hard turn at speed,
        n = 0                                                 # then the frames until the tyres grip again
        while sp.read8(SYM['yg_sl']) and n < 60: sp.run(duration=0.02, fast_forward=True); n += 1
        press(sp, 'Q', False)
        r['slide'] = n
        r['grip'] = list(sp.read(SYM['yg_gtab'], 4))
        return r
base = run_setup([]); print('1,1,1:', base)
ok(base['lv'] == [1, 1, 1, 2], 'every part starts at level 1, with 2 points to spend (%s)' % base['lv'])
ok(1.70 <= base['top'] <= 1.76, 'at 1, 1, 1 the top speed is 1.75 px a frame, as before (%.2f)' % base['top'])
spd = run_setup(['2', '2']); print('speed +2:', spd)
ok(spd['lv'] == [1, 3, 1, 0], 'key 2 twice: SPEED at level 3 (%s)' % spd['lv'])
ok(1.92 <= spd['top'] <= 1.98, 'SPEED 3: the top speed is 1.97 px a frame (%.2f)' % spd['top'])
acc = run_setup(['3', '3']); print('accel +2:', acc)
ok(acc['lv'] == [1, 1, 3, 0] and abs(acc['top'] - base['top']) < 0.02, 'key 3 twice: ACCEL at level 3, the top speed unchanged (%.2f)' % acc['top'])
ok(acc['t15'] is not None and base['t15'] is not None and acc['t15'] <= base['t15'] - 4, 'ACCEL 3: 1.5 px a frame comes sooner (%s frames, against %s)' % (acc['t15'], base['t15']))
grp = run_setup(['1', '1']); print('grip +2:', grp)
ok(grp['lv'] == [3, 1, 1, 0] and grp['grip'] == [25, 14, 14, 9] and base['grip'] == [16, 8, 8, 5],
   'key 1 twice: GRIP at level 3 - the tyres hold 29/256 px a frame of sideways speed (22 at level 1): %s' % grp['grip'])
mix = run_setup(['1', '2', '3', '0', '3', '1', '2']); print('mixed, 0 in the middle:', mix)
ok(mix['lv'] == [2, 1, 2, 0], 'a third key does nothing; 0 takes the points back to spend again (%s)' % mix['lv'])
print('RESULT:', 'PASS' if fails == 0 else '%d FAIL' % fails)
