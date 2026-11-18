"""Mock-ups: ways to show each car's health (armour) clearly (Grant, 18 Nov 2026: "The vertical health bars are not
visible, and the coffee cup is no longer relevant ... new ways to track the health. It needs to be quite visible").
Drawn on a real screen of the armour tape. Example health, top row to bottom: 6, 2, 5, 1, 4 pieces of 6.
Usage: python3 tools/make_health_mock.py <screen 352x288>. Writes docs/design/racetrack/health_options.png.
Nothing here is in the game."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
src = np.array(Image.open(sys.argv[1]).convert('RGB'))
X0, Y0, RW, RH = 256, 96, 48, 16
HP = [6, 2, 5, 1, 4]
K, W, R, G, Y = (0, 0, 0), (215, 215, 215), (215, 0, 0), (0, 215, 0), (215, 215, 0)
def rowcol(a, r): return tuple(int(v) for v in a[Y0 + r * RH + 1, X0 + 1])
def strip_bars(a):                                       # take today's thin bars off (the right 5 px of each row)
    for r in range(5): a[Y0 + r * RH:Y0 + (r + 1) * RH, X0 + RW - 5:X0 + RW] = rowcol(a, r)
    return a
def ink_of(c): return W if c[0] > 200 and c[1] < 60 and c[2] < 60 else K
def drain(a):                                            # A: the row's colour IS the gauge - one square (8 px) per piece, from the
    for r, n in enumerate(HP):                           # right; a lost square turns black, its ink white so nothing in it is lost
        c = np.array(rowcol(a, r))
        for q in range(n, 6):
            blk = a[Y0 + r * RH:Y0 + (r + 1) * RH, X0 + q * 8:X0 + q * 8 + 8]
            paper = (blk == c).all(axis=2); blk[paper] = K; blk[~paper] = W
    return a
def thick(a):                                            # B: six blocks along the foot of each row, in the row's own ink (the
    for r, n in enumerate(HP):                           # same two colours as the row, so no clash); a lost block is an outline
        c = rowcol(a, r); ink = ink_of(c); y = Y0 + r * RH + 12
        a[y:y + 4, X0:X0 + RW] = c
        for p in range(6):
            x = X0 + 1 + p * 8
            a[y:y + 3, x:x + 6] = ink
            if p >= n: a[y + 1, x + 1:x + 5] = c
    return a
def blocks(a):                                           # C: the row's right three squares black, three big blocks - green, then
    for r, n in enumerate(HP):                           # yellow at 3 or less, red at 1 (one ink a square: allowed). Half a block a piece.
        y0 = Y0 + r * RH
        a[y0:y0 + RH, X0 + 24:X0 + RW] = K
        col = G if n > 3 else Y if n > 1 else R
        for b in range(3):
            x = X0 + 25 + b * 8; full = n - 2 * b
            if full >= 2: a[y0 + 2:y0 + 14, x:x + 6] = col
            elif full == 1: a[y0 + 8:y0 + 14, x:x + 6] = col
    return a
def own(a):                                              # D: YOUR health big, where the mug was; a red border flash when low
    a[8 + 48 + 136:8 + 48 + 152, 8 + 48 + 168:8 + 48 + 192] = K
    n = HP[4]
    for p in range(6):
        x = 8 + 48 + 169 + p * 4; col = G if n > 3 else Y if n > 1 else R
        a[8 + 48 + 138:8 + 48 + 150, x:x + 3] = col
        if p >= n: a[8 + 48 + 139:8 + 48 + 149, x + 1:x + 2] = K      # (a lost piece: its outline, in the same ink)
    return a
S = 3; fnt = ImageFont.load_default()
base = strip_bars(src.copy())
OPTS = [('NOW', 'thin bars at the edge', src),
        ('A', "the row's colour shortens, a square a piece", drain(base.copy())),
        ('B', "six blocks along each row's foot", thick(base.copy())),
        ('C', 'three big blocks, green/yellow/red (gap time goes)', blocks(base.copy())),
        ('D', 'C, and yours big in place of the mug', own(blocks(base.copy())))]
crop = lambda a: Image.fromarray(a.astype(np.uint8)).crop((150, 84, 316, 210)).resize((166 * S, 126 * S), Image.NEAREST)
sheet = Image.new('RGB', (3 * (166 * S + 12) + 12, 2 * (126 * S + 30) + 8), (40, 42, 48)); d = ImageDraw.Draw(sheet)
for i, (tag, what, a) in enumerate(OPTS):
    ox = 12 + (i % 3) * (166 * S + 12); oy = 6 + (i // 3) * (126 * S + 30)
    d.text((ox, oy), tag + ': ' + what, fill=(236, 235, 230), font=fnt); sheet.paste(crop(a), (ox, oy + 18))
d.text((12 + 2 * (166 * S + 12), 6 + 126 * S + 30 + 20), 'Example health, top to bottom:\n6, 2, 5, 1, 4 pieces of 6\n(you are the red row, 4 of 6)', fill=(236, 235, 230), font=fnt)
out = os.path.join(ROOT, 'docs', 'design', 'racetrack', 'health_options.png'); sheet.save(out); print('wrote', out)
