"""Icons for the car's health gauge, to choose from (Grant, 14 Nov 2026: "could you mockup some
alternative icons about the heart size that represent engine health" - "a heart is for a person,
more than for a car, looking for something more mechanical"). Each is 16 x 13, an outline (O) that
stays and a fill (F) that empties from the top as health is lost, as the game draws its gauge
(racer.asm, dmg_draw). Usage: python3 tools/make_damage_icons.py -> docs/design/damage_icons.png
ICONS[name] is the art; the game's gauge is made from one of them."""
import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
EMP = [1, 2, 3, 4, 5, 6, 8, 10, 13]            # rows empty for damage 0..8 (dmg_emp)
ICONS = {
 'A  Cog': """
......OOOO......
..OO..OFFO..OO..
.OFFOOOFFOOOFFO.
.OFFFFFFFFFFFFO.
..OFFFOOOOFFFO..
OOOFFO....OFFOOO
OFFFFO....OFFFFO
OOOFFO....OFFOOO
..OFFFOOOOFFFO..
.OFFFFFFFFFFFFO.
.OFFOOOFFOOOFFO.
..OO..OFFO..OO..
......OOOO......""",
 'B  Engine': """
....OOOOOOOO....
....OFFFFFFO....
..OOOOOOOOOOOO..
..OFFFFFFFFFFO..
OOOFFFFFFFFFFOOO
OFOFFFFFFFFFFOFO
OFOFFFFFFFFFFOFO
OFOFFFFFFFFFFOFO
OOOFFFFFFFFFFOOO
..OFFFFFFFFFFO..
..OFFFFFFFFFFO..
..OFFFFFFFFFFO..
..OOOOOOOOOOOO..""",
 'C  Spanner': """
...OOO....OOO...
...OFO....OFO...
...OFO....OFO...
...OFFOOOOFFO...
....OFFFFFFO....
.....OFFFFO.....
.....OFFFFO.....
.....OFFFFO.....
.....OFFFFO.....
.....OFFFFO.....
.....OFFFFO.....
.....OFFFFO.....
.....OOOOOO.....""",
 'D  Fuel can': """
...OOOO...OOO...
...OFFO...OFO...
.OOOOOOOOOOOOOO.
.OFFFFFFFFFFFFO.
.OFFFFFFFFFFFFO.
.OFFFFFFFFFFFFO.
.OFFFFFFFFFFFFO.
.OFFFFFFFFFFFFO.
.OFFFFFFFFFFFFO.
.OFFFFFFFFFFFFO.
.OFFFFFFFFFFFFO.
.OFFFFFFFFFFFFO.
.OOOOOOOOOOOOOO.""",
 'E  Battery': """
...OOO....OOO...
...OFO....OFO...
OOOOOOOOOOOOOOOO
OFFFFFFFFFFFFFFO
OFFFFFFFFFFFFFFO
OFFFFFFFFFFFFFFO
OFFFFFFFFFFFFFFO
OFFFFFFFFFFFFFFO
OFFFFFFFFFFFFFFO
OFFFFFFFFFFFFFFO
OFFFFFFFFFFFFFFO
OFFFFFFFFFFFFFFO
OOOOOOOOOOOOOOOO""",
 'F  Piston': """
..OOOOOOOOOOOO..
..OFFFFFFFFFFO..
..OOOOOOOOOOOO..
..OFFFFFFFFFFO..
..OFFFFFFFFFFO..
..OOOOFFFFOOOO..
......OFFO......
......OFFO......
......OFFO......
.....OOFFOO.....
....OFFFFFFO....
....OFFOOFFO....
.....OO..OO.....""",
 'G  Car from above': """
....OOOOOOOO....
..OOOFFFFFFOOO..
.OFFOFFFFFFOFFO.
.OFFOFFFFFFOFFO.
..OOOFFFFFFOOO..
....OFFFFFFO....
....OFFFFFFO....
....OFFFFFFO....
..OOOFFFFFFOOO..
.OFFOFFFFFFOFFO.
.OFFOFFFFFFOFFO.
..OOOFFFFFFOOO..
....OOOOOOOO....""",
 'H  Heart (in the game now)': """
..OOOO....OOOO..
.OFFFFO..OFFFFO.
OFFFFFFOOFFFFFFO
OFFFFFFFFFFFFFFO
OFFFFFFFFFFFFFFO
OFFFFFFFFFFFFFFO
.OFFFFFFFFFFFFO.
..OFFFFFFFFFFO..
...OFFFFFFFFO...
....OFFFFFFO....
.....OFFFFO.....
......OFFO......
.......OO.......""",
}
for k in ICONS:
    ICONS[k] = ICONS[k].strip().split('\n'); assert len(ICONS[k]) == 13 and all(len(r) == 16 for r in ICONS[k]), k
def draw(art, dmg, s):
    im = Image.new('RGB', (20, 17), (0, 215, 215)); px = im.load()
    for y in range(17):                          # a bit of the cloth round the clear patch
        for x in range(20):
            if not (2 <= x < 18 and 2 <= y < 15) and y % 2 == 0 and x % 4 == (y & 2): px[x, y] = (0, 0, 215)
    for y, r in enumerate(art):
        for x, c in enumerate(r):
            if c == 'O' or (c == 'F' and y >= EMP[dmg]): px[2 + x, 2 + y] = (0, 0, 215)
    return im.resize((20 * s, 17 * s), Image.NEAREST)
if __name__ == '__main__':
    try: f = ImageFont.truetype('DejaVuSans-Bold.ttf', 22); fs = ImageFont.truetype('DejaVuSans.ttf', 17)
    except OSError: f = fs = ImageFont.load_default()
    BG, FG = (17, 18, 22), (236, 235, 230); LV = (0, 2, 4, 6, 8); S = 6
    W = 360 + len(LV) * (20 * S + 14) + 5 * 34 + 40; rowh = 17 * S + 26
    out = Image.new('RGB', (W, 70 + len(ICONS) * rowh + 10), BG); d = ImageDraw.Draw(out)
    d.text((20, 12), 'Health gauge icons, 16 x 13: the outline stays, the fill empties from the top (mock-up)', fill=(255, 255, 255), font=f)
    x0 = 360
    for i, lv in enumerate(LV): d.text((x0 + i * (20 * S + 14), 44), ['whole', '2 hits', '4 hits', '6 hits', '8: wrecked'][i], fill=FG, font=fs)
    d.text((x0 + len(LV) * (20 * S + 14) + 10, 44), 'real size', fill=FG, font=fs)
    for n, (name, art) in enumerate(ICONS.items()):
        y = 70 + n * rowh; d.text((20, y + 40), name, fill=FG, font=f)
        for i, lv in enumerate(LV): out.paste(draw(art, lv, S), (x0 + i * (20 * S + 14), y))
        for i, lv in enumerate(LV): out.paste(draw(art, lv, 1), (x0 + len(LV) * (20 * S + 14) + 10 + i * 34, y + 40))
    p = os.path.join(HERE, '..', 'docs', 'design', 'damage_icons.png'); out.save(p); print('wrote', os.path.normpath(p), out.size)
