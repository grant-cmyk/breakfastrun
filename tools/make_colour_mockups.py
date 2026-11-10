"""Colour options for the play window without white (Grant, 10 Nov 2026: the white
is hard on the eyes and adds to the flicker). Takes a real game screen from the
emulator and redraws the window in other ink / paper pairs; a second row tries a
lighter cloth (25% dots instead of the 50% checker, which shimmers when it
scrolls a pixel at a time). Writes docs/design/colours.png."""
import os, sys, numpy as np
from PIL import Image, ImageDraw
from zx._spectrum import Spectrum
import zx._spectrum as zs
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SYM = {}
for line in open(os.path.join(ROOT, 'build', 'racer.sym')):
    p = line.split()
    if len(p) >= 3 and p[1] == 'EQU': SYM[p[0].lower()] = int(p[2].rstrip('H'), 16)
PAL = [(0,0,0),(0,0,0xD7),(0xD7,0,0),(0xD7,0,0xD7),(0,0xD7,0),(0,0xD7,0xD7),(0xD7,0xD7,0),(0xD7,0xD7,0xD7)]
PALB = [(0,0,0),(0,0,0xFF),(0xFF,0,0),(0xFF,0,0xFF),(0,0xFF,0),(0,0xFF,0xFF),(0xFF,0xFF,0),(0xFF,0xFF,0xFF)]
with Spectrum(headless=True) as sp:
    sp.load_tape(os.path.join(ROOT, 'build', 'racer.tap'))
    while sp.read16(SYM['renders']) < 3: sp.run(duration=0.1, fast_forward=True)
    C = SYM['cars']
    sp.write(C + 1, bytes([276 & 255, 276 >> 8])); sp.write(C + 4, bytes([212 & 255, 212 >> 8]))  # by the plate
    sp.run(duration=0.4, fast_forward=True)
    scr = bytes(sp.read8(0x4000 + i) for i in range(6912))
bits = np.zeros((192, 256), np.uint8)
for y in range(192):
    a = ((y & 0xC0) << 5) | ((y & 7) << 8) | ((y & 0x38) << 2)
    bits[y] = np.unpackbits(np.frombuffer(scr[a:a + 32], np.uint8))
att = np.frombuffer(scr[6144:], np.uint8).reshape(24, 32)
cam = None
def render(win_ink, win_paper, bright, pattern=None):
    b = bits.copy()
    if pattern == 'dots':                  # swap the 50% checker for 25% dots in the window
        y0, x0 = 32, 8
        w = b[y0:y0 + 120, x0:x0 + 176]
        yy, xx = np.mgrid[0:120, 0:176]
        chk = ((xx + yy) & 1) == 0
        # only where the cloth is (checker pixels on, with no neighbour ink making a line)
        dots = (xx % 2 == 0) & (yy % 2 == 0)
        cloth = w.astype(bool) & chk
        lone = np.ones_like(cloth)
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            lone &= ~np.roll(np.roll(w.astype(bool), dy, 0), dx, 1)
        w[(cloth & lone) & ~dots] = 0
    img = np.zeros((192, 256, 3), np.uint8)
    for r in range(24):
        for c in range(32):
            v = int(att[r, c]); ink, paper, br = v & 7, (v >> 3) & 7, (v >> 6) & 1
            if 4 <= r <= 18 and 1 <= c <= 22: ink, paper, br = win_ink, win_paper, bright
            pal = PALB if br else PAL
            blk = b[r * 8:r * 8 + 8, c * 8:c * 8 + 8]
            img[r * 8:r * 8 + 8, c * 8:c * 8 + 8] = np.where(blk[..., None] == 1, pal[ink], pal[paper])
    full = np.zeros((240, 320, 3), np.uint8); full[:] = PAL[6]; full[24:216, 32:288] = img
    return Image.fromarray(full)
B, R, M, G, Cy, Y, K = 1, 2, 3, 4, 5, 6, 0
opts = [('now: blue on bright white', B, 7, 1, None),
        ('1 blue on cyan', B, Cy, 0, None), ('2 black on green', K, G, 0, None), ('3 blue on green', B, G, 0, None),
        ('4 red on yellow', R, Y, 0, None), ('5 black on cyan', K, Cy, 0, None), ('6 magenta on cyan', M, Cy, 0, None),
        ('1 with 25% dots', B, Cy, 0, 'dots'), ('2 with 25% dots', K, G, 0, 'dots'), ('4 with 25% dots', R, Y, 0, 'dots')]
S = 2; w, h = 320, 240; cols = 4; rows = (len(opts) + cols - 1) // cols
sheet = Image.new('RGB', (cols * (w * S + 16) - 16, rows * (h * S + 36)), (21, 23, 28)); d = ImageDraw.Draw(sheet)
for i, (lab, ink, paper, br, pat) in enumerate(opts):
    x, y = (i % cols) * (w * S + 16), (i // cols) * (h * S + 36)
    sheet.paste(render(ink, paper, br, pat).resize((w * S, h * S), Image.NEAREST), (x, y + 28)); d.text((x + 6, y + 8), lab.upper(), fill=(232, 230, 223))
sheet.save(os.path.join(ROOT, 'docs', 'design', 'colours.png')); print('ok')
