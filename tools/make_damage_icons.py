"""Icons for the car's health gauge, to choose from (Grant, 14 Nov 2026: "could you mockup some
alternative icons about the heart size that represent engine health" - "a heart is for a person,
more than for a car, looking for something more mechanical"). Each is 16 x 13, an outline (O) that
stays and a fill (F) that empties from the top as health is lost, as the game draws its gauge
(racer.asm, dmg_draw). Usage: python3 tools/make_damage_icons.py -> docs/design/damage_icons.png
It also writes src/dmgicon.asm, the one the game uses (GAME, below)."""
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
MORE = {     # a second round (Grant, 14 Nov 2026: "can you try a few more icons for health/damage")
 'I  Oil drop': """
.......OO.......
......OFFO......
......OFFO......
.....OFFFFO.....
....OFFFFFFO....
...OFFFFFFFFO...
..OFFFFFFFFFFO..
..OFFFFFFFFFFO..
..OFFFFFFFFFFO..
..OFFFFFFFFFFO..
...OFFFFFFFFO...
....OFFFFFFO....
.....OOOOOO.....""",
 'J  Nut': """
....OOOOOOOO....
...OFFFFFFFFO...
..OFFFFFFFFFFO..
.OFFFFOOOOFFFFO.
OFFFFO....OFFFFO
OFFFO......OFFFO
OFFFO......OFFFO
OFFFO......OFFFO
OFFFFO....OFFFFO
.OFFFFOOOOFFFFO.
..OFFFFFFFFFFO..
...OFFFFFFFFO...
....OOOOOOOO....""",
 'K  Shield': """
OOOOOOOOOOOOOOOO
OFFFFFFFFFFFFFFO
OFFFFFFFFFFFFFFO
OFFFFFFFFFFFFFFO
OFFFFFFFFFFFFFFO
OFFFFFFFFFFFFFFO
.OFFFFFFFFFFFFO.
.OFFFFFFFFFFFFO.
..OFFFFFFFFFFO..
...OFFFFFFFFO...
....OFFFFFFO....
.....OFFFFO.....
......OOOO......""",
 'L  Spark plug': """
......OOOO......
......OFFO......
.....OOFFOO.....
.....OFFFFO.....
.....OFFFFO.....
....OOFFFFOO....
...OFFFFFFFFO...
...OOOFFFFOOO...
.....OFFFFO.....
.....OFFFFO.....
.....OOFFOO.....
......OFFOOO....
......OOOO.O....""",
 'M  Car from the side': """
................
....OOOOOOO.....
...OFFFFFFFO....
..OFFFFFFFFFO...
.OFFFFFFFFFFFO..
OOOOOOOOOOOOOOOO
OFFFFFFFFFFFFFFO
OFFFFFFFFFFFFFFO
OFFFFFFFFFFFFFFO
OOOOOOOOOOOOOOOO
..OFFO....OFFO..
..OFFO....OFFO..
...OO......OO...""",
 'N  Crash helmet': """
....OOOOOOOO....
..OOFFFFFFFFOO..
.OFFFFFFFFFFFFO.
OFFFFFFFFFFFFFFO
OFFFFFFFFFFFFFFO
OFFFFFOOOOOOOOOO
OFFFFO.........O
OFFFFO.........O
OFFFFFOOOOOOOOOO
OFFFFFFFFFFFFFO.
OFFFFFFFFFFFFO..
.OFFFFFFFFFFO...
..OOOOOOOOOO....""",
 'O  Dial': """
....OOOOOOOO....
..OOFFFFFFFFOO..
.OFFFFFFFFFFFFO.
.OFFFFFFFFOOFFO.
OFFFFFFFFOOFFFFO
OFFFFFFFOOFFFFFO
OFFFFFFOOFFFFFFO
OFFFFFOOOOFFFFFO
OFFFFFOOOOFFFFFO
.OFFFFFFFFFFFFO.
.OFFFFFFFFFFFFO.
..OOFFFFFFFFOO..
....OOOOOOOO....""",
 'P  Lightning': """
......OOOOOOO...
.....OFFFFFO....
....OFFFFFO.....
...OFFFFFO......
..OFFFFFOOOOO...
.OFFFFFFFFFFO...
.OOOOOFFFFFO....
.....OFFFFO.....
....OFFFFO......
...OFFFO........
..OFFO..........
.OFO............
.OO.............""",
 'Q  Wheel': """
....OOOOOOOO....
..OOFFFFFFFFOO..
.OFFFOOOOOOFFFO.
.OFFO......OFFO.
OFFO........OFFO
OFFO...OO...OFFO
OFFO..OFFO..OFFO
OFFO...OO...OFFO
OFFO........OFFO
.OFFO......OFFO.
.OFFFOOOOOOFFFO.
..OOFFFFFFFFOO..
....OOOOOOOO....""",
}
for k in MORE:
    MORE[k] = MORE[k].strip().split('\n'); assert len(MORE[k]) == 13 and all(len(r) == 16 for r in MORE[k]), k
