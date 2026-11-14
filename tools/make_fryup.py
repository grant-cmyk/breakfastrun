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
def fryup(d=116):
    o, c = mc.round_obj('Fried egg and bacon on a plate, %d across' % d, d); o.label[o.label > 0] = mc.WHITE + 1
    y, x = np.mgrid[0:d, 0:d]
    ex, ey = c - 19, c + 2; t = np.arctan2(y - ey, x - ex)       # the egg: a wobbly outline, left of centre
    r = 19.5 + 1.4 * np.sin(2 * t + 0.6) + 0.8 * np.sin(3 * t + 2.2); dist = np.hypot(x - ex, y - ey)
    o.ink(((dist <= r) & (dist >= r - 1.6)).astype(np.uint8), 0, 0)
    m = o.second_ink(mc.disc(d, d, ex - 1, ey - 1, 6.4), mc.YELLOW)
    for (px, py) in ((int(ex) - 3, int(ey) - 3), (int(ex) - 4, int(ey) - 2)):    # a glint on the yolk
        if m[py, px]: o.bits[py, px] = 0; o.ink2[py, px] = 0
    for bx, ph, top, bot in ((c + 17, 0.0, -26, 26), (c + 29, 1.4, -15, 16)):   # two rashers, wavy, right of the egg
        cx = bx + 2.2 * np.sin((y - c) / 4.2 + ph)
        rasher = ((np.abs(x - cx) <= 4.2) & (y - c >= top) & (y - c <= bot)).astype(np.uint8)
        m = o.second_ink(rasher, mc.RED)
        fat = (np.abs(x - cx - 1.3) <= 0.6) & (m == 1)             # the streak of fat: the plate's white showing
        o.bits[fat] = 0; o.ink2[fat] = 0
    return o
if __name__ == '__main__':
    o = fryup(); mc.verify(o); print('no clash at any of the 64 positions')
    DESIGN = os.path.join(HERE, '..', 'docs', 'design')
    sb, sa = load(os.path.join(DESIGN, 'mock_objects_racing.bin')); win = sb[8:152, 8:184].copy(); clean = mc.clean_cloth(win)
    world = np.tile(clean[0:64, 0:64], (4, 4))
    W = (o.w + 23) // 8 * 8; H = (o.h + 23) // 8 * 8
    b, a = mc.compose(world[24:24 + H, 16:16 + W], [(o, (W - o.w) // 2 + 3, (H - o.h) // 2 + 2)])
    big, one, two = mc.show(b, a, 6), mc.show(b, a, 1), mc.show(b, a, 2)
    gb, ga = mc.compose(clean, [(o, 30, -44)], sprites=(mc.grow((win ^ clean).astype(np.uint8)), win))    # in the game's window, above the road
    sb[8:152, 8:184] = gb; sa[1:19, 1:23] = ga; scr = render(sb, sa, border=6, s=3)
    try: f = ImageFont.truetype('DejaVuSans-Bold.ttf', 24); fs = ImageFont.truetype('DejaVuSans.ttf', 18)
    except OSError: f = fs = ImageFont.load_default()
    BG, FG = (17, 18, 22), (236, 235, 230)
    out = Image.new('RGB', (big.width + scr.width + 60, max(big.height + 60 + two.height + 40, scr.height + 110) + 20), BG); d = ImageDraw.Draw(out)
    d.text((20, 14), 'Fried egg and bacon on a plate, from above: 116 pixels across (mock-up)', fill=(255, 255, 255), font=f)
    out.paste(big, (20, 60)); out.paste(one, (20, 60 + big.height + 20)); out.paste(two, (20 + one.width + 20, 60 + big.height + 20))
    d.text((20 + one.width + two.width + 60, 60 + big.height + 20), 'real size, and twice size', fill=FG, font=fs)
    out.paste(scr, (big.width + 40, 60))
    for k, t in enumerate(['In the game\'s window, part in view above the road.', 'Blue rim, white plate, yellow yolk, red bacon: four colours, no clash.',
                           'The egg\'s white is the plate\'s white inside a blue outline.']):
        d.text((big.width + 40, 60 + scr.height + 10 + 26 * k), t, fill=FG, font=fs)
    p = os.path.join(DESIGN, 'egg_bacon_plate.png'); out.save(p); print('wrote', os.path.normpath(p), out.size)
