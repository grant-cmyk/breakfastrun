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
two blues. The cloth, cars and O's are the real ones (docs/design/mock_objects_racing.bin: the
game's screen memory from zxdev, 14 Nov 2026: load build/racer.tap, 160 frames, Q, 250 frames);
the objects are new art.

Revised the same day (Grant: "the coloured items will not appear in the race area. They also need
to be designed with a top down view of things. So what would milk look like top down for
example"): every object is now drawn as seen from straight above the table - toast, a waffle,
sugar cubes, the top of a milk carton, butter on its dish, a place mat with a plate and a fried egg, a bowl of
cereal, a mug of tea, a jam jar's lid - and in the race picture they stand OFF the road.
Then (Grant: "the egg definitely needs yellow yolk ... maybe some white milk. A black coffee in a
cup"): a fried egg with a YELLOW yolk on white (two colours, the yolk's bold blue surround being
the 8 pixels of blue between them), a glass of milk in place of the carton top, and a black
coffee on a white saucer (black paper).

Writes docs/design/colour_objects.png: the objects (6x, 1x, 2x), the proof (one object scrolled
0-7 pixels across and down, and what goes wrong without the rule), and a whole race screen.
Usage: make_colour_objects.py"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
from make_layout_review import load, render, FONT, PAL
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
    def mask(self, m, colour):
        """An inside of any shape (None: white, for round_obj)."""
        self.bits[m == 1] = 0; self.label[m == 1] = 99 if colour is None else colour + 1
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

def disc(w, h, cx, cy, r):
    y, x = np.mgrid[0:h, 0:w]; return (np.hypot(x - cx, y - cy) <= r).astype(np.uint8)
def round_obj(name, d):
    """A round thing from above: the solid edge is its rim; the inside is a true circle, small
    enough (8 x root 2 = 11.3 pixels in) that no cell can hold both inside and cloth."""
    o = Obj(name, d, d, round_=True); c = (d - 1) / 2
    o.mask(disc(d, d, c, c, d / 2 - 11.4), None); return o, c

def toast():
    o = Obj('Slice of toast, 40 x 40, yellow', 40, 40); o.panel(8, 8, 32, 32, YELLOW)     # the crust is the edge
    o.ink(pic(["XXXXXXXXX", "X.......X", "X.......X", "X.......X", "X.......X", "X.......X", "XXXXXXXXX", ".XXXXXXXX"]), 18, 12)   # a pat of butter
    for (x, y) in ((11, 11), (14, 16), (10, 21), (13, 27), (19, 24), (24, 28), (28, 23), (29, 10), (15, 10), (21, 29)): o.ink(pic(["X"]), x, y)
    return o
def waffle():
    o = Obj('Waffle, 48 x 48, yellow', 48, 48); o.panel(8, 8, 40, 40, YELLOW)
    g = np.zeros((32, 32), dtype=np.uint8)
    for k in (6, 7, 14, 15, 22, 23): g[k, :] = 1; g[:, k + 1] = 1
    g[:, 31] = 1; g[30:, :] = 1; o.ink(g, 8, 8)
    return o
def sugar():
    o = Obj('Sugar cubes, 32 x 32, white', 32, 32); o.panel(8, 8, 24, 24, WHITE)
    c = np.zeros((16, 16), dtype=np.uint8); c[7:9, :] = 1; c[:, 7:9] = 1
    for (x, y) in ((2, 2), (4, 4), (11, 2), (13, 4), (2, 11), (4, 13), (12, 12)): c[y, x] = 1
    o.ink(c, 8, 8)
    return o
def glass():
    o, c = round_obj('Glass of milk, 48 across, white', 48)
    arc = ring(9.5, 1.3); arc[8:, :] = 0; arc[:, 8:] = 0; o.ink(arc, 14, 14)      # a highlight on the milk
    return o
def egg():
    """Two colours: the yolk is yellow, the white is white, and the 10 pixels of solid blue between
    them (8 on the square, so 10.5 on the round) is the yolk's bold outline."""
    n = 84; c = (n - 1) / 2; o = Obj('Fried egg, 84 across, white with a YELLOW yolk', n, n)
    y, x = np.mgrid[0:n, 0:n]; t = np.arctan2(y - c, x - c)
    o.shape = (np.hypot(x - c, y - c) <= 37.5 + 2.0 * np.sin(2 * t + 0.7) + 1.2 * np.sin(3 * t + 2)).astype(np.uint8)   # a wobbly white
    o.bits = o.shape.copy(); o.label[:] = 0
    o.panel(0, 0, n, n, WHITE)
    ringm = disc(n, n, c, c, 17.3); o.bits[ringm == 1] = 1; o.label[ringm == 1] = 0
    o.mask(disc(n, n, c, c, 6.7), YELLOW)
    o.ink(pic([".XX", "X..", "X.."]), 37, 37)                  # a glint on the yolk
    for (px, py) in ((20, 30), (60, 26), (24, 58), (58, 60), (41, 17), (44, 66)): o.ink(pic(["X"]), px, py)   # pepper
    return o
def coffee():
    """Black coffee: black paper. The cup's wall is the 8+ of blue between the black and the white saucer."""
    n = 76; c = (n - 1) / 2; o = Obj('Black coffee on a saucer, 76 across, black and white', n, n, round_=True)
    o.mask(disc(n, n, c, c, 26.4) & (1 - disc(n, n, c, c, 20.7)), WHITE)
    o.mask(disc(n, n, c, c, 10.2), BLACK)
    o.ink(np.ones((7, 8), dtype=np.uint8), 57, 34)             # the handle, lying across the saucer
    arc = ring(7.5, 1.3); arc[6:, :] = 0; arc[:, 6:] = 0; o.ink(arc, 30, 30)       # a highlight on the coffee
    o.ink(pic(["XX", "XX"]), 40, 41); o.ink(pic(["X"]), 43, 38)
    return o
def butter():
    o = Obj('Butter on its dish, 56 x 40, yellow', 56, 40); o.panel(8, 8, 48, 32, YELLOW)
    pat = np.zeros((14, 28), dtype=np.uint8); pat[0] = pat[-1] = 1; pat[:, 0] = pat[:, -1] = 1; pat[0, 0] = pat[0, -1] = pat[-1, 0] = pat[-1, -1] = 0
    pat[1:-1, 20] = 1; pat[3, 3:15] = 1; pat[5, 3:10] = 1      # the pat, one slice cut, a shine
    o.ink(pat, 14, 13)
    return o
def mat():
    o = Obj('Place mat and plate, 80 x 64, green and white', 80, 64)
    inside = np.zeros((64, 80), dtype=np.uint8); inside[8:56, 8:72] = 1
    o.mask(inside & (1 - disc(80, 64, 39.5, 31.5, 24.6)), GREEN)       # the mat; the plate's rim is 8+ of solid blue
    o.mask(disc(80, 64, 39.5, 31.5, 14.2), WHITE)                      # the plate
    o.ink(ring(9.5, 1.2), 30, 22)                              # the well of the plate
    for k in range(0, 44, 4): o.ink(pic(["X"]), 10, 10 + k); o.ink(pic(["X"]), 69, 10 + k)   # stitching
    return o
def bowl():
    o, c = round_obj('Bowl of cereal, 64 across, white', 64)
    o.ink(ring(19.5, 1.0), 12, 12)                             # the shadow under the rim
    for (x, y) in ((27, 16), (36, 19), (19, 24), (29, 26), (39, 29), (22, 34), (32, 36), (41, 38), (27, 43), (17, 30), (36, 44)):
        o.ink(ring(2.5, 1.3), x, y)                            # the O's
    return o
def mug():
    o, c = round_obj('Mug of tea, 48 across + handle, red', 48)
    big = Obj(o.name, 58, 48); big.shape[:] = 0; big.shape[:, :48] = o.shape
    big.shape[17:31, 44:57] = 1; big.shape[21:27, 49:54] = 0   # the handle, with its hole (cloth shows through)
    big.shape[17, 56] = big.shape[30, 56] = 0
    big.bits = big.shape.copy(); big.label[:] = 0; big.mask(disc(58, 48, c, c, 48 / 2 - 11.4), RED)
    arc = ring(9.5, 1.3); arc[8:, :] = 0; arc[:, 8:] = 0; big.ink(arc, 14, 14)    # a highlight on the tea
    return big
def jam():
    o, c = round_obj('Jam jar lid, 56 across, red', 56)
    o.label[o.label > 0] = RED + 1
    o.text('JAM', 16, 24)
    for (x, y) in ((27, 15), (21, 18), (33, 18), (27, 39), (21, 36), (33, 36)): o.ink(pic(["XX", "XX"]), x, y)
    return o
OBJECTS = [egg(), glass(), coffee(), toast(), waffle(), sugar(), butter(), mat(), bowl(), mug(), jam()]
for o in OBJECTS: o.label[o.label == 99] = WHITE + 1

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
    sb, sa = load(os.path.join(DESIGN, 'mock_objects_racing.bin'))      # the game today: window x 8-183, y 8-151
    win = sb[8:152, 8:184].copy(); clean = clean_cloth(win)
    world = np.tile(clean[0:64, 0:64], (4, 4))                 # plain cloth, as much as needed
    parts = []
    # 1. the objects: 6x, then real size and twice size, each on a bit of cloth, off the cell grid
    tiles = []
    for o in OBJECTS:
        W = (o.w + 23) // 8 * 8; H = (o.h + 23) // 8 * 8
        b, a = compose(world[:H, :W], [(o, (W - o.w) // 2 + 3, (H - o.h) // 2 + 2)])
        tiles.append((o.name, show(b, a, 5), show(b, a, 1), show(b, a, 2)))
    rows = []
    for chunk in (tiles[:5], tiles[5:]):
        hmax = max(t[1].height for t in chunk)
        row = Image.new('RGB', (sum(max(t[1].width, 300) + 20 for t in chunk), hmax + 60 + max(t[3].height for t in chunk) + 20), BG); d = ImageDraw.Draw(row); x = 0
        for name, big, one, two in chunk:
            n1, n2 = name.split(', ', 1)
            d.text((x, 0), n1, fill=(255, 255, 255), font=fs); d.text((x, 20), n2, fill=FG, font=fs)
            row.paste(big, (x, 46)); row.paste(one, (x, hmax + 60)); row.paste(two, (x + one.width + 16, hmax + 60)); x += max(big.width, 300) + 20
        rows.append(row)
    row = Image.new('RGB', (max(r.width for r in rows), sum(r.height for r in rows)), BG); y = 0
    for r in rows: row.paste(r, (0, y)); y += r.height
    parts.append(('1. The objects, all seen from straight above: a solid blue edge 8 pixels thick, a coloured inside. Shown 5x, then real size and twice size.', row))
    # 2. the proof: one object scrolled 0-7 pixels across, then down; and without the rule
    o = OBJECTS[0]; colour = WHITE
    thin = Obj('thin', o.w, o.h); thin.shape = o.shape.copy()  # the same egg with only a 2-pixel outline
    core = 1 - grow(grow((1 - o.shape).astype(np.uint8)))
    yolk = (o.label == YELLOW + 1).astype(np.uint8)
    thin.bits = (o.shape & (1 - core)) | (grow(grow(yolk)) & (1 - yolk)) | (o.bits & (o.label > 0))
    thin.label[:] = 0; thin.label[core == 1] = colour + 1
    PW, PH = (o.w + 47) // 8 * 8, (o.h + 31) // 8 * 8
    for title, axis in (('2a. The proof: the fried egg (two colours) and the cloth scrolled 0 to 7 pixels ACROSS the cell grid (white ticks = cell edges). Neither colour ever leaves the egg.', 0),
                        ('2b. The same scrolled 0 to 7 pixels DOWN. Last picture: what happens WITHOUT the rule (thin edge, colour on every cell the egg touches).', 1)):
        fr = []
        for k in list(range(8)) + ['wrong']:
            dx, dy = (3, 5) if k == 'wrong' else ((k, 0) if axis == 0 else (0, k))
            b, a = compose(world[8 - dy:8 - dy + PH, 8 - dx:8 - dx + PW], [((thin if k == 'wrong' else o), 20 + dx, 8 + dy)], wrong=(k == 'wrong'))
            im = show(b, a, 3); fm = Image.new('RGB', (im.width + 8, im.height + 30), BG); fd = ImageDraw.Draw(fm); fm.paste(im, (8, 30))
            for t in range(0, im.width + 1, 24): fd.line([(8 + t, 22), (8 + t, 29)], fill=(255, 255, 255))
            for t in range(0, im.height + 1, 24): fd.line([(0, 30 + t), (7, 30 + t)], fill=(255, 255, 255))
            fd.text((8, 0), 'WITHOUT the rule' if k == 'wrong' else '+%d px' % k, fill=(255, 120, 120) if k == 'wrong' else FG, font=fs)
            fr.append(fm)
        row = Image.new('RGB', (sum(i.width + 10 for i in fr), fr[0].height), BG); x = 0
        for i in fr: row.paste(i, (x, 0)); x += i.width + 10
        parts.append((title, row))
    # 3. the game's own screen: objects on the table OFF the road (the road runs between the rows
    #    of O's: across the middle and up the right-hand side here), and a car that has left the road
    x_ = (win ^ clean).astype(np.uint8); spr = grow(x_); sbits = win.copy()
    by = {o.name.split(',')[0]: o for o in OBJECTS}
    things = [(by['Fried egg'], -10, -38), (by['Glass of milk'], 74, -5)]
    b, a = compose(clean, things, sprites=(spr, sbits))
    sb[8:152, 8:184] = b; sa[1:19, 1:23] = a
    scr = render(sb, sa, border=6, s=3)
    notes = ['THE RULE: a solid blue edge at least 8 pixels thick; a cell is coloured only if it holds some',
             '  of the inside. Checked by the script at all 64 pixel positions for every object: no clash.',
             '',
             'TOP DOWN: everything is drawn as seen from straight above the table. The edge does a job in',
             '  each drawing: the crust of the toast, the rim of the bowl and the glass, the wall of the cup.',
             '',
             'THE EGG: yellow yolk on white. Two colours need 8 pixels of solid blue between them, so the',
             '  yolk has a bold blue surround 10 pixels thick; with the white and the outer edge the egg comes',
             '  to 84 across with a 13-pixel yolk. It cannot be made much smaller. On the place mat\'s plate',
             '  it would need three more rings (over 100 pixels), so the plate is left empty.',
             '',
             'THE COFFEE: black paper works - the cup wall is the blue between the black and the white saucer.',
             '  Blue drawing on black is dim: the highlight barely shows, so the coffee is best left plain.',
             '',
             'WHERE: landmarks on the table beside the track, never on the road. In this view the only room',
             '  off the road is the strip above it, 44 pixels deep: the egg is half in view (scrolling in from',
             '  the top, with no clash) and the milk beside it. The coffee (76 across) did not fit this view.',
             '',
             'COST: per picture, for each object in view, the game colours the cells that hold its inside',
             '  and puts back the ones it has left: about 10 to 60 colour writes each for these sizes.',
             '',
             'LIMITS: plain colours only, not BRIGHT. One ink: all the drawing is blue. Over the solid blue',
             '  edge a car shows only as its thin outline. Objects must not overlap each other, but may touch.']
    row = Image.new('RGB', (scr.width + 30 + 1000, scr.height), BG); d = ImageDraw.Draw(row); row.paste(scr, (0, 0))
    for k, t in enumerate(notes): d.text((scr.width + 30, 8 + 27 * k), t, fill=FG, font=fb)
    parts.append(('3. In the game as it is today (3x): the fried egg (half in view) and the glass of milk on the table above the road.', row))
    W = max(p[1].width for p in parts) + 40; H = sum(p[1].height + 60 for p in parts) + 20
    out = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(out); y = 14
    for title, im in parts:
        d.text((20, y), title, fill=(255, 255, 255), font=f); out.paste(im, (20, y + 38)); y += im.height + 60
    p = os.path.join(DESIGN, 'colour_objects.png'); out.save(p); print('wrote', os.path.normpath(p), out.size)
