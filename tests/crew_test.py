"""The crew chief's messages (Grant, 15 Nov 2026): a small face and a speech bubble INSIDE the play
window, at its foot - "the pitstop messages were not visible as the player is focused on the game
area". PICK 2 UPGRADES under the lights, GOOD LUCK at green, GREAT LAP! with its time, FINAL LAP!,
a word when you hit a cereal O; each up for about 3 seconds. Prints PASS/FAIL lines and RESULT."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'drive_test.py')).read()
src = src[:src.index('with Racer(headless=True)')].replace("os.path.dirname(os.path.abspath(__file__))", repr(HERE))
exec(src)
fails = 0
def ok(c, m):
    global fails
    print('PASS' if c else 'FAIL', m); fails += 0 if c else 1
attr = lambda sp, r, c: sp.read8(0x5800 + r * 32 + c)
def bubble(sp):                                    # (is it up, the ink in its two lines, the face's ink)
    sb = screen_bits(sp).astype(bool); up = all(attr(sp, r, c) == 0x78 for r in (17, 18) for c in range(7, 17))
    return up, int(sb[138:143, 72:136].sum()), int(sb[145:150, 72:136].sum()), int(sb[136:152, 56:72].sum())
def words(sp): return sp.read8(SYM['ms_id'] + 1)
with Racer(headless=True) as sp:
    sp.load_tape(TAP); t = 0
    while g(sp, 'renders') == 0 and t < 60: sp.run(duration=0.1, fast_forward=True); t += 0.1
    sp.run(duration=0.6, fast_forward=True); at_copy_done(sp)
    up, l1, l2, face = bubble(sp)
    ok(up and words(sp) == SYM['m_setup'] and l1 > 60 and l2 > 30 and face > 60, 'on the grid: the chief and his bubble at the foot of the window - PICK 2 UPGRADES / KEYS 1 2 3 (%d and %d pixels of letters, %d of face)' % (l1, l2, face))
    ok(not screen_bits(sp)[176:192, 128:208].any() or all(attr(sp, r, c) == 0x36 for r in (22, 23) for c in range(16, 26)), 'the bubble\'s picture is kept under the window where it cannot be seen: yellow on yellow')
    sp.run(duration=4.0, fast_forward=True)
    ok(not bubble(sp)[0] and all(attr(sp, r, c) == 0x29 for r in (17, 18) for c in range(7, 17)), 'after 3 seconds it goes: those cells the cloth\'s colours again')
    go_green(sp); press(sp, 'Q', False)
    for i in CPUS: put(sp, i, 4 + 40 * i, SY + 58); sp.write(CARS + i * CS + 19, bytes([0]))
    sp.run(duration=0.4, fast_forward=True); at_copy_done(sp)
    ok(bubble(sp)[0] and words(sp) == SYM['m_luck'], 'at green: GOOD LUCK!')
    sp.run(duration=6.0, fast_forward=True)
    sp.write(SYM['best_lap'], bytes([1070 & 255, 1070 >> 8])); sp.write(SYM['best_car'], bytes([0])); sp.write(SYM['best_seq'], bytes([sp.read8(SYM['best_seq']) + 1]))
    sp.run(duration=0.5, fast_forward=True); at_copy_done(sp)
    up, l1, l2, face = bubble(sp)
    ok(up and words(sp) == SYM['m_best'] and l1 > 40 and 15 < l2 < 60, 'your lap the best yet: GREAT LAP! with its time under it (%d pixels: 21.4)' % l2)
    sp.run(duration=6.0, fast_forward=True)
    sp.write(CARS + 25, bytes([3])); sp.run(duration=0.5, fast_forward=True); at_copy_done(sp)
    ok(bubble(sp)[0] and words(sp) == SYM['m_last'], 'starting the last lap: FINAL LAP! / BRING IT HOME')
    sp.run(duration=1.0, fast_forward=True)
    ok(bubble(sp)[0] and words(sp) == SYM['m_last'], 'and it is not pushed aside by another message a second later')
    # the other drivers
    sp.run(duration=5.0, fast_forward=True)
    sp.write(SYM['best_lap'], bytes([1000 & 255, 1000 >> 8])); sp.write(SYM['best_car'], bytes([1])); sp.write(SYM['best_seq'], bytes([sp.read8(SYM['best_seq']) + 1]))
    sp.run(duration=0.5, fast_forward=True); at_copy_done(sp)
    up, l1, l2, face = bubble(sp)
    ok(up and words(sp) == SYM['m_fast'] and sp.read8(SYM['ms_car']) == 1 and l1 > 60 and l2 > 25, 'another driver sets the best lap: FASTEST LAP BY / FRANK (%d pixels of name)' % l2)
    seen = set(); t = 0.0
    while t < 150 and not seen:
        sp.run(duration=0.5, fast_forward=True); t += 0.5
        if SYM['m_oth0'] <= words(sp) <= SYM['m_oth0'] + 3 and bubble(sp)[0]: seen.add((words(sp) - SYM['m_oth0'], sp.read8(SYM['ms_car'])))
    ok(bool(seen) and all(1 <= c <= 4 for _, c in seen), 'now and then, with nothing else to say, a remark about one of the other four by name (%.0f s in: remark %s)' % (t, sorted(seen)))
print('RESULT:', 'PASS' if fails == 0 else '%d FAIL' % fails)