for k in ICONS:
    ICONS[k] = ICONS[k].strip().split('\n'); assert len(ICONS[k]) == 13 and all(len(r) == 16 for r in ICONS[k]), k
THIRD = {    # a third round (Grant, 15 Nov 2026: "bring up alternative graphics for the damage. I would like to try something else")
 'Q  Battery': """
..OOO......OOO..
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
OFFFFFFFFFFFFFFO
OOOOOOOOOOOOOOOO""",
 'R  Shield': """
OOOOOOOOOOOOOOOO
OFFFFFFFFFFFFFFO
OFFFFFFFFFFFFFFO
OFFFFFFFFFFFFFFO
OFFFFFFFFFFFFFFO
OFFFFFFFFFFFFFFO
.OFFFFFFFFFFFFO.
.OFFFFFFFFFFFFO.
..OFFFFFFFFFFO..
...OFFFFFFFFO...
....OFFFFFFO....
.....OOFFOO.....
.......OO.......""",
 'S  Car': """
....OOOOOOOO....
..OOFFFFFFFFOO..
.OFFFFFFFFFFFFO.
OOFFOOOOOOOOFFOO
OOFFOFFFFFFOFFOO
.OFFOFFFFFFOFFO.
.OFFOOOOOOOOFFO.
.OFFFFFFFFFFFFO.
OOFFFFFFFFFFFFOO
OOFFOOOOOOOOFFOO
.OFFFFFFFFFFFFO.
..OOFFFFFFFFOO..
....OOOOOOOO....""",
 'T  Mug of coffee': """
................
OOOOOOOOOOOO....
OFFFFFFFFFFOOOO.
OFFFFFFFFFFO..OO
OFFFFFFFFFFO...O
OFFFFFFFFFFO...O
OFFFFFFFFFFO..OO
OFFFFFFFFFFOOOO.
OFFFFFFFFFFO....
OFFFFFFFFFFO....
OFFFFFFFFFFO....
.OFFFFFFFFO.....
..OOOOOOOO......""",
 'U  Slice of toast': """
..OOOOOOOOOOOO..
.OFFFFFFFFFFFFO.
OFFFFFFFFFFFFFFO
OFFFFFFFFFFFFFFO
.OFFFFFFFFFFFFO.
..OFFFFFFFFFFO..
..OFFFFFFFFFFO..
..OFFFFFFFFFFO..
..OFFFFFFFFFFO..
..OFFFFFFFFFFO..
..OFFFFFFFFFFO..
..OFFFFFFFFFFO..
..OOOOOOOOOOOO..""",
 'V  Petrol can': """
.....OOOO.......
.....O..O..OOO..
OOOOOOOOOOOOFO..
OFFFFFFFFFFFFO..
OFFFFFFFFFFFFO..
OFFFOFFFFOFFFO..
OFFFFOFFOFFFFO..
OFFFFFOOFFFFFO..
OFFFFOFFOFFFFO..
OFFFOFFFFOFFFO..
OFFFFFFFFFFFFO..
OFFFFFFFFFFFFO..
OOOOOOOOOOOOOO..""",
 'W  Bars': """
OOOOOOOOOOOOOOOO
OFFFFFFFFFFFFFFO
OOOOOOOOOOOOOOOO
OFFFFFFFFFFFFFFO
OOOOOOOOOOOOOOOO
OFFFFFFFFFFFFFFO
OOOOOOOOOOOOOOOO
OFFFFFFFFFFFFFFO
OOOOOOOOOOOOOOOO
OFFFFFFFFFFFFFFO
OOOOOOOOOOOOOOOO
OFFFFFFFFFFFFFFO
OOOOOOOOOOOOOOOO""",
 'X  Cross': """
.....OOOOOO.....
.....OFFFFO.....
.....OFFFFO.....
.....OFFFFO.....
OOOOOOFFFFOOOOOO
OFFFFFFFFFFFFFFO
OFFFFFFFFFFFFFFO
OFFFFFFFFFFFFFFO
OOOOOOFFFFOOOOOO
.....OFFFFO.....
.....OFFFFO.....
.....OFFFFO.....
.....OOOOOO.....""",
 'Y  Star': """
.......OO.......
......OFFO......
......OFFO......
OOOOOOFFFFOOOOOO
.OFFFFFFFFFFFFO.
..OFFFFFFFFFFO..
...OFFFFFFFFO...
...OFFFFFFFFO...
..OFFFFOOFFFFO..
..OFFFO..OFFFO..
.OFFOO....OOFFO.
.OOO........OOO.
................""",
}
for k in list(THIRD):
    THIRD[k] = THIRD[k].strip().split('\n'); assert len(THIRD[k]) == 13 and all(len(r) == 16 for r in THIRD[k]), k
