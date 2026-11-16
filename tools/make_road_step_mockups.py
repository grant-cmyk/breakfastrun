"""Mock-ups, MOVING: ways to hide the colour edge's 8-pixel steps on the white/yellow road trial (Grant,
16 Nov 2026: "the stepping edge is not great - can you mockup some options to minimise this effect? Perhaps
more blue around the corners where the jumping happens?"). Track 1's real map, the view gliding from the
start straight into the first bend; the road's colour re-decided by 8 x 8 square each picture, as the trial
does. Writes docs/design/roadwhite/step_options.gif and step_options.png. Nothing here is in the game."""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
src = open(os.path.join(ROOT, 'tests', 'drive_test.py')).read()
src = src[:src.index('with Racer(headless=True)')].replace("os.path.dirname(os.path.abspath(__file__))", repr(os.path.join(ROOT, 'tests')))
ns = {}; exec(src, ns)
world, wmask = ns['world'].astype(bool), ns['wmask']
wsrc = open(os.path.join(HERE, 'make_world.py')).read()
wns = {'__file__': os.path.join(HERE, 'make_world.py')}
exec(wsrc[:wsrc.index('road = road_mask(ROAD)')], wns)
ROAD, road_mask = wns['ROAD'], wns['road_mask']
H, W = world.shape
yy, xx = np.mgrid[0:H, 0:W]
dots = ((((xx >> 5) + (yy >> 5)) & 1) == 1) & (xx % 2 == 0) & (yy % 2 == 0)
def plain(width): return np.array(road_mask(width), dtype=bool)[:H, :W]
road = plain(ROAD)
BLUE, CYAN, WHITE, YEL, BCYAN = (0, 0, 215), (0, 215, 215), (215, 215, 215), (215, 215, 0), (0, 255, 255)
base = world | (dots & ~wmask)
band8 = plain(ROAD + 8) & ~plain(ROAD - 8)          # 4 px each side of the true edge: the colour's step is always under it
band12 = plain(ROAD + 14) & ~plain(ROAD - 10)
chk = ((xx + yy) % 2 == 0)
line = plain(ROAD + 2) & ~plain(ROAD - 2)
# name, what, ink, road colour, rule ('near': mostly road; 'in': wholly road)
OPTS = [
 ('NOW', 'the trial as it is', base, YEL, 'near'),
 ('A', 'solid blue kerb, 8 px, on the edge', base | band8, YEL, 'near'),
 ('B', 'half-tone blue kerb, 12 px', (base & ~band12) | (band12 & chk) | world, YEL, 'near'),
 ('C', 'colour kept inside the road + edge line', base | line, YEL, 'in'),
 ('D', 'a quieter colour: bright cyan road', base, BCYAN, 'near'),
 ('E', 'A with the kerb striped', (base & ~band8) | (band8 & (((xx + yy) // 4) % 2 == 0)) | (band8 & ~plain(ROAD + 5)) | (band8 & plain(ROAD - 5)) | world, YEL, 'near'),
]
S = 2; WW, WH = 176, 120
fnt = ImageFont.load_default()
def frame(vx, vy):
    sheet = Image.new('RGB', (3 * (WW * S + 12) + 12, 2 * (WH * S + 30) + 8), (17, 18, 22)); d = ImageDraw.Draw(sheet)
    for i, (tag, what, ink, rcol, rule) in enumerate(OPTS):
        ox = 12 + (i % 3) * (WW * S + 12); oy = 8 + (i // 3) * (WH * S + 30)
        d.text((ox, oy), tag + ': ' + what, fill=(236, 235, 230), font=fnt)
        cx0, cy0 = (vx + 4) // 8 * 8, (vy + 4) // 8 * 8                 # the squares the view is nearest to
        r = road[cy0:cy0 + WH + 8, cx0:cx0 + WW + 8]
        paper = np.empty((WH, WW, 3), np.uint8); paper[:] = CYAN
        for cy in range(15):
            for cx in range(22):
                q = r[cy * 8:cy * 8 + 8, cx * 8:cx * 8 + 8]
                if (q.all() if rule == 'in' else q.mean() >= 0.5): paper[cy * 8:cy * 8 + 8, cx * 8:cx * 8 + 8] = rcol
        win = ink[vy:vy + WH, vx:vx + WW]
        rgb = np.where(win[..., None], np.array(BLUE, np.uint8), paper)
        sheet.paste(Image.fromarray(rgb).resize((WW * S, WH * S), Image.NEAREST), (ox, oy + 16))
    return sheet
P0, P1, P2 = (168, 292), (300, 280), (360, 230)
path = [(int(P0[0] + (P1[0] - P0[0]) * t / 44), int(P0[1] + (P1[1] - P0[1]) * t / 44)) for t in range(44)] + \
       [(int(P1[0] + (P2[0] - P1[0]) * t / 36), int(P1[1] + (P2[1] - P1[1]) * t / 36)) for t in range(37)]
frames = [frame(*p) for p in path]
out = os.path.join(ROOT, 'docs', 'design', 'roadwhite')
pal = frames[40].convert('P', palette=Image.ADAPTIVE, colors=16)
fr = [f.quantize(palette=pal, dither=Image.NONE) for f in frames]
fr[0].save(os.path.join(out, 'step_options.gif'), save_all=True, append_images=fr[1:] + fr[::-1], duration=80, loop=0)
frames[60].save(os.path.join(out, 'step_options.png')); print('wrote', out, len(frames))
