"""Mock-up: big coloured objects INSIDE the scrolling play window that can never colour-clash
(Grant, 14 Nov 2026): "I would like to look at some features that put colour into the gameplay
area. That means that this would need to be cleverly done, so enough space around them to avoid
colour clash, clever use of black around them to minimise the effect of different colours, maybe
have a big mask so at no stage do character rows interfere with areas around them?" and "so
thinking of some big coloured objects - preferably square. Like a box or something".

The problem: the window is blue ink on cyan paper and scrolls a PIXEL at a time, but the Spectrum
only has colour per 8 x 8 cell, so a coloured thing that scrolls smoothly would drag its colour
over the cloth round it in 8-pixel jumps.

The "solid edge" rule this script draws and tests:
  - an object has a SOLID edge of the window's own blue ink, at least 8 pixels thick all round,
    and a coloured inside (blue-ink drawing on one paper colour);
  - a screen cell gets the object's colour ONLY if it holds some of the object's inside; every
    other cell stays the window's blue on cyan;
  - because the edge is 8 thick, a cell that holds any inside is always wholly within the object,
    and a cell that holds any cloth holds only cloth and solid blue edge - blue in both colours.
    So the colour boundary always falls under the solid blue edge, at every scroll position;
  - two colours in one object need 8 pixels of solid blue between them, for the same reason.
The script does not take this on trust: verify() slides every object through all 64 pixel
positions against the cell grid and asserts no cell ever mixes inside with cloth or two colours.

The Spectrum display is simulated properly: a bits array and an attributes array (one per 8 x 8
cell, chosen by the rule from where the object's pixels fall), then rendered. The objects use
plain (not BRIGHT) colours: a BRIGHT cell would show a brighter blue too, and the edge would be
two blues. The cloth, cars and O's are the real ones (the G3 mock-up of the race screen,
tools/make_screen_options3.py, on docs/design/mock_128_racing.bin); the objects are new art.

Writes docs/design/colour_objects.png: the objects (6x, 1x, 2x), the proof (one object scrolled
0-7 pixels across and down, and what goes wrong without the rule), and a whole race screen.
Usage: make_colour_objects.py"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
from make_layout_review import render, FONT, PAL
from make_screen_options3 import option_g3
DESIGN = os.path.join(ROOT, 'docs', 'design')
WIN = 0x29; EDGE = 8
BLACK, BLUE, RED, MAGENTA, GREEN, CYAN, YELLOW, WHITE = range(8)

# ---- drawing an object: shape (its footprint), bits (ink), label (0 = edge, else a paper colour + 1)
class Obj:
    def __init__(self, name, w, h, round_=False):
        self.name, self.w, self.h = name, w, h
        y, x = np.mgrid[0:h, 0:w]
        if round_: self.shape = (((x - (w - 1) / 2) ** 2 + (y - (h - 1) / 2) ** 2) <= (w / 2) ** 2).astype(np.uint8)
        else:
            self.shape = np.ones((h, w), dtype=np.uint8)
            for (cx, cy) in ((0, 0), (1, 0), (0, 1)):         # the corners, a touch rounded (outermost line only)
                for fx in (cx, w - 1 - cx):
                    for fy in (cy, h - 1 - cy): self.shape[fy, fx] = 0
        self.bits = self.shape.copy(); self.label = np.zeros((h, w), dtype=np.uint8)
    def panel(self, x0, y0, x1, y1, colour):
        """An inside, x0..x1-1 by y0..y1-1: only where there are 8 pixels of object every way."""
        ok = np.zeros_like(self.shape)
        for y in range(y0, y1):
            for x in range(x0, x1):
                if x >= EDGE and y >= EDGE and x + EDGE < self.w and y + EDGE < self.h and self.shape[y - EDGE:y + EDGE + 1, x - EDGE:x + EDGE + 1].all():
                    ok[y, x] = 1
        self.bits[ok == 1] = 0; self.label[ok == 1] = colour + 1
    def ink(self, art, x, y):                                 # blue drawing, kept to the insides
        h, w = art.shape; m = (art == 1) & (self.label[y:y + h, x:x + w] > 0)
        self.bits[y:y + h, x:x + w][m] = 1
    def text(self, s, x, y):
        t = np.zeros((8, 8 * len(s)), dtype=np.uint8)
        for k, ch in enumerate(s):
            g = FONT[(ord(ch) - 32) * 8:(ord(ch) - 32) * 8 + 8]
            for j in range(8):
                for i in range(8): t[j, 8 * k + i] = (g[j] >> (7 - i)) & 1
        self.ink(t, x, y)
def pic(rows): return np.array([[c == 'X' for c in r] for r in rows], dtype=np.uint8)
def ring(r, t=1.2, fill=False):
    n = int(2 * r + 1); y, x = np.mgrid[0:n, 0:n]; d = np.hypot(x - r, y - r)
    return ((d <= r + .3) & (fill | (d >= r - t))).astype(np.uint8)

def cereal():
    o = Obj('Cereal box, 48 x 64, yellow', 48, 64); o.panel(8, 8, 40, 56, YELLOW)
    o.text('CORN', 8, 9)
    o.ink(np.ones((1, 30), dtype=np.uint8), 9, 19)
    bowl = ring(11, fill=True); bowl[:11] = 0; o.ink(bowl, 12, 30); o.ink(np.ones((2, 26), dtype=np.uint8), 11, 40)
    o.ink(np.ones((2, 12), dtype=np.uint8), 18, 52)
    for (x, y) in ((14, 35), (19, 31), (24, 36), (29, 32), (33, 36), (22, 26), (27, 27)): o.ink(pic(["XX.", "XXX", ".XX"]), x, y)
    return o
def juice():
    o = Obj('Juice carton, 48 x 56, green', 48, 56); o.panel(8, 8, 40, 48, GREEN)
    o.ink(ring(12, 1.6), 11, 15)
    for k in range(6):
        t = np.pi * k / 6
        for r in np.arange(-10, 10.01, .25): o.ink(np.ones((1, 1), dtype=np.uint8), int(round(23 + r * np.cos(t))), int(round(27 + r * np.sin(t))))
    o.ink(ring(2.5, fill=True), 20, 24)
    o.ink(pic(["..XXXX", ".XXXXX", "XXXX..", "XX...."]), 30, 10)
    o.ink(np.ones((2, 28), dtype=np.uint8), 10, 44)
    return o
def milk():
    o = Obj('Milk carton, 48 x 48, white', 48, 48); o.panel(8, 8, 40, 40, WHITE)
    o.text('MILK', 8, 9)
    drop = ring(6, fill=True); o.ink(drop, 17, 25)
    for k in range(6): o.ink(np.ones((1, 2 * k + 1), dtype=np.uint8), 23 - k, 20 + k)
    o.bits[30:33, 20:22] = 0                                   # a glint in the drop
    o.ink(pic(["XX", "XX"]), 11, 34); o.ink(pic(["XX", "XX"]), 35, 22); o.ink(pic(["XX", "XX"]), 34, 35)
    return o
def jam():
    o = Obj('Jam jar from above, 56 across, red', 56, 56, round_=True); o.panel(0, 0, 56, 56, RED)
    o.text('JAM', 16, 24)
    for (x, y) in ((27, 13), (20, 17), (34, 17), (27, 40), (20, 37), (34, 37)): o.ink(pic(["XX", "XX"]), x, y)
    return o
def butter():
    o = Obj('Butter dish, 64 x 40, yellow', 64, 40); o.panel(8, 8, 56, 32, YELLOW)
    o.text('BUTTER', 8, 8)
    pat = np.zeros((11, 40), dtype=np.uint8); pat[0] = pat[-1] = 1; pat[:, 0] = pat[:, -1] = 1; pat[0, 0] = pat[0, -1] = pat[-1, 0] = pat[-1, -1] = 0
    pat[3, 4:30] = 1; pat[6, 4:20] = 1
    for k in range(9): pat[1 + k, 36 - k // 2 - 2] = 1
    o.ink(pat, 12, 19)
    return o
def sugar():
    o = Obj('Sugar cubes, 32 x 32, white', 32, 32); o.panel(8, 8, 24, 24, WHITE)
    c = np.zeros((16, 16), dtype=np.uint8); c[7:9, :] = 1; c[:, 7:9] = 1
    for (x, y) in ((2, 2), (4, 4), (11, 2), (13, 4), (2, 11), (4, 13), (12, 12)): c[y, x] = 1
    o.ink(c, 8, 8)
    return o
def tea():
    o = Obj('Tea tin, 48 x 64, TWO colours: red and white, 8 of blue between', 48, 64)
    o.panel(8, 8, 40, 24, RED); o.panel(8, 32, 40, 56, WHITE)
    o.text('TEA', 12, 12)
    cup = pic(["...X..X..X.....", "..X..X..X......", "...X..X..X.....", "...............", "XXXXXXXXXXXX...", "X..........XXX.", "X..........X..X", "X..........X..X",
               "X..........XXX.", ".X........X....", "..XXXXXXXX.....", "...............", "XXXXXXXXXXXXXX."])
    o.ink(np.kron(cup, np.ones((1, 1), dtype=np.uint8)), 16, 38)
    return o
OBJECTS = [cereal(), juice(), milk(), jam(), butter(), sugar(), tea()]

# ---- the Spectrum: bits and attributes for a piece of window with objects on it
def compose(cloth, things, sprites=None, wrong=False):
    """cloth: the bits of a cell-aligned piece of window. things: [(obj, x, y)]. sprites: (mask,
    bits) drawn over everything, as the game draws cars. Returns bits, attrs (the rule applied)."""
    H, W = cloth.shape; b = cloth.copy(); lab = np.zeros((H, W), dtype=np.uint8); cov = np.zeros((H, W), dtype=np.uint8)
    for o, x, y in things:
        for j in range(o.h):
            for i in range(o.w):
                yy, xx = y + j, x + i
                if 0 <= yy < H and 0 <= xx < W and o.shape[j, i]:
                    b[yy, xx] = o.bits[j, i]; lab[yy, xx] = o.label[j, i]; cov[yy, xx] = 1
    if sprites is not None: b[sprites[0] == 1] = sprites[1][sprites[0] == 1]
    a = np.full((H // 8, W // 8), WIN, dtype=np.uint8)
    for r in range(H // 8):
        for c in range(W // 8):
            cl = lab[r * 8:r * 8 + 8, c * 8:c * 8 + 8]; cc = cov[r * 8:r * 8 + 8, c * 8:c * 8 + 8]
            cols = set(cl[cl > 0].tolist())
            if wrong:                                          # the naive way: colour every cell the object touches
                if cc.any(): a[r, c] = (things[0][0].label.max() - 1) * 8 + BLUE
                continue
            if cols:
                assert len(cols) == 1 and cc.all(), 'colour clash'   # never: an inside with cloth, or two colours
                a[r, c] = (cols.pop() - 1) * 8 + BLUE
    return b, a
def verify(o):
    """Every one of the 64 positions against the cell grid: compose() asserts there is no clash."""
    for dy in range(8):
        for dx in range(8):
            compose(np.zeros((o.h + 24 - o.h % 8, o.w + 24 - o.w % 8), dtype=np.uint8), [(o, 8 + dx, 8 + dy)])
def show(b, a, s):
    H, W = b.shape; im = Image.new('RGB', (W, H)); px = im.load()
    for y in range(H):
        for x in range(W):
            at = a[y >> 3, x >> 3]; px[x, y] = PAL[at & 7] if b[y, x] else PAL[(at >> 3) & 7]
    return im.resize((W * s, H * s), Image.NEAREST)

def clean_cloth(w):
    """The cloth alone: it repeats every 32 pixels on the diagonal, so the majority of the pixels
    one or more checks away leaves out the cars and O's."""
    H, W = w.shape; v = np.zeros((H, W), dtype=int); n = np.zeros((H, W), dtype=int)
    for j in range(-4, 5):
        for i in range(-5, 6):
            if (i + j) % 2 or (i == 0 and j == 0): continue
            ys = slice(max(0, -32 * j), min(H, H - 32 * j)); xs = slice(max(0, -32 * i), min(W, W - 32 * i))
            yd = slice(max(0, 32 * j), min(H, H + 32 * j)); xd = slice(max(0, 32 * i), min(W, W + 32 * i))
            v[ys, xs] += w[yd, xd]; n[ys, xs] += 1
    return (v * 2 > n).astype(np.uint8)
