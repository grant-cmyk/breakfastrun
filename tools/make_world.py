"""Generate the scrolling world for stage 2: a top-down breakfast-table track
576 x 448 pixels, cut into 8x8 tiles. Writes src/world.asm.
  road        = blank table (white)
  road edges  = cereal O's
  off-road    = blank, with cereal hoops scattered on it
  start line  = a black-and-white checker band across the road
The scrolling window is ONE colour pair (a Spectrum can only colour 8x8 blocks,
which cannot follow a smooth pixel scroll), so everything here is ink on paper."""
import math, os, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
# WHICH TRACK (15 Nov 2026: one track a build - there is no room in memory for two).
#   TRACK=1 (or unset): track 1, exactly as before, into src/ (the files in the repository).
#   TRACK=2: THE BREAKFAST CLUB, its centre line from tools/make_track_designs.py. Give
#   WORLD_OUT=<folder> as well, so that track 1's files in src/ are left alone (build.sh does:
#   it builds a track other than 1 in a copy of src/ under build/).
TRACK = int(os.environ.get('TRACK') or 1)
SRC = os.environ.get('WORLD_OUT') or os.path.join(HERE, '..', 'src')       # where the .asm files go
BLD = os.environ.get('WORLD_OUT') or os.path.join(HERE, '..', 'build')     # ... and the previews
assert TRACK == 1 or os.environ.get('WORLD_OUT'), 'TRACK=%d needs WORLD_OUT=<folder>: src/ holds track 1' % TRACK
OUT = os.path.join(SRC, 'world.asm')
if TRACK != 1:                    # a later track's design (tools/make_track_designs.py): its centre line, its map's height
    sys.path.insert(0, HERE)
    import make_track_designs as _td
    _t = _td.TRACKS[TRACK - 1]
W, H = 72, (64 if TRACK == 1 else _t['H'])                     # tiles (64 rows: the bigger track, 10 Nov 2026) (a border wide enough that the
                                  # camera never has to stop at the world's edge)
PW, PH = W * 8, H * 8             # pixels
ROAD = 72                         # road width in pixels (48, 52, 56, 64, then 72 for the big cars - Grant, 10 Nov 2026)

# THE CORNER ARROWS' LOOK-AHEAD (the rest is further down: "THE CORNER ARROWS"). Change these to make the
# arrows show earlier, later, more or less often; the generator prints how many waypoints of the lap show one.
# How far ahead (all measured along the centre line, in pixels; top speed is 87.5 px a second):
A_LOOK   = 125     # a bend is announced when its turn-in is this near at most: with waypoints 32 to 41 px
                   # apart the arrow first shows 84 to 125 px before it - 1.0 to 1.4 s at top speed
A_SPAN   = 75      # the bend is judged by how far the road has turned this far after its turn-in
A_GENTLE = 22.5    # ... under this many degrees: nothing; up to A_SHARP: gentle; over: sharp
A_SHARP  = 67.5
A_LONG   = 200     # a straight this long (2.3 s flat out) is a "long straight"
A_EARLY  = 110     # ... announced when its start is this near at most (1.3 s) - unless a sharp corner still
A_ONTO   = 30      # lies before it - and until the car is this far along it
A_PASSED = 40      # the game counts a waypoint as passed 40 px before it (race_progress): a waypoint's
                   # byte is used from 40 px before the one before it

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
# a little bigger all round (Grant, 10 Nov 2026: a wider road, so a longer race): scaled
# about the start line, so the bottom straight, the line and the grid stay where they are
# Then bigger again (Grant, 10 Nov 2026: "the same design but wider road and longer route",
# for the 20 x 20 cars): 1.35 about the start line, and the whole world moved down DY so the
# top of the track fits (W stays 72 tiles - the game's surface and O maps assume it).
SCALE = 1.35
DY = 64
def tf(x, y): return 288 + (x - 288) * SCALE, 352 + (y - 352) * SCALE + DY
PATH = [tf(x, y) for x, y in PATH]
SY = 352 + DY                     # the bottom straight's middle: the start line and the grid
if TRACK != 1:                    # a later track: the centre line of its design (the start line is at x = 288 and
                                  # the grid behind it on a bottom straight, as on track 1)
    assert _t['W'] == W, 'the game\'s road-surface and O maps are 72 tiles wide'
    assert _t['lx'] == 256 + OFF or TRACK == 5
    PATH = list(_t['path']); SY = _t['sy']
LX = 256 + OFF if TRACK == 1 else _t['lx']      # the start line's x (track 5: 384 - its start straight begins further right)
BRIDGE = _t.get('bridge') if TRACK != 1 else None   # TRACK 5 only: the crossover (see the BRIDGE blocks below; nothing else changes for tracks 1-3)

def road_mask(width):
    im = Image.new('1', (PW, PH), 0)
    d = ImageDraw.Draw(im)
    pts = PATH + [PATH[0]]
    d.line(pts, fill=1, width=width, joint='curve')
    for x, y in pts:
        d.ellipse([x - width / 2, y - width / 2, x + width / 2, y + width / 2], fill=1)
    return im

road = road_mask(ROAD).load()
# THE MINI-MAP (Grant, 15 Nov 2026, of the sizes mocked up: "c (2)4 is good, and the inside parts could be blue - so
# no masking inside required"): 24 pixels wide, the road a SOLID ribbon about 3 pixels across, at 11/256 scale on
# every track (the taller track 3 is simply more lines). Ink only: the game ORs it over the scrolling picture each
# picture (map_blit, hud.asm), so the picture shows through everywhere that is not ribbon. Its columns 0-1 are
# empty: the gap from the window's edge. The game works a dot out as ((x + 8 - MMX0) * 11 / 256, (y + 8 - MMY0) * 11 / 256).
MW = 24; MSC = 11
_xs = [x for x in range(PW) if any(road[x, y] for y in range(0, PH, 4))]; _ys = [y for y in range(PH) if any(road[x, y] for x in range(0, PW, 4))]
MMX0 = min(_xs) - int(2.4 * 256 / MSC); MMY0 = min(_ys) - int(0.4 * 256 / MSC)   # the road's left edge on column 2, its top on line 0
def on_road(mx, my):
    x, y = MMX0 + int((mx * 256 + 128) / MSC), MMY0 + int((my * 256 + 128) / MSC)
    return 0 <= x < PW and 0 <= y < PH and road[x, y]
