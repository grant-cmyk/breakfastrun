"""Mock-up: the driver strip under the window (Grant, 10 Nov 2026): the LAP / TIME /
BEST lines go; in their place your face on the left, your inventory (3 slots - you
start with one NOS canister), and a message box ("GREAT DRIVING!" when you
overtake, "SUPERB LAP!", "GET IT TOGETHER!" when you hit the O's). Drawn on a real
race screen (docs/design/mock_screen.bin, from the game) with the Spectrum's own colours
and ROM letters. Writes docs/design/driver_strip.png."""
import os, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
scr = open(os.path.join(ROOT, 'docs', 'design', 'mock_screen.bin'), 'rb').read()
import zx                                         # the ROM's letters, from the emulator's own ROM
font = open(os.path.join(os.path.dirname(zx.__file__), 'roms', 'Spectrum48.rom'), 'rb').read()[0x3D00:0x4000]
PAL = [(0, 0, 0), (0, 0, 215), (215, 0, 0), (215, 0, 215), (0, 215, 0), (0, 215, 215), (215, 215, 0), (215, 215, 215)]
PALB = [(0, 0, 0), (0, 0, 255), (255, 0, 0), (255, 0, 255), (0, 255, 0), (0, 255, 255), (255, 255, 0), (255, 255, 255)]
def load():
    bits = np.zeros((192, 256), np.uint8)
    for y in range(192):
        a = ((y & 0xC0) << 5) | ((y & 7) << 8) | ((y & 0x38) << 2)
        bits[y] = np.unpackbits(np.frombuffer(scr[a:a + 32], np.uint8))
    return bits, bytearray(scr[6144:6912])
def render(bits, attr, s):
    img = np.zeros((192, 256, 3), np.uint8)
    for r in range(24):
        for c in range(32):
            at = attr[r * 32 + c]; pal = PALB if at & 64 else PAL
            ink, pap = np.array(pal[at & 7]), np.array(pal[(at >> 3) & 7])
            cell = bits[r * 8:r * 8 + 8, c * 8:c * 8 + 8][..., None]
            img[r * 8:r * 8 + 8, c * 8:c * 8 + 8] = np.where(cell, ink, pap)
    return Image.fromarray(img).resize((256 * s, 192 * s), Image.NEAREST)
fa = open(os.path.join(ROOT, 'tools', 'face_art.txt')).read()
YOU = re.search(r'== YOU face ==\n((?:[X.]{16}\n){16})', fa).group(1).split()
NOS = ["....XXXX....",      # valve handle
       "......X.....",
       "....XXXX....",      # neck
       "...XXXXXX...",
       "..X......X..",      # shoulders, the body white
       "..X.X....X..",      # a highlight
       "..XXXXXXXX..",      # the label band
       "..XXXXXXXX..",
       "..XXXXXXXX..",
       "..X.X....X..",
       "..X.X....X..",
       "..X......X..",
       "...XXXXXX..."]
def text(bits, s, col, row):
    for i, ch in enumerate(s):
        g = font[(ord(ch) - 32) * 8:(ord(ch) - 32) * 8 + 8]
        for j in range(8):
            bits[row * 8 + j, (col + i) * 8:(col + i + 1) * 8] = np.unpackbits(np.array([g[j]], np.uint8))
def strip(msg):
    bits, attr = load()
    bits[160:192, 0:192] = 0                       # the old LAP / TIME / BEST lines
    for r in range(20, 24):
        for c in range(24): attr[r * 32 + c] = 0x30
    for y in range(16):                            # your face, twice size, on your red
        for x in range(16):
            if YOU[y][x] == 'X': bits[160 + 2 * y:162 + 2 * y, 8 + 2 * x:10 + 2 * x] = 1
    for r in range(20, 24):
        for c in range(1, 5): attr[r * 32 + c] = 0x57
    for k in range(3):                             # the inventory: 3 slots, white, framed
        x0 = 48 + k * 16
        for r in (21, 22):
            for c in (6 + 2 * k, 7 + 2 * k): attr[r * 32 + c] = 0x78
        bits[168, x0 + 1:x0 + 15] = 1; bits[183, x0 + 1:x0 + 15] = 1
        bits[169:183, x0] = 1; bits[169:183, x0 + 15] = 1
    for y, row in enumerate(NOS):                  # slot 1: the NOS canister you start with
        for x, v in enumerate(row):
            if v == 'X': bits[169 + 1 + y, 48 + 2 + x] = 1
    x0, x1, y0, y1 = 104, 191, 160, 191            # the message box: white, rounded
    for r in range(20, 24):
        for c in range(13, 24): attr[r * 32 + c] = 0x78
    bits[y0, x0 + 2:x1 - 1] = 1; bits[y1, x0 + 2:x1 - 1] = 1
    bits[y0 + 2:y1 - 1, x0] = 1; bits[y0 + 2:y1 - 1, x1] = 1
    for (x, y) in ((x0 + 1, y0 + 1), (x1 - 1, y0 + 1), (x0 + 1, y1 - 1), (x1 - 1, y1 - 1)): bits[y, x] = 1
    bits[y0 + 13:y0 + 19, x0] = 0                  # a speech tail, pointing back at you
    for i in range(4):                             # (wide at the box, a point at the left)
        bits[y0 + 12 + i, x0 - 1 - i] = 1; bits[y0 + 19 - i, x0 - 1 - i] = 1
    bits[y0 + 15:y0 + 17, x0 - 5] = 1
    for i, line in enumerate(msg): text(bits, line, 14 + (9 - len(line)) // 2, 21 + i)
    return bits, attr
MSGS = [('GREAT', 'DRIVING!'), ('SUPERB', 'LAP!'), ('GET IT', 'TOGETHER!')]
b, a = strip(MSGS[0])
full = render(b, a, 2)
strips = [render(*strip(m), 3).crop((0, 152 * 3, 196 * 3, 192 * 3)) for m in MSGS]
W = max(full.width, strips[0].width) + 32
H = 40 + full.height + 24 + sum(s.height + 16 for s in strips)
out = Image.new('RGB', (W, H), (17, 18, 22)); d = ImageDraw.Draw(out); fnt = ImageFont.load_default()
d.text((16, 12), 'The driver strip: your face, your inventory (3), a message box  -  the whole screen (2x), then the strip (3x) with three messages', fill=(236, 235, 230), font=fnt)
out.paste(full, (16, 36)); y = 36 + full.height + 24
for s in strips: out.paste(s, (16, y)); y += s.height + 16
o = os.path.join(ROOT, 'docs', 'design', 'driver_strip.png'); out.save(o); print('wrote', os.path.normpath(o))
