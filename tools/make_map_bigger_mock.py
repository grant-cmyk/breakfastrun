"""Mock-up: the mini-map a little larger (Grant, 16 Nov 2026: "is it possible to make the track map slightly
larger?"). Track 1's ribbon at 24 px wide (today), 32 and 40, in the play window's bottom left corner over the
cloth. Writes docs/design/arrows/map_bigger_mock.png. Nothing here is in the game."""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
wsrc = open(os.path.join(HERE, 'make_world.py')).read()
wns = {'__file__': os.path.join(HERE, 'make_world.py')}
exec(wsrc[:wsrc.index('# THE MINI-MAP')], wns)
road, PW, PH = wns['road'], wns['PW'], wns['PH']
xs = [x for x in range(PW) if any(road[x, y] for y in range(0, PH, 4))]; ys = [y for y in range(PH) if any(road[x, y] for x in range(0, PW, 4))]
def ribbon(MW):
    sc = (MW - 3) / (max(xs) - min(xs) + 1)
    MH = int((max(ys) - min(ys) + 1) * sc) + 1
    m = np.zeros((MH, MW), bool)
    for my in range(MH):
        for mx in range(2, MW):
            x, y = min(xs) + int((mx - 2 + .5) / sc), min(ys) + int((my + .5) / sc)
            m[my, mx] = x < PW and y < PH and bool(road[x, y])
    return m
BLUE, CYAN = (0, 0, 215), (0, 215, 215)
yy, xx = np.mgrid[0:120, 0:176]
cloth = ((((xx >> 5) + (yy >> 5)) & 1) == 1) & (xx % 2 == 0) & (yy % 2 == 0)
S = 3; fnt = ImageFont.load_default()
sheet = Image.new('RGB', (3 * (176 * S + 16) + 16, 120 * S + 44), (17, 18, 22)); d = ImageDraw.Draw(sheet)
for i, MW in enumerate((24, 32, 40)):
    m = ribbon(MW); ink = cloth.copy()
    ink[120 - 3 - m.shape[0]:120 - 3, 0:MW] |= m
    rgb = np.where(ink[..., None], np.array(BLUE, np.uint8), np.array(CYAN, np.uint8)).astype(np.uint8)
    ox = 16 + i * (176 * S + 16)
    d.text((ox, 10), '%s: %d wide, %d lines%s' % ('ABC'[i], MW, m.shape[0], ' (today)' if MW == 24 else ''), fill=(236, 235, 230), font=fnt)
    sheet.paste(Image.fromarray(rgb).resize((176 * S, 120 * S), Image.NEAREST), (ox, 30))
    print(MW, m.shape)
out = os.path.join(ROOT, 'docs', 'design', 'arrows', 'map_bigger_mock.png'); sheet.save(out); print('wrote', out)
