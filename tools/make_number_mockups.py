"""Mock-up: each car's number on its roof (Grant, 10 Nov 2026: "make the cars bigger,
just enough to put their number into the car"). Bigger cars do not fit (a 24 x 24 car
is 2.25x the memory and drawing time), so: the number stamped into every heading of the
car's own 16 x 16 pictures, upright, at the middle - no cost in the game. Two looks:
A dark number on a white plate, B white number on a dark plate. Writes
docs/design/car_numbers.png (each car at 4 headings, 4x, and real size on the cloth)."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
src = open(os.path.join(HERE, 'make_data.py')).read()
ns = {'__file__': os.path.join(HERE, 'make_data.py')}
exec(src[:src.index("if __name__ == '__main__':")], ns)
frames, ink_of, mask_of = ns['all_frames'], ns['ink_of'], ns['mask_of']
DIG = {'1': ".X.XX..X..X.XXX", '2': "XX...X.X.X..XXX", '3': "XX...X.X...XXX.", '4': "X.XX.XXXX..X..X", '5': "XXXX..XX...XXX."}
NUM = {0: '1', 1: '2', 4: '3', 3: '4', 2: '5'}       # by car: the grid order (YOU 1 ... GREEN 5)
def stamp(ink, msk, d, style):
    ink = [r[:] for r in ink]; msk = [r[:] for r in msk]
    x0, y0 = 6, 5                                    # a 5 x 7 plate at the middle (cols 6-10, rows 5-11)
    for y in range(7):
        for x in range(5):
            msk[y0 + y][x0 + x] = 1
            ink[y0 + y][x0 + x] = 0 if style == 'A' else 1
    g = DIG[d]
    for y in range(5):
        for x in range(3):
            if g[y * 3 + x] == 'X': ink[y0 + 1 + y][x0 + 1 + x] = 1 if style == 'A' else 0
    return ink, msk
INK, PAP = (0, 0, 215), (0, 215, 215)
def cell(ink, msk, s, bg):
    im = Image.new('RGB', (16 * s, 16 * s), bg)
    for y in range(16):
        for x in range(16):
            if msk[y][x]:
                c = INK if ink[y][x] else PAP
                for a in range(s):
                    for b in range(s): im.putpixel((x * s + a, y * s + b), c)
    return im
S = 4; HEADS = [0, 2, 4, 6]
cars = [0, 1, 4, 3, 2]
W = 16 + 2 * (len(HEADS) * (16 * S + 8) + 40) + 40
out = Image.new('RGB', (W, 60 + len(cars) * (16 * S + 12) + 120), (17, 18, 22)); d = ImageDraw.Draw(out)
fnt = ImageFont.load_default()
for si, style in enumerate('AB'):
    ox = 16 + si * (len(HEADS) * (16 * S + 8) + 60)
    d.text((ox, 10), '%s: %s' % (style, 'dark number on a white plate' if style == 'A' else 'white number on a dark plate'), fill=(236, 235, 230), font=fnt)
    for ci, k in enumerate(cars):
        for hi, h in enumerate(HEADS):
            ink, msk = stamp(ink_of(frames[k][h]), mask_of(frames[k][h]), NUM[k], style)
            out.paste(cell(ink, msk, S, (40, 44, 52)), (ox + hi * (16 * S + 8), 30 + ci * (16 * S + 12)))
    # real size on the cloth: a strip of the five cars
    y = 30 + len(cars) * (16 * S + 12) + 10
    strip = Image.new('RGB', (5 * 20 + 8, 22), PAP)
    for ci, k in enumerate(cars):
        ink, msk = stamp(ink_of(frames[k][4]), mask_of(frames[k][4]), NUM[k], style)
        strip.paste(cell(ink, msk, 1, PAP), (4 + ci * 20, 3))
    out.paste(strip.resize((strip.width * 2, strip.height * 2), Image.NEAREST), (ox, y))
    d.text((ox, y + 50), 'real size (x2 here)', fill=(160, 165, 175), font=fnt)
o = os.path.join(ROOT, 'docs', 'design', 'car_numbers.png'); out.save(o); print('wrote', o)
