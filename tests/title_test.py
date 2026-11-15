"""The title / attract screen on the real ROM (Grant, 14 Nov 2026: "want the person to see they
choose 1UP or 2UP to play, K to customize keys, have the title screen have some kind of attract
sequence showing the different drivers, maybe a face and have that car skid around").
src/title.asm, title2.asm, title3.asm; layout A of docs/design/TITLE-SCREEN.md. Checks:
  - the title comes up after loading, before the race: logo twice the size, LAP RECORD, the cloth
    stage in its frame, a driver's card, the choices as a plain list (1 - ONE PLAYER, 2 - TWO PLAYERS, K - KEYS), the flashing prompt
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
PROMPT = 0x5800 + 8 * 32 + 10                        # TODAY'S MENU, red on the card: the title is up
TDV = lambda name: SYM['td'] + SYM[name + '_src'] - SYM['td_src']   # a table copied out of the program (title3.asm)
def attr(sp, r, c): return sp.read8(0x5800 + r * 32 + c)
def title_up(sp, limit=60.0):                        # run until the title is showing; the seconds it took
    t = 0.0
    while not (sp.read8(PROMPT) == 0x7A and screen_text(sp, 8, 10, 7) == "TODAY'S") and t < limit:
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
    A = np.array([[attr(sp, r, c) for c in range(32)] for r in range(24)])
    rr, cc = np.mgrid[0:24, 0:32]; edge = (rr < 3) | (rr > 20) | (cc < 3) | (cc > 28)
    ok((A[edge] == np.where((rr + cc) % 2 == 0, 0x50, 0x78)[edge]).all(),
       'the tablecloth: red and white checks, a cell each, 3 cells deep all round the card (black ink in every one, so the car cannot clash)')
    ok((sb[24:56, 72:184] == np.kron(LOGO, np.ones((2, 2), dtype=np.uint8))).all() and attr(sp, 5, 9) == 0x72 and attr(sp, 6, 22) == 0x77 and attr(sp, 3, 3) == 0x30 and attr(sp, 6, 28) == 0x30,
       'the logo twice its size, centred on the card\'s yellow head: RUN red, the egg white')
    ok(screen_text(sp, 8, 10, 12) == "TODAY'S MENU" and all(attr(sp, 8, c) == 0x7A for c in range(10, 22))
       and screen_text(sp, 10, 6, 13) == '1  ONE PLAYER' and screen_text(sp, 12, 6, 14) == '2  TWO PLAYERS' and screen_text(sp, 14, 6, 14) == 'K  CHOOSE KEYS'
       and all(attr(sp, r, c) == 0x78 for r in range(9, 16) for c in range(3, 29)),
       "TODAY'S MENU in red; the choices black on the white card: 1 ONE PLAYER, 2 TWO PLAYERS, K CHOOSE KEYS")
    ok([attr(sp, 16, 7 + 4 * i) for i in range(5)] == [0x57, 0x68, 0x60, 0x58, 0x78] and all(sb[128:144, 56 + 32 * i:72 + 32 * i].any() for i in range(5)),
       'the five drivers\' faces in a row, each on its car\'s colour')
    ok(screen_text(sp, 19, 6, 10) == 'LAP RECORD' and screen_text(sp, 19, 19, 6) == '-:--.-' and attr(sp, 19, 6) == 0x79,
       'LAP RECORD in blue at the card\'s foot (no record yet: -:--.-)')
    ok(screen_text(sp, 23, 5, 5) != 'PRESS' and screen_text(sp, 20, 6, 20).strip() == '' and all(attr(sp, 23, c) in (0x50, 0x78) for c in range(32)), 'no PRESS 1 OR 2 TO START line (Grant, 15 Nov 2026: "you can remove" it)')
    # the car's laps of the edge: 45 s, sampled 10 times a second
    card = np.zeros((192, 256), dtype=bool); card[24:168, 24:232] = True
    inner = np.zeros((192, 256), dtype=bool); inner[32:160, 32:224] = True      # (the car's corners cut 8 pixels into the card's)
    base = sb.copy(); spots = set(); leaks = 0; clash = 0; sides = set(); cw = 0; last = None
    for i in range(450):
        sp.run(duration=0.1, fast_forward=True)
        sb = screen_bits(sp)
        x, y = sp.read8(SYM['a_x'] + 1) - 8, sp.read8(SYM['a_y'] + 1) - 18      # its middle on the screen
        spots.add((x, y))
        sides.add('top' if y < 24 else 'bottom' if y > 168 else 'left' if x < 24 else 'right' if x > 232 else '?')
        leaks += int(((sb != base) & inner).sum())
        ink = sb & ~card
        if ink.any():
            ys, xs = np.nonzero(ink)
            if xs.max() - xs.min() > 20 or ys.max() - ys.min() > 20: leaks += 1000        # more than one car's worth of ink out there
        A2 = np.array([[attr(sp, r, c) for c in range(32)] for r in range(24)]); clash += int((A2 != A).sum())
    ok(len(spots) > 100 and sides >= {'top', 'bottom', 'left', 'right'}, 'your car laps the edge: seen on all four sides (%d different places in 45 s: the lap is the same each time, about 14 s)' % len(spots))
    ok(leaks == 0, 'it leaves nothing behind and never touches the menu (%d stray pixels)' % leaks)
    ok(clash == 0, 'not one colour cell changes while it runs: no colour clash')
    ok(g(sp, 'renders') == 0 and sp.read8(SYM['race_on']) == 0, 'no race runs behind the title')
    # 2: not built yet
    title_up(sp)
    tap(sp, '2', 0.2, 0.3)
    soon = screen_text(sp, 20, 6, 20)
    sp.run(duration=2.5, fast_forward=True)
    ok(soon.strip() == '2UP COMING SOON' and screen_text(sp, 20, 6, 20).strip() == '' and g(sp, 'renders') == 0,
       '2 says 2UP COMING SOON at the card\'s foot, then it goes (%r)' % soon.strip())

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
    sp.write(SYM['jin_on'], bytes([0xFF]))          # (the start ditty's automatic countdown held off from here on: the keys are what is tested - tests/finish_test.py has the ditty)
    ok(g(sp, 'renders') > 0 and frame_ok(sp), '1: the race screen, whole')
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
    ok(g(sp, 'renders') > 0 and frame_ok(sp) and car(sp, 0)['vx'] == 0,
       '1 at the title: the race screen, your car on the grid')
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
    ok(sp.read8(0x5800 + 6 * 32 + 5) == 0x70 and sp.read8(PROMPT) != 0x7A, 'the race over: the podium\'s card is up')
    tap(sp, 'Q', 0.2, 1.5)
    ok(sp.read8(PROMPT) == 0x7A and screen_text(sp, 8, 10, 12) == "TODAY'S MENU" and sp.read8(SYM['snd_rate']) == 0,
       'Q after the race: the title screen again, the engine quiet')
    ok(screen_text(sp, 19, 19, 6).strip() not in ('', '-:--.-') and (screen_bits(sp)[24:56, 72:184] == np.kron(LOGO, np.ones((2, 2), dtype=np.uint8))).all(),
       'it shows the lap record, and its logo is whole (read back from the race screen)')
    r0 = g(sp, 'renders'); sp.run(duration=3.0, fast_forward=True)
    ok(g(sp, 'renders') == r0 and len({(sp.read8(SYM['a_x'] + 1), sp.read8(SYM['a_y'] + 1)) for _ in range(20) if sp.run(duration=0.1, fast_forward=True) is None}) > 10,
       'the attract sequence runs again, no race behind it')
    tap(sp, '1', 0.3, 2.0)
    sb = screen_bits(sp)
    same = all((sb[y0:y1, x0:x1] == scr0[y0:y1, x0:x1]).all() for (y0, y1, x0, x1) in ((0, 8, 0, 256), (0, 48, 208, 256), (8, 160, 0, 8), (8, 160, 200, 208), (160, 168, 0, 208), (168, 184, 72, 128)))
    ok(frame_ok(sp) and same and sp.read8(SYM['race_on']) == 0 and car(sp, 0)['vx'] == 0,
       '1: a new race on the grid; the race screen put back whole (frame, mini-map, the logo under the window)')
    t = go_green(sp); sp.run(duration=1.0, fast_forward=True); press(sp, 'Q', False)
    ok(t < 4.0 and car(sp, 0)['vx'] > 1.0 and list(sp.read(SYM['su_lv'], 3)) == [2, 1, 2], 'and it races: green after %.1f s, the set-up kept' % t)
    bad = window_bad(sp)
    ok(bad == 0, 'the play window still matches the world map pixel for pixel, cars excluded (%d wrong)' % bad)

print('RESULT:', 'PASS' if fails == 0 else '%d FAIL' % fails)
sys.exit(1 if fails else 0)
