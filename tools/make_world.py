"""Generate the scrolling world for stage 2: a top-down breakfast-table track
576 x 448 pixels, cut into 8x8 tiles. Writes src/world.asm.
  road        = blank table (white)
  road edges  = cereal O's
  off-road    = blank, with cereal hoops scattered on it
  start line  = a black-and-white checker band across the road
The scrolling window is ONE colour pair (a Spectrum can only colour 8x8 blocks,
which cannot follow a smooth pixel scroll), so everything here is ink on paper."""
import math, os
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'src', 'world.asm')
W, H = 72, 56                     # tiles (a border wide enough that the
                                  # camera never has to stop at the world's edge)
PW, PH = W * 8, H * 8             # pixels
ROAD = 56                         # road width in pixels (48, then 52, then 56 - Grant, 10 Nov 2026)

# centre line of the loop (pixels) - a rounded shape with an S-bend
PATH = [(140, 300), (300, 300), (370, 300), (390, 260), (390, 200), (330, 170),
        (300, 130), (330, 100), (380, 95), (390, 80)]
PATH = [(140, 290), (360, 290), (385, 250), (385, 200), (330, 175), (300, 140),
        (330, 105), (370, 95), (385, 80)]
# simpler, reliable loop: rounded rectangle with a chicane on the top straight
PATH = []
def arc(cx, cy, r, a0, a1, n=10):
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        PATH.append((cx + r * math.cos(a), cy + r * math.sin(a)))
arc(380, 280, 40, 90, 0)          # bottom-right corner (going anticlockwise on screen)
arc(380, 120, 40, 0, -90)         # top-right
PATH.append((300, 80)); PATH.append((270, 120)); PATH.append((230, 120)); PATH.append((200, 80))
arc(140, 120, 40, -90, -180)      # top-left
arc(140, 280, 40, 180, 90)        # bottom-left

OFF = 32                          # the whole track moves this far in from the corner
PATH = [(x + OFF, y + OFF) for x, y in PATH]

def road_mask(width):
    im = Image.new('1', (PW, PH), 0)
    d = ImageDraw.Draw(im)
    pts = PATH + [PATH[0]]
    d.line(pts, fill=1, width=width, joint='curve')
    for x, y in pts:
        d.ellipse([x - width / 2, y - width / 2, x + width / 2, y + width / 2], fill=1)
    return im

road = road_mask(ROAD).load()
img = Image.new('1', (PW, PH), 0)        # 1 = ink
px = img.load()
# cereal O's mark both sides of the road (Grant, 9 Nov 2026), in place of kerbs.
# Each O is 8x8, its top-left snapped to the 8-px tile grid: every O is exactly
# one tile (one picture, drawn whole - the cheapest to draw). Walk the centre line; step out half a road plus 3 px.
O_RING = ["..####..", ".#.####.", "###..###", "##....##", "##....##", "###..###", ".######.", "..####.."]
def place_os():
    pts = PATH + [PATH[0]]
    seq = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0)))
        for i in range(n): seq.append((x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n))
    got = []
    for side in (-1, 1):
        last = None
        for i in range(len(seq)):
            (xa, ya), (xb, yb) = seq[i - 2], seq[(i + 2) % len(seq)]
            d = math.hypot(xb - xa, yb - ya) or 1
            nx, ny = -(yb - ya) / d, (xb - xa) / d
            cx, cy = seq[i][0] + side * nx * (ROAD / 2 + 3), seq[i][1] + side * ny * (ROAD / 2 + 3)
            p = (int(round((cx - 4) / 8)) * 8, int(round((cy - 4) / 8)) * 8)   # one tile each: cheapest to draw
            if last is None or math.hypot(p[0] - last[0], p[1] - last[1]) >= 18:
                if all(math.hypot(p[0] - q[0], p[1] - q[1]) >= 15 for q in got):
                    got.append(p); last = p
    return got
OS = place_os()
for ox, oy in OS:
    for j, r in enumerate(O_RING):
        for i, c in enumerate(r):
            if c == '#': px[ox + i, oy + j] = 1
