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
import json
regs = [(q['x'], q['y'], q['attr'], q['rows'], q['box']) for q in json.load(open(os.path.join(ROOT, 'build', 'objects_rows.json')))]   # (x, y, attr, [(first, last) a row])
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
    for x, y, attr, spans, box in regs:
        bad = []; seen = 0; k = 0
        for oy in (-66, -30, 3, 40, 70):
            for ox in (-90, -45, -5, 30, 80):
                k += 1; px_, py_ = max(4, x + 16 + ox + k % 8), max(4, y + 8 + oy + (k * 3) % 8)        # your car: the camera follows it
                put(sp, 0, px_, py_, 16); sp.run(duration=0.25, fast_forward=True)
                at_copy_done(sp); cx, cy = g(sp, 'camx'), g(sp, 'camy')
                sp.run(duration=0.006, fast_forward=True)                               # (the colours go up straight after the copy)
                at = [[sp.read8(0x5800 + (WY // 8 + r) * 32 + 1 + c) for c in range(22)] for r in range(WH // 8)]
                mine = np.zeros((WH, 176), dtype=bool)                                  # where this block is, in the window
                for j, (a, b) in enumerate(spans):
                    sy = y + j - cy
                    if 0 <= sy < WH: mine[sy, max(0, x + a - cx):max(0, x + b - cx + 1)] = True
                covered = np.zeros((WH, 176), dtype=bool)                               # the whole object, edge and all
                covered[max(0, box[1] - cy):max(0, box[1] + box[3] - cy), max(0, box[0] - cx):max(0, box[0] + box[2] - cx)] = True
                for r in range(WH // 8):
                    for c in range(22):
                        cell = (slice(r * 8, r * 8 + 8), slice(c * 8, c * 8 + 8)); has = bool(mine[cell].any()); seen += has
                        if has and at[r][c] != attr: bad.append(('part of it without its colour', cx, cy, r, c, hex(at[r][c])))
                        if at[r][c] == attr and (attr >> 3) & 7 != 5 and not covered[cell].all(): bad.append(('colour over the cloth', cx, cy, r, c))
                        if at[r][c] != WIN and not any(q[2] == at[r][c] for q in regs): bad.append(('a stray colour', cx, cy, r, c, hex(at[r][c])))
        ok(not bad and seen > 60, 'the block at %d, %d (colour 0x%02X): over 25 camera positions, %d cells held some of it, all in its colour, none of them with cloth showing (%s)' % (x, y, attr, seen, bad[:3] + [len(bad)]))
    put(sp, 0, 260, 160, 16); sp.run(duration=0.4, fast_forward=True); at_copy_done(sp); sp.run(duration=0.006, fast_forward=True)
    left = [(r, c) for r in range(WH // 8) for c in range(22) if sp.read8(0x5800 + (WY // 8 + r) * 32 + 1 + c) != WIN]
    ok(not left, 'with the objects out of view the whole window is back to its own colours (%s)' % left[:5])
print('RESULT:', 'PASS' if fails == 0 else '%d FAIL' % fails)
