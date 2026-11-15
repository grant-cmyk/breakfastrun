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
EVERY, HAPPY = art('face_art.txt', 'face'), art('face_moods.txt', 'happy'); SAD, EYES = art('face_moods.txt', 'sad'), art('face_moods.txt', 'eyes')
with Racer(headless=True) as sp:
    Spectrum.load_tape(sp, TAP)                         # (the plain loader: the header's holds the jingle off)
    t = 0.0
    while attr(sp, 8, 10) != 0x7A and t < 60: sp.run(duration=0.1, fast_forward=True); t += 0.1
    sp.run(duration=0.5, fast_forward=True)
    press(sp, '1', True); sp.run(duration=0.2, fast_forward=True); press(sp, '1', False)
    sp.run(duration=1.0, fast_forward=True)             # a second into the jingle
    w = screen_bits(sp)[8:160, 8:200]
    ok(g(sp, 'renders') >= 1 and w.sum() > 2000 and sp.read8(SYM['start_go']) == 0 and all(attr(sp, r, c) == 0x78 for r in (17, 18) for c in (7, 16)) and screen_bits(sp)[138:143, 72:136].any(),
       'while the jingle plays the grid is on the screen - the cloth, the cars, the chief\'s PICK 2 UPGRADES - not an empty window (%d pixels of picture)' % w.sum())
    t = 1.0; lit = None; flips = 0; last = None
    while sp.read8(SYM['race_on']) == 0 and t < 12:
        sp.run(duration=0.02, fast_forward=True); t += 0.02
        if lit is None and sp.read8(SYM['start_go']): lit = t
    ok(sp.read8(SYM['race_on']) == 1 and lit is not None and 5.3 < lit < 6.5 and 7.9 < t < 9.5,
       'no key pressed after 1: the jingle plays (48 steps, 5.8 s, two voices and a beat on the speaker), the lights come on by themselves %.1f s in, green at %.1f s' % (lit or 0, t))
    ok(sp.read16(SYM['mu_ptr']) - SYM['mu_tune'] < 4 and sp.read8(0x5C48) == sp.read8(SYM['td'] + 0x5C48 - SYM['td']), 'at green the race tune starts from its first note')
    hold(sp, ['Q'], 1.0)
    order = [4, 1, 0, 3, 2]                               # JANE (white) wins, FRANK (cyan) second, YOU third
    sp.write(SYM['order'], bytes(order)); sp.write(SYM['best_lap'], bytes([1070 & 255, 1070 >> 8])); sp.write(SYM['best_car'], bytes([4]))
    sp.write(SYM['you_laps'], bytes([0x56, 4, 0x2E, 4, 0x6A, 4])); sp.write(SYM['best_lapno'], bytes([2]))    # your laps: 22.2, 21.4, 22.6 s
    sp.write(SYM['race_over'], bytes([1])); sp.run(duration=0.6, fast_forward=True)
    press(sp, 'M', True); sp.run(duration=0.2, fast_forward=True); press(sp, 'M', False); sp.run(duration=1.5, fast_forward=True)
    early = attr(sp, 8, 10) != 0x7A                     # (the jingle again, over the podium: 5.8 s, and a key waits for it)
    sp.run(duration=5.0, fast_forward=True)
    ok(early and attr(sp, 6, 5) == 0x70, 'the jingle plays again as the chequered flag goes up: a key pressed during it does not leave the podium')
    sb = screen_bits(sp).astype(bool)
    A = np.array([[attr(sp, r, c) for c in range(32)] for r in range(24)])
    want = np.full((14, 16), 0x70); want[0] = 0x4F; want[13] = 0x4F
    want[2:9, 6:10] = COLOUR[4]; want[3:9, 2:6] = COLOUR[1]; want[4:9, 10:14] = COLOUR[0]
    ok((A[5:19, 5:21] == want).all(), 'the podium: a yellow card (rows 5-18, columns 5-20), blue head and foot, three steps in the drivers\' own colours - white, cyan, red - with yellow all round them')
    ok((A[5:17, 1:5] == 0x29).all() and (A[5:17, 21:25] == 0x29).all() and (A[19:20, 1:25] != 0x70).all() and (A[1:5, 5:21] != 0x70).all(), 'the cloth round the card keeps its own colours')
    def which(q, name):
        for k, d in (('every', EVERY), ('happy', HAPPY), ('sad', SAD), ('eyes', EYES)):
            if (q == d[name]).all(): return k
        return '?'
    seen = [set(), set(), set()]
    for k in range(30):                                 # the faces move: a step every 32 frames
        f = screen_bits(sp).astype(bool)
        seen[0].add(which(f[56:72, 96:112], 'WHITE')); seen[1].add(which(f[64:80, 64:80], 'CYAN')); seen[2].add(which(f[72:88, 128:144], 'YOU'))
        sp.run(duration=0.16, fast_forward=True)
    ok({'every', 'happy'} <= seen[0] <= {'every', 'eyes', 'happy'}, 'the winner\'s face moves between the everyday one and the HAPPY one (%s)' % ' '.join(sorted(seen[0])))
    ok(all({'every', 'sad'} <= q <= {'every', 'eyes', 'sad'} for q in seen[1:]), 'second and third move between everyday and SAD (%s; %s) - their eyes frames, where drawn, show as their own' % (' '.join(sorted(seen[1])), ' '.join(sorted(seen[2]))))
    sb = screen_bits(sp).astype(bool)
    ok(sb[72:88, 96:112].any() and sb[80:96, 64:80].any() and sb[88:104, 128:144].any() and sb[91:96, 96:112].any() and sb[99:104, 60:84].any() and sb[106:111, 128:144].any(),
       'each step has its place, large, and its driver\'s name in the small letters')
    ok(sb[41:46, 76:132].any() and sb[50:55, 92:116].any() and sb[121:126, 82:126].any() and sb[145:150, 78:130].any() and not sb[112:120, 40:168].any() and not sb[136:144, 40:168].any(),
       'CHEQUERED FLAG, WINNER, a clear row under the podium, FASTEST LAP, a clear row, PRESS ANY KEY')
    clock8 = np.array([[sp.read8(SYM['clock8'] + r) >> (7 - c) & 1 for c in range(8)] for r in range(8)], dtype=bool)
    ok((sb[128:136, 64:72] == clock8).all() and sb[130:135, 74:92].any() and sb[130:135, 98:120].any() and sb[130:135, 130:150].any() and not sb[128:136, 152:168].any(),
       'under FASTEST LAP: the clock icon, the time, whose it was, and LAP with its number')
    ok(all(sb[153 + 8 * i:158 + 8 * i, 209:220].sum() >= 20 and sb[153 + 8 * i:158 + 8 * i, 225:228].any() and sb[153 + 8 * i:158 + 8 * i, 232:247].any() and not sb[153 + 8 * i:158 + 8 * i, 220:225].any() for i in range(3))
       and (sb[153:158, 209:220] == sb[161:166, 209:220]).all() and not sb[168:192, 0:72].any(),
       'YOUR RACE, under the cars: LAP, its number and its time for each of your three laps (rows 19-21), the word whole')
    ok(sb[146:151, 208:256].sum() > 60 and [A[r, 26] for r in (19, 20, 21)] == [0x30, 0x70, 0x30] and (A[20, 26:32] == 0x70).all() and A[17, 26] == 0x4F,
       'FINISHED and your place above them; your best lap (the second, 21.4 s) picked out in bright yellow')
    shot(sp, 'podium.png')
    r0 = g(sp, 'renders'); sp.run(duration=1.0, fast_forward=True)
    ok(g(sp, 'renders') == r0 and attr(sp, 8, 10) != 0x7A, 'the race stays stopped under it, until a key')
    press(sp, 'M', True); sp.run(duration=0.2, fast_forward=True); press(sp, 'M', False); sp.run(duration=4.0, fast_forward=True)
    ok(attr(sp, 8, 10) == 0x7A and screen_text(sp, 8, 10, 12) == "TODAY'S MENU", 'any key (M): back to the title screen')
    # a second race, straight from that title (Grant's screenshots, 15 Nov 2026: the podium's colours and the
    # title's own picture were left in the window)
    sp.run(duration=1.0, fast_forward=True)
    press(sp, '1', True); sp.run(duration=0.2, fast_forward=True); press(sp, '1', False); sp.run(duration=1.5, fast_forward=True)
    A = np.array([[attr(sp, r, c) for c in range(32)] for r in range(24)]); w = screen_bits(sp).astype(bool)[8:160, 8:200]
    cars_ink = w[60:110, 20:140].sum()
    ok((A[4:17, 1:25] == 0x29).all() and (A[17:20, 4:7] == 0x29).all() and (A[17:20, 17:22] == 0x29).all(),
       'the second race: every cell of the window is the cloth\'s blue on cyan again - nothing of the podium\'s colours')
    ok(not w[36:44, 60:150].all(axis=1).any() and cars_ink > 150 and screen_text(sp, 8, 10, 12) != "TODAY'S MENU",
       'and it shows the grid while the jingle plays - not what the title left there (%d pixels of cars)' % cars_ink)
print('RESULT:', 'PASS' if fails == 0 else '%d FAIL' % fails)
