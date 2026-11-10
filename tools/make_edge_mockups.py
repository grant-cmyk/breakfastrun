"""Window-edge mock-ups: eight ways to edge the play window without the solid
1-pixel rectangle, on a real corner screen of the 22-wide trial. Everything is
drawn in the cells outside the window, once at the start of a race, so none of
them costs anything per picture. Spectrum rules: one ink and one paper a cell."""
import sys, numpy as np
from PIL import Image, ImageDraw
scr = open(sys.argv[1], 'rb').read(); OUT = sys.argv[2]
PAL = [(0,0,0),(0,0,0xD7),(0xD7,0,0),(0xD7,0,0xD7),(0,0xD7,0),(0,0xD7,0xD7),(0xD7,0xD7,0),(0xD7,0xD7,0xD7)]
PALB = [(0,0,0),(0,0,0xFF),(0xFF,0,0),(0xFF,0,0xFF),(0,0xFF,0),(0,0xFF,0xFF),(0xFF,0xFF,0),(0xFF,0xFF,0xFF)]
BLACK, BLUE, RED, MAG, GREEN, CYAN, YEL, WHITE = range(8)
def A(ink, paper, br=0): return (br << 6) | (paper << 3) | ink
bm0 = np.zeros((192, 256), np.uint8)
for y in range(192):
    a = ((y & 0xC0) << 5) | ((y & 7) << 8) | ((y & 0x38) << 2)
    bm0[y] = np.unpackbits(np.frombuffer(scr[a:a + 32], np.uint8))
at0 = np.frombuffer(scr[6144:6912], np.uint8).reshape(24, 32).copy()
WC0, WC1, WR0, WR1 = 1, 22, 4, 19
X0, X1, Y0, Y1 = WC0 * 8, (WC1 + 1) * 8, WR0 * 8, (WR1 + 1) * 8      # window pixels [X0,X1) x [Y0,Y1)
def inwin(r, c): return WR0 <= r <= WR1 and WC0 <= c <= WC1
def panel(r, c): return 25 <= c <= 31 and (1 <= r <= 3 or 5 <= r <= 15 or 17 <= r <= 22)
HUD = {(r, c) for r in (1, 2, 21, 22) for c in range(1, 23)}
def free(r, c): return not inwin(r, c) and not panel(r, c) and (r, c) not in HUD
RING = [(r, c) for r in range(WR0 - 1, WR1 + 2) for c in range(WC0 - 1, WC1 + 2) if not inwin(r, c)]
def base(attr, hud):
    bm = bm0.copy(); at = at0.copy()
    for r in range(24):
        for c in range(32):
            if free(r, c): bm[r*8:r*8+8, c*8:c*8+8] = 0; at[r, c] = attr
    for r, c in HUD: at[r, c] = hud
    return bm, at
def cell(bm, r, c, rows):
    for j, s in enumerate(rows): bm[r*8+j, c*8:c*8+8] = [ch == '#' for ch in s]
def render(bm, at, border):
    img = np.zeros((192 + 48, 256 + 64, 3), np.uint8); img[:] = PAL[border]
    for r in range(24):
        for c in range(32):
            v = int(at[r, c]); pal = PALB if v & 64 else PAL
            blk = bm[r*8:r*8+8, c*8:c*8+8]
            img[24+r*8:24+r*8+8, 32+c*8:32+c*8+8] = np.where(blk[..., None] == 1, pal[v & 7], pal[(v >> 3) & 7])
    return Image.fromarray(img)
def rect(bm, x0, y0, x1, y1): bm[y0:y1, x0:x1] = 1
def frame_px(bm, d, t):              # a band t px thick, d px outside the window
    rect(bm, X0-d-t, Y0-d-t, X1+d+t, Y0-d); rect(bm, X0-d-t, Y1+d, X1+d+t, Y1+d+t)
    rect(bm, X0-d-t, Y0-d, X0-d, Y1+d); rect(bm, X1+d, Y0-d, X1+d+t, Y1+d)
shots = []
YW = A(BLACK, YEL)
# A - no line: the colour change is the edge
bm, at = base(YW, YW); shots.append(('A  NO LINE - THE COLOUR CHANGE IS THE EDGE', render(bm, at, YEL)))
# B - drop shadow: the window floats above the table
bm, at = base(YW, YW)
rect(bm, X1, Y0 + 4, X1 + 4, Y1 + 4); rect(bm, X0 + 4, Y1, X1 + 4, Y1 + 4)
shots.append(('B  DROP SHADOW, NO OUTLINE', render(bm, at, YEL)))
# C - corner brackets only, like a camera viewfinder
bm, at = base(YW, YW)
L, T, D = 14, 2, 2
for (x, sx) in ((X0 - D - T, 1), (X1 + D, -1)):
    for (y, sy) in ((Y0 - D - T, 1), (Y1 + D, -1)):
        xa = x if sx == 1 else x + T - L; ya = y if sy == 1 else y + T - L
        rect(bm, xa, y, xa + L, y + T); rect(bm, x, ya, x + T, ya + L)
