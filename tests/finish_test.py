"""The race's start and end (Grant, 15 Nov 2026): after 1 at the title a ditty plays and the lights
come on by themselves; when the race is over the podium is shown in the window - a yellow card,
the first three on steps of their own colours with their names, the winner's happy face twice the
size, the fastest lap - and any key goes back to the title. Prints PASS/FAIL lines and RESULT."""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'drive_test.py')).read()
src = src[:src.index('with Racer(headless=True)')].replace("os.path.dirname(os.path.abspath(__file__))", repr(HERE))
exec(src)
fails = 0
def ok(c, m):
    global fails
    print('PASS' if c else 'FAIL', m); fails += 0 if c else 1
attr = lambda sp, r, c: sp.read8(0x5800 + r * 32 + c)
def art(path, kind):
    t = open(os.path.join(ROOT, 'tools', path)).read()
    return {m.group(1): np.array([[ch == 'X' for ch in r] for r in m.group(2).split()]) for m in re.finditer(r'== (\w+) %s ==\n((?:[X.]{16}\n){16})' % kind, t)}
CAR = ['YOU', 'CYAN', 'GREEN', 'PINK', 'WHITE']; COLOUR = [0x57, 0x68, 0x60, 0x58, 0x78]
EVERY, HAPPY = art('face_art.txt', 'face'), art('face_moods.txt', 'happy')
with Racer(headless=True) as sp:
    sp.load_tape(TAP)
    sp.write(SYM['jin_on'], bytes([1]))                 # (the header holds the ditty off for the other tests: on again, as after 1)
    t = 0.0; notes = set(); lit = None
    while sp.read8(SYM['race_on']) == 0 and t < 12:
        sp.run(duration=0.02, fast_forward=True); t += 0.02
        if sp.read8(SYM['jin_on']) == 1: notes.add(sp.read16(SYM['mu_ptr']))
        if lit is None and sp.read8(SYM['start_go']): lit = t
    ok(sp.read8(SYM['race_on']) == 1 and lit is not None and 2.0 < lit < 3.2 and 4.6 < t < 6.2 and len(notes) >= 15,
       'no key pressed: the ditty plays (%d of its steps seen), the lights come on by themselves %.1f s in, green at %.1f s' % (len(notes), lit or 0, t))
    ok(sp.read16(SYM['mu_ptr']) - SYM['mu_tune'] < 4, 'at green the race tune starts from its first note')
    hold(sp, ['Q'], 1.0)
    order = [4, 1, 0, 3, 2]                               # JANE (white) wins, FRANK (cyan) second, YOU third
    sp.write(SYM['order'], bytes(order)); sp.write(SYM['best_lap'], bytes([1070 & 255, 1070 >> 8])); sp.write(SYM['best_car'], bytes([4]))
    sp.write(SYM['race_over'], bytes([1])); sp.run(duration=0.6, fast_forward=True)
    sb = screen_bits(sp).astype(bool)
    A = np.array([[attr(sp, r, c) for c in range(32)] for r in range(24)])
    want = np.full((11, 16), 0x70); want[0] = 0x4F; want[10] = 0x4F
    want[2:9, 6:10] = COLOUR[4]; want[3:9, 2:6] = COLOUR[1]; want[4:9, 10:14] = COLOUR[0]
    ok((A[5:16, 5:21] == want).all(), 'the podium: a yellow card (rows 5-15, columns 5-20), blue head and foot, three steps in the drivers\' own colours - white, cyan, red - with yellow all round them')
    ok((A[5:17, 1:5] == 0x29).all() and (A[5:17, 21:25] == 0x29).all() and (A[16:20, 1:25] != 0x70).all() and (A[1:5, 5:21] != 0x70).all(), 'the cloth round the card keeps its own colours')
    ok((sb[56:72, 96:112] == HAPPY['WHITE']).all(), 'the winner\'s face is the HAPPY one, the same size as the others, on the top step')
    ok((sb[64:80, 64:80] == EVERY['CYAN']).all() and (sb[72:88, 128:144] == EVERY['GREEN' if False else 'YOU']).all(), 'second and third have their everyday faces')
    ok(sb[72:88, 96:112].any() and sb[80:96, 64:80].any() and sb[88:104, 128:144].any() and sb[91:96, 96:112].any() and sb[99:104, 60:84].any() and sb[106:111, 128:144].any(),
       'each step has its place, large, and its driver\'s name in the small letters')
    ok(sb[41:46, 76:132].any() and sb[50:55, 92:116].any() and sb[114:119, 46:90].any() and sb[114:119, 96:136].any() and sb[121:126, 78:130].any(),
       'CHEQUERED FLAG, WINNER, FASTEST LAP with a name and a time, PRESS ANY KEY')
    shot(sp, 'podium.png')
    r0 = g(sp, 'renders'); sp.run(duration=1.0, fast_forward=True)
    ok(g(sp, 'renders') == r0 and attr(sp, 8, 10) != 0x7A, 'the race stays stopped under it, until a key')
    press(sp, 'M', True); sp.run(duration=0.2, fast_forward=True); press(sp, 'M', False); sp.run(duration=4.0, fast_forward=True)
    ok(attr(sp, 8, 10) == 0x7A and screen_text(sp, 8, 10, 12) == "TODAY'S MENU", 'any key (M): back to the title screen')
print('RESULT:', 'PASS' if fails == 0 else '%d FAIL' % fails)
