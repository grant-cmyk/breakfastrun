"""Mock-up: each car's ARMOUR shown in the race-order panel (Grant, 17 Nov 2026: "We need to add 'armour' to the
cars as a gauge item ... I would love a way to show damage on each car in the HUD somewhere"). Three ways, drawn on
a real screen of the tighter-track tape. Usage: python3 tools/make_armour_hud_mock.py <screenshot 352x288>
Writes docs/design/racetrack/armour_hud_options.png. Nothing here is in the game."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
src = Image.open(sys.argv[1]).convert('RGB')
X0, Y0, RW, RH = 256, 96, 48, 16                      # the panel's five rows on the screen
ARM = [0.3, 0.7, 1.0, 0.5, 0.85]                      # an example: armour left, top row to bottom
K = (0, 0, 0)
def rowcol(a, r): return tuple(int(v) for v in a[Y0 + r * RH + 1, X0 + 1])
def opt_a(im):                                         # a bar along the foot of each row
    a = np.array(im)
    for r, f in enumerate(ARM):
        y = Y0 + r * RH + 13; ink = (255, 255, 255) if rowcol(a, r)[0] > 200 and rowcol(a, r)[1] < 60 and rowcol(a, r)[2] < 60 else K
        a[y:y + 3, X0 + 1:X0 + RW - 1] = rowcol(a, r)
        a[y + 2, X0 + 1:X0 + RW - 1] = ink; a[y:y + 2, X0 + 1:X0 + 1 + int((RW - 2) * f)] = ink
    return Image.fromarray(a)
def opt_b(im):                                         # five pips at the right of each row
    a = np.array(im)
    for r, f in enumerate(ARM):
        c = rowcol(a, r); ink = (255, 255, 255) if c[0] > 200 and c[1] < 60 and c[2] < 60 else K
        a[Y0 + r * RH + 2:Y0 + r * RH + 14, X0 + 26:X0 + RW] = c
        for p in range(5):
            x = X0 + 27 + p * 4; y = Y0 + r * RH + 4
            a[y:y + 8, x:x + 3] = ink
            if p >= round(f * 5): a[y + 1:y + 7, x + 1:x + 2] = c
    return Image.fromarray(a)
def opt_c(im):                                         # the row's colour drains away from the right, a square at a time
    a = np.array(im)
    for r, f in enumerate(ARM):
        c = np.array(rowcol(a, r), np.uint8)
        for cell in range(6):
            if cell >= round(f * 6):
                blk = a[Y0 + r * RH:Y0 + (r + 1) * RH, X0 + cell * 8:X0 + cell * 8 + 8]
                was = (blk == c).all(axis=2); blk[was] = K; blk[~was] = c
    return Image.fromarray(a)
S = 4; fnt = ImageFont.load_default()
crop = lambda im: im.crop((244, 84, 316, 180)).resize((72 * S, 96 * S), Image.NEAREST)
OPTS = [('NOW', 'no armour shown', src), ('A', 'a bar along the foot of each row', opt_a(src)),
        ('B', 'five pips (in place of the gap time)', opt_b(src)), ('C', "the row's colour drains to black", opt_c(src))]
sheet = Image.new('RGB', (len(OPTS) * (72 * S + 16) + 16, 96 * S + 44), (40, 42, 48)); d = ImageDraw.Draw(sheet)
for i, (tag, what, im) in enumerate(OPTS):
    ox = 16 + i * (72 * S + 16); d.text((ox, 8), tag + ': ' + what, fill=(236, 235, 230), font=fnt); sheet.paste(crop(im), (ox, 28))
out = os.path.join(ROOT, 'docs', 'design', 'racetrack', 'armour_hud_options.png'); sheet.save(out); print('wrote', out)
