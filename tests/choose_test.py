"""The CHOOSE SCREEN on the real ROM (Grant, 16 Nov 2026: "when you click 1 or 2, you get a screen that asks you which
track and which player ... left and right to choose the track, then click forward to select. Then click person and
then car ... Then on the car you choose one extra of acceleration, grip and speed").
The tape: build/racer_choose.tap (bash tools/build_choose.sh); src/choose.asm. Checks:
  1  the title has three choices, no "3 CHOOSE YOUR PLAYER"; 1 goes to the TRACK step
  2  the track step: left and right go round the three tracks, each name shown, the road drawn from that track's own
     surface map; after choosing, memory is byte for byte what that track's own build has
  3  the driver and car steps: seven of each, names shown, the picture twice the size; the ones chosen are the face in
     the race order and on the podium, and the car in the cars' table and the race order
  4  the extra: three bars, one pip each, the chosen one two; in the race each extra changes its own quantity only
  5  two players: player 2 chooses with 6, 7, 9; cannot have player 1's driver or car; both are in the race
Usage: python3 tests/choose_test.py [part ...]   (parts: title track mem who extra two; none = all)
Prints PASS/FAIL lines and RESULT."""
import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault('ZTAP', os.path.join(HERE, '..', 'build', 'racer_choose.tap'))
os.environ.setdefault('ZSYM', os.path.join(HERE, '..', 'build', 'racer_choose.sym'))
os.environ.setdefault('TSRC', os.path.join(HERE, '..', 'build', 'multi', 't1', 'src'))
src = open(os.path.join(HERE, 'drive_test.py')).read()
src = src[:src.index('with Racer(headless=True)')].replace("os.path.dirname(os.path.abspath(__file__))", repr(HERE))
exec(src)
PARTS = sys.argv[1:] or ['title', 'track', 'mem', 'who', 'extra', 'two']
fails = 0
def ok(c, m):
    global fails
    print('PASS' if c else 'FAIL', m); fails += 0 if c else 1
M = os.path.join(ROOT, 'build', 'multi')
attr = lambda sp, r, c: sp.read8(0x5800 + r * 32 + c)
def tap(sp, k, down=0.15, after=0.35):
    press(sp, k, True); sp.run(duration=down, fast_forward=True); press(sp, k, False); sp.run(duration=after, fast_forward=True)
def title(sp, tape=None):
    Spectrum.load_tape(sp, tape or TAP); t = 0.0
    while not (attr(sp, 8, 10) == 0x7A and screen_text(sp, 8, 10, 7) == "TODAY'S") and t < 60: sp.run(duration=0.1, fast_forward=True); t += 0.1
    sp.run(duration=0.6, fast_forward=True)
    if 'jin_on' in SYM and tape is None: sp.write(SYM['jin_on'], bytes([0xFF]))    # (the start jingle held off, as the other tests do)
def row_text(sp, r): return screen_text(sp, r, 3, 26).strip()
def heading(sp):
    """the step's heading: the big letters on rows 2-3 are the ROM's, twice the size - read every other pixel"""
    sb = screen_bits(sp); font = sp.read(0x3D00, 96 * 8); best = ''
    for c0 in (3, 4):                                    # (a heading of an odd number of letters starts on an odd column)
        out = ''
        for c in range(c0, 28, 2):
            cell = bytes(int(''.join(str(v) for v in sb[16 + 2 * k, c * 8:c * 8 + 16:2]), 2) for k in range(8))
            for code in range(96):
                if bytes(font[code * 8:code * 8 + 8]) == cell: out += chr(32 + code); break
            else: out += '?'
        if '?' not in out and out.strip(): best = out.strip()
    return best
def pic(sp):
    """the driver's or car's picture: 32 x 32 at (112, 80), each pixel twice the size -> 16 x 16"""
    q = screen_bits(sp)[80:112, 112:144]
    assert (q[0::2, 0::2] == q[1::2, 1::2]).all()
    return q[0::2, 0::2]
