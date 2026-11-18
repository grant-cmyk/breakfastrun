"""Mock-ups: variations of health option C - the race order's right three squares black, the health big in them (Grant,
18 Nov 2026: "for health can you do variations of C - then we don't need the mug or the corner display"). Every square
keeps to two colours: black paper and one ink. Example health, top row to bottom: 6, 2, 5, 1, 4 pieces of 6.
Usage: python3 tools/make_health_c_mock.py <screen 352x288>. Writes docs/design/racetrack/health_c_options.png."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
src = np.array(Image.open(sys.argv[1]).convert('RGB'))
X0, Y0, RW, RH = 256, 96, 48, 16
HP = [6, 2, 5, 1, 4]
K, R, G, Y, W = (0, 0, 0), (215, 0, 0), (0, 215, 0), (215, 215, 0), (215, 215, 215)
lvl = lambda n: G if n > 3 else Y if n > 1 else R
def base(a, r):
    a[Y0 + r * RH:Y0 + (r + 1) * RH, X0 + 24:X0 + RW] = K; return Y0 + r * RH
def put(a, x, y, rows, col):
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == '#': a[y + j, x + i] = col
def c1(a):                                   # three big blocks, half a block a piece, the colour by health
    for r, n in enumerate(HP):
        y0 = base(a, r)
        for b in range(3):
            x = X0 + 25 + b * 8; f = n - 2 * b
            if f >= 2: a[y0 + 2:y0 + 14, x:x + 6] = lvl(n)
            elif f == 1: a[y0 + 8:y0 + 14, x:x + 6] = lvl(n)
    return a
def c2(a):                                   # six thin blocks, one a piece (two a square), the colour by health
    for r, n in enumerate(HP):
        y0 = base(a, r)
        for p in range(n): x = X0 + 25 + p * 4; a[y0 + 2:y0 + 14, x:x + 3] = lvl(n)
    return a
def c3(a):                                   # three blocks, each its OWN colour: whole green, half yellow, gone a red outline
    for r, n in enumerate(HP):
        y0 = base(a, r)
        for b in range(3):
            x = X0 + 25 + b * 8; f = n - 2 * b
            if f >= 2: a[y0 + 2:y0 + 14, x:x + 6] = G
            elif f == 1: a[y0 + 8:y0 + 14, x:x + 6] = Y; a[y0 + 2:y0 + 8, x] = Y; a[y0 + 2:y0 + 8, x + 5] = Y; a[y0 + 2, x:x + 6] = Y
            else:
                a[y0 + 2, x:x + 6] = R; a[y0 + 13, x:x + 6] = R; a[y0 + 2:y0 + 14, x] = R; a[y0 + 2:y0 + 14, x + 5] = R
    return a
SHIELD = ['#######', '#######', '#######', '#######', '.#####.', '.#####.', '..###..', '...#...']
SHIELD_H = ['#######', '#.....#', '#.....#', '#######', '.#####.', '.#####.', '..###..', '...#...']
SHIELD_0 = ['#######', '#.....#', '#.....#', '#.....#', '.#...#.', '.#...#.', '..#.#..', '...#...']
def c4(a):                                   # three shields, full / half / empty, the colour by health
    for r, n in enumerate(HP):
        y0 = base(a, r)
        for b in range(3):
            f = n - 2 * b; put(a, X0 + 24 + b * 8, y0 + 4, SHIELD if f >= 2 else SHIELD_H if f == 1 else SHIELD_0, lvl(n))
    return a
def c5(a):                                   # a number, big: the pieces left, 0-6, the colour by health
    DIG = {str(d): Image.new('1', (8, 8)) for d in range(7)}
    rom = open('/home/user/zx-emulator/roms/48.rom', 'rb').read()
    for r, n in enumerate(HP):
        y0 = base(a, r)
        g = rom[0x3D00 + (ord(str(n)) - 32) * 8:0x3D00 + (ord(str(n)) - 32) * 8 + 8]
        for j in range(8):
            for i in range(8):
                if g[j] & (0x80 >> i): a[y0 + j * 2:y0 + j * 2 + 2, X0 + 28 + i * 2:X0 + 28 + i * 2 + 2] = lvl(n)
    return a
S = 3; fnt = ImageFont.load_default()
OPTS = [('C', 'three blocks, colour by health (as shown)', c1), ('C2', 'six thin blocks, one a piece', c2),
        ('C3', 'three blocks, each its own colour', c3), ('C4', 'three shields: full, half, empty', c4),
        ('C5', 'the pieces left as a big number', c5)]
crop = lambda a: Image.fromarray(a.astype(np.uint8)).crop((250, 88, 310, 182)).resize((60 * S, 94 * S), Image.NEAREST)
sheet = Image.new('RGB', (len(OPTS) * (60 * S + 14) + 14, 94 * S + 60), (40, 42, 48)); d = ImageDraw.Draw(sheet)
for i, (tag, what, fn) in enumerate(OPTS):
    ox = 14 + i * (60 * S + 14); d.text((ox, 8), tag, fill=(255, 212, 0), font=fnt); d.text((ox, 20), what, fill=(236, 235, 230), font=fnt)
    sheet.paste(crop(fn(src.copy())), (ox, 38))
d.text((14, 94 * S + 44), 'Example health, top to bottom: 6, 2, 5, 1, 4 pieces of 6. The red row is you.', fill=(236, 235, 230), font=fnt)
out = os.path.join(ROOT, 'docs', 'design', 'racetrack', 'health_c_options.png'); sheet.save(out); print('wrote', out)
