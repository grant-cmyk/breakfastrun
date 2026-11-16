"""The car frames: which headings are another heading turned upside down or mirrored, pixel for pixel?
Reads src/bigcars.asm and src/data.asm (big_tab and the frames that did not fit below the program).
    python3 tools/car_flips.py
Prints, for the top-bottom flip (the cheap one: draw the rows last to first), which of each car's 16 headings
could be dropped, the bytes saved, and every pixel that would change."""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.join(HERE, '..', 'src')
txt = open(os.path.join(SRC, 'bigcars.asm')).read() + open(os.path.join(SRC, 'data.asm')).read()
frames = {}
for m in re.finditer(r'^bf_(\d+)_(\d+):.*\n((?:        defb .*\n)+)', txt, re.M):
    rows = [[int(v, 16) for v in l.split('defb')[1].split(',')] for l in m.group(3).splitlines()]
    frames[(int(m.group(1)), int(m.group(2)))] = rows
tab = re.findall(r'dw bf_(\d+)_(\d+)\n\s+db (\d+),(\d+)', txt[txt.index('big_tab:'):])
info = {(int(k), int(h)): (int(f), int(n)) for k, h, f, n in tab}
NAMES = ['YOU', 'CYAN', 'WHITE', 'PINK', 'GREEN']
def bits(k, h, HB=40):
    """the frame as two pixel grids (mask, ink), HB rows x 16"""
    f, n = info[(k, h)]; g = [[0] * 16 for _ in range(HB)]; i = [[0] * 16 for _ in range(HB)]
    for r, row in enumerate(frames[(k, h)]):
        mk = (row[0] << 8) | row[2]; ik = (row[1] << 8) | row[3]
        for x in range(16):
            g[f + r][x] = (mk >> (15 - x)) & 1; i[f + r][x] = (ik >> (15 - x)) & 1
    return g, i
def rng(g):
    ys = [y for y, r in enumerate(g) if any(r)]
    return (ys[0], ys[-1]) if ys else (0, 0)
tot = sum(len(v) * 4 for v in frames.values())
print('%d frames, %d bytes of rows (4 bytes a row), big_tab %d bytes' % (len(frames), tot, 4 * len(info)))
PAIRS = [(5, 3), (6, 2), (7, 1), (8, 0), (9, 15), (10, 14), (11, 13)]      # heading a = heading b upside down?
saved = 0; changed = 0
for k in range(5):
    line = []
    for a, b in PAIRS:
        ga, ia = bits(k, a); gb, ib = bits(k, b)
        # upside down about the frame's own middle: find the shift that fits best
        best = None
        ya0, ya1 = rng(ga); yb0, yb1 = rng(gb)
        for sh in range(-6, 7):
          for xs in (0, -1, 1, -2, 2):
            d = 0
            for y in range(40):
                yy = (yb0 + yb1) - y + sh
                for x in range(16):
                    vb = (gb[yy][x - xs], ib[yy][x - xs]) if 0 <= yy < 40 and 0 <= x - xs < 16 else (0, 0)
                    d += (ga[y][x], ia[y][x]) != vb
            if best is None or d < best[0]: best = (d, sh, xs)
        line.append('%d<-%d: %s' % (a, b, 'exact' if best[0] == 0 else '%d px differ' % best[0]) + (' (%d px across)' % best[2] if best[2] else ''))
        saved += len(frames[(k, a)]) * 4; changed += best[0]
    print('%-5s ' % NAMES[k] + '; '.join(line))
print('top-bottom flip when drawn: 9 headings kept of 16 (0-4, 12-15): %d bytes of frames go; %d pixels would change in all' % (saved, changed))