def mem_face(sp, n): return np.unpackbits(np.frombuffer(bytes(sp.read(SYM['faces7'] + 32 * n, 32)), dtype=np.uint8)).reshape(16, 16)
def frame16(sp, entry, heading=0):
    """a car's picture as its frame has it: 16 x 16 from the table entry at `entry` (address, first row, rows), ink only"""
    a = sp.read16(entry + 4 * heading); first = sp.read8(entry + 4 * heading + 2); rows = sp.read8(entry + 4 * heading + 3)
    out = np.zeros((16, 16), dtype=np.uint8); flip = rows & 0x80; rows &= 0x7F
    for i in range(rows):
        y = first - 6 + i
        b = sp.read(a - 4 * i if flip else a + 4 * i, 4)
        if 0 <= y < 16: out[y] = np.unpackbits(np.array([b[1], b[3]], dtype=np.uint8))
    return out
def entry(sp, j): return SYM['big_tab'] + 64 * j if j < 5 else sp.read16(SYM['hp_cars']) + 64 * (j - 5)
NAMES = ['MAX', 'FRANK', 'SPIKE', 'BRUNO', 'JANE', 'SPECS', 'DOT']
CARN = [m[1].strip().upper() for m in re.findall(r'^car:\s*(\w+)\s+(.+?)\s*$', open(os.path.join(ROOT, 'tools', 'choose_cars.txt')).read(), re.M)]
TRKN = ["BREAKFAST AT TIFFANY'S", 'THE BREAKFAST CLUB', 'GREEN EGGS AND HAM']
def surface(t):
    s = open(os.path.join(M, 't%d' % t, 'src', 'world.asm')).read()
    h = int(re.search(r'MAPH\s+equ\s+(\d+)', s).group(1)); bits = []
    for l in s[s.index('surface_map:'):].splitlines()[1:]:
        if 'defb' not in l:
            if bits: break
            continue
        for b in l.split('defb')[1].split(';')[0].split(','): bits += [int(c) for c in b.strip().lstrip('%')]
    return 1 - np.array(bits[:72 * h], dtype=np.uint8).reshape(h, 72)          # 1 = road

# ---------------------------------------------------------------- 1: the title
if 'title' in PARTS:
    with Racer(headless=True) as sp:
        title(sp)
        ok(screen_text(sp, 10, 6, 13) == '1  ONE PLAYER' and screen_text(sp, 11, 6, 14) == '2  TWO PLAYERS' and screen_text(sp, 12, 6, 14) == 'K  CHOOSE KEYS'
           and screen_text(sp, 13, 6, 20) == '-' * 20 and screen_text(sp, 9, 6, 20) == '-' * 20 and not screen_bits(sp)[112:128, 24:232].any(),
           'the title: three choices on rows 10-12 - 1 ONE PLAYER, 2 TWO PLAYERS, K CHOOSE KEYS - closed by the rule on row 13; no "3 CHOOSE YOUR PLAYER", rows 14-15 clear')
        tap(sp, 'T')
        ok(attr(sp, 8, 10) == 0x7A and sp.read8(SYM['hp'] + 3) == 0, 'T does nothing at the title any more (the track is chosen on the choose screen)')
        tap(sp, '1')
        A = np.array([[attr(sp, r, c) for c in range(32)] for r in range(24)])
        ok(heading(sp) == 'TRACK' and (A[1:5, 3:29] == 0x67).sum() == 20 and ((A[1:5, 3:29] == 0x60) | (A[1:5, 3:29] == 0x67)).all() and (A[5:23, 3:29] == 0x78).all()
           and all(A[r, c] == (0x50 if (r + c) % 2 == 0 else 0x78) for r in (0, 23) for c in range(32)) and g(sp, 'renders') == 0,
           '1 goes to the choose screen, not the race: a card as the title\'s menu - green head (rows 1-4) with TRACK in white, white under it, the check cloth round it')
        ok(row_text(sp, 20) == 'LEFT / RIGHT TO CHOOSE' and row_text(sp, 21) == 'ACCELERATE TO SELECT' and screen_text(sp, 12, 10, 1) == '<' and screen_text(sp, 12, 22, 1) == '>',
           'it says how: LEFT / RIGHT TO CHOOSE, ACCELERATE TO SELECT, an arrow either side of the picture')

