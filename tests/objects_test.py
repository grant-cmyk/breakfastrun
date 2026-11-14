"""The coloured objects on the real ROM: for many camera positions round each object, at every
pixel offset against the 8 x 8 colour cells, every window cell that holds some of the object's
ink has the object's colour, and no cell with that colour holds any other ink (the cloth's dots,
an O) - the Spectrum's one-ink-a-cell rule, kept by how the object is drawn and placed. And with
the object out of view no cell keeps its colour. Prints PASS/FAIL lines and RESULT.
Only for a build with the objects in: OBJECTS=1 python3 tools/make_world.py; OBJECTS=1 bash build.sh"""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'drive_test.py')).read()
src = src[:src.index('with Racer(headless=True)')].replace("os.path.dirname(os.path.abspath(__file__))", repr(HERE))
exec(src)
if 'obj_paint' not in SYM:
    print('SKIP the coloured objects are not in this build (OBJECTS=1 python3 tools/make_world.py; OBJECTS=1 bash build.sh)'); print('RESULT: PASS'); raise SystemExit
regs = []                                             # (x, y, attr, [(first, last) a row])
t = open(os.path.join(ROOT, 'src', 'objects.asm')).read()
for m in re.finditer(r'dw (\d+),(\d+)[^\n]*\n\s+db 0x([0-9A-F]+),(\d+)\n((?:\s+db [\d,]+\n)+)', t):
    v = [int(n) for l in m.group(5).splitlines() for n in l.split('db')[1].split(',')]
    runs = list(zip(v[0::2], v[1::2]))                # (the file holds runs of 8 rows; the test wants the ink itself:
    regs.append((int(m.group(1)), int(m.group(2)), int(m.group(3), 16), runs))   # a run's span is where ink MAY be - the ink is read off the screen)
fails = 0
def ok(c, msg):
    global fails
    print('PASS' if c else 'FAIL', msg); fails += 0 if c else 1
WIN = 0x29
with Racer(headless=True) as sp:
    sp.load_tape(TAP); t = 0
    while g(sp, 'renders') == 0 and t < 60: sp.run(duration=0.1, fast_forward=True); t += 0.1
    go_green(sp); press(sp, 'Q', False); sp.run(duration=2.0, fast_forward=True)
    for i in CPUS: put(sp, i, 20 + 25 * i, 20); sp.write(CARS + i * CS + 19, bytes([0]))   # the others: parked far away
    for x, y, attr, spans in regs:
        bad = []; seen = 0; k = 0
        for oy in (-70, -41, -14, 3, 30, 61):
            for ox in (-95, -52, -9, 12, 47, 90):
                k += 1; px_, py_ = x + 30 + ox + k % 8, y + 20 + oy + (k * 3) % 8       # your car: the camera follows it
                put(sp, 0, px_, py_, 16); sp.run(duration=0.25, fast_forward=True)
                at_copy_done(sp); cx, cy = g(sp, 'camx'), g(sp, 'camy'); bits = screen_bits(sp)[WY:WY + WH, 8:184]; c0 = car(sp, 0)
                sp.run(duration=0.012, fast_forward=True)                               # (the colours go up straight after the copy)
                at = [[sp.read8(0x5800 + (WY // 8 + r) * 32 + 1 + c) for c in range(22)] for r in range(WH // 8)]
                mine = np.zeros((WH, 176), dtype=bool)                                  # where this region's ink is, in the window
                rows = len(spans) - 7
                for j in range(rows):                            # row j's own ink lies inside every run that covers it: the narrowest of them
                    cover = [spans[k] for k in range(j, j + 8) if spans[k][0] != 255]
                    a, b = max(c[0] for c in cover), min(c[1] for c in cover)
                    sy = y + j - cy
                    if 0 <= sy < WH and a <= b: mine[sy, max(0, x + a - cx):max(0, x + b - cx + 1)] = True
                ccx, ccy = c0['x'] - cx, c0['y'] - cy
                for r in range(WH // 8):
                    for c in range(22):
                        cell = (slice(r * 8, r * 8 + 8), slice(c * 8, c * 8 + 8))
                        if ccx - 8 < c * 8 + 8 and ccx + 24 > c * 8 and ccy - 8 < r * 8 + 8 and ccy + 24 > r * 8: continue   # (your car)
                        has = bool((bits[cell].astype(bool) & mine[cell]).any()); other = bool((bits[cell].astype(bool) & ~mine[cell]).any())
                        seen += has
                        if has and at[r][c] != attr: bad.append(('ink without its colour', cx, cy, r, c, hex(at[r][c])))
                        if at[r][c] == attr and other: bad.append(('colour over other ink', cx, cy, r, c))
                        if at[r][c] not in (WIN, attr) and not any(q[2] == at[r][c] for q in regs): bad.append(('a stray colour', cx, cy, r, c, hex(at[r][c])))
                if os.environ.get('DUMP') and any(q[1] == cx and q[2] == cy for q in bad if q[0] == 'ink without its colour'):
                    print('cam', cx, cy, 'car at', ccx, ccy, 'now cam', g(sp, 'camx'), g(sp, 'camy'))
                    for r in range(WH // 8): print(''.join(('#' if at[r][c] == attr else '.') + ('m' if (bits[r*8:r*8+8, c*8:c*8+8].astype(bool) & mine[r*8:r*8+8, c*8:c*8+8]).any() else ' ') for c in range(22)))
                    os.environ['DUMP'] = ''
        ok(not bad and seen > 100, 'the region at %d, %d (colour 0x%02X): over 36 camera positions, %d cells held its ink, all in its colour and no other ink with them (%s)' % (x, y, attr, seen, sorted({(b[0], b[3]) for b in bad}) + [len(bad)]))
    put(sp, 0, 60, 60, 16); sp.run(duration=0.4, fast_forward=True); at_copy_done(sp); sp.run(duration=0.012, fast_forward=True)
    left = [(r, c) for r in range(WH // 8) for c in range(22) if sp.read8(0x5800 + (WY // 8 + r) * 32 + 1 + c) != WIN]
    ok(not left, 'with the objects out of view the whole window is back to its own colours (%s)' % left[:5])
print('RESULT:', 'PASS' if fails == 0 else '%d FAIL' % fails)