shots.append(('C  CORNER BRACKETS ONLY', render(bm, at, YEL)))
# D - kerb band: red and white 4-px checks, like the track's own kerbs
bm, at = base(YW, YW)
CHK = ['####....'] * 4 + ['....####'] * 4
for r, c in RING:
    if free(r, c) or r == WR0 - 1: at[r, c] = A(RED, WHITE, 1); cell(bm, r, c, CHK)
shots.append(('D  KERB BAND, RED AND WHITE', render(bm, at, YEL)))
# E - tyre wall on grass, tyres painted white and black in turn
G = A(BLACK, GREEN)
bm, at = base(G, A(BLACK, GREEN))
TYRE = ['..####..', '.######.', '###..###', '##....##', '##....##', '###..###', '.######.', '..####..']
for i, (r, c) in enumerate(RING):
    at[r, c] = A(WHITE if (r + c) % 2 else BLACK, GREEN); cell(bm, r, c, TYRE)
shots.append(('E  TYRE WALL ON GRASS', render(bm, at, GREEN)))
# F - plate: a white china rim with a blue wavy band, rounded, on a blue cloth
B_ = A(BLUE, BLUE)
bm, at = base(B_, A(WHITE, BLUE))
for r, c in RING: at[r, c] = A(BLUE, WHITE, 1)
for x in range(X0 - 8, X1 + 8):                                   # wavy band 3-4 px out
    w = (x // 3) % 2
    bm[Y0 - 4 - w, x] = 1; bm[Y1 + 3 + w, x] = 1
for y in range(Y0 - 8, Y1 + 8):
    w = (y // 3) % 2
    bm[y, X0 - 4 - w] = 1; bm[y, X1 + 3 + w] = 1
shots.append(('F  SQUARE PLATE: CHINA RIM, BLUE CLOTH', render(bm, at, BLUE)))
# G - stitched hem: a running stitch 2 px out on a red cloth
R_ = A(WHITE, RED)
bm, at = base(R_, R_)
for x in range(X0 - 3, X1 + 3):
    if x % 5 < 3: bm[Y0 - 3, x] = 1; bm[Y1 + 2, x] = 1
for y in range(Y0 - 3, Y1 + 3):
    if y % 5 < 3: bm[y, X0 - 3] = 1; bm[y, X1 + 2] = 1
shots.append(('G  STITCHED HEM ON A RED CLOTH', render(bm, at, RED)))
# H - arcade bezel: a thick black band with rounded outer corners
bm, at = base(YW, YW)
frame_px(bm, 0, 7)
for k, n in enumerate([4, 2, 1, 1]):
    for (x, dx) in ((X0 - 7, 1), (X1 + 6, -1)):
        for (y, dy) in ((Y0 - 7, 1), (Y1 + 6, -1)):
            for i in range(n): bm[y + dy * k, x + dx * i] = 0; bm[y + dy * i, x + dx * k] = 0
shots.append(('H  ARCADE BEZEL, ROUNDED CORNERS', render(bm, at, YEL)))
# sheet: 4 x 2 at 2x, then a strip of top-left corner close-ups at 5x
S = 2; w, h = shots[0][1].size
cols, rows = 4, 2
sheet = Image.new('RGB', (cols * (w * S + 24) - 24, rows * (h * S + 40)), (21, 23, 28)); d = ImageDraw.Draw(sheet)
for i, (lab, im) in enumerate(shots):
    x, y = (i % cols) * (w * S + 24), (i // cols) * (h * S + 40)
    sheet.paste(im.resize((w * S, h * S), Image.NEAREST), (x, y + 32)); d.text((x + 8, y + 10), lab, fill=(232, 230, 223))
    im.resize((w * 3, h * 3), Image.NEAREST).save(OUT.replace('.png', '_%s.png' % 'abcdefgh'[i]))
sheet.save(OUT)
Z, cw, ch = 5, 72, 56                                              # crop round the top-left corner
crop = (32 + X0 - 24, 24 + Y0 - 20)
strip = Image.new('RGB', (4 * (cw * Z + 16) - 16, 2 * (ch * Z + 36)), (21, 23, 28)); d = ImageDraw.Draw(strip)
for i, (lab, im) in enumerate(shots):
    x, y = (i % 4) * (cw * Z + 16), (i // 4) * (ch * Z + 36)
    c = im.crop((crop[0], crop[1], crop[0] + cw, crop[1] + ch)).resize((cw * Z, ch * Z), Image.NEAREST)
    strip.paste(c, (x, y + 28)); d.text((x + 4, y + 8), lab[:1] + ' - top-left corner, 5x', fill=(232, 230, 223))
strip.save(OUT.replace('.png', '_corners.png')); print('ok')
