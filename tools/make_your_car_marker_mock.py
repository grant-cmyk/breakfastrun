"""WHICH ONE IS YOURS - mock-up of three marks for your car when a computer driver has the same car (Grant, 23 Nov 2026: "you
can take one of their cars, then there are two of them on the road. We need a simple way though - perhaps a small graphic
tweak to specify which is yours"). Each mark is at the car's middle or round its edge, so it looks the same at every one of
the 32 headings and the game can put it on any car's frames as it unpacks them (no new drawings).
  A  a white spot on the roof (2 x 2, ringed in ink)
  B  a target: an ink dot in a white ring
  C  a bolder outline: the white edge round your car 2 px (the others 1)
Drawn on the breakfast table (a patch of the real race screen), at the game's size and four times it.
Usage: python3 tools/make_your_car_marker_mock.py <race screenshot, 352 x 288 with border>
Writes docs/design/choose_popup/your_car_marks.png."""
import sys, os, re
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
shot = Image.open(sys.argv[1]).convert('RGB')
INK = (0, 0, 215); WHITE = (255, 255, 255)
def art(f, name, h):
    t = open(os.path.join(HERE, f)).read()
    return [list(r) for r in re.search(r'== %s heading %s ==\n((?:[Xo.]{16}\n){16})' % (name, h), t).group(1).split()]
def mark(g, k):
    g = [r[:] for r in g]
    if k == 'A':
        for y in range(6, 10):
            for x in range(6, 10): g[y][x] = 'X'
        for y in (7, 8):
            for x in (7, 8): g[y][x] = 'o'
    if k == 'B':
        for y in range(6, 10):
            for x in range(6, 10): g[y][x] = 'o'
        for y in (7, 8):
            for x in (7, 8): g[y][x] = 'X'
    return g
def draw(im, g, ox, oy, halo):
    solid = lambda x, y: 0 <= x < 16 and 0 <= y < 16 and g[y][x] != '.'
    for y in range(-halo, 16 + halo):
        for x in range(-halo, 16 + halo):
            if solid(x, y): im.putpixel((ox + x, oy + y), INK if g[y][x] == 'X' else WHITE)
            elif any(solid(x + i, y + j) for i in range(-halo, halo + 1) for j in range(-halo, halo + 1) if i * i + j * j <= halo * halo + 1):
                im.putpixel((ox + x, oy + y), WHITE)
# a patch of the table: the race screen's play area, no cars in it (the shot's left half, middle rows)
patch = shot.crop((48 + 16, 48 + 40, 48 + 16 + 120, 48 + 40 + 44))
CARS = [('car_art.txt', 'PINK', 'TANK'), ('car_art.txt', 'YOU', 'RACER'), ('car_art.txt', 'WHITE', 'DRAGSTER')]
rows = []
for opt, lab in (('', 'THEIRS'), ('A', 'A  WHITE SPOT'), ('B', 'B  TARGET'), ('C', 'C  BOLDER OUTLINE')):
    im = patch.copy()
    x = 4
    for f, n, _ in CARS:
        for h in ('0', '45'):
            g = art(f, n, h)
            draw(im, mark(g, opt) if opt in 'AB' and opt else g, x, 14, 2 if opt == 'C' else 1)
            x += 19
    rows.append((lab, im))
Z = 4; LW = 260
W = LW + patch.width * Z + patch.width + 40; H = len(rows) * (patch.height * Z + 12) + 40
sheet = Image.new('RGB', (W, H), (240, 240, 236)); d = ImageDraw.Draw(sheet)
d.text((10, 10), 'Tank, racer, dragster - nose up and at 45 degrees. Left: four times the size. Right: the size in the game.', fill=(0, 0, 0))
for i, (lab, im) in enumerate(rows):
    y = 34 + i * (patch.height * Z + 12)
    d.text((10, y + patch.height * Z // 2 - 6), lab + ('  (the computer car)' if lab == 'THEIRS' else '  (yours)'), fill=(0, 0, 0))
    sheet.paste(im.resize((patch.width * Z, patch.height * Z), Image.NEAREST), (LW, y))
    sheet.paste(im, (LW + patch.width * Z + 20, y + patch.height * Z // 2 - patch.height // 2))
sheet.save(os.path.join(ROOT, 'docs/design/choose_popup/your_car_marks.png')); print('written')
