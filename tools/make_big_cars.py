"""Draft 20 x 20 cars (Grant, 10 Nov 2026: "could you try design some larger cars" - big
enough to carry their race number). Built from his own 16 x 16 heading-0 cars in
tools/car_art.txt, one-bit-art skill: the same key shapes and values (his cars are solid
ink with paper features), mirror-symmetric about column 9 (bodies an odd width, so a
3-wide number sits dead centre), and the race number carved in paper out of a solid
5 x 7 plate (rule 8d). Writes tools/big_car_art.txt (heading 0 of each, for the car
editor) and docs/design/big_cars.png (before and after, 4x, and real size on the cloth)."""
import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
DIG = {'1': ".X.XX..X..X.XXX", '2': "XX...X.X.X..XXX", '3': "XX...X.X...XXX.", '4': "X.XX.XXXX..X..X", '5': "XXXX..XX...XXX."}
# left half and the centre column (cols 0..9); mirrored to cols 10..18; col 19 empty
HALF = {
 'YOU': ("1", 3, [          # number on the bonnet, rows 3-7
  "..........",
  ".......XXX",
  "......XXXX",
  ".....XXXXX",
  "..XXXXXXXX",
  "..XoXXXXXX",
  "..XoXXXXXX",
  "..XXXXXXXX",
  ".....XXXXX",
  "......Xooo",
  "......Xooo",
  ".....XXXXX",
  ".....XXXXX",
  "..XXXXXXXX",
  "..XoXXXXXX",
  "..XoXXXXXX",
  "..XXXXoooo",
  "...XXXoooo",
  "...XXXXXXX",
  ".........."]),
 'CYAN': ("2", 5, [         # number between the front wheels, rows 5-9
  "..........",
  ".......XXX",
  "......XXXX",
  "..XXXXoooo",
  "..X.XXXXXX",
  "..XX.XXXXX",
  "..X.XXXXXX",
  "..XX.XXXXX",
  ".....XXXXX",
  ".....XXXXX",
  ".....XXXXX",
  ".....Xoooo",
  ".....Xoooo",
  "..XXXXXXXX",
  "..XoXXoooo",
  "..XoXXXXXX",
  "..XoXXXXXX",
  "..XXXXoooo",
  "...XXXXXXX",
  ".........."]),
 'WHITE': ("3", 9, [        # Slim Jane: the number on her body, rows 9-13
  "..........",
  "..........",
  ".....XX..X",
  ".....XXXXX",
  ".....XX..X",
  ".....XX..X",
  ".........X",
  "........XX",
  ".......XXX",
  ".......XXX",
  ".......XXX",
  ".......XXX",
  ".......XXX",
  ".......XXX",
  ".......XXX",
  "....XX.XXX",
  "....XXXXXX",
  "....XX.XXX",
  "....XX....",
  ".........."]),
 'PINK': ("4", 10, [        # the tank: the number on the turret, ringed in paper
  "..........",
  "........XX",
  "........XX",
  "........XX",
  "........XX",
  ".XXX....XX",
  ".X.XXXXXXX",
  ".XX.XXXXXX",
  ".X.XXXXooo",
  ".XX.XXoXXX",
  ".X.XXXoXXX",
  ".XX.XXoXXX",
  ".X.XXXoXXX",
  ".XX.XXoXXX",
  ".X.XXXoXXX",
  ".XX.XXoXXX",
  ".X.XXXXooo",
  ".XX.XXXXXX",
  ".XXX......",
  ".........."]),
 'GREEN': ("5", 8, [        # the clown car: the number in its paper ring
  "..........",
  "..........",
  ".XX....XXX",
  ".XX..XXXXX",
  ".XX.XXXXXX",
  ".XX.XXXXXX",
  "....XXXooo",
  "....XXoXXX",
  "....XXoXXX",
  "....XXoXXX",
  "....XXoXXX",
  "....XXoXXX",
  "....XXoXXX",
  "....XXoXXX",
  "....XXXooo",
  ".XX.XXXXXX",
  ".XX.XXXXXX",
  ".XX..XXXXX",
  ".XX....XXX",
  ".........."]),
}
def build(name):
    d, y0, half = HALF[name]
    g = [list(h + h[:-1][::-1] + '.') for h in half]
    for y in range(5):
        for x in range(3):
            assert g[y0 - 1][8 + x] == 'X' and g[y0 + 5][8 + x] == 'X' and g[y0 + y][7] == 'X' and g[y0 + y][11] == 'X', name
            if DIG[d][y * 3 + x] == 'X': g[y0 + y][8 + x] = 'o'
    return [''.join(r) for r in g]
