"""Start lights for option G3 (Grant, 14 Nov 2026): "The start blocks. Not just a coloured square.
Put some design into them so it is clearer that these are the start lights. But the design is
better now".

G3 (tools/make_screen_options3.py) stays as it is; only the three lights in the play window
change. They still go unlit -> red -> red red -> red red red -> all green -> gone, and each 8 x 8
cell still has one ink and one paper, but now there are pixels in the cells: a lamp is a round
shape in a 2 x 2 block of cells (16 x 16 pixels) that share one ink and one paper, so nothing can
clash. (A post or rail cell is black on cyan, so the cloth's dots are wiped from it.) Three designs, all near the top centre of the window (lamps at cols 8-9, 11-12, 14-15,
rows 3-4), clear of the cars on the grid:

  L1  "Gantry"   - one black bar with rounded ends, hung from the frame on two posts; three round
                   lamps with a glint. The pixels never change: a lamp is dim blue when unlit,
                   bright red, then bright green - the game only writes colours.
  L2  "Pods"     - three separate black lamp boxes hanging from a rail; an unlit lamp is an empty
                   white ring, a lit one is a full disc (the game redraws the lamp when it lights).
  L3  "Glow"     - one black bar; a lamp is a lens ring, and when it lights its whole block glows
                   red (then green) with the ring in white; at GO the bar's two ends turn into
                   chequered flags. Again the pixels never change, only the colours.

Writes docs/design/start_lights.png: each design's five steps close up (5x) and at real size
(1x and 2x), then the whole G3 screen (3x) with the preferred design at the "red red" step.
Usage: make_start_lights.py"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
from make_layout_review import render
from make_screen_options2 import DESIGN, WIN, BEFORE
from make_screen_options3 import option_g3

STEPS = [('unlit', 0, False), ('red', 1, False), ('red red', 2, False), ('red red red', 3, False), ('all green: GO', 3, True)]
X0, Y0 = 64, 24                                 # the first lamp's top left: col 8, row 3
LINE = 0x28                                     # black ink on the window's cyan: posts, rails, bar ends
def disc(r, cx=7.5, cy=7.5):
    y, x = np.mgrid[0:16, 0:16]
    return ((x - cx) ** 2 + (y - cy) ** 2 <= r * r).astype(np.uint8)
GLINT = (disc(4.6) - disc(3.4)) * (np.mgrid[0:16, 0:16][0] < 7) * (np.mgrid[0:16, 0:16][1] < 7)
LAMP = disc(6.9) * (1 - GLINT)                  # a full lamp, 14 across, with a glint of housing in it
RING = disc(6.9) - disc(5.6)                    # an empty lamp
LENS = (disc(7.2) - disc(5.6)) | GLINT.astype(np.uint8)    # L3: a ring bezel and a glint
def lamp(b, a, k, art, at):
    x = X0 + 24 * k
    b[Y0:Y0 + 16, x:x + 16] = art; a[3:5, 8 + 3 * k:10 + 3 * k] = at
def colour(k, lit, go, unlit, red, green): return green if go else (red if k < lit else unlit)

def l1(b, a, lit, go):
    a[3:5, 7:17] = 0x00; b[Y0:Y0 + 16, 56:136] = 0             # the bar: black cells, cols 7-16
    for c, xs in ((7, slice(56, 60)), (16, slice(132, 136))):   # its ends: half a cell of cyan, rounded
        a[3:5, c] = LINE; b[Y0:Y0 + 16, c * 8:c * 8 + 8] = 1; b[Y0:Y0 + 16, xs] = 0
    for (x, y) in ((60, Y0), (131, Y0), (60, Y0 + 15), (131, Y0 + 15)): b[y, x] = 0
    for c in (10, 13): a[2, c] = LINE; b[16:24, c * 8:c * 8 + 8] = 0; b[16:24, c * 8 + 3:c * 8 + 5] = 1    # two posts up to the frame
    for k in range(3): lamp(b, a, k, LAMP, colour(k, lit, go, 0x01, 0x42, 0x44))
def l2(b, a, lit, go):
    a[2, 7:17] = LINE; b[16:24, 56:136] = 0; b[18:21, 60:132] = 1                    # the rail, hung from the frame
    for x in (62, 128): b[16:18, x:x + 2] = 1
    for k in range(3):
        x = X0 + 24 * k; b[21:24, x + 7:x + 9] = 1             # a hanger down to each box
        on = go or k < lit
        lamp(b, a, k, LAMP if on else RING, colour(k, lit, go, 0x07, 0x42, 0x44))
def l3(b, a, lit, go):
    a[3:5, 7:17] = 0x00; b[Y0:Y0 + 16, 56:136] = 0
    for c in (7, 16):                                          # the ends: a chequer, hidden (black on black) until GO
        for j in range(16):
            for i in range(8): b[Y0 + j, c * 8 + i] = (i // 4 + j // 4) % 2
        a[3:5, c] = 0x78 if go else 0x00
    for c in (10, 13): a[2, c] = LINE; b[16:24, c * 8:c * 8 + 8] = 0; b[16:24, c * 8 + 3:c * 8 + 5] = 1
    for k in range(3): lamp(b, a, k, LENS, colour(k, lit, go, 0x01, 0x57, 0x60))   # blue ring; white on red; black on green
DESIGNS = [('L1 - Gantry: one bar on two posts, round lamps with a glint. Unlit lamps are dim blue. Colours only - the pixels never change.', l1),
           ('L2 - Pods: three lamp boxes hanging from a rail. An unlit lamp is an empty white ring; lit, a full disc.', l2),
           ('L3 - Glow: lens rings in one bar; a lit lamp makes its whole block glow; chequered ends at GO. Colours only.', l3)]
PICK = l1

def screen(design, lit, go):
    b, a = option_g3('off'); a[4:6, 8:16] = WIN                # G3 on the grid, without the old blocks
    win = b[16:152, 8:184].copy(); design(b, a, lit, go)
    ch = b[16:152, 8:184] != win                               # pixels are only drawn in the lights' own cells
    assert not ch[32:, :].any() and (a[5:19, 1:23] == WIN).all()
    return b, a

if __name__ == '__main__':
    try:
        f = ImageFont.truetype('DejaVuSans-Bold.ttf', 22); fs = ImageFont.truetype('DejaVuSans.ttf', 16)
    except OSError: f = fs = ImageFont.load_default()
    BG, FG = (17, 18, 22), (236, 235, 230)
    BOX = (48, 8, 144, 48)                                     # the window's top middle: cols 6-17, rows 1-5
    def crop(design, lit, go, s):
        b, a = screen(design, lit, go); im = render(b, a, border=6, s=s)
        return im.crop(((32 + BOX[0]) * s, (24 + BOX[1]) * s, (32 + BOX[2]) * s, (24 + BOX[3]) * s))
    gap = 16; cw, ch = 96 * 5, 40 * 5
    W = gap + 5 * (cw + gap); rowh = 34 + 22 + ch + 12 + 80 + 26
    b, a = screen(PICK, 2, False); full = render(b, a, border=6, s=3)
    out = Image.new('RGB', (W, len(DESIGNS) * rowh + 40 + full.height + gap), BG); d = ImageDraw.Draw(out)
    for n, (title, design) in enumerate(DESIGNS):
        y = gap // 2 + n * rowh
        d.text((gap, y), title, fill=(255, 255, 255), font=f)
        for k, (name, lit, go) in enumerate(STEPS):
            x = gap + k * (cw + gap)
            d.text((x, y + 34), name, fill=FG, font=fs); out.paste(crop(design, lit, go, 5), (x, y + 56))
        y2 = y + 56 + ch + 12
        d.text((gap, y2 + 2), 'Real size:', fill=FG, font=fs); x = gap + 100
        for k, (name, lit, go) in enumerate(STEPS): out.paste(crop(design, lit, go, 1), (x + k * 104, y2))
        d.text((x + 5 * 104 + 30, y2 + 2), 'Twice size:', fill=FG, font=fs); x += 5 * 104 + 140
        for k, (name, lit, go) in enumerate(STEPS): out.paste(crop(design, lit, go, 2), (x + k * 200, y2))
    y = gap // 2 + len(DESIGNS) * rowh
    d.text((gap, y), 'In place: the G3 screen with L1 at "red red"', fill=(255, 255, 255), font=f); out.paste(full, (gap, y + 34))
    o = os.path.join(DESIGN, 'start_lights.png'); out.save(o); print('wrote', os.path.normpath(o), out.size)
