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
GAME = 'P'                                     # the one in the game (Grant, 14 Nov 2026: "lets do the lightning")
def game_art():
    return next(v for k, v in list(ICONS.items()) + list(MORE.items()) if k.startswith(GAME + ' '))
HALO = 2                                       # pixels of clear table kept round the icon, every way
def game_rows():
    """The gauge as the game draws it: 17 rows of 24 pixels - the icon with HALO clear pixels all
    round. Each row: (keep, outline, fill) as 24-bit numbers; keep = the table's pixels left alone."""
    art = game_art(); H, W = 13 + 2 * HALO, 24; sil = [[False] * W for _ in range(H)]
    for y, r in enumerate(art):
        for x, c in enumerate(r):
            if c != '.':
                for dy in range(-HALO, HALO + 1):
                    for dx in range(-HALO, HALO + 1): sil[y + HALO + dy][x + HALO + dx] = True
    rows = []
    for y in range(H):
        a = art[y - HALO] if 0 <= y - HALO < 13 else '.' * 16
        bit = lambda ch: sum(1 << (W - 1 - (x + HALO)) for x, c in enumerate(a) if c == ch)
        rows.append((sum(1 << (W - 1 - x) for x in range(W) if not sil[y][x]), bit('O'), bit('F')))
    return rows
def write_game():
    """src/dmgicon.asm: the gauge's art for dmg_draw - for each of a row's 3 bytes: keep, outline, fill."""
    name = next(k for k in list(ICONS) + list(MORE) if k.startswith(GAME + ' '))
    with open(os.path.join(HERE, '..', 'src', 'dmgicon.asm'), 'w') as g:
        g.write('; GENERATED by tools/make_damage_icons.py: the health gauge\'s icon, "%s", with %d clear pixels\n; round it. 17 rows; for each of a row\'s 3 bytes: the table\'s pixels to keep, the outline, the fill.\ndmg_heart:\n' % (name[3:], HALO))
        for keep, o, f in game_rows():
            g.write('        db ' + ','.join('0x%02X,0x%02X,0x%02X' % ((keep >> sh) & 255, (o >> sh) & 255, (f >> sh) & 255) for sh in (16, 8, 0)) + '\n')
if __name__ == '__main__':
    sheet(ICONS, 'Health gauge icons, 16 x 13: the outline stays, the fill empties from the top (mock-up)', 'damage_icons.png')
    sheet(MORE, 'More health gauge icons, 16 x 13 (mock-up)', 'damage_icons_2.png')
    write_game()