# ---------------------------------------------------------------- 2: the track step
if 'track' in PARTS:
    with Racer(headless=True) as sp:
        title(sp); tap(sp, '1')
        seen = []
        for k in range(4):
            t = [1, 2, 3][k % 3]; s = surface(t); sb = screen_bits(sp)
            got = sb[64:64 + s.shape[0], 96:168]
            ok(row_text(sp, 6) == TRKN[k % 3] and sp.read8(SYM['hp'] + 3) == k % 3 and (got == s).all() and not sb[64 + s.shape[0]:152, 96:168].any() and s.sum() > 400,
               'track step, %d to the right: %s by name; its road drawn from the track\'s own surface map, a pixel a tile (72 x %d, %d pixels of road, all matching)' % (k, TRKN[k % 3], s.shape[0], s.sum()))
            seen.append(row_text(sp, 6)); tap(sp, 'P')
        tap(sp, 'O'); tap(sp, 'O')
        ok(row_text(sp, 6) == TRKN[2], 'left from the first track goes round to the last (%s)' % row_text(sp, 6))
        tap(sp, 'A'); tap(sp, 'M')
        ok(heading(sp) == 'TRACK' and row_text(sp, 6) == TRKN[2], 'other keys do nothing')
        tap(sp, 'Q')
        ok(heading(sp) == 'DRIVER' and sp.read8(SYM['hp'] + 3) == 2, 'accelerate selects it: the DRIVER step, track 3 in its working places')

# ---------------------------------------------------------------- 2b: memory after choosing a track = that track's own build
if 'mem' in PARTS:
    def looks(tape, keys):
        out = []
        with Spectrum(headless=True) as sp:
            title(sp, tape)
            for k in keys: tap(sp, k)
            for w in (0.5, 2.3): sp.run(duration=w, fast_forward=True); out.append(bytes(sp.read(0, 65536)))
        return out
    AREAS = [(0x5B00, 0x5B4C + SYM['td_end2'] - SYM['td_src']), (0x5F00, SYM['lp_src']), (SYM['topmem'], SYM['code_end'])] \
        + [(0xD0A0 + 256 * k, 0xD0FA + 256 * k) for k in range(8)] + [(0xE800, SYM['hp']), (SYM['himem'], 0xFFF4)]
    lab = sorted((v, k) for k, v in SYM.items() if 0x5B00 <= v <= 0xFFFF)
    import bisect
    near = lambda a: '%s+%d' % (lab[bisect.bisect_right(lab, (a, '~')) - 1][1], a - lab[bisect.bisect_right(lab, (a, '~')) - 1][0])
    for i, t in enumerate([1, 2, 3]):
        a1, a2 = looks(TAP, ['1'] + ['P'] * (i if i else 3) + ['Q'])            # (the first track: all the way round and back to it; then selected)
        b1, b2 = looks(os.path.join(M, 'pad_t%d.tap' % t), [])
        var = lambda x: a1[x] != a2[x] or b1[x] != b2[x]
        diff = [x for lo, hi in AREAS for x in range(lo, hi) if a1[x] != b1[x] and not var(x)]
        own = [x for x in diff if SYM['ch_np'] <= x < SYM['cwho'] + 10 or x in (SYM['cr_draw'] + 1, SYM['cr_draw'] + 2, SYM['pb_attr'], SYM['pa_last'])]   # the choose screen's own variables
        scratch = [x for x in diff if 0xD2C0 <= x < 0xD2FA]                      # (cloth_pat, PNUM: printing's scratch)
        left = [x for x in diff if SYM['mapdat'] + 3 * 17 <= x < SYM['mapdat'] + 90]   # (the mini-map's strip past a shorter map's last line: start-up leftovers, as tests/multi_mem_check.py)
        rest = [x for x in diff if x not in own and x not in scratch and x not in left]
        ok(not rest, 'track %d chosen on the choose screen: %d bytes compared with its own build, %d differ%s (not counted: %d variables that change by themselves, %d of the choose screen\'s own, %d of printing\'s scratch, %d leftover bytes of the mini-map strip)'
           % (t, sum(hi - lo for lo, hi in AREAS), len(rest), '' if not rest else ' at ' + ' '.join('%04X(%s)' % (x, near(x)) for x in rest[:14]),
              sum(1 for lo, hi in AREAS for x in range(lo, hi) if var(x)), len(own), len(scratch), len(left)))

