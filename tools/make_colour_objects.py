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
cup"): a fried egg with a YELLOW yolk on white (two colours, at first with a bold blue surround
between them; then - Grant: "the white around the egg is white, the yolk is yellow. No blue in
an egg" - the yolk drawn in a SECOND INK, yellow, on the white paper, with 8+ pixels of plain
white between it and any blue; compose() asserts one ink and one paper in every cell), a glass of milk in place of the carton top, and a black
coffee on a white saucer (black paper).

Then (Grant: "for certain things, if we can give them space, then they can use 2 different
colours, and to create the illusion of being more blended, in the area just around it - perhaps
have cyan or blue as one of the two colours"): BLENDED objects with no blue edge - the shape is
ink in its own colour on the cloth's cyan paper, a second colour inside is paper, and 7 pixels
of cloth all round are wiped plain so that no blue ink can share a cell with it.

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

def grow(m):
    g = m.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            g[max(0, dy):m.shape[0] + min(0, dy), max(0, dx):m.shape[1] + min(0, dx)] |= m[max(0, -dy):m.shape[0] + min(0, -dy), max(0, -dx):m.shape[1] + min(0, -dx)]
    return g

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
        self.ink2 = np.zeros((h, w), dtype=np.uint8)           # a second ink colour (+1) for some ink pixels; 0 = blue
        self.wipe = np.zeros((h, w), dtype=np.uint8)           # cloth made plain here (blended objects' margin)
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
    def second_ink(self, m, colour):
        """Solid shapes in a SECOND ink colour, on this object's paper: kept (here, by trimming)
        at least 8 pixels - measured along each axis - from every blue ink pixel and every
        other paper, so no cell can ever hold two inks or two papers."""
        same = ((self.label == self.label[m == 1].max()) & (self.bits == 0)).astype(np.uint8); far = 1 - same
        for _ in range(8): far = grow(far)
        m = m & (1 - far); self.bits[m == 1] = 1; self.ink2[m == 1] = colour + 1; return m
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
    """White with a YELLOW yolk and no blue inside: the yolk is drawn in ink, and the cells that
    hold it are white paper with YELLOW ink. That works as long as no cell ever holds yolk and
    blue together, so there are 8+ pixels of plain white all round the yolk."""
    n = 66; c = (n - 1) / 2; o = Obj('Fried egg, 66 across, white with a YELLOW yolk', n, n)
    y, x = np.mgrid[0:n, 0:n]; t = np.arctan2(y - c, x - c)
    o.shape = (np.hypot(x - c, y - c) <= 30.6 + 1.4 * np.sin(2 * t + 0.7) + 0.9 * np.sin(3 * t + 2)).astype(np.uint8)   # a wobbly white
    o.bits = o.shape.copy(); o.label[:] = 0
    o.panel(0, 0, n, n, WHITE)
    m = o.second_ink(disc(n, n, c, c, 6.0), YELLOW)
    for (px, py) in ((30, 29), (29, 30), (29, 31)):            # a glint: white paper showing through the yolk
        if m[py, px]: o.bits[py, px] = 0; o.ink2[py, px] = 0
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
    o = Obj('Butter on its dish, 64 x 48, white dish, YELLOW pat', 64, 48); o.panel(8, 8, 56, 40, WHITE)
    pat = np.zeros((48, 64), dtype=np.uint8); pat[16:32, 16:48] = 1; pat[16, 16] = pat[16, 47] = pat[31, 16] = pat[31, 47] = 0
    m = o.second_ink(pat, YELLOW)
    o.bits[19, 20:36] = 0; o.bits[21, 20:28] = 0; o.bits[17:31, 40] = 0     # a shine and a cut slice, in white paper
    o.ink2[o.bits == 0] = 0
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

# ---- "blended" objects: no blue edge. The shape is INK in the object's colour on the cloth's own
# cyan paper; a second colour inside is PAPER (the yolk is a hole in the white ink, in cells whose
# paper is yellow). The pixels never change with the scroll, only the cells' colours. The price is
# space: 7 pixels of cloth all round are wiped plain, so no blue dot can share a cell with it.
MARGIN = 7
def blended(name, ink, colour, hole=None, hole_colour=None, cut=None):
    h, w = ink.shape; o = Obj(name, w + 2 * MARGIN + 2, h + 2 * MARGIN + 2); m = MARGIN + 1
    full = np.zeros((o.h, o.w), dtype=np.uint8); full[m:m + h, m:m + w] = ink
    o.shape = full.copy(); o.bits = full.copy(); o.label[:] = 0; o.ink2 = full * (colour + 1)
    if hole is not None:                                       # the second colour: only where 8 pixels inside the shape
        far = 1 - full
        for _ in range(8): far = grow(far)
        hm = np.zeros_like(full); hm[m:m + h, m:m + w] = hole; hm &= (1 - far)
        o.bits[hm == 1] = 0; o.ink2[hm == 1] = 0; o.label[hm == 1] = hole_colour + 1
    if cut is not None:                                        # thin lines of cloth colour drawn into the shape
        cm = np.zeros_like(full); cm[m:m + h, m:m + w] = cut; cm &= full
        o.bits[cm == 1] = 0; o.ink2[cm == 1] = 0
    near = full.copy()
    for _ in range(MARGIN): near = grow(near)
    o.wipe = near & (1 - full)
    return o
def blob(n, f):
    c = (n - 1) / 2; y, x = np.mgrid[0:n, 0:n]; t = np.arctan2(y - c, x - c)
    return (np.hypot(x - c, y - c) <= f(t)).astype(np.uint8)
def egg_blended():
    n = 46; white = blob(n, lambda t: 20.4 + 1.4 * np.sin(2 * t + 0.7) + 0.9 * np.sin(3 * t + 2))
    yolk = disc(n, n, 22.5, 22.5, 6.0); yolk[20, 20] = yolk[19, 21] = yolk[21, 19] = 0     # a white glint on the yolk
    return blended('Fried egg, 46 across, WHITE on the cloth, YELLOW yolk, no blue', white, WHITE, yolk, YELLOW)
def puddle():
    n = 48; m = blob(n, lambda t: 15 + 4 * np.sin(2 * t) + 3 * np.sin(3 * t + 1) + 1.5 * np.sin(5 * t))
    m |= disc(n, n, 42, 9, 2.6) | disc(n, n, 6, 40, 2.0) | disc(n, n, 44, 38, 1.6)
    return blended('Spilt milk, 48 across, white', m, WHITE)
def banana():
    w, h = 56, 34; y, x = np.mgrid[0:h, 0:w]; r = np.hypot(x - 27.5, y + 14); t = np.arctan2(y + 14, x - 27.5)
    u = (t - np.pi / 2) / 0.95                                 # -1 .. 1 along the fruit
    m = ((np.abs(u) <= 1) & (np.abs(r - 38) <= 6.5 * np.sqrt(np.clip(1 - u ** 2, 0, 1)) + 1.2)).astype(np.uint8)
    line = ((np.abs(u) <= 0.8) & (np.abs(r - 39.5) <= 0.5)).astype(np.uint8)
    return blended('Banana, 56 x 34, yellow', m, YELLOW, cut=line)
def strawberry():
    w, h = 40, 44; y, x = np.mgrid[0:h, 0:w]
    half = np.where(y < 16, 18.5 * np.sqrt(np.clip(1 - ((y - 16) / 16.0) ** 2, 0, 1)), 18.5 * np.clip(1 - np.clip((y - 16) / 28.0, 0, 1) ** 1.7, 0, 1))
    m = (np.abs(x - 19.5) <= half).astype(np.uint8)
    seeds = np.zeros((h, w), dtype=np.uint8)
    for (sx, sy) in ((19, 12), (14, 16), (24, 16), (19, 20), (15, 23), (23, 23), (19, 26)): seeds[sy:sy + 2, sx:sx + 2] = 1
    return blended('Strawberry, 40 x 44, red with YELLOW seeds', m, RED, seeds, YELLOW)
BLENDED = [egg_blended(), puddle(), banana(), strawberry()]
OBJECTS = [egg(), glass(), coffee(), toast(), waffle(), sugar(), butter(), mat(), bowl(), mug(), jam()]
for o in OBJECTS: o.label[o.label == 99] = WHITE + 1

# ---- the Spectrum: bits and attributes for a piece of window with objects on it
def compose(cloth, things, sprites=None, mode=None):
    """cloth: the bits of a cell-aligned piece of window. things: [(obj, x, y)]. sprites: (mask,
    bits) drawn over everything, as the game draws cars. Returns bits, attrs. For every cell it
    ASSERTS the Spectrum's rule: all ink pixels one ink colour, all paper pixels one paper colour
    (and none of an object's coloured inside in a cell that also holds cloth).
    mode 'nomargin': a blended object without its plain margin, unchecked - to show the fault.
    mode 'thin': a thin outline, colour only in cells wholly inside, unchecked - to compare."""
    H, W = cloth.shape; b = cloth.copy(); lab = np.zeros((H, W), dtype=np.uint8); cov = np.zeros((H, W), dtype=np.uint8); ik = np.zeros((H, W), dtype=np.uint8)
    for o, x, y in things:
        for j in range(o.h):
            for i in range(o.w):
                yy, xx = y + j, x + i
                if not (0 <= yy < H and 0 <= xx < W): continue
                if o.wipe[j, i] and mode != 'nomargin': b[yy, xx] = 0
                if o.shape[j, i]:
                    b[yy, xx] = o.bits[j, i]; lab[yy, xx] = o.label[j, i]; cov[yy, xx] = 1; ik[yy, xx] = o.ink2[j, i]
    a = np.full((H // 8, W // 8), WIN, dtype=np.uint8)
    for r in range(H // 8):
        for c in range(W // 8):
            sl = (slice(r * 8, r * 8 + 8), slice(c * 8, c * 8 + 8))
            cl, cc, cb, ci = lab[sl], cov[sl], b[sl], ik[sl]
            if mode == 'thin':
                if cc.all(): a[r, c] = (int(cl.max()) - 1) * 8 + BLUE
                continue
            papers = set(cl[cb == 0].tolist()); inks = set(ci[cb == 1].tolist()); cols = set(cl[cl > 0].tolist())
            if mode is None:
                assert len(papers) <= 1 and len(inks) <= 1 and len(cols) <= 1 and (not cols or cc.all()), 'colour clash'
            paper = (max(cols) - 1) if cols else CYAN
            ink = (max(inks) - 1) if inks and max(inks) else BLUE
            a[r, c] = paper * 8 + ink
    if sprites is not None: b[sprites[0] == 1] = sprites[1][sprites[0] == 1]
    return b, a
def verify(o):
    """Every one of the 64 positions against the cell grid, on empty cloth and on cloth that is ALL
    blue ink (the worst case for a blended object's margin): compose() asserts there is no clash."""
    for fill in (0, 1):
        for dy in range(8):
            for dx in range(8):
                compose(np.full((o.h + 24 - o.h % 8, o.w + 24 - o.w % 8), fill, dtype=np.uint8), [(o, 8 + dx, 8 + dy)])
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
if __name__ == '__main__':
    for o in OBJECTS + BLENDED: verify(o)
    print('verified: no clash at any of the 64 positions, for all', len(OBJECTS) + len(BLENDED), 'objects')
    try:
        f = ImageFont.truetype('DejaVuSans-Bold.ttf', 24); fs = ImageFont.truetype('DejaVuSans.ttf', 17); fb = ImageFont.truetype('DejaVuSans.ttf', 20)
    except OSError: f = fs = fb = ImageFont.load_default()
    BG, FG = (17, 18, 22), (236, 235, 230)
    sb, sa = load(os.path.join(DESIGN, 'mock_objects_racing.bin'))      # the game today: window x 8-183, y 8-151
    win = sb[8:152, 8:184].copy(); clean = clean_cloth(win)
    world = np.tile(clean[0:64, 0:64], (4, 4))                 # plain cloth, as much as needed
    parts = []
    # 1. the objects: 6x, then real size and twice size, each on a bit of cloth, off the cell grid
    def sheet_of(objs, per_row):
        tiles = []
        for o in objs:
            W = (o.w + 23) // 8 * 8; H = (o.h + 23) // 8 * 8
            b, a = compose(world[24:24 + H, 16:16 + W], [(o, (W - o.w) // 2 + 3, (H - o.h) // 2 + 2)])
            tiles.append((o.name, show(b, a, 5), show(b, a, 1), show(b, a, 2)))
        rows = []
        for k in range(0, len(tiles), per_row):
            chunk = tiles[k:k + per_row]; hmax = max(t[1].height for t in chunk)
            row = Image.new('RGB', (sum(max(t[1].width, 330) + 20 for t in chunk), hmax + 60 + max(t[3].height for t in chunk) + 20), BG); d = ImageDraw.Draw(row); x = 0
            for name, big, one, two in chunk:
                n1, n2 = name.split(', ', 1)
                d.text((x, 0), n1, fill=(255, 255, 255), font=fs); d.text((x, 20), n2, fill=FG, font=fs)
                row.paste(big, (x, 46)); row.paste(one, (x, hmax + 60)); row.paste(two, (x + one.width + 16, hmax + 60)); x += max(big.width, 330) + 20
            rows.append(row)
        row = Image.new('RGB', (max(r.width for r in rows), sum(r.height for r in rows)), BG); y = 0
        for r in rows: row.paste(r, (0, y)); y += r.height
        return row
    parts.append(('1. Objects with a SOLID BLUE EDGE, all seen from straight above: an edge 8 pixels thick, a coloured inside. Shown 5x, then real size and twice size.', sheet_of(OBJECTS, 6)))
    parts.append(('1b. BLENDED objects - no blue edge: the shape is ink in its own colour on the cloth\'s cyan, with 7 pixels of cloth wiped plain all round (look where the dots stop).', sheet_of(BLENDED, 4)))
    egg_b = BLENDED[0]
    # 2. the proof: one object scrolled 0-7 pixels across, then down; and without the rule
    o = egg_b
    PW, PH = (o.w + 47) // 8 * 8, (o.h + 31) // 8 * 8
    for title, axis in (('2a. The proof: the blended egg and the cloth scrolled 0 to 7 pixels ACROSS the cell grid (white ticks = cell edges). Every cell: one ink colour, one paper colour.', 0),
                        ('2b. The same scrolled 0 to 7 pixels DOWN. Last picture: what happens WITHOUT the plain margin - the cloth\'s dots next to the egg turn white.', 1)):
        fr = []
        for k in list(range(8)) + ['wrong']:
            dx, dy = (3, 5) if k == 'wrong' else ((k, 0) if axis == 0 else (0, k))
            b, a = compose(world[40 - dy:40 - dy + PH, 8 - dx:8 - dx + PW], [(o, 20 + dx, 8 + dy)], mode='nomargin' if k == 'wrong' else None)
            im = show(b, a, 3); fm = Image.new('RGB', (im.width + 8, im.height + 30), BG); fd = ImageDraw.Draw(fm); fm.paste(im, (8, 30))
            for t in range(0, im.width + 1, 24): fd.line([(8 + t, 22), (8 + t, 29)], fill=(255, 255, 255))
            for t in range(0, im.height + 1, 24): fd.line([(0, 30 + t), (7, 30 + t)], fill=(255, 255, 255))
            fd.text((8, 0), 'WITHOUT the margin' if k == 'wrong' else '+%d px' % k, fill=(255, 120, 120) if k == 'wrong' else FG, font=fs)
            fr.append(fm)
        row = Image.new('RGB', (sum(i.width + 10 for i in fr), fr[0].height), BG); x = 0
        for i in fr: row.paste(i, (x, 0)); x += i.width + 10
        parts.append((title, row))
    # 2c. the same egg three ways, and a car crossing it
    x_ = (win ^ clean).astype(np.uint8); g = grow(x_); seen = np.zeros_like(g); best = None
    for sy, sx in zip(*np.nonzero(g)):                        # find one car: the biggest blob about a car's size
        if seen[sy, sx]: continue
        st = [(sy, sx)]; seen[sy, sx] = 1; px = []
        while st:
            cy, cx = st.pop(); px.append((cy, cx))
            for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                if 0 <= ny < g.shape[0] and 0 <= nx < g.shape[1] and g[ny, nx] and not seen[ny, nx]: seen[ny, nx] = 1; st.append((ny, nx))
        ys = [q[0] for q in px]; xs = [q[1] for q in px]
        if max(ys) - min(ys) < 30 and max(xs) - min(xs) < 30 and (best is None or len(px) > len(best)): best = px
    def with_car(o, cx, cy, mode=None):
        W = (o.w + 39) // 8 * 8; H = (o.h + 23) // 8 * 8; ox, oy = (W - o.w) // 2 + 3, (H - o.h) // 2 + 2
        cl = world[40:40 + H, 8:8 + W]; m = np.zeros((H, W), dtype=np.uint8); sb_ = np.zeros((H, W), dtype=np.uint8)
        if cx is not None:
            cx, cy = ox + o.w // 2 - 24, oy + o.h // 2 - 6
            y0 = min(q[0] for q in best); x0 = min(q[1] for q in best)
            for (qy, qx) in best: m[cy + qy - y0, cx + qx - x0] = 1; sb_[cy + qy - y0, cx + qx - x0] = win[qy, qx]
        return compose(cl, [(o, ox, oy)], sprites=(m, sb_) if cx is not None else None, mode=mode)
    thin = Obj('thin', 46, 46); thin.shape = egg_b.shape[8:54, 8:54].copy(); core = 1 - grow(grow(1 - thin.shape))
    yk = disc(46, 46, 22.5, 22.5, 6.0); thin.bits = (thin.shape & (1 - core)) | (yk & (1 - disc(46, 46, 22.5, 22.5, 4.6))); thin.label = thin.shape * (WHITE + 1)
    cmp_ = [('Solid blue edge, yolk in a 2nd ink (66 across)', with_car(OBJECTS[0], None, 0)),
            ('BLENDED: white on the cloth (46 across + margin)', with_car(egg_b, None, 0)),
            ('Thin blue outline, colour a cell inside: WORSE', with_car(thin, None, 0, 'thin')),
            ('A car crossing the solid-edge egg', with_car(OBJECTS[0], 2, 30)),
            ('A car crossing the blended egg: it turns white', with_car(egg_b, 4, 26))]
    row = Image.new('RGB', (sum(max(c[1][0].shape[1] * 4, 380) + 110 for c in cmp_), 96 * 4 + 40), BG); d = ImageDraw.Draw(row); x = 0
    for name, (b, a) in cmp_:
        d.text((x, 0), name, fill=FG, font=fs); row.paste(show(b, a, 1), (x, 30)); row.paste(show(b, a, 4), (x + b.shape[1] + 12, 30)); x += max(b.shape[1] * 4, 380) + 110
    parts.append(('2c. One egg, three styles (real size, then 4x) - and what a car looks like crossing it.', row))
    # 3. the game's own screen: objects on the table OFF the road (the road runs between the rows
    #    of O's: across the middle and up the right-hand side here), and a car that has left the road
    spr = grow(x_); sbits = win.copy()
    by = {o.name.split(',')[0]: o for o in OBJECTS}
    things = [(egg_b, 4, -18), (by['Glass of milk'], 74, -5)]
    b, a = compose(clean, things, sprites=(spr, sbits))
    sb[8:152, 8:184] = b; sa[1:19, 1:23] = a
    scr = render(sb, sa, border=6, s=3)
    notes = ['THREE WAYS to put colour in the window. The script checks every object at all 64 pixel positions:',
             '  in every cell, all the ink is one colour and all the paper is one colour. No clash.',
             '',
             '1. SOLID BLUE EDGE (part 1): an edge of the window\'s own blue, 8 pixels thick; a cell is coloured',
             '  only if it holds some of the inside. Best for SQUARE, made things: toast, waffle, boxes, cups.',
             '  Needs no space round it - it can touch the O\'s, the road, or another object.',
             '',
             '2. A SECOND INK inside (the big egg, the butter): a solid shape in a second ink colour on the',
             '  object\'s paper, kept 8 pixels (along each axis) from any blue.',
             '',
             '3. BLENDED (part 1b): no blue at all. The shape is ink in its own colour on the cloth\'s cyan, so',
             '  its outline can be any shape and meets the cloth directly. A second colour inside (the yolk,',
             '  the seeds) is paper, 8 pixels in from the outline. THE PRICE IS SPACE: nothing blue may share',
             '  a cell with it, so 7 pixels of cloth all round are wiped plain (8 from blue to shape), and it',
             '  must stand that far from the O\'s, the road lines and other objects. Best for SOFT, natural',
             '  things: an egg, spilt milk, a banana, a strawberry. Green on cyan is too weak to use.',
             '',
             'CARS: a car is blue ink. Crossing a solid-edge object it stays blue. Crossing a BLENDED object',
             '  it turns that object\'s colour, cell by cell (see 2c) - so blended objects go where cars',
             '  rarely are. A thin blue outline with the colour a cell inside (2c, middle) is worse than',
             '  either: the colour sits in a blocky step inside the outline and jumps as the screen scrolls.',
             '',
             'WHERE: beside the track, never on the road. In this view the room off the road is a strip 44',
             '  pixels deep: the blended egg (most of it in view) and the glass of milk.',
             '',
             'COST: per picture, per object in view: colouring the cells it is in and putting back the ones',
             '  it left - about 10 to 60 colour writes. The pixels of an object never change with the scroll.',
             '  Plain colours only, not BRIGHT.']
    row = Image.new('RGB', (scr.width + 30 + 1000, scr.height), BG); d = ImageDraw.Draw(row); row.paste(scr, (0, 0))
    for k, t in enumerate(notes): d.text((scr.width + 30, 4 + 25 * k), t, fill=FG, font=fb)
    parts.append(('3. In the game as it is today (3x): the BLENDED fried egg and the solid-edge glass of milk on the table above the road.', row))
    W = max(p[1].width for p in parts) + 40; H = sum(p[1].height + 60 for p in parts) + 20
    out = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(out); y = 14
    for title, im in parts:
        d.text((20, y), title, fill=(255, 255, 255), font=f); out.paste(im, (20, y + 38)); y += im.height + 60
    p = os.path.join(DESIGN, 'colour_objects.png'); out.save(p); print('wrote', os.path.normpath(p), out.size)
