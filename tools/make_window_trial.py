"""Mock-ups: today's window, one column less, one row less - built from a real
screen captured at a corner (the .scr given), with Spectrum colours."""
import sys, numpy as np
from PIL import Image, ImageDraw
scr = open(sys.argv[1], 'rb').read(); OUT = sys.argv[2]
PAL = [(0,0,0),(0,0,0xD7),(0xD7,0,0),(0xD7,0,0xD7),(0,0xD7,0),(0,0xD7,0xD7),(0xD7,0xD7,0),(0xD7,0xD7,0xD7)]
PALB = [(0,0,0),(0,0,0xFF),(0xFF,0,0),(0xFF,0,0xFF),(0,0xFF,0),(0,0xFF,0xFF),(0xFF,0xFF,0),(0xFF,0xFF,0xFF)]
bm = np.zeros((192, 256), np.uint8)
for y in range(192):
    a = ((y & 0xC0) << 5) | ((y & 7) << 8) | ((y & 0x38) << 2)
    bm[y] = np.unpackbits(np.frombuffer(scr[a:a + 32], np.uint8))
at = np.frombuffer(scr[6144:6912], np.uint8).reshape(24, 32).copy()
def render(bm, at, tint=None):
    img = np.zeros((192 + 48, 256 + 64, 3), np.uint8); img[:] = PAL[6]
    for r in range(24):
        for c in range(32):
            v = int(at[r, c]); ink, paper, br = v & 7, (v >> 3) & 7, (v >> 6) & 1
            pal = PALB if br else PAL
            blk = bm[r*8:r*8+8, c*8:c*8+8]
            img[24+r*8:24+r*8+8, 32+c*8:32+c*8+8] = np.where(blk[..., None] == 1, pal[ink], pal[paper])
    im = Image.fromarray(img)
    if tint:
        ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        for (x0, y0, x1, y1), col in tint: d.rectangle([32 + x0, 24 + y0, 32 + x1, 24 + y1], fill=col)
        im = Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB')
    return im
def frame(bm, x0, y0, x1, y1):           # 2-px frame just outside the window [x0..x1) x [y0..y1)
    bm[y0-2:y0, x0-2:x1+2] = 1; bm[y1:y1+2, x0-2:x1+2] = 1
    bm[y0-2:y1+2, x0-2:x0] = 1; bm[y0-2:y1+2, x1:x1+2] = 1
W0, W1, Y0, Y1 = 8, 192, 32, 160          # today's window, pixels
# A: today
A = render(bm, at)
# B: one column less - 4 px off each side, the window 176 wide, cell 23 back to table yellow
b = bm.copy(); ba = at.copy()
win = bm[Y0:Y1, W0+4:W1-4].copy()
b[Y0-2:Y1+2, 0:200] = 0; b[Y0:Y1, W0:W0+176] = win
ba[4:20, 23] = 0x30; frame(b, W0, Y0, W0 + 176, Y1)
b[0:24, :] = bm[0:24, :]; b[168:192, 0:200] = bm[168:192, 0:200]     # message bar and bottom band unchanged
B = render(b, ba)
# C: one row less - 4 px off top and bottom, the window 120 high; the bottom band moves up a row
c = bm.copy(); ca = at.copy()
win = bm[Y0+4:Y1-4, W0:W1].copy()
c[Y0-2:192, 0:200] = 0; c[Y0:Y0+120, W0:W1] = win
frame(c, W0, Y0, W1, Y0 + 120)
c[160:176, 0:200] = bm[168:184, 0:200]                                   # LAP/TIME and BEST up a row
ca[19, 0:24] = 0x30; ca[20:22, 0:24] = at[21:23, 0:24]; ca[22, 0:24] = 0x30
C = render(c, ca)
# D: today with what each would lose shaded: red = the column option, blue = the row option
D = render(bm, at, tint=[((W0, Y0, W0+3, Y1-1), (255, 0, 0, 110)), ((W1-4, Y0, W1-1, Y1-1), (255, 0, 0, 110)),
                         ((W0, Y0, W1-1, Y0+3), (0, 80, 255, 110)), ((W0, Y1-4, W1-1, Y1-1), (0, 80, 255, 110))])
S = 2
ims = [A, B, C, D]
labels = ['TODAY  23 x 16 cells (184 x 128 px)', 'ONE COLUMN LESS  22 x 16 (176 x 128)', 'ONE ROW LESS  23 x 15 (184 x 120)', 'WHAT EACH LOSES  red = column, blue = row']
w, h = A.size
sheet = Image.new('RGB', (w * S * 2 + 24, (h * S + 40) * 2 + 8), (21, 23, 28))
d = ImageDraw.Draw(sheet)
for i, (im, lab) in enumerate(zip(ims, labels)):
    x, y = (i % 2) * (w * S + 24), (i // 2) * (h * S + 40)
    sheet.paste(im.resize((w * S, h * S), Image.NEAREST), (x, y + 32))
    d.text((x + 8, y + 10), lab, fill=(232, 230, 223))
sheet.save(OUT)
print('ok', sheet.size)