# ---------------------------------------------------------------- 3: driver and car
if 'who' in PARTS:
    with Racer(headless=True) as sp:
        title(sp); tap(sp, '1'); tap(sp, 'Q')
        ok(heading(sp) == 'DRIVER' and screen_text(sp, 6, 12, 8) == 'PLAYER 1' and all(attr(sp, 6, c) == 0x57 for c in range(12, 20)) and all(attr(sp, r, c) == 0x57 for r in range(10, 14) for c in range(14, 18)),
           'the DRIVER step: PLAYER 1 on red, the face on red as the race order has it')
        names = []; good = True
        for k in range(8):
            n = k % 7
            good = good and (pic(sp) == mem_face(sp, n)).all() and row_text(sp, 16) == NAMES[n]
            names.append(row_text(sp, 16)); tap(sp, 'P')
        ok(good and names == NAMES + ['MAX'], 'right goes through seven drivers and round again, each face twice its size with the name under it: %s' % ' '.join(names[:7]))
        for _ in range(4): tap(sp, 'P')                           # MAX + 1 + 4 = SPECS
        ok(row_text(sp, 16) == 'SPECS', 'SPECS, one of the two new drivers, is on show')
        tap(sp, 'Q')
        ok(heading(sp) == 'CAR' and list(sp.read(SYM['pwho'], 7)) == [5, 1, 2, 3, 4, 0, 6], 'accelerate: the CAR step; SPECS has the first car\'s seat and MAX his (%s)' % list(sp.read(SYM['pwho'], 7)))
        ncar = sp.read8(SYM['hp_ncar']); cn = []; good = True; first = {j: bytes(sp.read(entry(sp, j), 64)) for j in range(ncar)}
        for k in range(ncar + 1):
            j = k % ncar
            good = good and (pic(sp) == frame16(sp, entry(sp, j))).all() and row_text(sp, 16) == CARN[j]
            cn.append(row_text(sp, 16)); tap(sp, 'P')
        ok(good and ncar == len(CARN) >= 7 and cn[:ncar] == CARN, 'right goes through the %d cars of tools/choose_cars.txt and round again, each drawn nose up twice its size with its name: %s' % (ncar, ', '.join(cn[:ncar])))
        tap(sp, 'O'); tap(sp, 'O')                                # round to the last: TRUCK
        want = row_text(sp, 16); tap(sp, 'Q')
        j = CARN.index(want)
        ok(heading(sp) == 'EXTRA' and bytes(sp.read(SYM['big_tab'], 64)) == first[j] and bytes(sp.read(entry(sp, j), 64)) == first[0] and list(sp.read(SYM['cwho'], ncar))[0] == j,
           'accelerate: the EXTRA step; the %s\'s 16 headings are the first car\'s in the cars\' table, and the RACER\'s are where the %s\'s were' % (want, want))
        tap(sp, 'Q'); sp.run(duration=0.6, fast_forward=True)
        sb = screen_bits(sp)
        ok(g(sp, 'renders') > 0 and (sb[TOWER_Y * 8:TOWER_Y * 8 + 16, 240:256] == mem_face(sp, 5)).all(),
           'the race screen: SPECS\'s face is beside the first car in the race order')
        tw = sb[TOWER_Y * 8:TOWER_Y * 8 + 16, 216:232]
        ok((tw == frame16(sp, SYM['big_tab'], 4)).all() and tw.sum() > 60, 'and that car is the %s (its picture facing right, %d pixels, as its frame has it)' % (want, tw.sum()))
        ok(sp.read8(SYM['cars'] + SYM['c_kind']) == 0 and not window_bad(sp, stop=False), 'the window is whole: the cloth matches the map outside the cars')
        go_green(sp); hold(sp, ['Q'], 1.0)
        order = [0, 4, 1, 3, 2]
        sp.write(SYM['order'], bytes(order)); sp.write(SYM['race_over'], bytes([1])); sp.run(duration=0.6, fast_forward=True)
        sp.run(duration=7.0, fast_forward=True)
        seen = set()
        for k in range(30):
            f = screen_bits(sp)
            if (f[56:72, 96:112] == mem_face(sp, 5)).all(): seen.add('SPECS')
            for n in range(7):
                if n != 5 and (f[56:72, 96:112] == mem_face(sp, n)).all(): seen.add(NAMES[n])
            sp.run(duration=0.16, fast_forward=True)
        ok(seen == {'SPECS'}, 'the podium, you first: the winner\'s everyday face is SPECS\'s (%s)' % sorted(seen))
        tap(sp, 'M', after=1.0)
        sb = screen_bits(sp)
        ok(attr(sp, 8, 10) == 0x7A and (sb[128:144, 56:72] != mem_face(sp, 5)).sum() <= 6 and (sb[128:144, 56:72] != mem_face(sp, 0)).sum() > 20, 'a key: back to the title, the first face of its row SPECS\'s (%d pixels from his everyday face: his eyes move)' % (sb[128:144, 56:72] != mem_face(sp, 5)).sum())
        tap(sp, '1'); tap(sp, 'Q')
        ok(heading(sp) == 'DRIVER' and row_text(sp, 16) == 'SPECS', 'the next time round the choose screen starts on the driver chosen last time (SPECS)')