MH = max(my for my in range(64) if any(on_road(mx, my) for mx in range(MW))) + 1
mm = [[1 if on_road(mx, my) else 0 for mx in range(MW)] for my in range(MH)]
assert MH <= 30 and not any(on_road(MW, my) for my in range(MH)) and not any(r[0] or r[1] for r in mm), 'the mini-map does not fit %d x %d' % (MW, MH)
_thin = min(min(len(run) for run in ''.join(map(str, r)).split('0') if run) for r in mm)
assert _thin >= 2, 'the mini-map\'s ribbon is under 2 pixels somewhere'
print('mini-map: %d x %d at %d/256, from (%d, %d); the ribbon at least %d wide along a line' % (MW, MH, MSC, MMX0, MMY0, _thin))
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
if BRIDGE:                        # BRIDGE: no O stands on either road at the crossing, nor beside the bridge, its ramps or its concrete (as designed)
    _inner = road_mask(ROAD - 8).load()
    OS = [(ox, oy) for ox, oy in OS if not _inner[ox + 4, oy + 4]]
    _l, _r = _td.CON_BOX
    OS = [(ox, oy) for ox, oy in OS if not (-_l <= ox + 4 - BRIDGE['cross'][0] <= _r and BRIDGE['ramp_up'][0] - 4 <= oy + 4 <= BRIDGE['ramp_down'][1] + 4)]
    # ... but six go back where that left the road's edge bare (Grant, 16 Nov 2026: "the area on the inside track needs more boundary
    # circles"; tools/make_bridge_fix_mock.py found the places: gaps wider than track 1 has, clear of both roads, the wings and the walls)
    OS_ADDED = [(104, 280), (272, 368), (272, 296), (104, 256), (224, 440), (144, 440)]
    assert all(math.hypot(a - c, b - d) >= 15 for a, b in OS_ADDED for c, d in OS)
    OS += OS_ADDED
for ox, oy in OS:
    for j, r in enumerate(O_RING):
        for i, c in enumerate(r):
            if c == '#': px[ox + i, oy + j] = 1
