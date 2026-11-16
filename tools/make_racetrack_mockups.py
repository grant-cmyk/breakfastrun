"""Mock-ups, MOVING: a traditional race track in place of the breakfast table (Grant, 16 Nov 2026: "scrap the
table idea, and make a traditional race track ... I want the track to be black. The outside of the track will be
green ... mockup some sides/edge of the race track ... more options to hide the colour clash").
Track 1's real road shape, the view gliding along the start straight and into the first bend. Every panel obeys
the Spectrum's rule - two colours in each 8 x 8 square of the SCREEN, re-decided each picture - so what clashes
here would clash in the game. Writes docs/design/racetrack/edge_options.gif and edge_options.png.
Nothing here is in the game."""
import os, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
wsrc = open(os.path.join(HERE, 'make_world.py')).read()
wns = {'__file__': os.path.join(HERE, 'make_world.py')}
exec(wsrc[:wsrc.index('road = road_mask(ROAD)')], wns)
ROAD, road_mask, PW, PH = wns['ROAD'], wns['road_mask'], wns['PW'], wns['PH']
def plain(width): return np.array(road_mask(width), dtype=bool)
road = plain(ROAD); H, W = road.shape
yy, xx = np.mgrid[0:H, 0:W]
K, G, WH, RD, CY, YL, MG = (0, 0, 0), (0, 200, 0), (215, 215, 215), (215, 0, 0), (0, 215, 215), (215, 215, 0), (215, 0, 215)
grass = ~road
kerb = plain(ROAD + 8) & ~plain(ROAD - 8)                       # 4 px each side of the true edge
stripe = ((xx + yy) // 4) % 2 == 0
inset = plain(ROAD - 20) ^ plain(ROAD - 24)                     # a 2-px line 10 px in from the edge
dash = ((xx + yy) // 8) % 2 == 0
verge = plain(ROAD + 12) & grass & ((xx + yy) % 2 == 1)         # a 6-px half-tone shoulder: holes in the grass
# the cars: the red car's drawing, placed on the road by the start (one over the edge, to show what happens there)
ca = open(os.path.join(HERE, 'car_art.txt')).read()
art = re.search(r'== YOU heading 0 ==\n((?:[Xo.]{16}\n){16})', ca).group(1).split()
cink = np.array([[c == 'X' for c in r] for r in art]); cbody = np.array([[c != '.' for c in r] for r in art])
cink, cbody = np.rot90(cink, -1), np.rot90(cbody, -1)          # nose to the right, along the straight
X0 = 300; ye = next(y for y in range(330, H) if road[y, X0])
CARS = [(X0 - 40, ye - 7, RD), (X0, ye + 14, CY), (X0 + 44, ye + 34, YL), (X0 - 8, ye + 40, MG)]
carI = np.zeros((H, W), bool); carB = np.zeros((H, W), bool); carC = np.zeros((H, W), np.int8) - 1
for n, (x, y, c) in enumerate(CARS):
    carI[y:y + 16, x:x + 16] |= cink; carB[y:y + 16, x:x + 16] |= cbody; carC[y:y + 16, x:x + 16][cbody] = n
# a panel: (tag, what, mode, extra white ink, kerb mode)
OPTS = [('A', 'clean edge: grass drawn to the pixel', 'pix', None),
        ('B', 'A + a soft half-tone shoulder', 'pix', 'verge'),
        ('C', 'A + dashed white line, 10 px inside', 'pix', 'dash'),
        ('D', 'solid white kerb, 8 px, hides the steps', 'attr', 'kerb'),
        ('E', 'striped white kerb (steps show in the gaps)', 'attr', 'stripe'),
        ('F', 'red-and-white kerb (why not: red spills)', 'attr', 'red')]
S = 2; WW, WHT = 192, 152
fnt = ImageFont.load_default()
def panel(vx, vy, mode, extra):
    sl = (slice(vy, vy + WHT), slice(vx, vx + WW))
    g, cI, cB, cC = grass[sl], carI[sl], carB[sl], carC[sl]
    out = np.zeros((WHT, WW, 3), np.uint8)
    white = {'dash': inset & dash, 'kerb': kerb, 'stripe': kerb & stripe, 'red': kerb & stripe}.get(extra, np.zeros_like(road))[sl]
    hole = verge[sl] if extra == 'verge' else np.zeros_like(g)
    kb = kerb[sl]
    for cy in range(WHT // 8):
        for cx in range(WW // 8):
            c = (slice(cy * 8, cy * 8 + 8), slice(cx * 8, cx * 8 + 8))
            car = cC[c][cB[c]]; ccol = CARS[int(car[0])][2] if car.size else WH
            if mode == 'pix':                                   # grass is INK, to the pixel; a car's shape cuts it away
                ink = (g[c] & ~hole[c] & ~cB[c]) | cI[c] | white[c]
                icol = G if (g[c] & ~cB[c]).any() else (WH if white[c].any() else ccol); pcol = K
            else:                                               # grass is the square's PAPER, by majority
                pcol = G if g[c].mean() >= 0.5 else K
                ink = (white[c] & ~cB[c]) | cI[c]; icol = WH if white[c].any() else (K if pcol == G else ccol)
                if extra == 'red' and kb[c].any(): pcol = RD; icol = WH
            out[c] = np.where(ink[..., None], np.array(icol, np.uint8), np.array(pcol, np.uint8))
    return Image.fromarray(out).resize((WW * S, WHT * S), Image.NEAREST)
def frame(vx, vy):
    sheet = Image.new('RGB', (3 * (WW * S + 12) + 12, 2 * (WHT * S + 30) + 8), (40, 42, 48)); d = ImageDraw.Draw(sheet)
    for i, (tag, what, mode, extra) in enumerate(OPTS):
        ox = 12 + (i % 3) * (WW * S + 12); oy = 8 + (i // 3) * (WHT * S + 30)
        d.text((ox, oy), tag + ': ' + what, fill=(236, 235, 230), font=fnt)
        sheet.paste(panel(vx, vy, mode, extra), (ox, oy + 16))
    return sheet
P0, P1, P2 = (X0 - 130, ye - 60), (X0 - 40, ye - 50), (X0 + 60, ye - 110)
path = [(int(P0[0] + (P1[0] - P0[0]) * t / 45), int(P0[1] + (P1[1] - P0[1]) * t / 45)) for t in range(45)] + \
       [(int(P1[0] + (P2[0] - P1[0]) * t / 40), int(P1[1] + (P2[1] - P1[1]) * t / 40)) for t in range(41)]
frames = [frame(*p) for p in path]
out = os.path.join(ROOT, 'docs', 'design', 'racetrack'); os.makedirs(out, exist_ok=True)
pal = frames[30].convert('P', palette=Image.ADAPTIVE, colors=16)
fr = [f.quantize(palette=pal, dither=Image.NONE) for f in frames]
fr[0].save(os.path.join(out, 'edge_options.gif'), save_all=True, append_images=fr[1:] + fr[::-1], duration=80, loop=0)
frames[30].save(os.path.join(out, 'edge_options.png')); print('wrote', out, len(frames), X0, ye)
