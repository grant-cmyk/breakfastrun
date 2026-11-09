"""Generate the scrolling world for stage 2: a top-down breakfast-table track
576 x 448 pixels, cut into 8x8 tiles. Writes src/world.asm.
  road        = blank table (white)
  road edges  = 2-pixel black lines
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
ROAD = 48                         # road width in pixels

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
# kerbs: a 4-px chequered band along both edges of the road, its 4x4 blocks
# locked to the world grid, so the same tiles repeat along a straight
def near_edge(x, y, d):
    return any(not road[x + dx, y + dy] if 0 <= x + dx < PW and 0 <= y + dy < PH else True
               for dx in range(-d, d + 1, 2) for dy in range(-d, d + 1, 2))
for y in range(PH):
    for x in range(PW):
        if road[x, y]:
            if near_edge(x, y, 4) and ((x // 4) + (y // 4)) % 2 == 0:
                px[x, y] = 1                                   # the chequer (it is the edge)
# start line: checker band 8px tall across the bottom straight at x=256..263
for y in range(240 + OFF, 340 + OFF):
    for x in range(256 + OFF, 264 + OFF):
        if road[x, y] and not px[x, y] and ((x // 4) + (y // 4)) % 2 == 0:
            px[x, y] = 1

# scenery off the road, straight top-down, drawn in the one-bit-art house
# style: trees (an outlined canopy, the shadow side dithered, the lit side
# paper), bushes, and houses (roof outline, ridge, dithered shadow half,
# a solid chimney). Placed on the 8-px grid so their tiles repeat.
TREE = ["....######......",
        "..##......##....",
        ".#..........#...",
        ".#...........#..",
        "#............#..",
        "#...........#.#.",
        "#..........#.#.#",
        "#.........#.#.##",
        "#........#.#.#.#",
        ".#.....#.#.#.#.#",
        ".#......#.#.#.##",
        "..#..#.#.#.#.##.",
        "...##.#.#.#.##..",
        ".....########...",
        "................",
        "................"]
BUSH = ["..####..",
        ".#....#.",
        "#....#.#",
        "#...#.##",
        "#..#.#.#",
        ".#.#.##.",
        "..####..",
        "........"]
HOUSE = ["########################",
         "#..........#...........#",
         "#..........#.#.#.#.#.#.#",
         "#..........##.#.#.#.#.##",
         "#....##....#.#.#.#.#.#.#",
         "#....##....##.#.#.#.#.##",
         "#..........#.#.#.#.#.#.#",
         "#..........##.#.#.#.#.##",
         "#..........#.#.#.#.#.#.#",
         "#..........##.#.#.#.#.##",
         "#..........#.#.#.#.#.#.#",
         "#..........##.#.#.#.#.##",
         "#..........#.#.#.#.#.#.#",
         "#..........##.#.#.#.#.##",
         "#..........#...........#",
         "########################"]
import random
random.seed(7)
far = road_mask(ROAD + 28).load()
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
            if c == '#': px[tx * 8 + x, ty * 8 + y] = 1
houses = [(19, 15), (37, 21), (9, 46), (58, 8), (26, 47)]   # a few, inside and out
for tx, ty in houses:
    if free(tx, ty, 3, 2): place(HOUSE, tx, ty)
for ty in range(1, H - 2):
    for tx in range(1, W - 2):
        r = random.random()
        if r < 0.020 and free(tx, ty, 2, 2): place(TREE, tx, ty)
        elif r < 0.028 and free(tx, ty, 1, 1): place(BUSH, tx, ty)

# cut into tiles
tiles = {bytes(8): 0}
order = [bytes(8)]
mapb, surf = [], []
for ty in range(H):
    for tx in range(W):
        t = bytes(sum((px[tx * 8 + i, ty * 8 + j] << (7 - i)) for i in range(8)) for j in range(8))
        if t not in tiles:
            tiles[t] = len(order); order.append(t)
        mapb.append(tiles[t])
        on = sum(road[tx * 8 + i, ty * 8 + j] for i in range(8) for j in range(8))
        surf.append(0 if on >= 32 else 1)
assert len(order) <= 256, 'too many tiles: %d' % len(order)

# start: on the bottom straight, left of the line, facing right (angle 16 of 64)
start_x, start_y = 200 - 8 + OFF, 320 - 8 + OFF
with open(OUT, 'w') as f:
    f.write('; GENERATED by tools/make_world.py - do not edit by hand\n')
    f.write('; world %d x %d tiles (%d x %d pixels), %d different tiles\n\n' % (W, H, PW, PH, len(order)))
    f.write('MAPW    equ %d\nMAPH    equ %d\nSTARTX  equ %d\nSTARTY  equ %d\nSTARTA  equ 16\n\n' % (W, H, start_x, start_y))
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
with open(OUT, 'a') as f:
    f.write('\n; waypoints for the computer cars: centre line, racing order (x, y)\n')
    f.write('NWP     equ %d\n' % NWP)
    # the first waypoint past the start line (lap counting) and your first target
    ws = min((k for k, (x, y) in enumerate(wps) if abs(y - (320 + OFF)) < 30 and x > 264 + OFF), key=lambda k: wps[k][0])
    f.write('WS      equ %d          ; first waypoint after the start line\n' % ws)
    f.write('PLAYERWP equ %d\n' % first_wp(start_x + 8, start_y + 8))
    for n, (x, y) in enumerate(cpu):
        f.write('CPU%dX   equ %d\nCPU%dY   equ %d\nCPU%dWP  equ %d\n' % (n, x, n, y, n, first_wp(x + 8, y + 8)))
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
with open(OUT, 'a') as f:
    f.write('\n; the mini-map: road edges at 1/8 scale from world (64,32), 7 bytes x 48 rows\nminimap:\n')
    for row in mm:
        f.write('        defb ' + ','.join('%%%s' % ''.join(str(v) for v in row[i:i + 8]) for i in range(0, MW, 8)) + '\n')
open(os.path.join(HERE, '..', 'build', 'minimap.txt'), 'w').write('\n'.join(''.join('#' if v else '.' for v in r) for r in mm) + '\n')

big = img.convert('L').point(lambda v: 0 if v else 255).resize((PW * 2, PH * 2), Image.NEAREST)
big.save(os.path.join(HERE, '..', 'build', 'world_preview.png'))
print('tiles:', len(order), ' road tiles:', surf.count(0))
