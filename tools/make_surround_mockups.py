"""Surround mock-ups: four themes for everything outside the play window, on
a real screen captured at a corner (22-wide trial). Spectrum rules: one ink and
one paper per 8x8 cell, 15 colours. The surround is drawn once, so any of these
costs nothing per picture."""
import sys, numpy as np
from PIL import Image, ImageDraw
scr = open(sys.argv[1], 'rb').read(); OUT = sys.argv[2]
PAL = [(0,0,0),(0,0,0xD7),(0xD7,0,0),(0xD7,0,0xD7),(0,0xD7,0),(0,0xD7,0xD7),(0xD7,0xD7,0),(0xD7,0xD7,0xD7)]
PALB = [(0,0,0),(0,0,0xFF),(0xFF,0,0),(0xFF,0,0xFF),(0,0xFF,0),(0,0xFF,0xFF),(0xFF,0xFF,0),(0xFF,0xFF,0xFF)]
BLACK, BLUE, RED, MAG, GREEN, CYAN, YEL, WHITE = range(8)
def A(ink, paper, br=1): return (br << 6) | (paper << 3) | ink
bm0 = np.zeros((192, 256), np.uint8)
for y in range(192):
    a = ((y & 0xC0) << 5) | ((y & 7) << 8) | ((y & 0x38) << 2)
    bm0[y] = np.unpackbits(np.frombuffer(scr[a:a + 32], np.uint8))
at0 = np.frombuffer(scr[6144:6912], np.uint8).reshape(24, 32).copy()
WC0, WC1, WR0, WR1 = 1, 22, 4, 19                 # the window's cells
def keep(r, c):                                   # cells the surround must not touch
    if WR0 <= r <= WR1 and WC0 <= c <= WC1: return True                       # window
    if 25 <= c <= 31 and (1 <= r <= 3 or 5 <= r <= 15 or 17 <= r <= 22): return True   # panel
    return False
HUDTXT = [(r, c) for r in (1, 2) for c in range(1, 23)] + [(r, c) for r in (21, 22) for c in range(1, 23)]
def base():
    bm = bm0.copy(); at = at0.copy()
    for r in range(24):                           # wipe the old frame and surround
        for c in range(32):
            if not keep(r, c) and (r, c) not in HUDTXT:
                bm[r*8:r*8+8, c*8:c*8+8] = 0
    return bm, at
def cell(bm, r, c, rows):                         # 8 strings of 8 '#'/'.' into a cell
    for j, s in enumerate(rows):
        bm[r*8+j, c*8:c*8+8] = [1 if ch == '#' else 0 for ch in s]
def surround(bm, at, fn):
    for r in range(24):
        for c in range(32):
            if not keep(r, c) and (r, c) not in HUDTXT: fn(bm, at, r, c)
def hud_strip(bm, at, attr):
    for r, c in HUDTXT: at[r, c] = attr
def render(bm, at, border=None):
    img = np.zeros((192 + 48, 256 + 64, 3), np.uint8)
    img[:] = PAL[border if border is not None else int(at[0, 0]) >> 3 & 7]
    for r in range(24):
        for c in range(32):
            v = int(at[r, c]); ink, paper, br = v & 7, (v >> 3) & 7, (v >> 6) & 1
            pal = PALB if br else PAL
            blk = bm[r*8:r*8+8, c*8:c*8+8]
            img[24+r*8:24+r*8+8, 32+c*8:32+c*8+8] = np.where(blk[..., None] == 1, pal[ink], pal[paper])
    return Image.fromarray(img)