if BRIDGE:                        # BRIDGE: its ink - look P4 (concrete wings, walls along the ramps, kerb walls in cyan only) with the
    # tunnel mouth dithered (D1). Plain tiles OR'd onto the cloth like the O's (no masks: the cloth's dots show through).
    _gw, _gi, _tw, _ti, _cells, _mb = _td.plan_parts(BRIDGE, os.environ.get('BRIDGE_LOOK', 'P4D1').replace('NONE', 'P4D1'))
    _xc, _yc = BRIDGE['cross']; _x0, _x1 = _xc - ROAD // 2, _xc + ROAD // 2
    # THE CONCRETE (Grant's own picture, 16 Nov 2026): each wing ("leg") and the wall along the ramps are ONE clean shape - an
    # outline round the outside of wall and wing together, nothing drawn where they join, and the cloth's dots wiped off inside
    # (BR_WIPE: masked tiles, as the breakfast things have). The tunnel mouths' dither stays (a cloth dot always falls on its ink).
    _m0, _m1 = _yc - ROAD // 2, _yc + ROAD // 2
    _mouth = {(x, y) for (x, y) in _tw if _m0 <= y < _m1}
    _conc = _gw | _tw
    _edge = {(x, y) for (x, y) in _conc - _mouth if ((x - 1, y) not in _conc and x < _xc) or ((x + 1, y) not in _conc and x > _xc)
             or ((x, y - 1) not in _conc) or ((x, y + 1) not in _conc)}
    _ink = _edge | {(x, y) for (x, y) in _ti if (x, y) in _mouth}
    BR_WIPE = set(_conc - _mouth)
    # THE KERB WALLS (his picture; K2 of the mock-up): one wall the whole way - a blue line down both sides, 8 x 8 blocks blue and
    # cyan in turn between them, the cyan ones clean paper (wiped). Cyan and blue only.
    # THE GAME DRAWS THEM ITSELF (kerb_draw, bridge.asm: two bytes a pixel line, against 48 full tiles of which 12 masked), so they
    # are NOT in the map's tiles - only the closing line across each kerb's foot is. KERB is the picture, for the tests and previews:
    # 0 clean paper, 1 ink, by (x, y).
    KERB = {}
    for xa in (_x0 - 8, _x1):
        for y in range(BRIDGE['ramp_up'][0], BRIDGE['ramp_down'][1]):
            blue = ((y - BRIDGE['ramp_up'][0]) // 8) % 2 == 0
            for i in range(8): KERB[(xa + i, y)] = int(blue or i in (0, 7))
        for i in range(8): _ink.add((xa + i, BRIDGE['ramp_down'][1] - 1)); KERB[(xa + i, BRIDGE['ramp_down'][1] - 1)] = 1
    if os.environ.get('KERB_TILES'):   # (to compare: the kerbs as map tiles, the way they were first built)
        _ink |= {q for q, v in KERB.items() if v}; BR_WIPE |= {q for q, v in KERB.items() if not v}
    for a_, z_ in (BRIDGE['ramp_up'], BRIDGE['ramp_down']):
        for y0 in range(a_ + 2, z_, int(os.environ.get('BR_CHEV', 16))):
            for k in range(12):
                for yy in (y0 + 11 - k, y0 + 10 - k): _ink.add((_xc - 1 - k, yy)); _ink.add((_xc + k, yy))
    for (x, y) in (_ink if os.environ.get('BRIDGE_LOOK') != 'NONE' else ()): px[x, y] = 1
# the starting grid (Grant, 10 Nov 2026): the classic stagger, two lanes - P1
# on the inside (the upper lane: the first bend is a left-hander), P2 beside it
# and 16 px back, P3 behind P1, and so on. Top-left of each car, facing right.
LANE_A, LANE_B = SY - 14 - 8, SY + 14 - 8        # lane centres 14 px either side of the middle (11 for 16 x 16 cars)
GRID = [(LX - 40, LANE_A), (LX - 56, LANE_B), (LX - 72, LANE_A), (LX - 88, LANE_B), (LX - 104, LANE_A)]   # x on the 8-px tile grid: the boxes share tiles
GRID_ORDER = [0, 1, 4, 3, 2]                     # car in each place: YOU, CYAN, WHITE, PINK, GREEN
for gx, gy in GRID:                              # a grid box behind each: [ shape, 1 px lines
    for y in range(gy - 1, gy + 17):
        if road[gx - 3, y]: px[gx - 3, y] = 1
    for x in range(gx - 3, gx + 4):
        for y in (gy - 1, gy + 16):
            if road[x, y]: px[x, y] = 1
# start line: checker band 8px tall across the bottom straight at x=256..263
for y in range(SY - 60, SY + 60):
    for x in range(LX, LX + 8):
        if BRIDGE and (x // 8 * 8, y // 8 * 8) in OS: continue      # (BRIDGE: an O's tile holds the O alone - the game knows an O by its tile)
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
# (14 Nov 2026: with OBJECTS=1 the blue things give their memory to the coloured objects - there
# is no room for both. KEEP_OLD says how many of them stay.)
all_old = [('plate', 32, 24), ('knife', 39, 24), ('fork', 30, 24), ('spoon', 41, 24),
          ('egg', 24, 21), ('toast', 25, 31), ('juice', 44, 32), ('bacon', 34, 33),
          ('juice', 3, 3), ('toast', 60, 3), ('egg', 63, 47), ('bacon', 3, 50), ('plate', 61, 22),
          ('egg', 2, 24), ('toast', 30, 1), ('fork', 66, 36), ('knife', 68, 36), ('juice', 45, 50),
          ('bacon', 14, 2), ('egg', 24, 49)]
KEEP_OLD = int(os.environ.get('KEEP_OLD', 0 if os.environ.get('OBJECTS') else 99))
wanted = all_old[:KEEP_OLD]
# TRACK 2's things, in TILES as they stand (not spread by tf). The rows of road are 3 to 5 tiles apart,
# so nothing fits between them: the plate is inside the top right-hand loop, an egg in the pocket left
# of the dip and one in the dip's mouth, the fork and knife down the strip inside the left-hand
# straight, eggs and toast in the corners and on the right-hand edge.
# MEMORY decides how many: this track has 48 more cereal O's (96 bytes of row lists) and 15 more
# waypoints (60 bytes) than track 1, and the program has 5 bytes free. So ten things of four kinds - a
# second or third egg costs 18 bytes where a new kind costs 50 to 90: the juice, the bacon and the spoon
# of track 1 are left out. (All twelve: 198 bytes over in the program and 34 at TOPMEM.)
T2_THINGS = [('plate', 48, 15), ('egg', 16, 16), ('egg', 34, 1), ('egg', 2, 58), ('egg', 66, 2), ('toast', 67, 32),
             ('toast', 2, 2), ('toast', 65, 59), ('fork', 15, 22), ('knife', 15, 42)]
if os.environ.get('T2_THINGS'): T2_THINGS = [(n, int(x), int(y)) for n, x, y in (w.split(':') for w in os.environ['T2_THINGS'].split(','))]   # (to try a layout: name:x:y,...)
# TRACK 3, BREAKFAST OF CHAMPIONS (72 x 84): the 20 more rows of map cost 400 bytes (the road, the O's and the
# index, 20 bytes a row), its 79 more O's 158 and its waypoints 60 - so there is room for five small things only.
T3_THINGS = [('egg', 3, 25), ('egg', 67, 2), ('egg', 11, 80), ('toast', 21, 38), ('toast', 54, 62)]
if TRACK == 2: wanted = T2_THINGS[:KEEP_OLD]
if TRACK == 3: wanted = (T2_THINGS if os.environ.get('T2_THINGS') else T3_THINGS)[:KEEP_OLD]
if TRACK == 5: wanted = []        # BRIDGE: no breakfast things on this track - their memory is the bridge's
assert TRACK in (1, 2, 3, 5), 'tracks 1, 2, 3 and 5 only (4 does not fit in memory)'
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
# ---- the COLOURED objects (Grant, 14 Nov 2026: "build the objects"; tools/make_fryup.py draws
#      them, with the colour rules of tools/make_colour_objects.py). Their pixels are map tiles
#      like everything else; their colours are regions the game paints into the attribute cells
#      each picture (src/objects.asm, obj_paint in racer.asm): for each colour, the span of
#      its ink on every pixel row. They stand OFF the road ("these shapes should not spill
#      into the road area"), on whole tiles, clear of the O's and the other things. ----
sys.path.insert(0, HERE)
import make_fryup as mf
CYAN_INK = lambda c: 0x28 + c                                   # paper cyan, this ink
def jam_tart():
    o = mf.mc.Obj('Jam tart, 32 x 32, red', 32, 32); o.panel(8, 8, 24, 24, mf.mc.RED)
    for (x, y) in ((11, 11), (19, 12), (14, 16), (20, 19), (11, 20), (16, 21)): o.ink(mf.mc.pic(["X"]), x, y)   # pips in the jam
    return o
_by = {o.name.split(',')[0]: o for o in mf.mc.OBJECTS}
SMALL = {'sugar': _by['Sugar cubes'], 'toast': _by['Slice of toast'], 'tart': jam_tart()}
# SMALL objects only (Grant, 14 Nov 2026, "build the objects", after the mug measured 5 TV frames a
# picture): square, blue-edged, 4 or 5 tiles a side, so one in view costs a few per cent of a
# picture. (object, wanted tile x, y) - each goes to the nearest free place off the road.
WANT = os.environ.get('OBJECT_LIST', 'sugar:47:39,toast:57:27,tart:60:6,sugar:36:3,toast:14:28,tart:22:56,sugar:8:8,toast:40:57')
COLOURED = [(SMALL[n], int(x), int(y)) for n, x, y in (w.split(':') for w in WANT.split(','))] if os.environ.get('OBJECTS') else []   # off unless OBJECTS=1
extra_mask = []; regions = []; boxes = []
for o, wtx, wty in COLOURED:
    w, h = (o.w + 7) // 8, (o.h + 7) // 8; best = None
    for dy in range(-6, 7):
        for dx in range(-6, 7):
            if free(wtx + dx, wty + dy, w, h) and (best is None or abs(dx) + abs(dy) < best[0]): best = (abs(dx) + abs(dy), wtx + dx, wty + dy)
    if not best:
        print('no room near there; places with room:', [(x, y) for y in range(0, H - h, 2) for x in range(0, W - w, 2) if free(x, y, w, h)])
    assert best, 'no room for ' + o.name
    _, tx, ty = best
    for j in range(h + 1):
        for i in range(w + 1): taken.add((tx + i, ty + j))
    for y in range(o.h):
        for x in range(o.w):
            if o.shape[y, x] or o.wipe[y, x]: extra_mask.append((tx * 8 + x, ty * 8 + y))
            if o.shape[y, x] and o.bits[y, x]: px[tx * 8 + x, ty * 8 + y] = 1; ipx[tx * 8 + x, ty * 8 + y] = 1
    def region(m, attr):
        ys = [y for y in range(o.h) if m[y].any()]
        spans = [((int(m[y].nonzero()[0][0]), int(m[y].nonzero()[0][-1])) if m[y].any() else (255, 0)) for y in range(ys[0], ys[-1] + 1)]
        regions.append((o.name, tx * 8, ty * 8 + ys[0], attr, spans)); boxes.append((tx * 8, ty * 8, o.w, o.h))
    for col in sorted(set(o.ink2[(o.bits == 1) & (o.label == 0)].tolist())):     # ink in a colour of its own, on the cloth's cyan
        if col: region((o.ink2 == col) & (o.bits == 1) & (o.label == 0), CYAN_INK(col - 1))
    for lab in sorted(set(o.label[o.label > 0].tolist())):      # a coloured inside (its paper): with the ink that is on or round it
        m = o.label == lab
        ys_, xs_ = m.nonzero()                                  # the game colours a RECTANGLE: the inside's bounding box. A cell that
        m = m.copy(); m[ys_.min():ys_.max() + 1, xs_.min():xs_.max() + 1] = True   # holds any of it reaches at most 7 pixels beyond - still inside the 8-pixel edge
        near = o.ink2[(mf.mc.grow(m.astype('uint8')) == 1) & (o.bits == 1)]
        region(m, (lab - 1) * 8 + (int(near.max()) - 1 if near.size and near.max() else 1))
    print('coloured: %s at pixel %d, %d' % (o.name, tx * 8, ty * 8))
def runs8(spans):
    """For j = -7 .. rows - 1: the first and last ink pixel over rows j .. j + 7 (what a colour
    cell covers when its top line is row j) - the game looks one of these up for each cell row."""
    out = []
    for j in range(-7, len(spans)):
        got = [sp for sp in spans[max(0, j):j + 8] if sp[0] != 255]
        out.append((min(a for a, b in got), max(b for a, b in got)) if got else (255, 0))
    return out
with open(os.path.join(SRC, 'objects.asm'), 'w') as g:
    g.write('; GENERATED by tools/make_world.py - the coloured objects\' colours. A block (8 bytes): the\n; world x, y of its first row, the attribute, its height - 1, its first and last pixel from\n; x. The list ends with 0xFFFF. (Rectangles only: an object with a shaped inside - the mug,\n; an egg - needs a span for each row, which obj_paint had once: see the git history.)\nobj_tab:\n')
    for name, x, y, attr, spans in regions:
        assert len(set(spans)) == 1 and len(spans) <= 256, name + ': its coloured inside is not a rectangle'
        g.write('        dw %d,%d                ; %s\n        db 0x%02X,%d,%d,%d\n' % (x, y, name, attr, len(spans) - 1, spans[0][0], spans[0][1]))
    g.write('        dw 0xFFFF\n')
import json; json.dump([dict(name=n, x=x, y=y, attr=a_, rows=sp, box=bx) for (n, x, y, a_, sp), bx in zip(regions, boxes)], open(os.path.join(BLD, 'objects_rows.json'), 'w'))   # (each row's own span: for tests/objects_test.py)
placed = []
for name, tx, ty in wanted:
    shape = I[name]
    if TRACK == 1: tx, ty = (int(round(v / 8)) for v in tf(tx * 8, ty * 8))   # (spread with the track)
    w, h = len(shape[0]) // 8, len(shape) // 8
    best = None
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            if free(tx + dx, ty + dy, w, h):
                k = (dark_tiles(shape, tx + dx, ty + dy), abs(dx) + abs(dy))
                if best is None or k < best[0]: best = (k, tx + dx, ty + dy)
    if best:
        place(shape, best[1], best[2]); placed.append(name)
        if TRACK != 1: print('  %s at tile %d, %d (asked %d, %d)' % (name, best[1], best[2], tx, ty))
    else: assert TRACK == 1, 'no room for the %s near tile %d, %d' % (name, tx, ty)
print('placed:', ' '.join(placed)); print('cereal Os:', len(OS))

# the NOS canisters (Grant, 10 Nov 2026): A just behind the grid, B in the middle of
# the top area (the bottom of the dip). On plain road tiles, as two masked tiles each
# (it sits on the cloth like the breakfast things); the game shows one at a time by
# setting their tiles in the row lists (NOS_*_T*) to their numbers or to 0.
import re as _re
_fa = open(os.path.join(HERE, 'face_art.txt')).read()
_nos = _re.search(r'== NOS face ==\n((?:[X.]{16}\n){16})', _fa).group(1).split()
_ys = [y for y in range(16) if 'X' in _nos[y]]
NOS_ART = [_nos[y][4:12] for y in _ys]                # 8 wide x 12 tall
def _can(cx, cy):                                     # centre -> tile x, tile y, row offset
    top = int(round(cy)) - 6
    ty, dy = top // 8, top % 8
    if dy > 4: dy = 4                                  # (12 rows in 2 tiles)
    return int(cx - 4) // 8, ty, dy
_dip = [p for p in PATH if p[1] > PATH[0][1] - 200]    # B: the bottom of the dip in the top area
_tops = sorted(PATH, key=lambda p: p[1])[:0]
_d = [p for i, p in enumerate(PATH) if 0 < i < len(PATH) - 1 and p[1] > PATH[i - 1][1] - 1e-6 and p[1] > 200 - 999]
_mid = [p for p in PATH if abs(p[0] - 288) < 80 and p[1] < SY - 100]
_bx = sum(p[0] for p in _mid) / len(_mid); _by = max(p[1] for p in _mid)
CANS = {'A': _can(156, SY), 'B': _can(_bx, _by)}      # A just behind the grid
# C: the OIL CAN (Grant, 14 Nov 2026: health for a damaged car) - on the left-hand straight, half-way up
OIL_ART = ['........', '..XXX...', '.X...XX.', 'XXXXXXXX', 'X......X', 'X.XXXX.X', 'X.X..X.X', 'X.XXXX.X', 'X......X', 'X......X', 'XXXXXXXX', '........']
_left = min(PATH, key=lambda p: (abs(p[1] - (SY - 170)), p[0]))
CANS['C'] = _can(min(p[0] for p in PATH if abs(p[1] - _left[1]) < 20), _left[1])
if TRACK == 2:
    # THE BREAKFAST CLUB: A just behind the grid as on track 1; B half a lap on, in the middle of the
    # third row (the cars come along it flat out); C, the oil can, half-way up the left-hand straight
    CANS = {'A': _can(156, SY), 'B': _can(330, 220), 'C': _can(68, 254)}
if TRACK == 3:
    # BREAKFAST OF CHAMPIONS: A behind the grid; B at the foot of the fold in the middle (half a lap on);
    # C, the oil can, on the long straight down the left-hand side
    CANS = {'A': _can(156, SY), 'B': _can(288, 490), 'C': _can(116, 190)}
if TRACK == 5:
    # A FRIDGE TOO FAR: A behind the grid; B on the top lane (half a lap on); C, the oil can, on the left-hand straight
    # (16 Nov 2026: A and B moved a few pixels onto WHITE squares of the cloth, as C was - a can on a dotted square needs masked tiles,
    # and this track's masks are the bridge's concrete now)
    CANS = {'A': _can(LX - 132, SY - 14), 'B': _can(276, 72), 'C': _can(68, 200)}
for k, (tx, ty, dy) in CANS.items():
    for y, row in enumerate(OIL_ART if k == 'C' else NOS_ART):
        for x, c in enumerate(row):
            if c == 'X': px[tx * 8 + x, ty * 8 + dy + y] = 1; ipx[tx * 8 + x, ty * 8 + dy + y] = 1
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
if BRIDGE and not os.environ.get('BR_NOWIPE'): extra_mask += sorted(BR_WIPE)                    # (BRIDGE: the concrete and the kerbs' cyan blocks are clean)
for (x, y) in extra_mask: imask[y, x] = True                # (a coloured object hides the cloth under all of it, margin too)
# cut into tiles: plain ones first (ink only, OR'd onto the cloth), then the
# masked ones (from TM_FIRST), each with an index into the de-duplicated masks
def tbytes(get, tx, ty):
    return bytes(sum((int(get(tx * 8 + i, ty * 8 + j)) << (7 - i)) for i in range(8)) for j in range(8))
yy, xx = np.mgrid[0:PH, 0:PW]                         # the cloth's dithered pixels
cloth_on = ((((xx >> 5) + (yy >> 5)) & 1) == 1) & ((yy & 1) == 0) & ((xx & 3) == (yy & 2))   # 1 in 8, staggered
cells = {}
_inkb = np.array(img, dtype=bool)
for ty in range(H):
    for tx in range(W):
        ink = tbytes(lambda x, y: px[x, y], tx, ty)
        sl = (slice(ty * 8, ty * 8 + 8), slice(tx * 8, tx * 8 + 8))
        if BRIDGE:                             # BRIDGE: a mask holds only the cloth dots it has to hide (not those under ink, nor pixels where the
            _need = imask[sl] & cloth_on[sl] & ~_inkb[sl]   # cloth has no dot) - the same picture on the screen, and far fewer different masks
            msk = bytes(np.packbits(_need, axis=1).ravel().tolist()) if _need.any() else bytes(8)
        elif (imask[sl] & cloth_on[sl]).any():   # the mask hides some cloth: needed
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
TOPDATA = os.path.join(SRC, 'topdata.asm')
with open(TOPDATA, 'w') as f:
    f.write('; GENERATED by tools/make_world.py - do not edit by hand\n')
    f.write('; data kept at the top of memory (see TOPMEM): the masks, the mini-map\n')
    f.write('; the breakfast things\' masks\n')
    f.write('; for each masked tile (number - TM_FIRST): which mask\ntmask_idx_src:\n')
    for i in range(0, len(midx), 16):
        f.write('        defb ' + ','.join(str(v) for v in midx[i:i + 16]) + '\n')
    f.write('; the masks, 8 bytes each (1 = covers the cloth)\ntmask_src:\n')
    for m in umasks:
        if BRIDGE:                # BRIDGE: 4 bytes a mask - the cloth has dots on a tile's lines 0, 2, 4 and 6 only (tdraw_mb reads them so)
            assert not any(m[1::2]); m = m[0::2]
        f.write('        defb ' + ','.join('0x%02X' % b for b in m) + '\n')
assert len(order) <= 256, 'too many tiles: %d' % len(order)

# start: on the bottom straight, left of the line, facing right (angle 16 of 64)
start_x, start_y = GRID[0]                       # you: on pole
with open(OUT, 'w') as f:
    f.write('; GENERATED by tools/make_world.py - do not edit by hand\n')
    f.write('; world %d x %d tiles (%d x %d pixels), %d different tiles\n\n' % (W, H, PW, PH, len(order)))
    f.write('MAPW    equ %d\nMAPH    equ %d\nSTARTX  equ %d\nSTARTY  equ %d\nSTARTA  equ 16\n' % (W, H, start_x, start_y))
    f.write('TRACK_SY equ %d     ; the bottom straight\'s middle (the tests drive there)\n' % SY)
    f.write('TM_FIRST equ %d      ; tiles from here on are masked (the breakfast things)\n\n' % TM_FIRST)
    if BRIDGE:                    # BRIDGE: this track keeps no O map - the game finds the O's in the row lists (o_at, bridge.asm), by their tile number
        _o = bytes(sum((c == '#') << (7 - i) for i, c in enumerate(r)) for r in O_RING)
        assert all(cells[(ox // 8, oy // 8)] == (_o, bytes(8)) for ox, oy in OS), 'an O shares its tile with something else: %r' % [(ox, oy) for ox, oy in OS if cells[(ox // 8, oy // 8)] != (_o, bytes(8))]
        assert sum(1 for v in cells.values() if v == (_o, bytes(8))) == len(OS)
        f.write('O_TILE  equ %d      ; the cereal O\'s tile\n' % num[(_o, bytes(8))])
        (u0, u1), (d0, d1), (r0, r1) = BRIDGE['ramp_up'], BRIDGE['deck'], BRIDGE['ramp_down']; _xc, _yc = BRIDGE['cross']
        f.write('; the bridge (bridge.asm): the upper road x BR_X0..BR_X1, from the foot of one ramp BR_Y0 to the other\'s BR_Y3 (the level deck\n; BR_Y1..BR_Y2); the lower road goes under at y BR_M0..BR_M1 and is covered from x BR_H0 to BR_H1\n')
        f.write('BR_X0   equ %d\nBR_X1   equ %d\nBR_Y0   equ %d\nBR_Y1   equ %d\nBR_Y2   equ %d\nBR_Y3   equ %d\nBR_M0   equ %d\nBR_M1   equ %d\nBR_H0   equ %d\nBR_H1   equ %d\n'
                % (_xc - ROAD // 2, _xc + ROAD // 2, u0, d0, d1, r1, _yc - ROAD // 2, _yc + ROAD // 2, BRIDGE['hidden'][1], BRIDGE['hidden'][0]))
    f.write('; tile pictures, 8 bytes each (tile 0 = blank). Page aligned so a\n; tile never crosses a 256-byte page.\n        defs (256 - ($ & 255)) & 255\ntiles:\n')
    for i, t in enumerate(order):
        f.write('        defb ' + ','.join('0x%02X' % b for b in t) + '   ; %d\n' % i)
    # the map, stored as a LIST of the non-blank tiles in each row: most of the
    # table is blank, and the renderer then only looks at tiles it must draw
    nosq = []
    # rows up to TOP_ROWS bytes go to the top of memory (topdata.asm; Grant's sweep: the
    # mini-map's 336 bytes freed there), the rest stay here; the index points at both
    TOP_ROWS = 320
    if TRACK == 3: TOP_ROWS = 388        # (its things have fewer masks up there: 68 bytes more of the rows fit, and the program needs them)
    if TRACK == 5: TOP_ROWS = 366        # (BRIDGE: the concrete's masks are up there too)
    TOP_ROWS = int(os.environ.get('TOP_ROWS') or TOP_ROWS)   # (tools/make_multi.py: the same room up there for every track of one load)
    top_used, where = 0, {}
    toprows = open(os.path.join(SRC, 'toprows.asm'), 'w')
    toprows.write('; GENERATED by tools/make_world.py - map rows kept at the top of memory\n')
    # ... and rows go where there is room outside the program (15 Nov 2026), in src/hirows.asm: in the back
    # buffer's unused bottom-row strips (90 bytes on page D1, 32 on D2: racer.asm, STRIP1-2), in the 54 bytes of the title's unused a_sav (STRIP3) - D1
    # holds the corner arrows' table first (a byte a waypoint) - and in the 49 bytes above the screen-copy routine.
    NWP_ = min(round(sum(math.dist(p, q) for p, q in zip(PATH, PATH[1:] + PATH[:1])) / 32), 61)
    BINS = [['s1', 90 - NWP_, 0, ' - s1_src + STRIP1', []], ['hi', 49, 0, ' - hi_src + HIMEM', []], ['s2', 32, 0, ' - s2_src + STRIP2', []], ['s3', 54, 0, ' - s3_src + STRIP3', []]]
    if BRIDGE: BINS.append(['tk', int(os.environ.get('BR_TK', 90)), 0, ' - tk_src + BR_ROW2', []])    # BRIDGE: bytes at the bottom of the stack's page (bridge.asm)
    for ty in range(H):
        ent = [(tx, mapb[ty * W + tx]) for tx in range(W) if mapb[ty * W + tx]]
        line = 'row_%d:  defb %d' % (ty, len(ent)) + ''.join(',%d,%d' % e for e in ent) + '\n'
        n = 1 + 2 * len(ent)
        if top_used + n <= TOP_ROWS:
            toprows.write(line); top_used += n; where[ty] = ' - high_src + TOPMEM'
        elif any(bn[2] + n <= bn[1] for bn in BINS):
            bn = next(bn for bn in BINS if bn[2] + n <= bn[1]); bn[4].append(line); bn[2] += n; where[ty] = bn[3]
        else:
            f.write(line); where[ty] = ''
        for k, (ctx, cty, dy) in CANS.items():
            for j in (0, 1):
                if ty == cty + j:
                    i = [e[0] for e in ent].index(ctx)
                    nosq.append('NOS_%s_T%d equ row_%d%s + %d   ; its tile in the list\nNOS_%s_V%d equ %d\n'
                                % (k, j, ty, where[ty], 2 + 2 * i, k, j, ent[i][1]))
    toprows.close()
    with open(os.path.join(SRC, 'hirows.asm'), 'w') as hirows:
        hirows.write('; GENERATED by tools/make_world.py - map rows kept outside the program: after the arrows\' table on strip 1, above\n; the screen-copy routine (HIMEM), and on strips 2 and 3 of the back buffer\'s unused bottom rows - racer.asm, start_once\n')
        for bn in BINS: hirows.write(''.join(bn[4]) + {'s1': 's1_end:\nhi_src:\n', 'hi': 'hi_end:\ns2_src:\n', 's2': 's2_end:\ns3_src:\n', 's3': 's3_end:\n' + ('tk_src:\n' if BRIDGE else ''), 'tk': 'tk_end:\n'}[bn[0]])
    print('row lists: %d bytes at TOPMEM, %s outside the program' % (top_used, ' + '.join(str(bn[2]) for bn in BINS)))
    # (the index of the row lists is kept in the buffer's bottom rows: src/rowidx.asm)
    with open(os.path.join(SRC, 'rowidx.asm'), 'w') as g:
        g.write('; GENERATED by tools/make_world.py - do not edit by hand\n')
        g.write('; the map: for each of the %d tile rows, a pointer to its list\nrow_index_src:\n' % H)
        for ty in range(H):
            g.write('        dw row_%d%s\n' % (ty, where[ty]))
    f.write('; each list: how many tiles, then (column, tile number) pairs, left to right\n')
    f.write('\n; the NOS canisters: where their tiles sit in the row lists, and their numbers\n' + ''.join(nosq))
    for k, (ctx, cty, dy) in CANS.items():
        f.write('NOS_%s_X equ %d\nNOS_%s_Y equ %d   ; its centre\n' % (k, ctx * 8 + 4, k, cty * 8 + dy + 6))
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
# The game keeps a car's progress, laps * NWP + waypoints passed, in ONE BYTE, with 246 to 249 kept for
# the cars that have finished (progress, racer.asm), and a waypoint's place in the table as number * 4 in
# a byte (wp_delta). So over 3 laps at most 61 waypoints: a longer track has them a little further apart
# (track 2: 61, one every 34.8 px, for 66 at 32 px). Track 1 has 46.
NWP = min(NWP, 61)
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
cpu = [GRID[1], GRID[4], GRID[3], GRID[2]]       # CYAN P2, GREEN P5, PINK P4, WHITE P3
def first_wp(cx, cy):
    ahead = [k for k, (x, y) in enumerate(wps) if abs(y - cy) < 30 and x > cx + 16]
    return min(ahead, key=lambda k: wps[k][0] - cx)
WPOUT = os.path.join(SRC, 'waypoints.asm')
with open(OUT, 'a') as f:
    f.write('\n; (the waypoints are in waypoints.asm, placed where they fill an alignment gap)\n')
with open(WPOUT, 'w') as f:
    f.write('; GENERATED by tools/make_world.py - do not edit by hand\n')
    f.write('\n; waypoints for the computer cars: centre line, racing order (x, y)\n')
    f.write('NWP     equ %d\n' % NWP)
    if BRIDGE:                    # BRIDGE: the waypoints a car heads for while it is on the bridge (bridge.asm: a computer car beside it, heading for one, is put on)
        _up = [k for k, (x, y) in enumerate(wps) if x == BRIDGE['cross'][0] and BRIDGE['ramp_up'][0] < y <= BRIDGE['ramp_down'][1] + 8]
        assert _up == list(range(_up[0], _up[0] + len(_up)))
        f.write('WP_UP0  equ %d\nWP_UPN  equ %d\n' % (_up[0], len(_up)))
    # the first waypoint past the start line (lap counting) and your first target
    ws = min((k for k, (x, y) in enumerate(wps) if abs(y - SY) < 30 and x > LX + 8), key=lambda k: wps[k][0])
    f.write('WS      equ %d          ; first waypoint after the start line\n' % ws)
    f.write('PLAYERWP equ %d\n' % first_wp(start_x + 8, start_y + 8))
    for n, (x, y) in enumerate(cpu):
        f.write('CPU%dX   equ %d\nCPU%dY   equ %d\nCPU%dWP  equ %d\n' % (n, x, n, y, n, first_wp(x + 8, y + 8)))
with open(WPOUT, 'a') as f:
    f.write('waypoints:\n')
    for x, y in wps:
        f.write('        dw %d,%d\n' % (x, y))
print('waypoints:', NWP)

# ---------------------------------------------------------------------------------------------
# THE CORNER ARROWS (Grant, 15 Nov 2026: "a couple of rows in front of my car, a flashing arrow
# pointing either diagonally right or sharp right to indicate turns. A long straight stretch gets an
# early flashing straight in the direction of the straight"). One byte a waypoint, read by the game for
# the waypoint YOUR car is heading for (arrow_draw, racer.asm): 0 = no arrow, else kind * 8 + direction.
#   direction 0-7: where the arrow points on the screen, 0 = up, clockwise in eighths of a turn
#   kind      1 a long straight is coming: the arrow lies along it
#             2, 3 a gentle bend to the left, to the right: the arrow is 45 degrees off the road's line
#             4, 5 a sharp corner to the left, to the right: 90 degrees off it
_N = int(round(total)); _st = total / _N
def _pt(d):
    d %= total; i = 0
    while d > seglen[i] and i < len(seglen) - 1: d -= seglen[i]; i += 1
    (x0, y0), (x1, y1) = loop[i], loop[i + 1]; t = d / seglen[i]
    return x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
_P = [_pt(i * _st) for i in range(_N)]
def _head(i):                        # the road's line at point i: degrees clockwise from up the screen
    (ax, ay), (bx, by) = _P[(i - 6) % _N], _P[(i + 6) % _N]
    return math.degrees(math.atan2(bx - ax, -(by - ay)))
_H = [_head(i) for i in range(_N)]
def _wrap(a): return (a + 180) % 360 - 180
_stra = [abs(_wrap(_H[(i + 8) % _N] - _H[(i - 8) % _N])) < 2.0 for i in range(_N)]     # on a straight
_runs = []                           # the long straights: (first point, points, direction)
_i0 = next(i for i in range(_N) if not _stra[i])
i = 0
while i < _N:
    j = (_i0 + i) % _N
    if _stra[j]:
        n = 0
        while n < _N and _stra[(j + n) % _N]: n += 1
        if (n + 16) * _st >= A_LONG: _runs.append((j, n, _H[(j + n // 2) % _N]))      # (+ 16: the test above trims 8 px off each end)
        i += n
    else: i += 1
A_NAMES = ['none', 'straight', 'gentle left', 'gentle right', 'sharp left', 'sharp right']
def arrow_at(k):                      # where the car typically is while waypoint k's byte is used: a point of _P
    sp = total / NWP
    return int(round(((k - 1) * sp - A_PASSED + sp / 2) / _st)) % _N
def arrow_code(k):
    sp = total / NWP
    c = arrow_at(k)
    hc = _H[c]; kind = 0; turn = 0
    for d in range(int((A_LOOK - sp / 2) / _st) + 1):                      # the next bend: its turn-in
        dev = _wrap(_H[(c + d) % _N] - hc)
        if abs(dev) > 10:
            sg = 1 if dev > 0 else -1
            mag = max(sg * _wrap(_H[(c + d + e) % _N] - hc) for e in range(int(A_SPAN / _st) + 1))
            if mag >= A_SHARP: kind = 4 + (sg > 0); turn = 2 * sg
            elif mag >= A_GENTLE: kind = 2 + (sg > 0); turn = sg
            break
    direction = (int(round(hc / 45.0)) + turn) % 8
    if kind < 4:
        for j, n, hd in _runs:                                             # a long straight about to start, or just begun
            ahead = ((j - c + _N // 2) % _N - _N // 2) * _st
            if -A_ONTO <= ahead <= A_EARLY: kind = 1; direction = int(round(hd / 45.0)) % 8
    return kind * 8 + direction if kind else 0
ACODES = [arrow_code(k) for k in range(NWP)]
with open(os.path.join(SRC, 'arrowtab.asm'), 'w') as f:
    f.write('; GENERATED by tools/make_world.py - the corner arrows: a byte a waypoint (the one your car is heading\n')
    f.write('; for): 0 none, else kind * 8 + direction - kind 1 straight, 2/3 gentle left/right, 4/5 sharp left/right;\n')
    f.write('; direction 0-7, 0 = up the screen, clockwise. Look-ahead: bend %d px, straight %d px (%d px long or more).\n' % (A_LOOK, A_EARLY, A_LONG))
    f.write('arrow_tab_src:\n')
    for k, v in enumerate(ACODES):
        f.write('        defb %d   ; %d: %s%s\n' % (v, k, A_NAMES[v >> 3], (', pointing ' + ['up', 'up-right', 'right', 'down-right', 'down', 'down-left', 'left', 'up-left'][v & 7]) if v else ''))
print('arrows:', ' '.join('%d:%s' % (k, ['-', 'St', 'gL', 'gR', 'SL', 'SR'][v >> 3]) for k, v in enumerate(ACODES) if v))
if True:                              # a picture of them, for checking: build/arrows_preview.png (or WORLD_OUT)
    _im = img.convert('L').point(lambda v: 150 if v else 255).convert('RGB'); _d = ImageDraw.Draw(_im)
    _col = [(0, 0, 0), (0, 160, 0), (230, 140, 0), (230, 140, 0), (220, 0, 0), (220, 0, 0)]
    for k, ((wx, wy), v) in enumerate(zip(wps, ACODES)):     # (drawn where the car is when it sees it, not at the waypoint)
        _d.ellipse([wx - 3, wy - 3, wx + 3, wy + 3], outline=(120, 120, 255))
        x, y = _P[arrow_at(k)]
        _d.text((x + 5, y - 12), str(k), fill=(0, 0, 200))
        if v:
            a = math.radians((v & 7) * 45); dx, dy = math.sin(a), -math.cos(a)
            _d.line([x - 9 * dx, y - 9 * dy, x + 9 * dx, y + 9 * dy], fill=_col[v >> 3], width=3)
            _d.ellipse([x + 9 * dx - 3, y + 9 * dy - 3, x + 9 * dx + 3, y + 9 * dy + 3], fill=_col[v >> 3])
    _im.resize((PW * 2, PH * 2), Image.NEAREST).save(os.path.join(BLD, 'arrows_preview.png'))

obits = [[0] * W for _ in range(H)]                # where the cereal O's are: cars bounce off them
for ox, oy in OS: obits[oy // 8][ox // 8] = 1
with open(os.path.join(SRC, 'omap.asm'), 'w') as f:   # (in the program: see racer.asm)
    f.write('\n; the cereal O\'s: one BIT per tile (1 = an O: solid - cars bounce off it),\n')
    f.write('; %d bytes a row, leftmost tile in the top bit\nomap_src:\n' % (W // 8))
    for r in obits:
        f.write('        defb ' + ','.join('%%%s' % ''.join(str(b) for b in r[i:i + 8]) for i in range(0, W, 8)) + '\n')
with open(os.path.join(SRC, 'minimap.asm'), 'w') as f:   # (start-up area: start_once copies it to MAPDAT)
    f.write('; GENERATED by tools/make_world.py - the mini-map, ORed over the window\'s bottom left corner each picture\n')
    f.write('MMX0    equ %d\nMMY0    equ %d   ; the mini-map: world (x, y) -> ((x - MMX0) * %d / 256, ...)\nMAP_H   equ %d\n' % (MMX0, MMY0, MSC, MH))
    f.write('; %d lines of 3 bytes of ink: the road as a solid ribbon\nminimap_src:\n' % MH)
    for row in mm:
        f.write('        defb ' + ','.join('%%%s' % ''.join(str(v) for v in row[i:i + 8]) for i in range(0, MW, 8)) + '\n')
open(os.path.join(BLD, 'minimap.txt'), 'w').write('\n'.join(''.join('#' if v else '.' for v in r) for r in mm) + '\n')

big = img.convert('L').point(lambda v: 0 if v else 255).resize((PW * 2, PH * 2), Image.NEAREST)
big.save(os.path.join(BLD, 'world_preview.png'))
print('tiles:', len(order), ' road tiles:', surf.count(0))
