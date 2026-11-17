"""Mock-up: four ways to put TWO PLAYERS on one screen (Grant, 17 Nov 2026: "two players would exist in the same
screen, need to research options here to make this possible"). Track 1's road in the race-track look; red is
player 1, cyan player 2. Layouts only: the colours here are not held to the two-colours-a-square rule.
Writes docs/design/racetrack/two_player_options.png. Nothing here is in the game."""
import os, re, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
wsrc = open(os.path.join(HERE, 'make_world.py')).read()
wns = {'__file__': os.path.join(HERE, 'make_world.py')}
exec(wsrc[:wsrc.index('road = road_mask(ROAD)')], wns)
ROAD, road_mask, PATH = wns['ROAD'], wns['road_mask'], wns['PATH']
PAD = 160
def plain(w): return np.pad(np.array(road_mask(w), dtype=bool), PAD)
grass = ~plain(ROAD + 20); line = plain(ROAD + 16) & ~plain(ROAD + 14)
K, G, RD, CY, WH = (0, 0, 0), (0, 200, 0), (215, 0, 0), (0, 215, 215), (215, 215, 215)
world = np.zeros(grass.shape + (3,), np.uint8); world[grass] = G; world[line] = G
ca = open(os.path.join(HERE, 'car_art.txt')).read()
art = re.search(r'== YOU heading 0 ==\n((?:[Xo.]{16}\n){16})', ca).group(1).split()
aI = Image.fromarray((np.array([[c == 'X' for c in r] for r in art]) * 255).astype(np.uint8))
aB = Image.fromarray((np.array([[c != '.' for c in r] for r in art]) * 255).astype(np.uint8))
pts = []
for i in range(len(PATH)):
    (x0, y0), (x1, y1) = PATH[i], PATH[(i + 1) % len(PATH)]
    n = max(1, int(math.hypot(x1 - x0, y1 - y0) / 2))
    pts += [(x0 + PAD + (x1 - x0) * t / n, y0 + PAD + (y1 - y0) * t / n) for t in range(n)]
def at(i):
    (x, y), (x2, y2) = pts[i % len(pts)], pts[(i + 3) % len(pts)]
    return x, y, math.atan2(y2 - y, x2 - x)
def scene(cars):                                   # the world with these cars on it
    w = world.copy()
    for (x, y, a, col) in cars:
        deg = -math.degrees(a) - 90
        ri = np.array(aI.rotate(deg, resample=Image.NEAREST)) > 0; rb = np.array(aB.rotate(deg, resample=Image.NEAREST)) > 0
        px, py = int(x) - 8, int(y) - 8
        w[py:py + 16, px:px + 16][rb] = K; w[py:py + 16, px:px + 16][ri] = col
    return w
def view(w, cx, cy, ww, wh): return Image.fromarray(w[int(cy) - wh // 2:int(cy) - wh // 2 + wh, int(cx) - ww // 2:int(cx) - ww // 2 + ww])
I1 = 150                                            # player 1 here; player 2 a little behind (A) or far behind (B, C)
p1 = at(I1); near = at(I1 - 30); far = at(I1 - 190)
off = lambda p, d: (p[0] - math.sin(p[2]) * d, p[1] + math.cos(p[2]) * d, p[2])
S = 2; fnt = ImageFont.load_default()
sheet = Image.new('RGB', (2 * (256 * S + 16) + 16, 2 * (192 * S + 44) + 12), (40, 42, 48)); d = ImageDraw.Draw(sheet)
def put(k, title, note, img):
    ox = 16 + (k % 2) * (256 * S + 16); oy = 8 + (k // 2) * (192 * S + 44)
    d.text((ox, oy), title, fill=(236, 235, 230), font=fnt); d.text((ox, oy + 12), note, fill=(170, 172, 178), font=fnt)
    sheet.paste(img.resize((img.width * S, img.height * S), Image.NEAREST), (ox, oy + 28))
def screen(): return Image.new('RGB', (256, 192), (215, 215, 0))
# A: one shared window, the view between the two cars
a, b = off(p1, -8), off(near, 10); w = scene([a + (RD,), b + (CY,)])
im = screen(); im.paste(view(w, (a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 192, 152), (8, 8)); put(0, 'A: ONE SHARED VIEW', 'the view sits between you; fall off the screen and you lose the point', im)
# B: split top and bottom
w = scene([off(p1, 0) + (RD,), off(far, 0) + (CY,)])
im = screen(); im.paste(view(w, p1[0], p1[1], 192, 72), (8, 8)); im.paste(view(w, far[0], far[1], 192, 72), (8, 88)); put(1, 'B: SPLIT, TOP AND BOTTOM', 'each player a window 192 x 72: wide, but little to see up and down', im)
# C: split left and right
im = screen(); im.paste(view(w, p1[0], p1[1], 120, 176), (4, 8)); im.paste(view(w, far[0], far[1], 120, 176), (132, 8)); put(2, 'C: SPLIT, LEFT AND RIGHT', 'each a window 120 x 176 (the race order and panel give up their space)', im)
# D: the whole track on one screen, no scrolling
x0, x1 = PAD + 20, world.shape[1] - PAD - 20; y0, y1 = PAD + 30, world.shape[0] - PAD - 10
whole = Image.fromarray(scene([off(p1, 0) + (RD,), off(far, 0) + (CY,)])[y0:y1, x0:x1]).resize((256, int(256 * (y1 - y0) / (x1 - x0))), Image.NEAREST)
im = Image.new('RGB', (256, 192), G); im.paste(whole, (0, (192 - whole.height) // 2)); put(3, 'D: THE WHOLE TRACK, NO SCROLLING', 'today\'s track shrunk to fit: the cars come out about 7 pixels long', im)
out = os.path.join(ROOT, 'docs', 'design', 'racetrack', 'two_player_options.png'); sheet.save(out); print('wrote', out, whole.size)
