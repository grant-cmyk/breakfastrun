"""Mock-ups: the word RUN on the title's green band (Grant, 15 Nov 2026: "the run should not touch the
bottom white area, it should be surround by green. Can you mockup some alternative fonts or
effects for the RUN word"). The band is a row taller (rows 3-7), so there is green under RUN.
Over the real title with its band green (docs/design/layout_src/title_green.png); checked for clash.
Usage: python3 tools/make_run_options.py -> docs/design/run_options.png"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_layout_options as L
from PIL import Image
K, BY, BW, BR = L.K, L.BY, L.BW, L.BR; BG = (0, 255, 0)
T = Image.open(os.path.join(L.D, 'layout_src', 'title_green.png')).convert('RGB')
LOGO = [l.strip() for l in open(os.path.join(L.HERE, '..', 'build', 'logo.txt'))]
def base():
    s = L.Scr(); s.paste(T, 0, 0); return s
def rom(s, text, x, y, sx, sy, ink, shear=0, keep=lambda gx, gy, px, py: True, gap=0):
    """The ROM's letters, each pixel sx by sy, leaning shear pixels a letter-row; keep() can cut pixels out."""
    for i, ch in enumerate(text):
        g = L.ROM[0x3D00 + (ord(ch) - 32) * 8:][:8]
        for gy in range(8):
            for gx in range(8):
                if g[gy] >> (7 - gx) & 1:
                    for dy in range(sy):
                        for dx in range(sx):
                            px = x + i * (8 * sx + gap) + gx * sx + dx + shear * (7 - gy); py = y + gy * sy + dy
                            if keep(gx, gy, px, py): s.im.putpixel((px, py), ink)
def r_now():                                    # the logo's own RUN, twice the size, in yellow
    s = base()
    for y in range(8, 16):
        for x in range(36):
            if LOGO[y][x] == '#': s.d.rectangle((88 + 2 * x, 40 + 2 * (y - 8), 89 + 2 * x, 41 + 2 * (y - 8)), fill=BY)
    return s
def r_solid():
    s = base(); rom(s, 'RUN', 88, 40, 3, 2, BY, shear=1); return s
def r_speed():                                  # white, leaning, lines streaming off behind it
    s = base(); rom(s, 'RUN', 112, 40, 3, 2, BW, shear=1)
    for k, (y, x0) in enumerate(((43, 88), (47, 92), (51, 88))): s.d.rectangle((x0, y, 108 + 2 * k, y + 1), fill=BW)
    return s
def r_badge():                                  # a red plate, RUN white on it
    s = base(); s.fill(11, 5, 10, 2, BR); rom(s, 'RUN', 92, 40, 3, 2, BW); return s
def r_cheq():                                   # filled with the flag's checks
    s = base(); rom(s, 'RUN', 88, 40, 3, 2, BY, keep=lambda gx, gy, px, py: ((px // 2 + py // 2) % 2 == 0) or gy in (1, 7)); return s
def r_stripe():                                 # cut through by two lines, leaning: the old computer-game speed look
    s = base(); rom(s, 'RUN', 88, 40, 3, 2, BY, shear=1, keep=lambda gx, gy, px, py: (py - 40) not in (5, 10)); return s
def r_wide():                                   # spaced right across under BREAKFAST, upright
    s = base(); rom(s, 'RUN', 88, 40, 3, 2, BW, gap=20); return s
def r_small():                                  # the same size as the menu's letters, spaced out, with a line each side
    s = base(); s.text('R U N', 15, 6, BY)
    s.d.rectangle((88, 51, 114, 52), fill=BY); s.d.rectangle((166, 51, 198, 52), fill=BY); return s
if __name__ == '__main__':
    L.sheet([('1  As now', 'the logo\'s own slanted RUN, in yellow, green under it', r_now),
             ('2  Solid slant', 'heavy leaning letters, yellow', r_solid),
             ('3  Speed lines', 'white, leaning, lines streaming behind', r_speed),
             ('4  Red plate', 'white RUN on a red plate, green all round', r_badge),
             ('5  Chequered', 'the letters filled with the flag\'s checks', r_cheq),
             ('6  Cut lines', 'leaning, two lines cut through: the arcade look', r_stripe),
             ('7  Wide', 'white, upright, spread under the whole of BREAKFAST', r_wide),
             ('8  Small', 'spaced small letters between two lines', r_small)],
            'Breakfast Run - the word RUN on the green band (green all round it)', 'run_options.png')