# ---------------------------------------------------------------- 4: the extra
if 'extra' in PARTS:
    def pips(sp):
        sb = screen_bits(sp); out = []
        for r in (10, 12, 14): out.append([int(sb[r * 8 + 3, c * 8 + 3]) for c in (21, 23)] + [attr(sp, r, 8)])
        return out
    def run_extra(n, plain_grip=False):
        with Racer(headless=True) as sp:
            title(sp); tap(sp, '1'); tap(sp, 'Q'); tap(sp, 'Q'); tap(sp, 'Q')
            r = {'head': heading(sp), 'text': [screen_text(sp, 10, 8, 12), screen_text(sp, 12, 8, 4), screen_text(sp, 14, 8, 5)], 'p0': pips(sp)}
            for _ in range(n): tap(sp, 'P')
            r['p'] = pips(sp); tap(sp, 'Q'); sp.run(duration=0.5, fast_forward=True)
            r['lv'] = list(sp.read(SYM['su_lv'], 4)); r['clean'] = not window_bad(sp, stop=False)
            tap(sp, '1'); tap(sp, '2'); tap(sp, '3'); r['lv2'] = list(sp.read(SYM['su_lv'], 4))      # (the old set-up keys: nothing now)
            go_green(sp); press(sp, 'Q', False); sp.run(duration=0.3, fast_forward=True)
            for i in CPUS: put(sp, i, 20 + 25 * i, SY + 58)
            put(sp, 0, 60, SY - 8, 16); sp.run(duration=0.3, fast_forward=True)
            # frame by frame (a breakpoint each picture is too coarse): the forward speed each 1/50 s, from Q down
            if plain_grip: sp.write(SYM['yg_gtab'], bytes([16, 8, 8, 5]))      # (the same run with the plain car's tyres: the one thing GRIP changes)
            press(sp, 'Q', True); v = []; f0 = sp.read8(23672)
            for k in range(170):
                sp.run(duration=0.02, fast_forward=True); v.append(car(sp, 0)['vx'])
            r['top'] = max(v); r['t15'] = next(i for i, x in enumerate(v) if x >= 1.5); r['t10'] = next(i for i, x in enumerate(v) if x >= 1.0)
            r['grip'] = list(sp.read(SYM['yg_gtab'], 4)); r['push'] = sp.read16(SYM['yg_pushv']); r['topv'] = sp.read16(SYM['yg_topv'])
            press(sp, 'P', True); sp.run(duration=0.3, fast_forward=True); press(sp, 'P', False)
            n = 0; y0 = car(sp, 0)['y']
            while sp.read8(SYM['yg_sl']) and n < 120: sp.run(duration=0.02, fast_forward=True); n += 1
            r['slide'] = n; press(sp, 'Q', False); r['vs'] = abs(s16(sp.read16(SYM['yg_vs'])))
            return r
    base_free = None
    R = [run_extra(n) for n in range(3)]
    for n, nm in enumerate(['ACCELERATION', 'GRIP', 'SPEED']): print('   ', nm, {k: R[n][k] for k in ('lv', 'top', 't10', 't15', 'grip', 'push', 'topv', 'slide')})
    A, G, S = R
    ok(A['head'] == 'EXTRA' and A['text'] == ['ACCELERATION', 'GRIP', 'SPEED'] and A['p0'] == [[1, 1, 0x70], [1, 0, 0x78], [1, 0, 0x78]],
       'the EXTRA step: ACCELERATION, GRIP, SPEED, a filled pip each; the one the choice is on is lit yellow and has a second (%s)' % A['p0'])
    ok(G['p'] == [[1, 0, 0x78], [1, 1, 0x70], [1, 0, 0x78]] and S['p'] == [[1, 0, 0x78], [1, 0, 0x78], [1, 1, 0x70]], 'right moves the choice, and the second pip with it: GRIP, then SPEED')
    ok(A['lv'] == [1, 1, 2, 0] and G['lv'] == [2, 1, 1, 0] and S['lv'] == [1, 2, 1, 0] and all(r['lv2'] == r['lv'] for r in R),
       'the race starts with that part at level 2 and the other two at 1, no points to spend; keys 1 2 3 before the lights change nothing now')
    ok(all(r['clean'] for r in R), 'on the grid the window is the cloth and the cars only: the crew chief does not ask for upgrades with keys 1 2 3 any more')
    ok(1.90 <= S['top'] <= 1.93 and 1.74 <= A['top'] <= 1.76 and 1.74 <= G['top'] <= 1.76 and S['topv'] == 492 and A['topv'] == G['topv'] == 448,
       'SPEED: top speed %.2f px a frame against %.2f (+%.1f%%); ACCELERATION and GRIP leave it at %.2f, %.2f' % (S['top'], G['top'], 100 * (S['top'] / G['top'] - 1), A['top'], G['top']))
    ok(A['t15'] < G['t15'] - 2 and A['t10'] < G['t10'] and abs(S['t15'] - G['t15']) <= 1 and abs(S['t10'] - G['t10']) <= 1 and A['push'] == 71 and G['push'] == S['push'] == 64,
       'ACCELERATION: 1.5 px a frame %d frames after the key against %d, 1.0 after %d against %d (push 71 against 64, +10.9%%); SPEED and GRIP get away as the plain car does (1.5 after %d and %d: the same within the frame the key lands in)' % (A['t15'], G['t15'], A['t10'], G['t10'], S['t15'], G['t15']))
    ok(G['grip'] == [18, 9, 9, 6] and A['grip'] == S['grip'] == [16, 8, 8, 5], 'GRIP: the tyres hold %s where the others hold %s (sideways speed cancelled a frame, 1/256 px: gripping, with accelerate, sliding, both)' % (G['grip'], A['grip']))
    P = run_extra(1, plain_grip=True)
    print('    GRIP chosen, the plain tyres put back:', {k: P[k] for k in ('grip', 'slide', 'top', 't15')})
    ok(G['slide'] < P['slide'], 'GRIP: after the same hard turn at the same speed the slide ends sooner than the same car on the plain tyres (%d frames against %d)' % (G['slide'], P['slide']))

