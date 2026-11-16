"""OPTIONS ONLY (nothing here is in the game): small changes to how track 5's bridge is drawn that would make it
cheaper, each shown 4x as it is now and as it would be - docs/design/tracks/bridge_efficiency_options.png.
Grant, 16 Nov 2026: "if there is a subtle way to improve the efficiency in drawing it - with small changes - I'm
open to options". The figures on the sheet say which are measured and which are estimates.
Run: python3 tools/make_bridge_efficiency.py"""
import os, runpy, tempfile, contextlib, io
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ['TRACK'] = '5'; os.environ['WORLD_OUT'] = tempfile.mkdtemp()
with contextlib.redirect_stdout(io.StringIO()):
    w = runpy.run_path(os.path.join(HERE, 'make_world.py'))
B, ROAD, cloth = w['BRIDGE'], w['ROAD'], w['cloth_on']
xc, yc = B['cross']; x0, x1 = xc - ROAD // 2, xc + ROAD // 2
(u0, u1), (d0, d1), (r0, r1) = B['ramp_up'], B['deck'], B['ramp_down']; m0, m1 = yc - ROAD // 2, yc + ROAD // 2
def now():
    ink = np.array(w['img'], dtype=bool).copy(); wipe = np.array(w['imask'], dtype=bool).copy()
    for (x, y), v in w['KERB'].items(): ink[y, x] = bool(v); wipe[y, x] = True
    return ink, wipe
def e1(ink, wipe):                       # the mouths' dither on every other line
    for xa in (x0 - 16, x1 + 8): ink[m0 + 1:m1:2, xa:xa + 8] = False
def e2(ink, wipe):                       # two arrows a ramp
    for a_ in (u0, r0): ink[a_ + 17:a_ + 32, xc - 12:xc + 12] = False
def e3(ink, wipe):                       # a tile that holds any concrete has all its dots wiped
    c = np.zeros_like(wipe)
    for (x, y) in w['BR_WIPE']: c[y, x] = True
    for ty in range(u0 // 8, r1 // 8):
        for tx in range((x0 - 48) // 8, (x1 + 48) // 8):
            if c[ty * 8:ty * 8 + 8, tx * 8:tx * 8 + 8].any(): wipe[ty * 8:ty * 8 + 8, tx * 8:tx * 8 + 8] = True
def e4(ink, wipe):                       # the concrete not wiped at all (as the first tape)
    for (x, y) in w['BR_WIPE']: wipe[y, x] = False
CYAN, BLUE, YEL, BLACK, RED = (0, 215, 215), (0, 0, 215), (215, 215, 0), (0, 0, 0), (215, 0, 0)
def render(fn, box, s=4):
    ink, wipe = now()
    if fn: fn(ink, wipe)
    xa, ya, xb, yb = box
    bit = ink[ya:yb, xa:xb] | (cloth[ya:yb, xa:xb] & ~wipe[ya:yb, xa:xb])
    return Image.fromarray(np.where(bit[..., None], np.array(BLUE, dtype=np.uint8), np.array(CYAN, dtype=np.uint8))).resize(((xb - xa) * s, (yb - ya) * s), Image.NEAREST)
font = lambda n: ImageFont.load_default(size=n)
OPTS = [
 ('E1  TUNNEL MOUTH: DITHER ON EVERY OTHER LINE', e1, (104, 290, 168, 382), True,
  ['The band reads a shade lighter.', 'ESTIMATE: 18 tiles with 4 inked lines each instead of 8:', 'about 6,300 T a picture with the mouths in view. No bytes.']),
 ('E2  TWO ARROWS ON EACH RAMP, NOT THREE', e2, (148, 236, 228, 292), True,
  ['ESTIMATE: 12 fewer tiles: about 6,000 T a picture with a ramp', 'in view, and 24 bytes. (Measured with two arrows 24 px apart,', 'off the tile grid: 10.3 pictures a second against 10.2.)']),
 ('E3  WIPE THE DOTS BY WHOLE TILES', e3, (216, 236, 296, 300), True,
  ['A tile with any concrete in it loses all its dots: a few', 'dots just outside the walls and wings go.', 'ESTIMATE: 17 masks become 2: about 120 bytes. No speed.']),
 ('E4  THE CONCRETE NOT WIPED (as the first tape)', e4, (208, 248, 288, 296), False,
  ['The cloth shows through the wings and walls again.', 'MEASURED (an earlier build of today): 10.7 pictures a second', 'against 10.2 - the 18 masked tiles are the dearest thing here.']),
]
pad = 24; cw = 92 * 4; W_ = pad + len(OPTS) * (2 * 80 * 4 // 2 + 330 + pad)
colw = 700
sheet = Image.new('RGB', (pad + 2 * (colw + pad), 150 + 2 * 520 + 250), YEL); d = ImageDraw.Draw(sheet)
d.text((pad, 14), 'TRACK 5 BRIDGE - ways to draw it more cheaply (OPTIONS, 4x; left: as it is in the tape now, right: with the change)', fill=BLACK, font=font(26))
d.text((pad, 52), 'None of these is in the tape: each can be seen, so each waits for your word. Recommended: E1 + E2 + E3 (marked).', fill=BLACK, font=font(20))
for i, (title, fn, box, rec, lines) in enumerate(OPTS):
    x = pad + (i % 2) * (colw + pad); y = 100 + (i // 2) * 520
    a = render(None, box); b = render(fn, box)
    d.text((x, y), title, fill=BLACK, font=font(22))
    if rec: d.text((x + d.textlength(title, font=font(22)) + 14, y + 2), '- RECOMMENDED', fill=RED, font=font(20))
    sheet.paste(a, (x, y + 34)); sheet.paste(b, (x + a.size[0] + 16, y + 34))
    d.text((x, y + 38 + a.size[1]), 'now', fill=BLACK, font=font(16)); d.text((x + a.size[0] + 16, y + 38 + a.size[1]), 'with the change', fill=BLACK, font=font(16))
    for j, l in enumerate(lines): d.text((x, y + 62 + a.size[1] + 20 * j), l, fill=BLACK, font=font(17))
y = 100 + 2 * 520
for j, l in enumerate([
    'ALREADY IN THE TAPE - they change nothing you can see (the first three are the same pixels; the fourth moves two cans):',
    '  A1  The kerb walls are drawn by a routine of their own, two bytes a line, not as 48 map tiles (12 of them masked). MEASURED: 9.8 -> 10.2 pictures a second at the crossing.',
    '  A2  A mask holds only the cloth dots it has to hide: 22 different masks became 17, and tiles whose dots are all under ink need none.',
    '  A3  A quicker routine for this track\'s masked tiles. MEASURED: about 7,000 T a picture less with the whole bridge in view (with A1\'s second pass).',
    '  A4  The NOS can behind the grid and the one on the top lane moved 14 and 24 px onto white squares of the cloth: no masks for them (about 45 bytes).',
    'WHERE THE TIME GOES (MEASURED, your car parked, no other car in view): 187,500 T a picture on the start straight; 271,400 with the whole bridge in view.',
    'A picture is shown every 4 TV frames while its work is under about 227,000 T, else every 5: so the whole bridge in view runs at 10 pictures a second whatever is done here,',
    'and the options matter for the views with part of it (a ramp: 227,600 T now; a mouth: 218,900). Classification: Internal. Made by tools/make_bridge_efficiency.py.']):
    d.text((pad, y + 24 * j), l, fill=BLACK, font=font(17))
sheet.save(os.path.join(HERE, '..', 'docs', 'design', 'tracks', 'bridge_efficiency_options.png'))
print('saved', sheet.size)
