"""COLOUR CLASH, SCORED (Grant, 16 Nov 2026: "I want us to keep trying to find clever ways to avoid the colour clash
... the black road suddenly becomes green whilst the car is over it. I want you to be able to score the colour
clash for me. The more background colour changes during the car moving across areas where colour changes, the
worse the score"; and "dithering just for a character block area outside the black line").
The same drive for every rule: a car misses a bend, crosses the dashed white limit line and the black run-off,
over an 8-pixel half-tone shoulder into solid grass, crawls, and comes back. Each picture is drawn under the
Spectrum's rule (two colours in each 8 x 8 square of the screen) and compared with the picture as it OUGHT to be
(the scenery as if the car were not there, the car in its own colour):
  BACKGROUND = scenery pixels showing the wrong colour (this is the score Grant asked for), a picture
  CAR        = pixels of the car's outline not in the car's colour, a picture
Writes docs/design/racetrack/clash_score.gif, clash_score.png and prints the table. Nothing here is in the game."""
import os, re, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
wsrc = open(os.path.join(HERE, 'make_world.py')).read()
wns = {'__file__': os.path.join(HERE, 'make_world.py')}
exec(wsrc[:wsrc.index('road = road_mask(ROAD)')], wns)
ROAD, road_mask, PATH = wns['ROAD'], wns['road_mask'], wns['PATH']
PAD = 140
def plain(width): return np.pad(np.array(road_mask(width), dtype=bool), PAD)
grass_area = ~plain(ROAD + 20)                               # the grass starts 10 px beyond the track's limit
yy, xx = np.mgrid[0:grass_area.shape[0], 0:grass_area.shape[1]]
shoulder = plain(ROAD + 36) & grass_area                     # its first 8 px: a half-tone shoulder
GREEN = grass_area & (~shoulder | ((xx + yy) % 2 == 0))      # the pixels that are green
WHITE = plain(ROAD) & ~plain(ROAD - 4) & (((xx + yy) // 8) % 2 == 0)   # the dashed white limit line
K, G, WH, CY = (0, 0, 0), (0, 200, 0), (215, 215, 215), (0, 215, 215)
ca = open(os.path.join(HERE, 'car_art.txt')).read()
art = re.search(r'== YOU heading 0 ==\n((?:[Xo.]{16}\n){16})', ca).group(1).split()
aI = Image.fromarray((np.array([[c == 'X' for c in r] for r in art]) * 255).astype(np.uint8))
aB = Image.fromarray((np.array([[c != '.' for c in r] for r in art]) * 255).astype(np.uint8))
pts = []
for i in range(len(PATH)):
    (x0, y0), (x1, y1) = PATH[i], PATH[(i + 1) % len(PATH)]
    n = max(1, int(math.hypot(x1 - x0, y1 - y0) / 2))
    pts += [(x0 + PAD + (x1 - x0) * t / n, y0 + PAD + (y1 - y0) * t / n) for t in range(n)]
hd = lambda i: math.atan2(pts[(i + 4) % len(pts)][1] - pts[i % len(pts)][1], pts[(i + 4) % len(pts)][0] - pts[i % len(pts)][0])
turn = lambda i: abs((hd(i + 24) - hd(i) + math.pi) % (2 * math.pi) - math.pi)
ic = next(i for i in range(40, len(pts)) if turn(i) > 0.9 and turn(i - 30) < 0.1)
x, y = pts[ic - 45]; h = hd(ic - 45); tgt = ic - 45; track = []; phase = 0; deep = 0
for f in range(500):
    on_grass = grass_area[int(y), int(x)]; v = 0.45 if on_grass else 2.0
    if phase == 0:
        tgt += 1; x, y = pts[tgt]; h = hd(tgt)
        if tgt >= ic + 4: phase = 1
    else:
        if phase == 1:
            deep += on_grass
            if deep > 70: phase = 2; tgt = min(range(ic, ic + 200), key=lambda j: math.hypot(pts[j % len(pts)][0] - x, pts[j % len(pts)][1] - y)) + 30
        else:
            tx, ty = pts[tgt % len(pts)]; want = math.atan2(ty - y, tx - x)
            h += max(-0.06, min(0.06, (want - h + math.pi) % (2 * math.pi) - math.pi))
            if math.hypot(tx - x, ty - y) < 14: tgt += 2
        x += math.cos(h) * v; y += math.sin(h) * v
    track.append((x, y, h))
    if phase == 2 and not on_grass and tgt > ic + 120: break
RULES = [('1', 'car colour on green (the last mock-up)'),
         ('2', 'green always wins (the car goes green)'),
         ('3', 'fewest pixels change: green or black paper, by majority'),
         ('4', 'edge squares: car in green with a black rim; grass: car colour'),
         ('5', 'as 4 without the rim: the car\'s black body is its mask'),
         ('6', 'black-and-green car on ALL grass, with a black rim')]   # (Grant: "briefly change the colour of the car - use a
                                                                       # mask colour to make it visible - so a black and green mask")
S = 2; WW, WHT = 192, 152
fnt = ImageFont.load_default()
tot = {r: [0, 0, 0, 0, 0] for r, _ in RULES}                 # background sum, background peak, car sum, car peak, pictures off the black
def draw(n, x, y, h, cam, want_img):
    vx, vy = int(cam[0]) - WW // 2, int(cam[1]) - WHT // 2
    deg = -math.degrees(h) - 90
    ri = np.array(aI.rotate(deg, resample=Image.NEAREST)) > 0; rb = np.array(aB.rotate(deg, resample=Image.NEAREST)) > 0
    cI = np.zeros((WHT, WW), bool); cB = np.zeros((WHT, WW), bool)
    px, py = int(x) - vx - 8, int(y) - vy - 8
    cI[py:py + 16, px:px + 16] = ri; cB[py:py + 16, px:px + 16] = rb
    rim = cB.copy(); rim[1:] |= cB[:-1]; rim[:-1] |= cB[1:]; rim[:, 1:] |= cB[:, :-1]; rim[:, :-1] |= cB[:, 1:]
    g, w = GREEN[vy:vy + WHT, vx:vx + WW], WHITE[vy:vy + WHT, vx:vx + WW]
    ideal = np.zeros((WHT, WW, 3), np.uint8); ideal[g] = G; ideal[w] = WH
    off = bool((g & cB).any() or (g[py:py + 16, px:px + 16]).any())
    sheet = Image.new('RGB', (3 * (WW * S + 10) + 10, 2 * (WHT * S + 46) + 6), (40, 42, 48)) if want_img else None
    d = ImageDraw.Draw(sheet) if want_img else None
    for k, (rule, what) in enumerate(RULES):
        out = ideal.copy()
        for qy in range(max(0, py // 8), min(WHT // 8, (py + 15) // 8 + 1)):
            for qx in range(max(0, px // 8), min(WW // 8, (px + 15) // 8 + 1)):
                c = (slice(qy * 8, qy * 8 + 8), slice(qx * 8, qx * 8 + 8))
                if not cB[c].any(): continue
                bg = ~cB[c]; ng = int((g[c] & bg).sum()); nk = int(bg.sum()) - ng
                if ng == 0: ink, icol, pcol = cI[c] | (w[c] & bg), CY, K                 # on the black: the car's colour wins over the line
                elif rule == '1' or (rule == '3' and ng >= nk) or (rule in '45' and nk == 0): ink, icol, pcol = cI[c], CY, G
                elif rule == '3': ink, icol, pcol = cI[c] | (g[c] & bg) | (w[c] & bg), CY, K
                elif rule == '2': ink, icol, pcol = cI[c] | (g[c] & bg) | (w[c] & bg), G, K
                elif rule == '5': ink, icol, pcol = cI[c] | (g[c] & bg) | (w[c] & bg), G, K
                else: ink, icol, pcol = cI[c] | (g[c] & ~rim[c]) | (w[c] & ~rim[c]), G, K   # rules 4 and 6: a black rim round the car
                out[c] = np.where(ink[..., None], np.array(icol, np.uint8), np.array(pcol, np.uint8))
        b = int(((out != ideal).any(axis=2) & ~cB).sum()); cl = int(((out != np.array(CY, np.uint8)).any(axis=2) & cI).sum())
        t = tot[rule]; t[0] += b; t[1] = max(t[1], b); t[2] += cl; t[3] = max(t[3], cl); t[4] += off
        if want_img:
            ox = 10 + (k % 3) * (WW * S + 10); oy = (k // 3) * (WHT * S + 46)
            d.text((ox, oy + 6), '%s: %s' % (rule, what), fill=(236, 235, 230), font=fnt)
            sheet.paste(Image.fromarray(out).resize((WW * S, WHT * S), Image.NEAREST), (ox, oy + 22))
            d.text((ox, oy + 26 + WHT * S), 'now: background %3d  car %3d      so far: background %5d  car %5d' % (b, cl, t[0], t[2]), fill=(255, 212, 0), font=fnt)
    return sheet
frames = []; cam = list(track[0][:2]); still = None
for n, (x, y, h) in enumerate(track):
    cam[0] += (x - cam[0]) * 0.2; cam[1] += (y - cam[1]) * 0.2
    slow = grass_area[int(y), int(x)] or shoulder[int(y), int(x)]
    keep = (n % 2 == 0) or slow
    f = draw(n, x, y, h, cam, keep)
    if keep: frames.append(f)
    if still is None and shoulder[int(y), int(x)]: still = len(frames) - 1
out = os.path.join(ROOT, 'docs', 'design', 'racetrack')
pal = frames[still].convert('P', palette=Image.ADAPTIVE, colors=16)
fr = [f.quantize(palette=pal, dither=Image.NONE) for f in frames]
fr[0].save(os.path.join(out, 'clash_score.gif'), save_all=True, append_images=fr[1:] + [fr[-1]] * 25, duration=70, loop=0)
frames[still].save(os.path.join(out, 'clash_score.png'))
print('%d pictures in the drive, %d of them with the car off the black' % (len(track), tot['1'][4]))
print('rule | background: total, worst picture | car: total, worst picture')
for r, what in RULES: print('%s | %6d %4d | %6d %4d | %s' % (r, tot[r][0], tot[r][1], tot[r][2], tot[r][3], what))
