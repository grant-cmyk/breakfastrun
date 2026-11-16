"""Mock-ups: ways to tell the road from the table at a glance (Grant, 16 Nov 2026:
"I need a way to show areas that are in the track and outside of the track better ...
I want a way to see what is road area better"). The real map of track 1 through the
176 x 120 window, as tools/make_road_mockups.py draws it. Writes
docs/design/road_edge_options.png. Mock-ups only: nothing here is in the game."""
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
BLUE, CYAN, WHITE, YEL = (0, 0, 215), (0, 215, 215), (255, 255, 255), (215, 215, 0)
base = world | (dots & ~wmask)
def keep(clear, add):                       # dots rubbed out under 'clear', then 'add' inked, the map's own ink on top
    return world | (dots & ~wmask & ~clear) | (add & ~wmask)
line = road & ~plain(ROAD - 4)                                           # 2 px just inside each edge
kerb = road & ~plain(ROAD - 8)
stripes = ((xx + yy) // 4) % 2 == 0
centre = plain(3) & (((xx + yy) // 6) % 2 == 0)
OPTS = [
 ('NOW', 'only the O\'s mark the edge', base, None),
 ('A', 'solid line along both edges', keep(line, line), None),
 ('B', 'striped kerb along both edges', keep(kerb, kerb & stripes), None),
 ('C', 'dashed line down the middle', keep(plain(5), centre), None),
 ('D', 'road plain, cloth only outside', keep(road, np.zeros_like(road)), None),
 ('E', 'road in WHITE, by colour square', base, WHITE),
 ('F', 'A + E: edge line and white road', keep(line, line), WHITE),
]
VIEWS = [(248 - 88 + 8, 352 - 60), (360, 250)]
S = 2
fnt = ImageFont.load_default()
cw, ch = 176 * S, 120 * S
COLS = 4
rows = (len(OPTS) + COLS - 1) // COLS
bh = 22 + len(VIEWS) * (ch + 8)
sheet = Image.new('RGB', (COLS * (cw + 16) + 16, rows * (bh + 14) + 16), (17, 18, 22))
d = ImageDraw.Draw(sheet)
for i, (tag, what, ink, rcol) in enumerate(OPTS):
    ox = 16 + (i % COLS) * (cw + 16); oy = 12 + (i // COLS) * (bh + 14)
    d.text((ox, oy), tag + ': ' + what, fill=(236, 235, 230), font=fnt)
    for j, (vx, vy) in enumerate(VIEWS):
        win = ink[vy:vy + 120, vx:vx + 176]
        paper = np.empty((120, 176, 3), np.uint8); paper[:] = CYAN
        if rcol:                                                          # colour goes by 8 x 8 square of the SCREEN
            r = road[vy:vy + 120, vx:vx + 176]
            for cy in range(15):
                for cx in range(22):
                    if r[cy * 8:cy * 8 + 8, cx * 8:cx * 8 + 8].mean() >= 0.5:
                        paper[cy * 8:cy * 8 + 8, cx * 8:cx * 8 + 8] = rcol
        rgb = np.where(win[..., None], np.array(BLUE, np.uint8), paper)
        sheet.paste(Image.fromarray(rgb).resize((cw, ch), Image.NEAREST), (ox, oy + 16 + j * (ch + 8)))
out = os.path.join(ROOT, 'docs', 'design', 'road_edge_options.png')
sheet.save(out); print('wrote', os.path.normpath(out))
