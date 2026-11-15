"""Mock-ups: RUN with a line through its middle, two colours - top and bottom (Grant, 15 Nov 2026:
"make some more options. I liked the line through the middle. Possible to make it two colours -
top and bottom?"). RUN is two character rows high, so each row can have an ink of its own: the
cut sits on the join. Over the real title with its green band; checked for clash.
Usage: python3 tools/make_run_split_options.py -> docs/design/run_split_options.png"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_layout_options as L, make_run_options as R, make_run_speed_options as V
K, BW, BY, BR, BB, BM = L.K, L.BW, L.BY, L.BR, L.BB, L.BM
CUT = (47, 48)                                  # the line through: a pixel either side of the join of the two rows
def two(draw, top, bot):                        # draw(ink, keep) twice: the top row's half, the bottom row's
    draw(top, lambda gx, gy, px, py: py < CUT[0]); draw(bot, lambda gx, gy, px, py: py > CUT[1])
def lines(s, top, bot, x1=108):
    s.d.rectangle((88, 42, x1, 43), fill=top); s.d.rectangle((92, 45, x1 + 2, 46), fill=top)
    s.d.rectangle((92, 49, x1 + 2, 50), fill=bot); s.d.rectangle((88, 52, x1, 53), fill=bot)
def lines3(s, top, bot, x1=108):
    s.d.rectangle((88, 42, x1, 43), fill=top); s.d.rectangle((94, 46, x1 + 2, 46), fill=top); s.d.rectangle((94, 49, x1 + 2, 49), fill=bot)
    s.d.rectangle((88, 52, x1, 53), fill=bot)
def block(top, bot, shear=1, font=V.BLOCK, gap=3, ln=lines3):
    def f():
        s = R.base(); two(lambda ink, keep: V.art(s, font, 114, 40, 3, 2, ink, shear=shear, gap=gap, keep=keep), top, bot); ln(s, top, bot); return s
    return f
def rom(top, bot):
    def f():
        s = R.base()
        for dx in (0, 2): two(lambda ink, keep: R.rom(s, 'RUN', 112 + dx, 40, 3, 2, ink, shear=1, keep=keep), top, bot)
        lines3(s, top, bot); return s
    return f
def logo(top, bot):                             # the logo's own RUN: its split is already on the join
    def f():
        s = R.base()
        for y in range(8, 16):
            for x in range(36):
                if R.LOGO[y][x] == '#': s.d.rectangle((116 + 2 * x, 40 + 2 * (y - 8), 117 + 2 * x, 41 + 2 * (y - 8)), fill=top if y < 12 else bot)
        lines3(s, top, bot, 110); return s
    return f
if __name__ == '__main__':
    L.sheet([('S1  Block: yellow over white', 'the egg\'s two colours', block(BY, BW)),
             ('S2  Block: white over yellow', 'the other way up', block(BW, BY)),
             ('S3  Block: white over black', 'bottom half in BREAKFAST\'s black', block(BW, K)),
             ('S4  Block: yellow over red', 'egg and ketchup; red is the weaker half on green', block(BY, BR)),
             ('S5  Block upright: white over yellow', 'no lean', block(BW, BY, shear=0)),
             ('S6  Wide block: yellow over white', 'broader letters', block(BY, BW, font=V.WIDE, gap=1)),
             ('S7  Spectrum heavy: white over yellow', 'the Spectrum\'s own letters, thickened', rom(BW, BY)),
             ('S8  The logo\'s RUN: white over yellow', 'today\'s letters; their split already sits on the join', logo(BW, BY)),
             ('S9  Block: white over blue', 'a cold bottom half', block(BW, BB)),
             ('S10  Block: yellow over magenta', 'loud', block(BY, BM))],
            'Breakfast Run - RUN cut through the middle, a colour above and a colour below', 'run_split_options.png')
