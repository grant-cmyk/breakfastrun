"""HUD mock-ups as real Spectrum screens: a 256x192 bitmap, one ink/paper/bright
attribute per 8x8 cell, the ROM font, the real race frame and the real cars."""
import json, os, numpy as np
from PIL import Image
S = os.environ['S']
P = json.load(open(S + '/parts.json')); FONT = P['font']; CARS = P['cars']
WIN = np.load(S + '/win.npy')
PAL = [(0,0,0),(0,0,0xD7),(0xD7,0,0),(0xD7,0,0xD7),(0,0xD7,0),(0,0xD7,0xD7),(0xD7,0xD7,0),(0xD7,0xD7,0xD7)]
PALB = [(0,0,0),(0,0,0xFF),(0xFF,0,0),(0xFF,0,0xFF),(0,0xFF,0),(0,0xFF,0xFF),(0xFF,0xFF,0),(0xFF,0xFF,0xFF)]
BLACK, BLUE, RED, MAG, GREEN, CYAN, YEL, WHITE = range(8)
class Screen:
    def __init__(s, paper=YEL, border=YEL):
        s.bm = np.zeros((192, 256), np.uint8); s.border = border
        s.attr = [[(BLACK, paper, 0) for _ in range(32)] for _ in range(24)]
    def cells(s, r0, c0, r1, c1, ink, paper, bright=0):
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1): s.attr[r][c] = (ink, paper, bright)
    def text(s, r, c, t, ink=BLACK, paper=None, bright=0):
        for i, ch in enumerate(t):
            g = FONT[(ord(ch) - 32) * 8:(ord(ch) - 31) * 8]
            for j in range(8): s.bm[r * 8 + j, (c + i) * 8:(c + i) * 8 + 8] = np.unpackbits(np.uint8(g[j]))
            if paper is not None: s.attr[r][c + i] = (ink, paper, bright)
    def big(s, r, c, t, ink=BLACK, paper=None, bright=0):     # font at 2x: 2x2 cells a letter
        for i, ch in enumerate(t):
            g = FONT[(ord(ch) - 32) * 8:(ord(ch) - 31) * 8]
            for j in range(8):
                row = np.repeat(np.unpackbits(np.uint8(g[j])), 2)
                for k in (0, 1): s.bm[r * 8 + 2 * j + k, (c + 2 * i) * 8:(c + 2 * i) * 8 + 16] = row
            if paper is not None: s.cells(r, c + 2 * i, r + 1, c + 2 * i + 1, ink, paper, bright)
    def car(s, y, x, k):
        for j, (m0, i0, m1, i1) in enumerate(CARS[k]):
            for bb, (m, ink) in enumerate(((m0, i0), (m1, i1))):
                mb, ib = np.unpackbits(np.uint8(m)), np.unpackbits(np.uint8(ink))
                seg = s.bm[y + j, x + 8 * bb:x + 8 * bb + 8]
                seg[mb == 1] = 0; seg[ib == 1] = 1
    def window(s, r0, c0, wcols, rows=16):
        x0 = (192 - wcols * 8) // 2                          # crop the real frame round your car
        s.bm[r0 * 8:r0 * 8 + rows * 8, c0 * 8:(c0 + wcols) * 8] = WIN[:rows * 8, x0:x0 + wcols * 8]
        s.cells(r0, c0, r0 + rows - 1, c0 + wcols - 1, BLACK, WHITE, 1)
        y0, y1, xa, xb = r0 * 8 - 2, (r0 + rows) * 8 + 1, c0 * 8 - 2, (c0 + wcols) * 8 + 1
        s.bm[y0:y0 + 2, xa:xb + 1] = 1; s.bm[y1 - 1:y1 + 1, xa:xb + 1] = 1
        s.bm[y0:y1 + 1, xa:xa + 2] = 1; s.bm[y0:y1 + 1, xb - 1:xb + 1] = 1
    def png(s, path, scale=3):
        img = np.zeros((192 + 48, 256 + 64, 3), np.uint8); img[:] = PAL[s.border]
        for r in range(24):
            for c in range(32):
                ink, paper, br = s.attr[r][c]; pal = PALB if br else PAL
                blk = s.bm[r * 8:r * 8 + 8, c * 8:c * 8 + 8]
                img[24 + r * 8:24 + r * 8 + 8, 32 + c * 8:32 + c * 8 + 8] = np.where(blk[..., None] == 1, pal[ink], pal[paper])
        Image.fromarray(img).resize((img.shape[1] * scale, img.shape[0] * scale), Image.NEAREST).save(path)

# A - bottom strip: 22 wide, centred; one HUD line under the window
a = Screen(); a.window(4, 5, 22)
a.text(1, 9, 'BREAKFAST RUN')
a.text(21, 5, 'LAP 2/3'); a.text(21, 14, '3RD', WHITE, RED, 1); a.text(21, 21, '0:42.6')
a.png(S + '/mock_a.png')

# B - position tower: 23 wide at the left, a panel on the right
b = Screen(); b.window(4, 1, 23)
b.text(1, 1, 'BREAKFAST RUN')
b.text(4, 25, ' RACE ', WHITE, BLUE, 1)
order = [1, 3, 0, 2, 4]                                     # leader first; you are 3rd
paper = {0: RED, 1: CYAN, 2: GREEN, 3: MAG, 4: WHITE}
for i, k in enumerate(order):
    r = 6 + 2 * i
    b.cells(r, 25, r + 1, 30, BLACK, paper[k], 1)
    b.text(r, 25, str(i + 1), BLACK, paper[k], 1)
    b.car(r * 8, 27 * 8, k)
    if k == 0: b.cells(r, 25, r + 1, 30, WHITE, RED, 1)
b.text(17, 25, 'LAP'); b.big(18, 25, '2', BLACK, YEL, 1); b.text(19, 27, '/3')
b.text(21, 25, '0:42')
b.png(S + '/mock_b.png')

# C - top banner: 22 wide, window moved down; a big place on the left
c = Screen(); c.window(6, 5, 22)
c.big(1, 5, '3RD', WHITE, RED, 1)
c.text(1, 19, 'LAP   2/3'); c.text(2, 19, 'TIME 0:42'); c.text(3, 19, 'BEST 0:14')
c.text(23, 9, 'BREAKFAST RUN')
c.png(S + '/mock_c.png')

# D - wings: 22 wide, centred; lap on the left wing, the field on the right wing
d = Screen(); d.window(4, 5, 22)
d.text(1, 9, 'BREAKFAST RUN')
d.text(4, 0, 'LAP'); d.big(6, 0, '2', WHITE, BLUE, 1); d.text(7, 2, '/3')
d.text(11, 0, 'TIME'); d.text(12, 0, '0:42')
for i, k in enumerate(order):
    r = 4 + 3 * i
    pk, ik = (RED, WHITE) if k == 0 else (paper[k], BLACK)
    d.cells(r, 28, r + 1, 31, ik, pk, 1)
    d.text(r, 28, str(i + 1), ik, pk, 1)
    d.car(r * 8, 29 * 8 + 4, k)
d.png(S + '/mock_d.png')
print('ok')