def load_art():                   # Grant's drawings (tools/big_car_art.txt) win over the drafts
    import re
    p = os.path.join(HERE, 'big_car_art.txt')
    if not os.path.exists(p): return None
    t = open(p).read()
    if "GRANT'S DRAWINGS" not in t: return None
    return {m.group(1): m.group(2).split()[:20] for m in re.finditer(r'== (\w+) big heading 0 ==\n((?:[Xo.]{20}\n){20})', t)}
BIG = load_art() or {n: build(n) for n in HALF}

def small(name):
    t = open(os.path.join(HERE, 'car_art.txt')).read().splitlines()
    i = t.index('== %s heading 0 ==' % name)
    return t[i + 1:i + 17]
INK, PAP = (0, 0, 215), (0, 215, 215)
def pic(g, s, bg):
    n = len(g); im = Image.new('RGB', (n * s, n * s), bg); px = im.load()
    solid = [[c != '.' for c in r] for r in g]
    for y in range(n):
        for x in range(n):
            halo = any(solid[y + j][x + i] for j in (-1, 0, 1) for i in (-1, 0, 1) if 0 <= y + j < n and 0 <= x + i < n)
            if not halo: continue
            c = INK if g[y][x] == 'X' else PAP
            for a in range(s):
                for b in range(s): px[x * s + a, y * s + b] = c
    return im
def cloth(w, h):                     # the game's cloth: 32-px checks, dark ones 1 dot in 8
    im = Image.new('RGB', (w, h), PAP); px = im.load()
    for y in range(h):
        for x in range(w):
            if ((x // 32) + (y // 32)) % 2 and ((y % 4 == 0 and x % 4 == 0) or (y % 4 == 2 and x % 4 == 2)):
                px[x, y] = INK
    return im
if __name__ == '__main__':
    if load_art() is None:
     with open(os.path.join(HERE, 'big_car_art.txt'), 'w') as f:
        f.write("BREAKFAST RUN BIG CAR ART v1 - DRAFTS, not in the game\n"
                "X = ink   o = paper   . = empty. 20 x 20, heading 0 (facing up), each with its race\n"
                "number carved in paper. Generated by tools/make_big_cars.py from Grant's 16 x 16 cars;\n"
                "edit them in the car editor's Big cars mode and paste the copy back here.\n\n")
        for n, g in BIG.items():
            f.write('== %s big heading 0 ==\n' % n + '\n'.join(g) + '\n\n')
    order = ['YOU', 'CYAN', 'WHITE', 'PINK', 'GREEN']
    S = 6; fnt = ImageFont.load_default()
    W = 20 + len(order) * (20 * S + 24); out = Image.new('RGB', (W, 470 + 20 * S), (17, 18, 22)); d = ImageDraw.Draw(out)
    d.text((20, 8), 'Before: 16 x 16 (as in the game)', fill=(236, 235, 230), font=fnt)
    d.text((20, 40 + 16 * S), 'After: 20 x 20, Grant\'s drawings', fill=(236, 235, 230), font=fnt)
    for i, n in enumerate(order):
        x = 20 + i * (20 * S + 24)
        d.text((x, 24), n if n != 'WHITE' else 'WHITE (Jane)', fill=(160, 165, 175), font=fnt)
        out.paste(pic(small(n), S, (40, 44, 52)), (x + 2 * S, 36))
        out.paste(pic(BIG[n], S, (40, 44, 52)), (x, 56 + 16 * S))
    y = 80 + 36 * S
    d.text((20, y), 'Real size on the cloth (shown 3x): the 16 x 16 cars above, the 20 x 20 below', fill=(236, 235, 230), font=fnt)
    strip = cloth(176, 56)
    for i, n in enumerate(order):
        strip.paste(pic(small(n), 1, PAP), (8 + i * 34, 4), pic(small(n), 1, PAP).convert('L').point(lambda v: 255 if v != 215 * 0 else 0) if False else None)
    # paste with the car's own halo as the mask
    def paste(im, g, x0, y0):
        m = pic(g, 1, (0, 0, 0)); mk = Image.new('L', m.size, 0); mp = mk.load(); src = m.load()
        for yy in range(m.size[1]):
            for xx in range(m.size[0]): mp[xx, yy] = 0 if src[xx, yy] == (0, 0, 0) else 255
        im.paste(m, (x0, y0), mk)
    strip = cloth(176, 56)
    for i, n in enumerate(order):
        paste(strip, small(n), 10 + i * 34, 6); paste(strip, BIG[n], 8 + i * 34, 30)
    out.paste(strip.resize((176 * 3, 56 * 3), Image.NEAREST), (20, y + 16))
    p = os.path.join(ROOT, 'docs', 'design', 'big_cars.png'); out.save(p); print('wrote', p)