CHK = ['####....'] * 4 + ['....####'] * 4
DITH = ['#.#.#.#.', '.#.#.#.#'] * 4
# A - gingham tablecloth: 2x2-cell checks, red / white, blended where they cross
bm, at = base()
def gingham(bm, at, r, c):
    a, b = (r // 2) % 2, (c // 2) % 2
    if a and b: at[r, c] = A(RED, RED)
    elif not a and not b: at[r, c] = A(WHITE, WHITE)
    else: at[r, c] = A(RED, WHITE); cell(bm, r, c, DITH)
surround(bm, at, gingham); hud_strip(bm, at, A(BLACK, WHITE))
for r in range(WR0 - 1, WR1 + 2):                  # a white rim round the window, black line inside
    for c in range(WC0 - 1, WC1 + 2):
        if not keep(r, c) and (r, c) not in HUDTXT and (r in (WR0 - 1, WR1 + 1) or c in (WC0 - 1, WC1 + 1)):
            at[r, c] = A(BLACK, WHITE); bm[r*8:r*8+8, c*8:c*8+8] = 0
x0, x1, y0, y1 = WC0 * 8, (WC1 + 1) * 8, WR0 * 8, (WR1 + 1) * 8
bm[y0-2:y0, x0-2:x1+2] = 1; bm[y1:y1+2, x0-2:x1+2] = 1; bm[y0:y1, x0-2:x0] = 1; bm[y0:y1, x1:x1+2] = 1
IA = render(bm, at, RED)
# B - chequered-flag frame on green baize
bm, at = base()
def baize(bm, at, r, c):
    at[r, c] = A(GREEN, GREEN, 0)
surround(bm, at, baize); hud_strip(bm, at, A(WHITE, GREEN, 0))
for r in range(WR0 - 1, WR1 + 2):
    for c in range(WC0 - 1, WC1 + 2):
        if (r in (WR0 - 1, WR1 + 1) or c in (WC0 - 1, WC1 + 1)) and not keep(r, c):
            at[r, c] = A(BLACK, WHITE); cell(bm, r, c, CHK)
IB = render(bm, at)
# C - wooden table, and the window as a placemat with a lace edge
bm, at = base()
GRAIN = ['########', '........', '...##...', '........', '########', '........', '.....#..', '........']
def wood(bm, at, r, c):
    at[r, c] = A(YEL, RED, 0)
    rows = GRAIN[(r * 3) % 8:] + GRAIN[:(r * 3) % 8]
    cell(bm, r, c, [s[c % 8:] + s[:c % 8] for s in rows])
surround(bm, at, wood); hud_strip(bm, at, A(YEL, RED, 0))
LACE_T = ['........', '..####..', '.#....#.', '#..##..#', '#.#..#.#', '########', '########', '########']
for c in range(WC0 - 1, WC1 + 2):
    for r, rows in ((WR0 - 1, LACE_T), (WR1 + 1, LACE_T[::-1])):
        at[r, c] = A(BLACK, WHITE) if False else A(WHITE, RED, 1); cell(bm, r, c, rows)
for r in range(WR0, WR1 + 1):
    at[r, WC0 - 1] = A(WHITE, RED, 1); cell(bm, r, WC0 - 1, [''.join(row[7 - i] for row in LACE_T) for i in range(8)])
    left = [''.join(row[7 - i] for row in LACE_T) for i in range(8)]
    at[r, WC1 + 1] = A(WHITE, RED, 1); cell(bm, r, WC1 + 1, [x[::-1] for x in left])
IC = render(bm, at)
# D - kitchen tiles: 2x2-cell blue and white tiles with a corner motif, blue grout
bm, at = base()
TILE = {(0, 0): ['########', '#.......', '#..##...', '#.#.....', '#.#.....', '#.......', '#.......', '#.......'],
        (0, 1): ['########', '.......#', '...##..#', '.....#.#', '.....#.#', '.......#', '.......#', '.......#'],
        (1, 0): ['#.......', '#.......', '#.......', '#.#.....', '#.#.....', '#..##...', '#.......', '########'],
        (1, 1): ['.......#', '.......#', '.......#', '.....#.#', '.....#.#', '...##..#', '.......#', '########']}
def tiles(bm, at, r, c):
    at[r, c] = A(BLUE, WHITE); cell(bm, r, c, TILE[(r % 2, c % 2)])
surround(bm, at, tiles); hud_strip(bm, at, A(WHITE, BLUE))
for r in range(WR0 - 1, WR1 + 2):
    for c in range(WC0 - 1, WC1 + 2):
        if (r in (WR0 - 1, WR1 + 1) or c in (WC0 - 1, WC1 + 1)) and not keep(r, c):
            at[r, c] = A(WHITE, BLUE); bm[r*8:r*8+8, c*8:c*8+8] = 0
x0, x1, y0, y1 = WC0 * 8, (WC1 + 1) * 8, WR0 * 8, (WR1 + 1) * 8
bm[y0-3:y0-1, x0-3:x1+3] = 1; bm[y1+1:y1+3, x0-3:x1+3] = 1; bm[y0-3:y1+3, x0-3:x0-1] = 1; bm[y0-3:y1+3, x1+1:x1+3] = 1
ID = render(bm, at)
labels = ['A  GINGHAM TABLECLOTH', 'B  CHEQUERED-FLAG FRAME ON GREEN', 'C  WOODEN TABLE, LACE PLACEMAT', 'D  KITCHEN TILES']
S = 2; w, h = IA.size
sheet = Image.new('RGB', (w * S * 2 + 24, (h * S + 40) * 2 + 8), (21, 23, 28)); d = ImageDraw.Draw(sheet)
for i, (im, lab) in enumerate(zip([IA, IB, IC, ID], labels)):
    x, y = (i % 2) * (w * S + 24), (i // 2) * (h * S + 40)
    sheet.paste(im.resize((w * S, h * S), Image.NEAREST), (x, y + 32)); d.text((x + 8, y + 10), lab, fill=(232, 230, 223))
    im.resize((w * 3, h * 3), Image.NEAREST).save(OUT.replace('.png', '_%s.png' % 'abcd'[i]))
sheet.save(OUT); print('ok')
