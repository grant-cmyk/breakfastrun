"""Mock-ups: the title's logo, so the egg can be seen (Grant, 15 Nov 2026: "on the title screen the
egg yellow on white is not really visible. Suggest we go do more mockups for a title logo, or find
a way to make the egg visible"). The trouble: the yolk is a 6 x 6 pixel hole of yellow in white -
the two colours the Spectrum tells apart least. Real screens over the built title
(docs/design/layout_src/title_b.png), checked for colour clash.
Usage: python3 tools/make_logo_options.py -> docs/design/logo_options.png"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_layout_options as L
from PIL import Image
K, B, R, Y, BY, BW, BR, BB = L.K, L.B, L.R, L.Y, L.BY, L.BW, L.BR, L.BB
T = Image.open(os.path.join(L.D, 'layout_src', 'title_b.png')).convert('RGB')
LOGO = [l.strip() for l in open(os.path.join(L.HERE, '..', 'build', 'logo.txt'))]
def words(s, cx, cy, band=True):                # BREAKFAST over RUN, twice the size, from cell (cx, cy)
    if band: s.fill(cx, cy + 2, 10, 2, BY)
    for y in range(16):
        for x in range(56 if y < 8 else 36):
            if LOGO[y][x] == '#':
                s.d.rectangle(((cx * 8 + 2 * x, cy * 8 + 2 * y, cx * 8 + 2 * x + 1, cy * 8 + 2 * y + 1)), fill=K if y < 8 else BR)
def blob(x, y, big):                            # is (x, y) in the egg's white? a lumpy shape: three overlapping ellipses
    parts = ((16, 16, 15, 12), (11, 20, 10, 10), (22, 12, 9, 9)) if big else ((16, 8, 15, 7), (10, 9, 9, 6), (23, 7, 8, 6))
    return any(((x - a) / c) ** 2 + ((y - b) / d) ** 2 <= 1 for a, b, c, d in parts)
def egg(s, cx, cy, big, white, ground, yolk, yolk_paper, line=None):
    """An egg at cell (cx, cy): 4 x 4 cells big, or 4 x 2. The yolk has cells of its own (2 x 2 big, 1 x 1
    small... small: 2 x 1), so it can be a colour pair of its own: yolk on yolk_paper."""
    w, h = 32, 32 if big else 16
    yc = (16, 16, 7.5) if big else (16, 8, 6.5)
    for y in range(h):
        for x in range(w):
            inside = blob(x, y, big); px = (cx * 8 + x, cy * 8 + y)
            in_cells = (8 <= x < 24 and 8 <= y < 24) if big else (8 <= x < 24)
            disc = (x + .5 - yc[0]) ** 2 + (y + .5 - yc[1]) ** 2 <= yc[2] ** 2
            if line is not None:                # a line drawing: outline of the white, outline of the yolk, on the ground
                edge = inside and not all(blob(x + dx, y + dy, big) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                ring = disc and not ((x + .5 - yc[0]) ** 2 + (y + .5 - yc[1]) ** 2 <= (yc[2] - 1.6) ** 2)
                s.im.putpixel(px, line if edge or ring else ground)
            elif in_cells: s.im.putpixel(px, yolk if disc else yolk_paper)
            else: s.im.putpixel(px, white if inside else ground)
def base():
    s = L.Scr(); s.paste(T, 0, 0); s.fill(3, 3, 26, 4, Y); return s
def o_now():
    s = L.Scr(); s.paste(T, 0, 0); return s
def o_bigyolk():                                # the same place and size, the yolk a big disc in cells of its own
    s = base(); words(s, 9, 3); egg(s, 19, 5, False, BW, BY, BY, BW); return s
def o_line():                                   # the egg a black line drawing on the band
    s = base(); words(s, 9, 3); egg(s, 19, 5, False, None, BY, None, None, line=K); return s
def o_big_left():                               # a big egg beside both words
    s = base(); egg(s, 5, 3, True, BW, Y, BY, BW); words(s, 11, 3); return s
def o_big_plate():                              # ... on a blue plate
    s = base(); s.fill(5, 3, 4, 4, B); egg(s, 5, 3, True, BW, B, BY, BW); words(s, 11, 3); return s
def o_big_line():                               # ... as a line drawing
    s = base(); egg(s, 5, 3, True, None, Y, None, None, line=K); words(s, 11, 3); return s
def o_big_pan():                                # ... in a black pan, the yolk ringed by the pan's black
    s = base(); s.fill(5, 3, 4, 4, K); egg(s, 5, 3, True, BW, K, BY, K); words(s, 11, 3); return s
if __name__ == '__main__':
    L.sheet([('NOW', 'the yolk is a small yellow hole in the white', o_now),
             ('A  Bigger yolk', 'same logo; the yolk a 13-pixel disc with cells of its own', o_bigyolk),
             ('B  Line egg', 'same logo; the egg drawn in black line on the yellow band', o_line),
             ('C  Big egg', 'a large egg left of both words, a 15-pixel yolk', o_big_left),
             ('D  Big egg on a plate', 'as C on a blue plate: the white has an edge all round', o_big_plate),
             ('E  Big line egg', 'as C drawn in black line', o_big_line),
             ('F  Egg in the pan', 'white on black; black shows at the yolk\'s corners', o_big_pan)],
            'Breakfast Run - the title logo: making the egg show', 'logo_options.png')
