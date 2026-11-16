"""Mock-up, MOVING: a car runs wide at a bend, slides over the white limit line and the black run-off into the
grass, crawls there, and comes back (Grant, 16 Nov 2026: "the car must be able to go over into the grass. If it
does, it goes very slowly. Then for the green area, the car is masked and keeps its shape, so the colour around
it for that time would be the car colour and green"). Left: the grass's green wins in a shared square (the car
goes green). Right: Grant's rule - a square the car shares with grass is the CAR's colour on GREEN.
The Spectrum's rule holds in both: two colours in each 8 x 8 square of the screen.
Writes docs/design/racetrack/grass_slide.gif and grass_slide.png. Nothing here is in the game."""
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
grass = ~plain(ROAD + 20)                                    # the grass starts 10 px beyond the track's limit
limit = plain(ROAD) & ~plain(ROAD - 4)                       # the white limit line
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
ic = next(i for i in range(40, len(pts)) if turn(i) > 0.9 and turn(i - 30) < 0.1)     # a bend after a straight
# the drive: along the middle to the bend, straight on into the grass, a crawl, then back to the road
x, y = pts[ic - 45]; h = hd(ic - 45); tgt = ic - 45; track = []; phase = 0; deep = 0
for f in range(400):
    on_grass = grass[int(y), int(x)]
    v = 0.45 if on_grass else 2.0                             # "it goes very slowly"
    if phase == 0:
        tgt += 1; x, y = pts[tgt]; h = hd(tgt)
        if tgt >= ic + 4: phase = 1
    else:
        if phase == 1:
            deep += on_grass
            if deep > 55: phase = 2; tgt = min(range(ic, ic + 200), key=lambda j: math.hypot(pts[j % len(pts)][0] - x, pts[j % len(pts)][1] - y)) + 30
        else:
            tx, ty = pts[tgt % len(pts)]; want = math.atan2(ty - y, tx - x)
            h += max(-0.06, min(0.06, (want - h + math.pi) % (2 * math.pi) - math.pi))
            if math.hypot(tx - x, ty - y) < 14: tgt += 2
        x += math.cos(h) * v; y += math.sin(h) * v
    track.append((x, y, h))
    if phase == 2 and not on_grass and tgt > ic + 120: break
S = 3; WW, WHT = 192, 152
fnt = ImageFont.load_default()
OPTS = [('before', "the grass's green wins: the car goes green"), ('new', "the car keeps its colour: its squares are car colour on green")]
def frame(x, y, h, cam):
    vx, vy = int(cam[0]) - WW // 2, int(cam[1]) - WHT // 2
    deg = -math.degrees(h) - 90
    ri = np.array(aI.rotate(deg, resample=Image.NEAREST)) > 0; rb = np.array(aB.rotate(deg, resample=Image.NEAREST)) > 0
    cI = np.zeros((WHT, WW), bool); cB = np.zeros((WHT, WW), bool)
    px, py = int(x) - vx - 8, int(y) - vy - 8
    cI[py:py + 16, px:px + 16] = ri; cB[py:py + 16, px:px + 16] = rb
    g, white = grass[vy:vy + WHT, vx:vx + WW], limit[vy:vy + WHT, vx:vx + WW]
    sheet = Image.new('RGB', (2 * (WW * S + 12) + 12, WHT * S + 38), (40, 42, 48)); d = ImageDraw.Draw(sheet)
    for k, (mode, what) in enumerate(OPTS):
        out = np.zeros((WHT, WW, 3), np.uint8)
        for qy in range(WHT // 8):
            for qx in range(WW // 8):
                c = (slice(qy * 8, qy * 8 + 8), slice(qx * 8, qx * 8 + 8))
                car = cB[c].any(); gr = (g[c] & ~cB[c]).any()
                if car and gr and mode == 'new':                 # the car's colour on green: only the car is ink
                    ink, icol, pcol = cI[c], CY, G
                elif car and not gr and mode == 'new':           # on the black: the car's colour wins over the line
                    ink, icol, pcol = cI[c] | (white[c] & ~cB[c]), CY, K
                else:
                    ink = (g[c] & ~cB[c]) | cI[c] | (white[c] & ~cB[c])
                    icol = G if gr else (WH if white[c].any() else CY); pcol = K
                out[c] = np.where(ink[..., None], np.array(icol, np.uint8), np.array(pcol, np.uint8))
        ox = 12 + k * (WW * S + 12)
        d.text((ox, 8), what, fill=(236, 235, 230), font=fnt)
        sheet.paste(Image.fromarray(out).resize((WW * S, WHT * S), Image.NEAREST), (ox, 26))
    return sheet
frames = []; cam = list(track[0][:2]); still = None
for n, (x, y, h) in enumerate(track):
    cam[0] += (x - cam[0]) * 0.2; cam[1] += (y - cam[1]) * 0.2
    if n % 2 == 0 or grass[int(y), int(x)]:
        frames.append(frame(x, y, h, cam))
        if still is None and grass[int(y), int(x)] and grass[int(y + 8 * math.sin(h)), int(x + 8 * math.cos(h))]: still = len(frames) + 6
out = os.path.join(ROOT, 'docs', 'design', 'racetrack')
pal = frames[len(frames) // 2].convert('P', palette=Image.ADAPTIVE, colors=16)
fr = [f.quantize(palette=pal, dither=Image.NONE) for f in frames]
fr[0].save(os.path.join(out, 'grass_slide.gif'), save_all=True, append_images=fr[1:], duration=70, loop=0)
frames[min(still or 0, len(frames) - 1)].save(os.path.join(out, 'grass_slide.png')); print('wrote', len(frames), 'frames; bend at', ic, 'drive', len(track))
