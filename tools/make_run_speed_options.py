"""Mock-ups: RUN with the three speed lines, in different letters (Grant, 15 Nov 2026: "I love the
speed lines, can you make font variations for RUN with those speed lines of 3"). Over the real
title with its green band; checked for clash.
Usage: python3 tools/make_run_speed_options.py -> docs/design/run_speed_options.png"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_layout_options as L, make_run_options as R
BW, BY = L.BW, L.BY
BLOCK = {'R': ['#####.', '##..##', '##..##', '#####.', '##.##.', '##..##', '##..##', '##..##'],
         'U': ['##..##'] * 7 + ['.####.'],
         'N': ['##..##', '###.##', '######', '######', '##.###', '##..##', '##..##', '##..##']}
ROUND = {'R': ['####..', '#...#.', '#...#.', '####..', '#.#...', '#..#..', '#...#.', '#...#.'],
         'U': ['#...#.'] * 7 + ['.###..'],
         'N': ['#...#.', '##..#.', '##..#.', '#.#.#.', '#.#.#.', '#..##.', '#..##.', '#...#.']}
WIDE = {'R': ['######..', '##...##.', '##...##.', '######..', '##.##...', '##..##..', '##...##.', '##...##.'],
        'U': ['##...##.'] * 6 + ['###.###.', '.#####..'],
        'N': ['##...##.', '###..##.', '####.##.', '##.####.', '##..###.', '##...##.', '##...##.', '##...##.']}
def lines(s, x1=108, ink=BW, y0=43):
    for k, (y, x0) in enumerate(((y0, 88), (y0 + 4, 92), (y0 + 8, 88))): s.d.rectangle((x0, y, x1 + 2 * k, y + 1), fill=ink)
def art(s, font, x, y, sx, sy, ink, shear=1, gap=3, keep=lambda gx, gy, px, py: True, outline=False):
    for i, ch in enumerate('RUN'):
        g = font[ch]; w = len(g[0])
        on = lambda gx, gy: 0 <= gy < 8 and 0 <= gx < w and g[gy][gx] == '#'
        for gy in range(8):
            for gx in range(w):
                if not on(gx, gy): continue
                if outline and all(on(gx + dx, gy + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))): continue
                for dy in range(sy):
                    for dx in range(sx):
                        px = x + i * (w * sx + gap) + gx * sx + dx + shear * (7 - gy); py = y + gy * sy + dy
                        if keep(gx, gy, px, py): s.im.putpixel((px, py), ink)
def v1():
    s = R.base(); R.rom(s, 'RUN', 112, 40, 3, 2, BW, shear=1); lines(s); return s
def v2():                                       # the same letters struck twice: heavier
    s = R.base(); R.rom(s, 'RUN', 112, 40, 3, 2, BW, shear=1); R.rom(s, 'RUN', 114, 40, 3, 2, BW, shear=1); lines(s); return s
def v3():
    s = R.base(); art(s, BLOCK, 114, 40, 3, 2, BW); lines(s); return s
def v4():
    s = R.base(); art(s, BLOCK, 114, 40, 3, 2, BW, shear=0); lines(s); return s
def v5():
    s = R.base(); art(s, ROUND, 114, 40, 3, 2, BW, gap=6); lines(s); return s
def v6():
    s = R.base(); art(s, WIDE, 112, 40, 3, 2, BW, gap=1, outline=True); lines(s); return s
def v7():                                       # the logo's own RUN, in white
    s = R.base()
    for y in range(8, 16):
        for x in range(36):
            if R.LOGO[y][x] == '#': s.d.rectangle((116 + 2 * x, 40 + 2 * (y - 8), 117 + 2 * x, 41 + 2 * (y - 8)), fill=BW)
    lines(s, 110); return s
def v8():                                       # the lines run on through the letters
    s = R.base(); art(s, BLOCK, 114, 40, 3, 2, BW, keep=lambda gx, gy, px, py: (py - 40) not in (5, 6, 10, 11) or px > 150)
    for y, x0 in ((43, 88), (47, 92), (51, 88)): s.d.rectangle((x0, y, 112, y + 1), fill=BW)
    return s
if __name__ == '__main__':
    L.sheet([('3a  Spectrum letters', 'as on the last sheet', v1),
             ('3b  Spectrum letters, heavy', 'the same, thicker strokes', v2),
             ('3c  Block, leaning', 'drawn letters: thick, square', v3),
             ('3d  Block, upright', 'the same without the lean', v4),
             ('3e  Thin and round', 'light letters, spaced', v5),
             ('3f  Outline', 'hollow wide letters', v6),
             ('3g  The logo\'s own RUN', 'today\'s split letters, in white', v7),
             ('3h  Lines through', 'block letters, the lines cutting into the R', v8)],
            'Breakfast Run - RUN with its three speed lines: the letters', 'run_speed_options.png')