# start line: checker band 8px tall across the bottom straight at x=256..263
for y in range(240 + OFF, 340 + OFF):
    for x in range(256 + OFF, 264 + OFF):
        if road[x, y] and not px[x, y] and ((x // 4) + (y // 4)) % 2 == 0:
            px[x, y] = 1

import random
random.seed(7)
items_img = Image.new('1', (PW, PH), 0)  # the breakfast things alone, for their masks
ipx = items_img.load()
far = road_mask(ROAD + 24).load()   # things stay clear of the O's (a band 12 px each side wider than the road)
taken = set()
def free(tx, ty, w, h):
    for j in range(h):
        for i in range(w):
            if (tx + i, ty + j) in taken: return False
            for yy in range(8):
                for xx in range(8):
                    X, Y = (tx + i) * 8 + xx, (ty + j) * 8 + yy
                    if not (0 <= X < PW and 0 <= Y < PH) or far[X, Y]: return False
    return True
def place(shape, tx, ty):
    w, h = len(shape[0]) // 8, len(shape) // 8
    for j in range(h + 1):
        for i in range(w + 1):
            taken.add((tx + i - 0, ty + j - 0))
    for y, row in enumerate(shape):
        for x, c in enumerate(row):
            if c == '#': px[tx * 8 + x, ty * 8 + y] = 1; ipx[tx * 8 + x, ty * 8 + y] = 1
# the breakfast table: a few big things, so only one or two are in view at
# a time (tools/make_breakfast.py draws them)
import importlib.util
spec = importlib.util.spec_from_file_location('bf', os.path.join(HERE, 'make_breakfast.py'))
bf = importlib.util.module_from_spec(spec); spec.loader.exec_module(bf)
I = bf.ITEMS
wanted = [('plate', 32, 24), ('knife', 39, 24), ('fork', 30, 24), ('spoon', 41, 24),
          ('egg', 24, 21), ('toast', 25, 31), ('juice', 44, 32), ('bacon', 34, 33),
          ('juice', 3, 3), ('toast', 60, 3), ('egg', 63, 47), ('bacon', 3, 50), ('plate', 61, 22),
          ('egg', 2, 24), ('toast', 30, 1), ('fork', 66, 36), ('knife', 68, 36), ('juice', 45, 50),
          ('bacon', 14, 2), ('egg', 24, 49)]
# Each thing is masked so it sits on the tablecloth, but a tile only needs its
# mask (slower to draw) where the mask covers a dark, dithered check. So try
# positions near the one wanted and take the one with fewest such tiles.
def shape_mask(shape):
    h, w = len(shape), len(shape[0])
    a = [[c == '#' for c in r] for r in shape]
    d = [[any(0 <= y + j < h and 0 <= x + i < w and a[y + j][x + i] for j in (-1, 0, 1) for i in (-1, 0, 1))
          for x in range(-1, w + 1)] for y in range(-1, h + 1)]
    H2, W2 = h + 2, w + 2
    out = [[False] * W2 for _ in range(H2)]; st = [(y, x) for y in range(H2) for x in (0, W2 - 1)] + [(y, x) for y in (0, H2 - 1) for x in range(W2)]
    while st:
        y, x = st.pop()
        if 0 <= y < H2 and 0 <= x < W2 and not out[y][x] and not d[y][x]:
            out[y][x] = True; st += [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]
    return [(x - 1, y - 1) for y in range(H2) for x in range(W2) if not out[y][x]]
def dark_tiles(shape, tx, ty):
    tl = set()
    for x, y in shape_mask(shape):
        X, Y = tx * 8 + x, ty * 8 + y
        if ((X >> 5) + (Y >> 5)) & 1: tl.add((X >> 3, Y >> 3))
    return len(tl)
placed = []
for name, tx, ty in wanted:
    shape = I[name]
    w, h = len(shape[0]) // 8, len(shape) // 8
    best = None
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            if free(tx + dx, ty + dy, w, h):
                k = (dark_tiles(shape, tx + dx, ty + dy), abs(dx) + abs(dy))
                if best is None or k < best[0]: best = (k, tx + dx, ty + dy)
    if best:
        place(shape, best[1], best[2]); placed.append(name)
print('placed:', ' '.join(placed)); print('cereal Os:', len(OS))

# masks: the breakfast things sit ON the tablecloth (Grant, 10 Nov 2026) - a 1-px
# white halo round each, and solid inside its outline. Drawn (cloth AND NOT mask) OR ink.
import numpy as np
from collections import deque
ia = np.array(items_img, dtype=bool)
d = ia.copy()
for dy in (-1, 0, 1):
    for dx in (-1, 0, 1):
        d |= np.roll(np.roll(ia, dy, 0), dx, 1)
seen = np.zeros_like(d); q = deque((y, x) for y in range(PH) for x in (0, PW - 1)); q.extend((y, x) for y in (0, PH - 1) for x in range(PW))
while q:
    y, x = q.popleft()
    if 0 <= y < PH and 0 <= x < PW and not seen[y, x] and not d[y, x]:
        seen[y, x] = True; q.extend(((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)))
imask = d | ~seen
# cut into tiles: plain ones first (ink only, OR'd onto the cloth), then the
# masked ones (from TM_FIRST), each with an index into the de-duplicated masks
def tbytes(get, tx, ty):
    return bytes(sum((int(get(tx * 8 + i, ty * 8 + j)) << (7 - i)) for i in range(8)) for j in range(8))
yy, xx = np.mgrid[0:PH, 0:PW]                         # the cloth's dithered pixels
cloth_on = ((((xx >> 5) + (yy >> 5)) & 1) == 1) & ((xx & 1) == 0) & ((yy & 1) == 0)   # 25% dots
cells = {}
for ty in range(H):
    for tx in range(W):
        ink = tbytes(lambda x, y: px[x, y], tx, ty)
        sl = (slice(ty * 8, ty * 8 + 8), slice(tx * 8, tx * 8 + 8))
        if (imask[sl] & cloth_on[sl]).any():   # the mask hides some cloth: needed
            msk = tbytes(lambda x, y: imask[y, x], tx, ty)
        else:                                  # on white cloth: plain OR is the same
            msk = bytes(8)
        cells[(tx, ty)] = (ink, msk)
plain = [bytes(8)] + sorted({ink for ink, m in cells.values() if not any(m) and any(ink)})
masked = sorted({(ink, m) for ink, m in cells.values() if any(m)})
TM_FIRST = len(plain)
order = plain + [ink for ink, m in masked]
num = {(ink, bytes(8)): i for i, ink in enumerate(plain)}
num.update({k: TM_FIRST + i for i, k in enumerate(masked)})
umasks = sorted({m for ink, m in masked})
midx = [umasks.index(m) for ink, m in masked]
mapb, surf = [], []
for ty in range(H):
    for tx in range(W):
        ink, m = cells[(tx, ty)]
        mapb.append(num[(ink, m)] if any(m) else num[(ink, bytes(8))])
        on = sum(road[tx * 8 + i, ty * 8 + j] for i in range(8) for j in range(8))
        surf.append(0 if on >= 32 else 1)
print('masked tiles:', len(masked), ' different masks:', len(umasks))
TOPDATA = os.path.join(HERE, '..', 'src', 'topdata.asm')
with open(TOPDATA, 'w') as f:
    f.write('; GENERATED by tools/make_world.py - do not edit by hand\n')
    f.write('; data kept at the top of memory (see TOPMEM): the masks, the mini-map\n')
    f.write('; the breakfast things\' masks\n')
    f.write('; for each masked tile (number - TM_FIRST): which mask\ntmask_idx_src:\n')
    for i in range(0, len(midx), 16):
        f.write('        defb ' + ','.join(str(v) for v in midx[i:i + 16]) + '\n')
    f.write('; the masks, 8 bytes each (1 = covers the cloth)\ntmask_src:\n')
    for m in umasks:
        f.write('        defb ' + ','.join('0x%02X' % b for b in m) + '\n')
assert len(order) <= 256, 'too many tiles: %d' % len(order)

# start: on the bottom straight, left of the line, facing right (angle 16 of 64)
start_x, start_y = 200 - 8 + OFF, 320 - 8 + OFF
with open(OUT, 'w') as f:
    f.write('; GENERATED by tools/make_world.py - do not edit by hand\n')
    f.write('; world %d x %d tiles (%d x %d pixels), %d different tiles\n\n' % (W, H, PW, PH, len(order)))
    f.write('MAPW    equ %d\nMAPH    equ %d\nSTARTX  equ %d\nSTARTY  equ %d\nSTARTA  equ 16\n' % (W, H, start_x, start_y))
    f.write('TM_FIRST equ %d      ; tiles from here on are masked (the breakfast things)\n\n' % TM_FIRST)
    f.write('; tile pictures, 8 bytes each (tile 0 = blank). Page aligned so a\n; tile never crosses a 256-byte page.\n        defs (256 - ($ & 255)) & 255\ntiles:\n')
    for i, t in enumerate(order):
        f.write('        defb ' + ','.join('0x%02X' % b for b in t) + '   ; %d\n' % i)
    # the map, stored as a LIST of the non-blank tiles in each row: most of the
    # table is blank, and the renderer then only looks at tiles it must draw
    f.write('\n; the map: for each of the %d tile rows, a pointer to its list\nrow_index:\n' % H)
    for ty in range(H):
        f.write('        dw row_%d\n' % ty)
    f.write('; each list: how many tiles, then (column, tile number) pairs, left to right\n')
    for ty in range(H):
        ent = [(tx, mapb[ty * W + tx]) for tx in range(W) if mapb[ty * W + tx]]
        f.write('row_%d:  defb %d' % (ty, len(ent)) + ''.join(',%d,%d' % e for e in ent) + '\n')
    f.write('\n; surface: one BIT per tile, 1 = off-road (slower); %d bytes a row,\n' % (W // 8))
    f.write('; leftmost tile in the top bit\nsurface_map:\n')
    for ty in range(H):
        row = surf[ty * W:(ty + 1) * W]
        f.write('        defb ' + ','.join('%%%s' % ''.join(str(b) for b in row[i:i + 8]) for i in range(0, W, 8)) + '\n')

# waypoints: the centre line every ~32 px, in racing order, for the computer cars
loop = PATH + [PATH[0]]
seglen = [math.dist(loop[i], loop[i + 1]) for i in range(len(PATH))]
total = sum(seglen)
NWP = round(total / 32)
wps = []
for k in range(NWP):
    d = k * total / NWP
    i = 0
    while d > seglen[i]:
        d -= seglen[i]; i += 1
    (x0, y0), (x1, y1) = loop[i], loop[i + 1]
    t = d / seglen[i]
    wps.append((round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t)))
# computer cars start beside the player, one each side
cpu = [(start_x, start_y - 16), (start_x, start_y + 16),     # front row: three abreast
       (start_x - 28, start_y - 8), (start_x - 28, start_y + 8)]  # second row: two
def first_wp(cx, cy):
    ahead = [k for k, (x, y) in enumerate(wps) if abs(y - cy) < 30 and x > cx + 16]
    return min(ahead, key=lambda k: wps[k][0] - cx)
WPOUT = os.path.join(HERE, '..', 'src', 'waypoints.asm')
with open(OUT, 'a') as f:
    f.write('\n; (the waypoints are in waypoints.asm, placed where they fill an alignment gap)\n')
with open(WPOUT, 'w') as f:
    f.write('; GENERATED by tools/make_world.py - do not edit by hand\n')
    f.write('\n; waypoints for the computer cars: centre line, racing order (x, y)\n')
    f.write('NWP     equ %d\n' % NWP)
    # the first waypoint past the start line (lap counting) and your first target
    ws = min((k for k, (x, y) in enumerate(wps) if abs(y - (320 + OFF)) < 30 and x > 264 + OFF), key=lambda k: wps[k][0])
    f.write('WS      equ %d          ; first waypoint after the start line\n' % ws)
    f.write('PLAYERWP equ %d\n' % first_wp(start_x + 8, start_y + 8))
    for n, (x, y) in enumerate(cpu):
        f.write('CPU%dX   equ %d\nCPU%dY   equ %d\nCPU%dWP  equ %d\n' % (n, x, n, y, n, first_wp(x + 8, y + 8)))
with open(WPOUT, 'a') as f:
    f.write('waypoints:\n')
    for x, y in wps:
        f.write('        dw %d,%d\n' % (x, y))
print('waypoints:', NWP)

# the mini-map: the road at 1/8 scale, from (64,32), 56 x 48 px (7 x 6
# cells in the panel), drawn as its two edges so a car's dot shows between
MW, MH = 56, 48
def on_road(mx, my):
    x, y = 64 + mx * 8 + 4, 32 + my * 8 + 4
    return 0 <= x < PW and 0 <= y < PH and road[x, y]
mm = [[0] * MW for _ in range(MH)]
for my in range(MH):
    for mx in range(MW):
        if on_road(mx, my) and any(not on_road(mx + dx, my + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            mm[my][mx] = 1
smx = (256 + OFF + 4 - 64) // 8                   # the start line: a tick across the road
for my in range(MH):
    if on_road(smx, my): mm[my][smx] = 1
obits = [[0] * W for _ in range(H)]                # where the cereal O's are: cars bounce off them
for ox, oy in OS: obits[oy // 8][ox // 8] = 1
with open(TOPDATA, 'a') as f:
    f.write('\n; the cereal O\'s: one BIT per tile (1 = an O: solid - cars bounce off it),\n')
    f.write('; %d bytes a row, leftmost tile in the top bit\nomap_src:\n' % (W // 8))
    for r in obits:
        f.write('        defb ' + ','.join('%%%s' % ''.join(str(b) for b in r[i:i + 8]) for i in range(0, W, 8)) + '\n')
with open(TOPDATA, 'a') as f:
    f.write('\n; the mini-map: road edges at 1/8 scale from world (64,32), 7 bytes x 48 rows\nminimap_src:\n')
    for row in mm:
        f.write('        defb ' + ','.join('%%%s' % ''.join(str(v) for v in row[i:i + 8]) for i in range(0, MW, 8)) + '\n')
open(os.path.join(HERE, '..', 'build', 'minimap.txt'), 'w').write('\n'.join(''.join('#' if v else '.' for v in r) for r in mm) + '\n')

big = img.convert('L').point(lambda v: 0 if v else 255).resize((PW * 2, PH * 2), Image.NEAREST)
big.save(os.path.join(HERE, '..', 'build', 'world_preview.png'))
print('tiles:', len(order), ' road tiles:', surf.count(0))