# ---------------------------------------------------------------- 5: two players
if 'two' in PARTS:
    with Racer(headless=True) as sp:
        title(sp); tap(sp, '2')
        ok(heading(sp) == 'TRACK' and sp.read8(SYM['ch_np']) == 2, '2 at the title: the choose screen, for two')
        tap(sp, 'Q'); tap(sp, 'P'); tap(sp, 'P')                  # player 1: SPIKE
        tap(sp, 'Q'); tap(sp, 'P'); tap(sp, 'P'); tap(sp, 'P')    # ... the TANK
        car1 = row_text(sp, 16); tap(sp, 'Q'); tap(sp, 'P'); tap(sp, 'Q')   # ... GRIP
        ok(heading(sp) == 'DRIVER' and screen_text(sp, 6, 12, 8) == 'PLAYER 2' and all(attr(sp, 6, c) == 0x68 for c in range(12, 20)) and attr(sp, 10, 14) == 0x68,
           'after player 1\'s three steps: DRIVER again, PLAYER 2 on cyan (the second car\'s colour)')
        was = row_text(sp, 16)
        for k in 'OPQ': tap(sp, k)
        ok(heading(sp) == 'DRIVER' and row_text(sp, 16) == was, 'player 1\'s keys do nothing now')
        names = []
        for k in range(7): names.append(row_text(sp, 16)); tap(sp, '7')
        ok(names[6] == names[0] and sorted(names[:6]) == sorted(n for n in NAMES if n != 'SPIKE'), 'player 2 goes round with 7 (and 6): six drivers, SPIKE - player 1\'s - not among them (%s)' % ' '.join(names[:6]))
        tap(sp, '6'); p2 = row_text(sp, 16); tap(sp, '9')
        ok(heading(sp) == 'CAR' and names[0] == p2, '6 goes back one (from %s to %s); 9 selects' % (names[1], p2))
        cn = []
        ncar = sp.read8(SYM['hp_ncar'])
        for k in range(ncar - 1): cn.append(row_text(sp, 16)); tap(sp, '7')
        ok(car1 not in cn and len(set(cn)) == ncar - 1, 'the cars: %d to choose from, player 1\'s %s not among them (%s)' % (ncar - 1, car1, ', '.join(cn)))
        tap(sp, '7'); c2 = row_text(sp, 16); tap(sp, '9')
        ok(heading(sp) == 'EXTRA' and screen_text(sp, 6, 12, 8) == 'PLAYER 2', 'then player 2\'s EXTRA')
        tap(sp, '7'); tap(sp, '7'); tap(sp, '9'); sp.run(duration=0.6, fast_forward=True)
        who = list(sp.read(SYM['pwho'], 7)); cw = list(sp.read(SYM['cwho'], ncar))
        ok(g(sp, 'renders') > 0 and who[0] == 2 and NAMES[who[1]] == p2 and CARN[cw[0]] == car1 and CARN[cw[1]] == c2 and len(set(who)) == 7,
           'the race: car 1 is SPIKE in the %s, car 2 is %s in the %s; the computer cars have four of the other drivers (%s)' % (car1, p2, c2, ' '.join(NAMES[i] for i in who[2:5])))
        sb = screen_bits(sp)
        ok((sb[TOWER_Y * 8:TOWER_Y * 8 + 16, 240:256] == mem_face(sp, who[0])).all() and (sb[TOWER_Y * 8 + 16:TOWER_Y * 8 + 32, 240:256] == mem_face(sp, who[1])).all()
           and (sb[TOWER_Y * 8 + 16:TOWER_Y * 8 + 32, 216:232] == frame16(sp, SYM['big_tab'] + 64, 4)).all(),
           'the race order shows both: SPIKE\'s face first, %s\'s second with the %s' % (p2, c2))
        ok(list(sp.read(SYM['su_lv'], 4)) == [2, 1, 1, 0] and list(sp.read(SYM['ch_ex'], 2)) == [1, 2], 'player 1\'s car has player 1\'s extra (GRIP); player 2\'s (SPEED) is remembered but drives nothing - the computer drives the second car')
print('RESULT:', 'PASS' if fails == 0 else '%d FAIL' % fails)
