"""Table mock-ups: the play window as a chequered tablecloth. The dark checks are
a dither (the window has one ink and one paper colour, because the scroll moves
a pixel at a time and colour cells cannot follow it). Cereal O's mark both sides
of the road. Breakfast things, O's and cars are masked, so they sit on the
cloth in white. Usage: make_table_mockups.py corner.scr out.png"""
import sys, os, math, json, numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
SCR, OUT = sys.argv[1], sys.argv[2]
# the world's road and breakfast things, from make_world.py (stops before it writes anything)
src = open(os.path.join(HERE, 'make_world.py')).read()
ns = {'__file__': os.path.join(HERE, 'make_world.py'), '__name__': 'mock'}
exec(src[:src.index('# cut into tiles')], ns)
PW, PH, ROAD, PATH = ns['PW'], ns['PH'], ns['ROAD'], ns['PATH']
road = np.array(ns['road_mask'](ROAD), dtype=bool)
world = np.array(ns['img'], dtype=bool)
items = world & ~road                                   # breakfast things (kerbs and line are on the road)
def dilate(a):
    b = a.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            b |= np.roll(np.roll(a, dy, 0), dx, 1)
    return b
def outside(a):                                         # pixels reachable from the edge without crossing ink
    from collections import deque
    h, w = a.shape; seen = np.zeros_like(a); q = deque()
    for x in range(w): q += [(0, x), (h - 1, x)]
    for y in range(h): q += [(y, 0), (y, w - 1)]
    while q:
        y, x = q.popleft()
        if 0 <= y < h and 0 <= x < w and not seen[y, x] and not a[y, x]:
            seen[y, x] = True; q += [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]
    return seen
item_mask = dilate(items) | ~outside(dilate(items))     # halo, and solid inside every outline
# cereal O: a thick ring with a glint, its hole shows the cloth
O = ["..####..", ".#.####.", "###..###", "##....##", "##....##", "###..###", ".######.", "..####.."]
Oink = np.array([[c == '#' for c in r] for r in O])
Oholes = ~outside(Oink) & ~Oink
Omask = (dilate(np.pad(Oink, 1)) & ~np.pad(Oholes, 1))
Oink = np.pad(Oink, 1)
# O's along both sides of the road: walk the centre line, step out half a road plus 3 px
pts = PATH + [PATH[0]]
seq = []
for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
    n = max(1, int(math.hypot(x1 - x0, y1 - y0)))
    for i in range(n): seq.append((x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n))
os_ = []
for side in (-1, 1):
    last = None; acc = 0
    for i in range(len(seq)):
        (xa, ya), (xb, yb) = seq[i - 2], seq[(i + 2) % len(seq)]
        d = math.hypot(xb - xa, yb - ya) or 1
        nx, ny = -(yb - ya) / d, (xb - xa) / d
        p = (seq[i][0] + side * nx * (ROAD / 2 + 3), seq[i][1] + side * ny * (ROAD / 2 + 3))
        if last is None or math.hypot(p[0] - last[0], p[1] - last[1]) >= 15:
            if all(math.hypot(p[0] - q[0], p[1] - q[1]) >= 12 for q in os_):
                os_.append(p); last = p
start = np.zeros_like(world); start[:, :] = False
for y in range(240 + 32, 340 + 32):                     # the start line, as in make_world.py
    for x in range(256 + 32, 264 + 32):
        if road[y, x]: start[y, x] = True
car_art = json.load(open(sys.argv[3]))                  # [car][3 headings] rows of X o .
def frames(k):
    g = [np.array([[c for c in r] for r in h]) for h in car_art[k]]
    md = lambda a: np.array([[a[15 - c][15 - r] for c in range(16)] for r in range(16)])
    f = [g[0], g[1], g[2], md(g[1])]
    for i in range(4, 16): f.append(np.rot90(f[i - 4], -1))
    return f
