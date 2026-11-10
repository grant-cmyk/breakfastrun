"""Layout review mock-ups (Grant, 10 Nov 2026: "review the overall design and, within the zx
spectrum limitations of pixels and colour and colour clash, make some design recommendations
for the layout"; then "the faces at the bottom are too blocky - they should be smaller").
Works on a real race screen (screen memory saved from the emulator), so every change keeps to
the Spectrum's rules: 256 x 192 pixels, one ink and one paper colour per 8 x 8 cell, BRIGHT per
cell. Writes docs/design/layout_now.png (the screen today, numbered) and
docs/design/layout_proposed.png (the recommendations applied), both shown 3x with the border.
Usage: make_layout_review.py race.scr"""
import os, sys, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import zx
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
FONT = open(os.path.join(os.path.dirname(zx.__file__), 'roms', 'Spectrum48.rom'), 'rb').read()[0x3D00:0x4000]
PAL = [(0, 0, 0), (0, 0, 215), (215, 0, 0), (215, 0, 215), (0, 215, 0), (0, 215, 215), (215, 215, 0), (215, 215, 215)]
PALB = [(0, 0, 0), (0, 0, 255), (255, 0, 0), (255, 0, 255), (0, 255, 0), (0, 255, 255), (255, 255, 0), (255, 255, 255)]

def load(path):
    m = open(path, 'rb').read()
    bits = np.zeros((192, 256), dtype=np.uint8)
    for y in range(192):
        a = ((y & 0xC0) << 5) | ((y & 7) << 8) | ((y & 0x38) << 2)
        for xb in range(32):
            v = m[a + xb]
            for i in range(8): bits[y, xb * 8 + i] = (v >> (7 - i)) & 1
    attrs = np.frombuffer(m[6144:6912], dtype=np.uint8).reshape(24, 32).copy()
    return bits, attrs

def render(bits, attrs, border=6, s=3):
    im = Image.new('RGB', (256 + 64, 192 + 48), PAL[border]); px = im.load()
    for y in range(192):
        for x in range(256):
            a = attrs[y >> 3, x >> 3]; pal = PALB if a & 0x40 else PAL
            px[32 + x, 24 + y] = pal[a & 7] if bits[y, x] else pal[(a >> 3) & 7]
    return im.resize((im.width * s, im.height * s), Image.NEAREST)

def text(bits, s, cx, cy, big=False):            # ROM letters at cell (cx, cy); big = 2x
    for k, ch in enumerate(s):
        g = FONT[(ord(ch) - 32) * 8:(ord(ch) - 32) * 8 + 8]
        for j in range(8):
            for i in range(8):
                on = (g[j] >> (7 - i)) & 1
                if big:
                    bits[cy * 8 + 2 * j:cy * 8 + 2 * j + 2, (cx + 2 * k) * 8 + 2 * i:(cx + 2 * k) * 8 + 2 * i + 2] = on
                else:
                    bits[cy * 8 + j, (cx + k) * 8 + i] = on

def face(name):
    t = open(os.path.join(HERE, 'face_art.txt')).read()
    return re.search(r'== %s face ==\n((?:[X.]{16}\n){16})' % name, t).group(1).split()

def cells(attrs, c0, r0, w, h, a): attrs[r0:r0 + h, c0:c0 + w] = a

if __name__ == '__main__':
    bits, attrs = load(sys.argv[1])
    out = os.path.join(ROOT, 'docs', 'design')
    # ---- today, numbered
    now = render(bits, attrs); d = ImageDraw.Draw(now)
    try: f = ImageFont.truetype('DejaVuSans-Bold.ttf', 22)
    except OSError: f = ImageFont.load_default()
    marks = [(1, 4, 1), (2, 7, 10), (3, 26, 6), (4, 27, 18), (5, 2, 21), (6, 21, 21), (7, 14, 21)]
    for n, cx, cy in marks:
        x, y = (32 + cx * 8) * 3, (24 + cy * 8) * 3
        d.ellipse([x - 17, y - 17, x + 17, y + 17], fill=(255, 255, 255), outline=(0, 0, 0), width=3)
        d.text((x, y), str(n), fill=(0, 0, 0), font=f, anchor='mm')
    now.save(os.path.join(out, 'layout_now.png'))
    # ---- proposed
    b, a = bits.copy(), attrs.copy()
    # 1. your place and lap in the message bar while racing (rows 1-2, cols 0-23)
    b[8:24, 0:192] = 0; cells(a, 0, 1, 24, 2, 0x30)
    text(b, '3RD', 1, 1, big=True); cells(a, 1, 1, 6, 2, 0x57)            # bright white on red: you
    text(b, 'LAP', 9, 2); text(b, '2/3', 12, 1, big=True); cells(a, 12, 1, 6, 2, 0x70)   # bright black on yellow
    text(b, '0:23.4', 18, 2)
    # 2. the faces at their own size (16 x 16, one 2 x 2 cell block each), the bubble wider
    strip = b[160:192, :].copy()
    b[160:192, 0:192] = 0; cells(a, 0, 20, 24, 4, 0x30)
    yf = face('YOU'); cf = face('CREW')
    for j in range(16):
        for i in range(16):
            b[168 + j, 8 + i] = yf[j][i] == 'X'
            b[168 + j, 168 + i] = cf[j][i] == 'X'
    cells(a, 1, 21, 2, 2, 0x57); cells(a, 21, 21, 2, 2, 0x4F)
    b[160:192, 32:80] = strip[:, 32:80]; a[20:24, 4:10] = attrs[20:24, 4:10]   # the inventory, as now
    bx0, bx1, by0, by1 = 88, 160, 161, 182      # (it fills its cells: rows 20-22)                                      # the bubble, reaching the chief
    b[by0:by1 + 1, bx0:bx1 + 1] = 0
    b[by0, bx0 + 2:bx1 - 1] = 1; b[by1, bx0 + 2:bx1 - 1] = 1; b[by0 + 2:by1 - 1, bx0] = 1; b[by0 + 2:by1 - 1, bx1] = 1
    for (x, y) in [(bx0 + 1, by0 + 1), (bx1 - 1, by0 + 1), (bx0 + 1, by1 - 1), (bx1 - 1, by1 - 1)]: b[y, x] = 1
    b[168:176, bx1 + 1:bx1 + 6] = 0
    for k in range(4): b[169 + k, bx1 + 1 + k] = 1; b[174 - k, bx1 + 1 + k] = 1
    b[162:182, 90:150] |= strip[8:28, 90:150]                                   # the words, as now
    cells(a, 11, 20, 10, 3, 0x78)
    b[160:192, 184:192] = 0
    now2 = render(b, a)
    now2.save(os.path.join(out, 'layout_proposed.png'))
    print('wrote layout_now.png, layout_proposed.png')