def grow(m):
    g = m.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            g[max(0, dy):m.shape[0] + min(0, dy), max(0, dx):m.shape[1] + min(0, dx)] |= m[max(0, -dy):m.shape[0] + min(0, -dy), max(0, -dx):m.shape[1] + min(0, -dx)]
    return g

if __name__ == '__main__':
    for o in OBJECTS: verify(o)
    print('verified: no clash at any of the 64 positions, for all', len(OBJECTS), 'objects')
    try:
        f = ImageFont.truetype('DejaVuSans-Bold.ttf', 24); fs = ImageFont.truetype('DejaVuSans.ttf', 17); fb = ImageFont.truetype('DejaVuSans.ttf', 20)
    except OSError: f = fs = fb = ImageFont.load_default()
    BG, FG = (17, 18, 22), (236, 235, 230)
    sb, sa = option_g3('race'); win = sb[16:152, 8:184].copy(); clean = clean_cloth(win)
    world = np.tile(clean[0:64, 0:64], (4, 4))                 # plain cloth, as much as needed
    parts = []                                                 # (label, image) rows to stack
    # 1. the objects: 6x, then real size and twice size, each on a bit of cloth, off the cell grid
    tiles = []
    for o in OBJECTS:
        W = (o.w + 23) // 8 * 8; H = (o.h + 23) // 8 * 8
        b, a = compose(world[:H, :W], [(o, (W - o.w) // 2 + 3, (H - o.h) // 2 + 2)])
        tiles.append((o.name, show(b, a, 6), show(b, a, 1), show(b, a, 2)))
    hmax = max(t[1].height for t in tiles)
    row = Image.new('RGB', (sum(t[1].width + 20 for t in tiles), hmax + 34 + 190), BG); d = ImageDraw.Draw(row); x = 0
    for name, big, one, two in tiles:
        d.text((x, 4), name if len(name) < 40 else name[:name.index(',') + 9] + ' TWO colours', fill=FG, font=fs)
        row.paste(big, (x, 30)); row.paste(one, (x, hmax + 44)); row.paste(two, (x + one.width + 16, hmax + 44)); x += big.width + 20
    parts.append(('1. The objects: a solid blue edge 8 pixels thick, a coloured inside. Shown 6x, then real size and twice size.', row))
    # 2. the proof: one object scrolled 0-7 pixels across, then down; and without the rule
    o = OBJECTS[0]; thin = Obj('thin', o.w, o.h); thin.panel(8, 8, 40, 56, YELLOW)
    thin.bits[:] = thin.shape; thin.bits[2:-2, 2:-2] = o.bits[2:-2, 2:-2] * 0; thin.label[:] = 0; thin.label[2:-2, 2:-2] = YELLOW + 1
    thin.bits[8:-8, 8:-8] = o.bits[8:-8, 8:-8]
    for title, axis in (('2a. The proof: the cereal box and the cloth scrolled 0 to 7 pixels ACROSS the cell grid (white ticks = cell edges). The colour never leaves the box.', 0),
                        ('2b. The same scrolled 0 to 7 pixels DOWN. Last picture: what happens WITHOUT the rule (thin edge, colour on every cell the box touches).', 1)):
        fr = []
        for k in list(range(8)) + ['wrong']:
            off = 3 if k == 'wrong' else k; dx, dy = (off, 0) if axis == 0 else (0, off)
            if k == 'wrong': dx, dy = 3, 5
            b, a = compose(world[8 - dy:96 - dy, 8 - dx:104 - dx] if True else None, [((thin if k == 'wrong' else o), 20 + dx, 8 + dy)], wrong=(k == 'wrong'))
            im = show(b, a, 3); fm = Image.new('RGB', (im.width + 8, im.height + 30), BG); fd = ImageDraw.Draw(fm); fm.paste(im, (8, 30))
            for t in range(0, im.width + 1, 24): fd.line([(8 + t, 22), (8 + t, 29)], fill=(255, 255, 255))
            for t in range(0, im.height + 1, 24): fd.line([(0, 30 + t), (7, 30 + t)], fill=(255, 255, 255))
            fd.text((8, 0), 'WITHOUT the rule' if k == 'wrong' else '+%d px' % k, fill=(255, 120, 120) if k == 'wrong' else FG, font=fs)
            fr.append(fm)
        row = Image.new('RGB', (sum(i.width + 10 for i in fr), fr[0].height), BG); x = 0
        for i in fr: row.paste(i, (x, 0)); x += i.width + 10
        parts.append((title, row))
    # 3. a whole race screen (the G3 look): three objects on the cloth, a car driving over one
    spr = grow((win ^ clean).astype(np.uint8))
    by = {o.name.split(',')[0]: o for o in OBJECTS}
    things = [(by['Butter dish'], 11, 2), (by['Milk carton'], 107, 3), (by['Jam jar from above'], 44, 55)]
    b, a = compose(clean, things, sprites=(spr, win))
    sb[16:152, 8:184] = b; sa[2:19, 1:23] = a
    scr = render(sb, sa, border=6, s=3)
    notes = ['THE RULE: a solid blue edge at least 8 pixels thick; a cell is coloured only if it holds some',
             '  of the inside. Checked by the script at all 64 pixel positions for every object: no clash.',
             '',
             'SIZES: the edge takes 8 pixels each side, so an object must be at least 17 x 17 to have any',
             '  inside at all; every pixel of the inside is ALWAYS coloured, at every position (it does',
             '  not need a spare 15). In practice 32 x 32 (a 16 x 16 inside) is the smallest worth drawing;',
             '  48 x 48 and up look best. Round shapes work too (the jam jar): the inside is whatever is',
             '  8 pixels in from the outline. Two colours need 8 pixels of solid blue between them (the tea tin).',
             '',
             'COST: per picture, for each object in view, the game colours the cells that hold its inside',
             '  and puts back the ones it has left: about 10 to 35 colour writes for these sizes (cereal',
             '  box 24-35, butter dish 18-28). The object itself is drawn once into the world like the',
             '  cloth; cars need no change - over a box a car is simply blue on that colour.',
             '',
             'LIMITS: plain colours only, not BRIGHT (a BRIGHT cell would also brighten its blue, and the',
             '  edge would show two blues). One ink: the drawing on a box is always blue. Objects must',
             '  not overlap each other, but need no gap: they may even touch. O\'s and cars may sit beside',
             '  or on a box (on the inside they are blue on the box colour). Where a car\'s 1-pixel halo',
             '  crosses the edge it shows the box colour inside the edge and cyan outside - a tiny nick.',
             '  Half the width of a small box is edge, so small boxes look heavy; yellow on the yellow',
             '  table surround is no problem - inside the window everything round it is cyan.']
    row = Image.new('RGB', (scr.width + 30 + 980, scr.height), BG); d = ImageDraw.Draw(row); row.paste(scr, (0, 0))
    for k, t in enumerate(notes): d.text((scr.width + 30, 8 + 27 * k), t, fill=FG, font=fb)
    parts.append(('3. On the race screen (G3 look, 3x): butter dish, milk carton and jam jar on the cloth; a car driving over the jam jar.', row))
    W = max(p[1].width for p in parts) + 40; H = sum(p[1].height + 60 for p in parts) + 20
    out = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(out); y = 14
    for title, im in parts:
        d.text((20, y), title, fill=(255, 255, 255), font=f); out.paste(im, (20, y + 38)); y += im.height + 60
    p = os.path.join(DESIGN, 'colour_objects.png'); out.save(p); print('wrote', os.path.normpath(p), out.size)
