"""Mock-ups, MOVING, of the CORNERS on a black track with green outside (Grant, 16 Nov 2026: "the issue is the
corners - how to minimise colour clash and block jerkiness in corners"). The view follows the road's middle
round track 1; a red car sits mid-road and a cyan one hugs the edge. Every panel obeys the Spectrum's rule:
two colours in each 8 x 8 square of the screen, re-decided each picture.
Writes docs/design/racetrack/corner_options.gif and corner_options.png. Nothing here is in the game."""
import os, re, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
wsrc = open(os.path.join(HERE, 'make_world.py')).read()
wns = {'__file__': os.path.join(HERE, 'make_world.py')}
exec(wsrc[:wsrc.index('road = road_mask(ROAD)')], wns)
ROAD, road_mask, PATH = wns['ROAD'], wns['road_mask'], wns['PATH']
def plain(width): return np.array(road_mask(width), dtype=bool)
PAD = 120
def padm(m, v=False): return np.pad(m, PAD, constant_values=v)
road = plain(ROAD); H, W = road.shape
yy, xx = np.mgrid[0:H + 2 * PAD, 0:W + 2 * PAD]
K, G, WH, RD, CY = (0, 0, 0), (0, 200, 0), (215, 215, 215), (215, 0, 0), (0, 215, 215)
grass0 = padm(~road, True)                                   # grass from the road's true edge
grassR = padm(~plain(ROAD + 20), True)                       # grass from 10 px further out: a black run-off
kerb = padm(plain(ROAD + 8) & ~plain(ROAD - 8))
limit = padm(plain(ROAD) & ~plain(ROAD - 4))                 # a 2-px line just inside the true edge
dash = ((xx + yy) // 8) % 2 == 0
shoulder = padm(plain(ROAD + 32)) & grassR & ((xx + yy) % 2 == 1)
none = np.zeros_like(grass0)
ca = open(os.path.join(HERE, 'car_art.txt')).read()
art = re.search(r'== YOU heading 0 ==\n((?:[Xo.]{16}\n){16})', ca).group(1).split()
aI = Image.fromarray((np.array([[c == 'X' for c in r] for r in art]) * 255).astype(np.uint8))
aB = Image.fromarray((np.array([[c != '.' for c in r] for r in art]) * 255).astype(np.uint8))
# the road's middle, a point every 2 px
pts = []
for i in range(len(PATH)):
    (x0, y0), (x1, y1) = PATH[i], PATH[(i + 1) % len(PATH)]
    n = max(1, int(math.hypot(x1 - x0, y1 - y0) / 2))
    pts += [(x0 + (x1 - x0) * t / n, y0 + (y1 - y0) * t / n) for t in range(n)]
def at(i):
    (x, y), (x2, y2) = pts[i % len(pts)], pts[(i + 3) % len(pts)]
    return x + PAD, y + PAD, math.atan2(y2 - y, x2 - x)
# (tag, what, mode, grass, white ink)
OPTS = [('1', 'colour by square alone: the jerkiness', 'attr', grass0, none),
        ('2', 'solid white kerb over it: steps hidden', 'attr', grass0, kerb),
        ('3', 'grass drawn to the pixel: no steps', 'pix', grass0, none),
        ('4', '3 + black run-off, dashed limit line', 'pix', grassR, limit & dash),
        ('5', '3 + black run-off, solid limit line', 'pix', grassR, limit),
        ('6', '5 + a half-tone shoulder to the grass', 'pix', grassR, limit)]
S = 2; WW, WHT = 192, 152
fnt = ImageFont.load_default()
def frame(i):
    cx, cy, th = at(i); vx, vy = int(cx) - WW // 2, int(cy) - WHT // 2
    cI = np.zeros((WHT, WW), bool); cB = np.zeros((WHT, WW), bool); cC = np.zeros((WHT, WW), np.int8)
    rx, ry, rth = at(i - 22); off = ROAD / 2 - 5              # the cyan car, behind, its wheels on the true edge
    for n, (x, y, a) in enumerate(((cx, cy, th), (rx - math.sin(rth) * off, ry + math.cos(rth) * off, rth))):
        deg = -math.degrees(a) - 90
        ri = np.array(aI.rotate(deg, resample=Image.NEAREST)) > 0; rb = np.array(aB.rotate(deg, resample=Image.NEAREST)) > 0
        px, py = int(x) - vx - 8, int(y) - vy - 8
        if 0 <= px < WW - 16 and 0 <= py < WHT - 16:
            cI[py:py + 16, px:px + 16] |= ri; cB[py:py + 16, px:px + 16] |= rb; cC[py:py + 16, px:px + 16][rb] = n
    sl = (slice(vy, vy + WHT), slice(vx, vx + WW))
    sheet = Image.new('RGB', (3 * (WW * S + 12) + 12, 2 * (WHT * S + 30) + 8), (40, 42, 48)); d = ImageDraw.Draw(sheet)
    for k, (tag, what, mode, gr, wh) in enumerate(OPTS):
        g, white = gr[sl], wh[sl]; hole = shoulder[sl] if tag == '6' else none[sl]
        out = np.zeros((WHT, WW, 3), np.uint8)
        for qy in range(WHT // 8):
            for qx in range(WW // 8):
                c = (slice(qy * 8, qy * 8 + 8), slice(qx * 8, qx * 8 + 8))
                car = cC[c][cB[c]]; ccol = (RD, CY)[int(car[0])] if car.size else WH
                if mode == 'pix':
                    ink = (g[c] & ~hole[c] & ~cB[c]) | cI[c] | (white[c] & ~cB[c])
                    icol = G if (g[c] & ~cB[c]).any() else (WH if white[c].any() else ccol); pcol = K
                else:
                    pcol = G if g[c].mean() >= 0.5 else K
                    ink = (white[c] & ~cB[c]) | cI[c]; icol = WH if white[c].any() else (K if pcol == G else ccol)
                out[c] = np.where(ink[..., None], np.array(icol, np.uint8), np.array(pcol, np.uint8))
        ox = 12 + (k % 3) * (WW * S + 12); oy = 8 + (k // 3) * (WHT * S + 30)
        d.text((ox, oy), tag + ': ' + what, fill=(236, 235, 230), font=fnt)
        sheet.paste(Image.fromarray(out).resize((WW * S, WHT * S), Image.NEAREST), (ox, oy + 16))
    return sheet
N = len(pts); frames = [frame(i) for i in range(0, N, 2)]
out = os.path.join(ROOT, 'docs', 'design', 'racetrack'); os.makedirs(out, exist_ok=True)
pal = frames[10].convert('P', palette=Image.ADAPTIVE, colors=16)
fr = [f.quantize(palette=pal, dither=Image.NONE) for f in frames]
fr[0].save(os.path.join(out, 'corner_options.gif'), save_all=True, append_images=fr[1:], duration=70, loop=0)
best = max(range(len(frames)), key=lambda j: abs(at(j * 2 + 20)[2] - at(j * 2)[2]) % 3)
frames[best].save(os.path.join(out, 'corner_options.png')); print('wrote', out, len(frames), 'lap px', N * 2)