def draw(art, dmg, s):
    im = Image.new('RGB', (20, 17), (0, 215, 215)); px = im.load()
    for y in range(17):                          # a bit of the cloth round the clear patch
        for x in range(20):
            if not (2 <= x < 18 and 2 <= y < 15) and y % 2 == 0 and x % 4 == (y & 2): px[x, y] = (0, 0, 215)
    for y, r in enumerate(art):
        for x, c in enumerate(r):
            if c == 'O' or (c == 'F' and y >= EMP[dmg]): px[2 + x, 2 + y] = (0, 0, 215)
    return im.resize((20 * s, 17 * s), Image.NEAREST)
def sheet(icons, title, name):
    try: f = ImageFont.truetype('DejaVuSans-Bold.ttf', 22); fs = ImageFont.truetype('DejaVuSans.ttf', 17)
    except OSError: f = fs = ImageFont.load_default()
    BG, FG = (17, 18, 22), (236, 235, 230); LV = (0, 2, 4, 6, 8); S = 6; x0 = 360
    W = x0 + len(LV) * (20 * S + 14) + 5 * 34 + 40; rowh = 17 * S + 26
    out = Image.new('RGB', (W, 70 + len(icons) * rowh + 10), BG); d = ImageDraw.Draw(out)
    d.text((20, 12), title, fill=(255, 255, 255), font=f)
    for i, lv in enumerate(LV): d.text((x0 + i * (20 * S + 14), 44), ['whole', '2 hits', '4 hits', '6 hits', '8: wrecked'][i], fill=FG, font=fs)
    d.text((x0 + len(LV) * (20 * S + 14) + 10, 44), 'real size', fill=FG, font=fs)
    for n, (nm, art) in enumerate(icons.items()):
        y = 70 + n * rowh; d.text((20, y + 40), nm, fill=FG, font=f)
        for i, lv in enumerate(LV): out.paste(draw(art, lv, S), (x0 + i * (20 * S + 14), y))
        for i, lv in enumerate(LV): out.paste(draw(art, lv, 1), (x0 + len(LV) * (20 * S + 14) + 10 + i * 34, y + 40))
    p = os.path.join(HERE, '..', 'docs', 'design', name); out.save(p); print('wrote', os.path.normpath(p), out.size)
GAME = 'Steaming mug'                          # the one in the game, from tools/gauge_mugs.txt (Grant, 15 Nov 2026: "I like 2 the steaming mug";
                                               # before it 'P  Lightning'). Its top three rows are the steam, which dmg_anim (plate_slow.asm) moves.
def mugs():
    import re
    t = open(os.path.join(HERE, 'gauge_mugs.txt')).read()
    return {m.group(1): m.group(2).split() for m in re.finditer(r'== (.+) ==\n((?:[OF.]{16}\n){13})', t)}
def game_art():
    return mugs()[GAME]
HALO = 4                                       # the icon sits 4 pixels in from the window's edge (2 until the mug: its steam is then all in the middle byte)
def game_rows():
    """The gauge as the game draws it: 16 rows of 24 pixels - 3 colour cells by 2, ALL of them
    cleared (so nothing else in those cells can take the icon's colour: Grant, 14 Nov 2026, "these
    would need a decent mask to prevent colour clash"), the icon's 13 rows from the second.
    Each row: (keep, outline, fill) as 24-bit numbers; keep is 0."""
    art = game_art(); W = 24; rows = []
    for y in range(16):
        a = art[y - 1] if 0 <= y - 1 < 13 else '.' * 16
        bit = lambda ch: sum(1 << (W - 1 - (x + HALO)) for x, c in enumerate(a) if c == ch)
        rows.append((0, bit('O'), bit('F')))
    return rows
def write_game():
    """src/dmgicon.asm: the gauge's art for dmg_draw - for each of a row's 3 bytes: outline, fill."""
    name = '   ' + GAME
    with open(os.path.join(HERE, '..', 'src', 'dmgicon.asm'), 'w') as g:
        g.write('; GENERATED by tools/make_damage_icons.py: the health gauge\'s icon, "%s". 16 rows (a clear one,\n; its 13, two clear); for each of a row\'s 3 bytes: the outline, the fill.\ndmg_heart:\n' % name[3:])
        for keep, o, f in game_rows():
            g.write('        db ' + ','.join('0x%02X,0x%02X' % ((o >> sh) & 255, (f >> sh) & 255) for sh in (16, 8, 0)) + '\n')
if __name__ == '__main__':
    sheet(ICONS, 'Health gauge icons, 16 x 13: the outline stays, the fill empties from the top (mock-up)', 'damage_icons.png')
    sheet(MORE, 'More health gauge icons, 16 x 13 (mock-up)', 'damage_icons_2.png')
    sheet(THIRD, 'A third set of health gauge icons, 16 x 13 (mock-up)', 'damage_icons_3.png')
    write_game()
