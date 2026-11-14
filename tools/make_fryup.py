"""A fried egg and bacon on a plate, seen from above (Grant, 14 Nov 2026: "can you show me a fried
egg and bacon on a plate"), in the solid-edge style of tools/make_colour_objects.py: the plate's
rim is the thick blue edge, the plate is white paper, the egg's white is a blue outline on it,
the yolk is YELLOW ink and the bacon RED ink - each kept 8 pixels from any other ink, so no cell
ever holds two. Checked at all 64 positions against the cell grid. A mock-up.
Usage: python3 tools/make_fryup.py   -> docs/design/egg_bacon_plate.png"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import make_colour_objects as mc
from make_layout_review import load, render
def far8(m):
    """Everything within 8 pixels (along each axis) of m: where another ink may not go."""
    for _ in range(8): m = mc.grow(m)
    return m
def fryup(d=104):
    """The plate is CYAN, like the cloth but plain, inside a blue rim (Grant, 14 Nov 2026: "the
    plate can be cyan, so the white of the egg shows, no outline of the egg required, the yolk sits
    inside of the white so that its character blocks are yellow on white"). The egg's white is
    WHITE ink, the yolk a hole in it whose cells have YELLOW paper, the bacon RED ink."""
    o = mc.Obj('Fried egg and bacon on a cyan plate, %d across' % d, d, d, round_=True); c = (d - 1) / 2
    y, x = np.mgrid[0:d, 0:d]
    rim = (o.shape == 1) & (np.hypot(x - c, y - c) > d / 2 - 8)
    o.bits = rim.astype(np.uint8); o.label[:] = 0
    used = o.bits.copy() | (1 - o.shape)                         # ink so far (and the cloth outside)
    ex, ey = c - 15, c + 2; t = np.arctan2(y - ey, x - ex)       # the egg's white: a wobbly shape, left of centre
    white = ((np.hypot(x - ex, y - ey) <= 19.5 + 1.6 * np.sin(2 * t + 0.6) + 1.0 * np.sin(3 * t + 2.2)) & (far8(used.copy()) == 0)).astype(np.uint8)
    o.bits[white == 1] = 1; o.ink2[white == 1] = mc.WHITE + 1
    yolk = mc.disc(d, d, ex - 1, ey - 1, 6.4) & (1 - far8(1 - white))   # the yolk: 8 pixels inside the white every way
    yolk[int(ey) - 4, int(ex) - 4] = yolk[int(ey) - 3, int(ex) - 5] = 0  # a glint
    o.bits[yolk == 1] = 0; o.ink2[yolk == 1] = 0; o.label[yolk == 1] = mc.YELLOW + 1
    used |= white
    for bx, ph, top, bot in ((c + 20, 0.0, -24, 24), (c + 32, 1.4, -13, 14)):    # the rashers, wavy, right of the egg
        cx = bx + 2.2 * np.sin((y - c) / 4.2 + ph)
        rasher = ((np.abs(x - cx) <= 4.2) & (y - c >= top) & (y - c <= bot) & (far8(used.copy()) == 0)).astype(np.uint8)
        fat = (np.abs(x - cx - 1.3) <= 0.6) & (rasher == 1)       # the streak of fat: the plate showing
        o.bits[rasher == 1] = 1; o.ink2[rasher == 1] = mc.RED + 1
        o.bits[fat] = 0; o.ink2[fat] = 0
    return o
def coffee_mug():
    """Black coffee in a white mug, from above (Grant, 14 Nov 2026: "coffee should be black in a
    mug/cup"): no blue at all. The mug's wall and handle are WHITE ink on the cloth's cyan; the
    coffee is a hole in it whose cells have BLACK paper - the wall is 8+ pixels thick, so no cell
    holds both coffee and cloth. The glint on the coffee is the same white ink."""
    w, h = 60, 46; c = 22.5                                     # (the wall is 11.4 thick: 8 pixels on the diagonal too)
    body = mc.disc(w, h, c, c, 22.4); handle = np.zeros((h, w), dtype=np.uint8); handle[16:30, 42:59] = 1; handle[16, 58] = handle[29, 58] = 0
    hole = np.zeros((h, w), dtype=np.uint8); hole[20:26, 49:54] = 1                 # the handle's hole: cloth shows through
    o = mc.blended('Black coffee in a white mug, 60 x 46', (body | handle) & (1 - hole), mc.WHITE, mc.disc(w, h, c, c, 11.0), mc.BLACK)
    m = mc.MARGIN + 1; arc = mc.ring(7.5, 1.3); arc[6:, :] = 0; arc[:, 6:] = 0       # a glint: white ink on the black
    for j in range(arc.shape[0]):
        for i in range(arc.shape[1]):
            yy, xx = m + 15 + j, m + 15 + i
            if arc[j, i] and o.label[yy, xx] == mc.BLACK + 1: o.bits[yy, xx] = 1; o.ink2[yy, xx] = mc.WHITE + 1
    return o
def line_mug(saucer=False):
    """Black coffee in a mug drawn as a BLACK LINE DRAWING on the cloth's cyan (Grant, 14 Nov 2026:
    "the mug can be cyan or blue, need to allow for the black coffee to be fuller in the mug, so if
    we do a black line drawing ... the surrounding area of the mug is black on cyan"). One ink,
    black: the mug's outline, its handle and the coffee itself; the mug's wall is cyan showing
    between the outline and the coffee, so the coffee can fill the mug. With a saucer: one more ring."""
    R = 27 if saucer else 20; w, h = 2 * R + (4 if saucer else 16), 2 * R + 1; c = float(R)
    y, x = np.mgrid[0:h, 0:w]; r = np.hypot(x - c, y - c)
    ink = (r <= R + .3).astype(np.uint8); cut = np.zeros((h, w), dtype=np.uint8)
    if saucer:
        cut |= ((r <= R - 2.2) & (r > 20.3)).astype(np.uint8)        # the saucer: a line, then cyan
    cut |= ((r <= 17.6) & (r > 15.2)).astype(np.uint8)               # the mug's wall: cyan between outline and coffee
    hy0, hy1, hx0, hx1 = int(c) - 6, int(c) + 7, int(c) + 18, int(c) + 33   # the handle: an outlined loop
    ink[hy0:hy1, hx0:min(hx1, w)] = 1; cut[hy0 + 2:hy1 - 2, hx0 + 2:min(hx1, w) - 2] |= 1
    if saucer: cut[hy0:hy1, int(c) + 21:w] &= ((r > R - 2.2) | (r <= 20.3))[hy0:hy1, int(c) + 21:w].astype(np.uint8)
    cut &= (1 - ((r <= 20.3) & (r > 17.6)).astype(np.uint8)) | ((x >= hx0 + 2) & (r > 20.3)).astype(np.uint8)   # (the outline stays whole)
    arc = ((np.abs(np.hypot(x - c, y - c) - 9.5) <= 0.8) & (x < c - 3) & (y < c - 3)).astype(np.uint8)       # a glint on the coffee
    cut |= arc; cut[int(c) + 6:int(c) + 8, int(c) + 5:int(c) + 7] = 1
    return mc.blended('Black coffee, a black line mug%s, %d x %d' % (' and saucer' if saucer else '', w, h), ink, mc.BLACK, cut=cut)
if __name__ == '__main__':
    objs = [fryup(), line_mug(), line_mug(True), coffee_mug()]
    for o in objs: mc.verify(o)
    print('no clash at any of the 64 positions')
    DESIGN = os.path.join(HERE, '..', 'docs', 'design')
    sb, sa = load(os.path.join(DESIGN, 'mock_objects_racing.bin')); win = sb[8:152, 8:184].copy(); clean = mc.clean_cloth(win)
    world = np.tile(clean[0:64, 0:64], (4, 4))
    try: f = ImageFont.truetype('DejaVuSans-Bold.ttf', 24); fs = ImageFont.truetype('DejaVuSans.ttf', 18)
    except OSError: f = fs = ImageFont.load_default()
    BG, FG = (17, 18, 22), (236, 235, 230); cards = []
    for o in objs:
        W = (o.w + 23) // 8 * 8; H = (o.h + 23) // 8 * 8
        b, a = mc.compose(world[24:24 + H, 16:16 + W], [(o, (W - o.w) // 2 + 3, (H - o.h) // 2 + 2)])
        big, one, two = mc.show(b, a, 4), mc.show(b, a, 1), mc.show(b, a, 2)
        card = Image.new('RGB', (max(big.width, one.width + two.width + 20), big.height + two.height + 56), BG)
        ImageDraw.Draw(card).text((0, 0), o.name, fill=FG, font=fs); card.paste(big, (0, 28)); card.paste(one, (0, big.height + 44)); card.paste(two, (one.width + 20, big.height + 44)); cards.append(card)
    gb, ga = mc.compose(clean, [(objs[0], -6, -65), (objs[1], 104, -22)], sprites=(mc.grow((win ^ clean).astype(np.uint8)), win))   # in the game's window, on the table ABOVE the road: nothing may spill into the road (Grant, 14 Nov 2026)
    sb[8:152, 8:184] = gb; sa[1:19, 1:23] = ga; scr = render(sb, sa, border=6, s=3)
    notes = ['In the game\'s window: both stand on the table above the road, clear of it and of the O\'s, so only part is in view.',
             'PLATE: blue rim, a plain cyan plate, the egg in white with no outline, the yolk\'s cells yellow on white, red bacon.',
             'MUG (new): a black line drawing on the cloth\'s cyan - the mug is cyan, the coffee fills it. With a saucer beside it.',
             'The earlier white mug is last, to compare.',
             'Every cell checked: one ink colour and one paper colour, at all 64 positions against the grid.']
    out = Image.new('RGB', (sum(c.width + 30 for c in cards) + scr.width + 40, max(max(c.height for c in cards), scr.height + 30 * len(notes) + 20) + 80), BG); d = ImageDraw.Draw(out)
    d.text((20, 14), 'Fried egg and bacon on a cyan plate, and black coffee in a mug three ways, from above (mock-up)', fill=(255, 255, 255), font=f)
    x = 20
    for c in cards: out.paste(c, (x, 60)); x += c.width + 30
    out.paste(scr, (x, 60))
    for k, t in enumerate(notes): d.text((x, 60 + scr.height + 10 + 28 * k), t, fill=FG, font=fs)
    p = os.path.join(DESIGN, 'egg_bacon_plate.png'); out.save(p); print('wrote', os.path.normpath(p), out.size)