CARF = [frames(k) for k in range(5)]
def cloth(kind, C=32):
    yy, xx = np.mgrid[0:PH, 0:PW]
    dark = ((xx // C) + (yy // C)) % 2 == 1
    if kind == 'half': pat = (xx + yy) % 2 == 0
    elif kind == 'quarter': pat = (xx % 2 == 0) & (yy % 2 == 0)
    elif kind == 'lines': pat = (xx + yy) % 4 == 0
    return dark & pat
def compose(kind, cars):
    bm = cloth(kind)
    bm &= ~item_mask; bm |= items
    bm[start] = ((np.mgrid[0:PH, 0:PW][1] // 4 + np.mgrid[0:PH, 0:PW][0] // 4) % 2 == 0)[start]
    for x, y in os_:
        X, Y = int(round(x)) - 5, int(round(y)) - 5
        win = bm[Y:Y + 10, X:X + 10]; win &= ~Omask; win |= Oink
    for k, (x, y, h) in enumerate(cars):
        g = CARF[k][h]; solid = g != '.'
        m = dilate(np.pad(solid, 1))[1:-1, 1:-1] | solid
        win = bm[y:y + 16, x:x + 16]; win &= ~m; win |= (g == 'X')
    return bm
# the real screen around the window: HUD, panel and logo; window and frame redrawn
scr = open(SCR, 'rb').read()
PAL = [(0,0,0),(0,0,0xD7),(0xD7,0,0),(0xD7,0,0xD7),(0,0xD7,0),(0,0xD7,0xD7),(0xD7,0xD7,0),(0xD7,0xD7,0xD7)]
PALB = [(0,0,0),(0,0,0xFF),(0xFF,0,0),(0xFF,0,0xFF),(0,0xFF,0),(0,0xFF,0xFF),(0xFF,0xFF,0),(0xFF,0xFF,0xFF)]
bm0 = np.zeros((192, 256), np.uint8)
for y in range(192):
    a = ((y & 0xC0) << 5) | ((y & 7) << 8) | ((y & 0x38) << 2)
    bm0[y] = np.unpackbits(np.frombuffer(scr[a:a + 32], np.uint8))
at0 = np.frombuffer(scr[6144:6912], np.uint8).reshape(24, 32).copy()
X0, X1, Y0, Y1 = 8, 184, 32, 160
def screen(bmw, ink=0):
    bm = bm0.copy(); at = at0.copy()
    bm[24:168, 0:192] = 0                                # old frame
    bm[Y0 - 7:Y1 + 7, X0 - 7:X1 + 7] = 1                 # the arcade bezel
    for k, n in enumerate([4, 2, 1, 1]):
        for (x, dx) in ((X0 - 7, 1), (X1 + 6, -1)):
            for (y, dy) in ((Y0 - 7, 1), (Y1 + 6, -1)):
                for i in range(n): bm[y + dy * k, x + dx * i] = 0; bm[y + dy * i, x + dx * k] = 0
    bm[Y0:Y1, X0:X1] = bmw
    at[4:20, 1:23] = 0x78 | ink
    img = np.zeros((192 + 48, 256 + 64, 3), np.uint8); img[:] = PAL[6]
    for r in range(24):
        for c in range(32):
            v = int(at[r, c]); pal = PALB if v & 64 else PAL
            blk = bm[r*8:r*8+8, c*8:c*8+8]
            img[24+r*8:24+r*8+8, 32+c*8:32+c*8+8] = np.where(blk[..., None] == 1, pal[v & 7], pal[(v >> 3) & 7])
    return Image.fromarray(img)
CAM = (int(sys.argv[4]), int(sys.argv[5])) if len(sys.argv) > 5 else (100, 40)
CARS = json.loads(sys.argv[6]) if len(sys.argv) > 6 else []
shots = []
for lab, kind, ink in [('A  CHECKS 32 PX, 50% DITHER', 'half', 0), ('B  CHECKS 32 PX, 25% DOTS', 'quarter', 0),
                       ('C  CHECKS 32 PX, DIAGONAL LINES', 'lines', 0), ('D  AS A, WITH BLUE INK', 'half', 1)]:
    bm = compose(kind, CARS)
    cx, cy = CAM
    shots.append((lab, screen(bm[cy:cy + 128, cx:cx + 176], ink)))
S = 2; w, h = shots[0][1].size
sheet = Image.new('RGB', (w * S * 2 + 24, (h * S + 40) * 2), (21, 23, 28)); d = ImageDraw.Draw(sheet)
for i, (lab, im) in enumerate(shots):
    x, y = (i % 2) * (w * S + 24), (i // 2) * (h * S + 40)
    sheet.paste(im.resize((w * S, h * S), Image.NEAREST), (x, y + 32)); d.text((x + 8, y + 10), lab, fill=(232, 230, 223))
    im.resize((w * 3, h * 3), Image.NEAREST).save(OUT.replace('.png', '_%s.png' % 'abcd'[i]))
sheet.save(OUT)
# and the whole table, small, for choosing where to look
Image.fromarray(((~compose('half', [])) * 255).astype(np.uint8)).save(OUT.replace('.png', '_world.png'))
print('O count', len(os_))
