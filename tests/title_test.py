"""The title / attract screen on the real ROM (Grant, 14 Nov 2026: "want the person to see they
choose 1UP or 2UP to play, K to customize keys, have the title screen have some kind of attract
sequence showing the different drivers, maybe a face and have that car skid around").
src/title.asm, title2.asm, title3.asm; layout A of docs/design/TITLE-SCREEN.md. Checks:
  - the title comes up after loading, before the race: logo twice the size, LAP RECORD, the cloth
    stage in its frame, a driver's card, 1 = 1UP, 2 = 2UP, K = KEYS, the flashing prompt
  - the attract sequence: the car moves, only on the cloth, leaves skid marks; all five drivers
    take their turn (number, name, face colour change)
  - 2 says 2UP COMING SOON and the prompt comes back
  - K: the five keys are asked for in turn, a key in use or a set-up key is refused; the car then
    answers to the new keys in the race and not to the old ones; the race screen names the new key
  - 1 starts the race as before (Q, the lights, green); the set-up keys 1 2 3 still work and the
    1 that left the title did not spend a point
  - after a race the accelerate key goes back to the title (with the lap record), and 1 gives a
    whole race screen again
Prints PASS/FAIL lines and RESULT."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'drive_test.py')).read()
src = src[:src.index('with Racer(headless=True)')].replace("os.path.dirname(os.path.abspath(__file__))", repr(HERE))
exec(src)
fails = 0
def ok(c, m):
    global fails
    print('PASS' if c else 'FAIL', m); fails += 0 if c else 1
PROMPT = 0x5800 + 23 * 32 + 5                        # the flashing PRESS 1 OR 2 TO START
TDV = lambda name: SYM['td'] + SYM[name + '_src'] - SYM['td_src']   # a table copied out of the program (title3.asm)
def attr(sp, r, c): return sp.read8(0x5800 + r * 32 + c)
def title_up(sp, limit=60.0):                        # run until the title is showing; the seconds it took
    t = 0.0
    while not (sp.read8(PROMPT) == 0xB0 and screen_text(sp, 23, 5, 5) == 'PRESS') and t < limit:
        sp.run(duration=0.1, fast_forward=True); t += 0.1
    return t
def tap(sp, k, down=0.2, after=0.4):
    press(sp, k, True); sp.run(duration=down, fast_forward=True); press(sp, k, False); sp.run(duration=after, fast_forward=True)
def load(sp):                                        # (the plain loader: Racer.load_tape goes on past the title)
    Spectrum.load_tape(sp, TAP)
    return title_up(sp)
STAGE = (slice(40, 136), slice(16, 128))             # the cloth: 112 x 96 pixels at (16, 40)
def cloth_clean():                                   # 32-pixel checks, the dark ones dotted
    v, u = np.mgrid[0:96, 0:112]
    return ((((u >> 5) + (v >> 5)) & 1) == 1) & (((v & 3) == 0) & ((u & 3) == 2) | ((v & 3) == 2) & ((u & 3) == 0))
LOGO = np.array([[c == '#' for c in l.strip()] for l in open(os.path.join(ROOT, 'build', 'logo.txt'))], dtype=np.uint8)

# ---------------------------------------------------------------- 1: the title, and the attract sequence
with Racer(headless=True) as sp:
    t = load(sp)
    ok(t < 60 and g(sp, 'renders') == 0, 'the title screen comes up after loading, before any race picture (%.1f s after the tape)' % t)
    sp.run(duration=0.5, fast_forward=True)
    sb = screen_bits(sp)
    ok((sb[0:32, 8:120] == np.kron(LOGO, np.ones((2, 2), dtype=np.uint8))).all() and attr(sp, 2, 1) == 0x72 and attr(sp, 3, 14) == 0x77,
       'the logo twice its size, top left: RUN red, the egg white')
    ok(screen_text(sp, 0, 19, 10) == 'LAP RECORD' and attr(sp, 0, 17) == 0x4F and sb[8:24, 144:240].any(),
       'LAP RECORD top right, a big line under it (no record yet: -:--.-)')
    ok(all(attr(sp, r, c) == 0x29 for r in range(5, 17) for c in range(2, 16)) and attr(sp, 4, 1) == 0x31 and attr(sp, 17, 16) == 0x31
       and sb[35, 13:131].all() and sb[36, 12:132].all() and sb[139, 12:132].all() and sb[140, 13:131].all() and sb[37:139, 11:13].all() and sb[37:139, 131:133].all()
       and not sb[37:40, 13:131].any() and not sb[136:139, 13:131].any(),
       'the stage: 14 x 12 cells of blue-on-cyan cloth in a slim blue frame')
    ok(screen_text(sp, 5, 18, 13) == 'DRIVER 1 OF 5' and attr(sp, 5, 18) == 0x4F and attr(sp, 16, 30) == 0x78 and screen_text(sp, 7, 23, 3) == 'YOU'
       and attr(sp, 6, 18) == 0x57 and sb[48:80, 144:176].any() and sb[104:136, 176:208].any(),
       'the driver\'s card: DRIVER 1 OF 5, a face on the car\'s colour, YOU, the car')
    ok(sb[152:168, 8:24].any() and attr(sp, 19, 1) == 0x47 and attr(sp, 19, 3) == 0x57 and screen_text(sp, 21, 1, 8) == '1 PLAYER'
       and attr(sp, 19, 11) == 0x47 and attr(sp, 19, 13) == 0x4F and screen_text(sp, 21, 11, 9) == '2 PLAYERS'
       and attr(sp, 19, 21) == 0x47 and attr(sp, 19, 23) == 0x78 and screen_text(sp, 21, 23, 8) == 'REDEFINE',
       'the choices, each with its key as a key cap: 1 1UP (red), 2 2UP (blue), K KEYS')
    ok(screen_text(sp, 23, 5, 21) == 'PRESS 1 OR 2 TO START' and all(attr(sp, 23, c) == 0xB0 for c in range(5, 26)),
       'PRESS 1 OR 2 TO START, flashing')
    # the attract sequence: 45 s, sampled 10 times a second
    off0 = sb.copy(); off0[STAGE] = 0; off0[40:136, 144:248] = 0          # everything but the cloth and the card
    seen = {}; spots = set(); leaks = 0; clean = cloth_clean(); clash = 0; most = 0
    for i in range(450):
        sp.run(duration=0.1, fast_forward=True)
        sb = screen_bits(sp)
        d = screen_text(sp, 5, 25, 1)
        if d in '12345': seen[d] = (screen_text(sp, 7, 23, 5).strip(), attr(sp, 6, 18))     # (as last seen: the card is redrawn bit by bit)
        spots.add((sp.read8(SYM['a_x'] + 1), sp.read8(SYM['a_y'] + 1)))
        o = sb.copy(); o[STAGE] = 0; o[40:136, 144:248] = 0
        leaks += int((o != off0).sum())
        extra = (sb[STAGE] != clean); most = max(most, int(extra.sum()))
        clash += sum(1 for r in range(5, 17) if bytes(sp.read(0x5800 + r * 32 + 2, 14)) != bytes([0x29]) * 14)
    ok(len(spots) > 300, 'the car on the stage moves (%d different places in 45 s)' % len(spots))
    ok(leaks == 0, 'nothing is drawn outside the cloth and the card while it runs (%d pixels changed)' % leaks)
    ok(most > 150, 'the car leaves skid marks on the cloth (up to %d pixels on it besides the checks)' % most)
    ok(clash == 0, 'the cloth stays blue on cyan all the while: no colour clash')
    names = [seen.get(d, ('', 0))[0] for d in '12345']
    ok(len(seen) == 5 and names == ['YOU', 'CYAN', 'GREEN', 'PINK', 'SLIM'] and [seen[d][1] for d in '12345'] == [0x57, 0x68, 0x60, 0x58, 0x78],
       'all five drivers take their turn, each with its name and colour (%s)' % ' '.join(names))
    ok(g(sp, 'renders') == 0 and sp.read8(SYM['race_on']) == 0, 'no race runs behind the title')
    # 2: not built yet
    title_up(sp)
    tap(sp, '2', 0.2, 0.3)
    soon = screen_text(sp, 23, 5, 21)
    sp.run(duration=2.5, fast_forward=True)
    ok(soon.strip() == '2UP COMING SOON' and screen_text(sp, 23, 5, 21) == 'PRESS 1 OR 2 TO START' and g(sp, 'renders') == 0,
       '2 says 2UP COMING SOON, then the prompt again (%r)' % soon.strip())

    # ---------------------------------------------------------------- 2: K - the keys
    tap(sp, 'K', 0.2, 0.5)
    rows = [screen_text(sp, 6 + 2 * i, 10, 10).strip() for i in range(5)]
    caps = ''.join(screen_text(sp, 6 + 2 * i, 21, 1) for i in range(5))
    ok(rows == ['LEFT', 'RIGHT', 'ACCELERATE', 'BRAKE', 'NOS'] and caps == 'OPQAS' and screen_text(sp, 14, 21, 2) == 'SP'
       and screen_text(sp, 17, 7, 17) == 'PRESS THE KEY FOR' and attr(sp, 6, 10) == 0x70 and attr(sp, 6, 21) == 0xC7 and attr(sp, 8, 10) == 0x78,
       'K: the keys screen - the five keys with today\'s (O P Q A SPACE), the first row lit, its cap flashing')
    tap(sp, '1'); tap(sp, 'ENTER'); tap(sp, 'CAPS SHIFT' if 'CAPS SHIFT' in zs.KEYS else 'CS')
    ok(sp.read8(SYM['k_i']) == 0, 'a set-up key (1), ENTER and a shift are refused')
    tap(sp, 'Z')
    ok(sp.read8(SYM['k_i']) == 1 and screen_text(sp, 6, 21, 1) == 'Z' and attr(sp, 8, 10) == 0x70, 'Z for LEFT: taken, shown, and RIGHT is asked for')
    tap(sp, 'Z')
    ok(sp.read8(SYM['k_i']) == 1, 'Z again for RIGHT: refused (in use)')
    tap(sp, 'X')
    tap(sp, 'SPACE')
    ok(sp.read8(SYM['k_i']) == 2, 'SPACE to accelerate: refused (the race screen has to name the key)')
    tap(sp, 'L'); tap(sp, 'M'); tap(sp, 'N', 0.2, 1.0)
    ok(title_up(sp, 5.0) < 5.0 and bytes(sp.read(TDV('key_ch'), 5)) == b'ZXLMN', 'after the fifth key: back to the title (keys %r)' % bytes(sp.read(TDV('key_ch'), 5)))
    tap(sp, '1', 0.2, 2.0)
    ok(g(sp, 'renders') > 0 and frame_ok(sp) and screen_text(sp, 22, 1, 9) == ' PRESS L ', '1: the race screen, whole, and its strip says PRESS L')
    hold(sp, ['Q'], 1.0); hold(sp, ['O', 'P', 'A'], 0.5)
    ok(sp.read8(SYM['start_go']) == 0 and sp.read8(SYM['cars'] + 11) == 0, 'the old keys (Q O P A) do nothing now')
    press(sp, 'L', True); t = 0.0
    while sp.read8(SYM['race_on']) == 0 and t < 4.0: sp.run(duration=0.02, fast_forward=True); t += 0.02
    sp.run(duration=1.0, fast_forward=True)
    c = car(sp, 0)
    ok(t < 4.0 and c['vx'] > 1.0, 'L: the lights, green after %.1f s, and the car pulls away (%.2f px a frame)' % (t, c['vx']))
    a0 = c['ang']; press(sp, 'Z', True); sp.run(duration=0.3, fast_forward=True); press(sp, 'Z', False); a1 = car(sp, 0)['ang']
    press(sp, 'X', True); sp.run(duration=0.6, fast_forward=True); press(sp, 'X', False); a2 = car(sp, 0)['ang']
    ok(((a0 - a1) & 63) in range(1, 32) and ((a2 - a1) & 63) in range(1, 32), 'Z steers left, X right (heading %d, %d, %d)' % (a0, a1, a2))
    inv0 = list(sp.read(SYM['inv'], 3)); press(sp, 'SPACE', True); sp.run(duration=0.2, fast_forward=True); press(sp, 'SPACE', False)
    b0 = sp.read8(SYM['boost_t']); press(sp, 'N', True); sp.run(duration=0.2, fast_forward=True); press(sp, 'N', False)
    ok(inv0 == [1, 0, 0] and b0 == 0 and sp.read8(SYM['boost_t']) > 0 and list(sp.read(SYM['inv'], 3)) == [0, 0, 0], 'N fires the NOS; SPACE no longer does')
    press(sp, 'L', False); sp.run(duration=1.5, fast_forward=True); v0 = abs(car(sp, 0)['vx']) + abs(car(sp, 0)['vy'])
    press(sp, 'M', True); sp.run(duration=0.4, fast_forward=True); press(sp, 'M', False)
    ok(sp.read8(SYM['cars'] + 11) & 8 or abs(car(sp, 0)['vx']) + abs(car(sp, 0)['vy']) < v0, 'M brakes')

# ---------------------------------------------------------------- 3: 1 = the race as before; after it, the title again
with Racer(headless=True) as sp:
    load(sp)
    tap(sp, '1', 0.3, 2.0)
    ok(g(sp, 'renders') > 0 and frame_ok(sp) and screen_text(sp, 22, 1, 9) == ' PRESS Q ' and car(sp, 0)['vx'] == 0,
       '1 at the title: the race screen, your car on the grid, PRESS Q')
    scr0 = screen_bits(sp)
    ok(list(sp.read(SYM['su_lv'], 4)) == [1, 1, 1, 2], 'the 1 that left the title did not spend a set-up point (%s)' % list(sp.read(SYM['su_lv'], 4)))
    tap(sp, '1', 0.2, 0.3); tap(sp, '3', 0.2, 0.3)
    ok(list(sp.read(SYM['su_lv'], 4)) == [2, 1, 2, 0], 'the set-up keys still work before the start: 1 and 3 give GRIP 2, ACCEL 2 (%s)' % list(sp.read(SYM['su_lv'], 4)))
    t = go_green(sp)
    sp.run(duration=1.0, fast_forward=True); press(sp, 'Q', False)
    ok(t < 4.0 and car(sp, 0)['vx'] > 1.0, 'Q: the lights, green after %.1f s, and away' % t)
    # the end of a race, by hand (drive_test.py drives a whole race to the flag and through the title):
    sp.write(SYM['rec_lap'], bytes([0x2A, 0x03]))                 # a lap record of 810 frames: 16.2 s
    sp.write(SYM['race_over'], bytes([1]))
    sp.run(duration=1.0, fast_forward=True)
    ok(screen_text(sp, 12, 8, 7) == 'PRESS Q' and sp.read8(PROMPT) != 0xB0, 'the race over: the box says PRESS Q')
    tap(sp, 'Q', 0.2, 1.5)
    ok(sp.read8(PROMPT) == 0xB0 and screen_text(sp, 23, 5, 21) == 'PRESS 1 OR 2 TO START' and sp.read8(SYM['snd_rate']) == 0,
       'Q after the race: the title screen again, the engine quiet')
    ok(screen_bits(sp)[8:24, 144:240].any() and (screen_bits(sp)[0:32, 8:120] == np.kron(LOGO, np.ones((2, 2), dtype=np.uint8))).all(),
       'it shows the lap record, and its logo is whole (read back from the race screen)')
    r0 = g(sp, 'renders'); sp.run(duration=3.0, fast_forward=True)
    ok(g(sp, 'renders') == r0 and len({(sp.read8(SYM['a_x'] + 1), sp.read8(SYM['a_y'] + 1)) for _ in range(20) if sp.run(duration=0.1, fast_forward=True) is None}) > 10,
       'the attract sequence runs again, no race behind it')
    tap(sp, '1', 0.3, 2.0)
    sb = screen_bits(sp)
    same = all((sb[y0:y1, x0:x1] == scr0[y0:y1, x0:x1]).all() for (y0, y1, x0, x1) in ((0, 8, 0, 256), (0, 64, 192, 256), (8, 152, 0, 8), (8, 152, 184, 192), (152, 160, 0, 192)))
    ok(frame_ok(sp) and same and sp.read8(SYM['race_on']) == 0 and screen_text(sp, 22, 1, 9) == ' PRESS Q ' and car(sp, 0)['vx'] == 0,
       '1: a new race on the grid; the race screen put back whole (frame, logo, mini-map)')
    t = go_green(sp); sp.run(duration=1.0, fast_forward=True); press(sp, 'Q', False)
    ok(t < 4.0 and car(sp, 0)['vx'] > 1.0 and list(sp.read(SYM['su_lv'], 3)) == [2, 1, 2], 'and it races: green after %.1f s, the set-up kept' % t)
    bad = window_bad(sp)
    ok(bad == 0, 'the play window still matches the world map pixel for pixel, cars excluded (%d wrong)' % bad)

print('RESULT:', 'PASS' if fails == 0 else '%d FAIL' % fails)
sys.exit(1 if fails else 0)
