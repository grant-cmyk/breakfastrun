"""Track DESIGNS for Breakfast Run: track 1 (as built by tools/make_world.py) and three new,
longer tracks. This script only makes design material - it does NOT touch the game:

    docs/design/tracks/track2.png, track3.png, track4.png   each new track, drawn large
    docs/design/tracks/tracks_overview.png                  all four at the same scale
    docs/design/tracks/TRACKS.md                            the note, with the figures
    docs/design/tracks/tracks_data.json                     vertices, waypoints, figures

The world of each track is put together the SAME way make_world.py does it (the pieces below
are copied from it - it cannot be imported, since importing it rewrites src/*.asm): the road
mask, the cereal O's, the grid and start line, the breakfast things with their masks, the
NOS / oil cans, the cut into 8 x 8 tiles. So "distinct tiles" here is make_world.py's
"tiles: N", and track 1 through this script must give make_world.py's own numbers
(the script checks that it does: see EXPECT_T1).

A new track's centre line is a polygon whose corners are rounded with a given radius
(straights and arcs, as track 1 is built), in racing order: anticlockwise on screen, the
start on a bottom straight heading right - as track 1.

Run:  python3 tools/make_track_designs.py
"""
import math, os, re, json, importlib.util
from collections import deque
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, '..', 'docs', 'design', 'tracks')
ROAD = 72                          # road width in pixels (make_world.py)
WP_STEP = 32                       # a waypoint every ~32 px of centre line (make_world.py)
WIN_W, WIN_H = 192, 152            # the play window, pixels
CLEAR_TILES = 3                    # cloth wanted between two sections of road
EXPECT_T1 = dict(os=128, nwp=46, road_tiles=1665)   # make_world.py's printed figures for track 1

# ------------------------------------------------------------------ the centre lines
def track1_path():
    """Track 1's centre line: copied from make_world.py, to the letter."""
    PATH = []
    def arc(cx, cy, r, a0, a1, n=10):
        for i in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * i / n)
            PATH.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    arc(380, 280, 40, 90, 0)
    arc(380, 120, 40, 0, -90)
    PATH.append((300, 80)); PATH.append((270, 120)); PATH.append((230, 120)); PATH.append((200, 80))
    arc(140, 120, 40, -90, -180)
    arc(140, 280, 40, 180, 90)
    OFF = 32
    PATH = [(x + OFF, y + OFF) for x, y in PATH]
    return [tf1(x, y) for x, y in PATH]
def tf1(x, y): return 288 + (x - 288) * 1.35, 352 + (y - 352) * 1.35 + 64

def rounded(verts):
    """verts: (x, y, radius) corners of a closed polygon in racing order. Returns the centre
    line as points: each corner replaced by an arc of its radius (a point every ~5 px)."""
    n = len(verts); out = []; tl = []
    for i in range(n):
        (x0, y0, _), (x1, y1, r), (x2, y2, _) = verts[i - 1], verts[i], verts[(i + 1) % n]
        ax, ay = x1 - x0, y1 - y0; bx, by = x2 - x1, y2 - y1
        la, lb = math.hypot(ax, ay), math.hypot(bx, by)
        ax, ay, bx, by = ax / la, ay / la, bx / lb, by / lb
        cross = ax * by - ay * bx
        phi = math.atan2(cross, ax * bx + ay * by)             # the turn at this corner
        t = r * math.tan(abs(phi) / 2); tl.append(t)
        sx, sy = x1 - ax * t, y1 - ay * t                      # where the arc starts
        s = 1 if phi > 0 else -1
        cx, cy = sx - s * ay * r, sy + s * ax * r              # its centre
        a0 = math.atan2(sy - cy, sx - cx)
        steps = max(2, int(math.ceil(abs(phi) * r / 5)))
        for k in range(steps + 1):
            a = a0 + phi * k / steps
            out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    for i in range(n):                                         # the arcs must fit on the sides
        side = math.dist(verts[i][:2], verts[(i + 1) % n][:2])
        assert tl[i] + tl[(i + 1) % n] <= side + 1e-6, 'corners %d and %d do not fit on their side' % (i, (i + 1) % n)
    clean = [out[0]]                                           # (an arc's end can be the next one's start)
    for p in out[1:]:
        if math.dist(p, clean[-1]) > 1e-6: clean.append(p)
    if math.dist(clean[0], clean[-1]) < 1e-6: clean.pop()
    return clean

M = 68                             # the centre line stays this far inside the map (track 1: 66.6)
XL, XR = M, 576 - M                # 68 .. 508: all four maps are 72 tiles wide (the game needs it)

def track2_verts():
    """THE BREAKFAST CLUB - toast-rack switchbacks: three hairpins and track 1's dip. 72 x 64."""
    yb, p = 64 * 8 - 72, 110                                   # the start straight; row spacing
    y2, y3, yt, yd = yb - p, yb - 2 * p, M, yb - 2 * p - 104    # rows; the top; the bottom of the dip
    xh = XL + 98                                               # the left hairpin stops short of the way home
    rt = (y3 - yt) / 2
    return [(XL, yb, 55), (XR, yb, 55), (XR, y2, 55), (xh, y2, 55), (xh, y3, 55), (XR, y3, rt), (XR, yt, rt),
            (364, yt, 56), (316, yd, 56), (252, yd, 56), (204, yt, 56), (XL, yt, 70)]

def track3_verts():
    """BREAKFAST OF CHAMPIONS - the fast one: long straights, wide sweeps, one fast kink. 72 x 84."""
    yb = 84 * 8 - 72; yt = M; yf = yb - 110                    # the fold comes down to here
    return [(XL, yb, 80), (XR, yb, 90), (XR, yt, 90), (348, yt, 60), (348, yf, 60), (228, yf, 60),
            (228, yt, 56), (116, yt, 56), (116, 250, 150), (XL, 380, 150)]

def track4_verts():
    """THE DANISH GIRL - the pastry swirl: in round the outside, a hairpin in the middle, out again. 72 x 91."""
    b2 = 91 * 8 - 72; b1 = b2 - 110                            # the two bottom lanes
    t1, t2 = M, M + 110                                        # the two top lanes
    m1 = (t2 + b1 - 110) // 2; m2 = m1 + 110                   # the two middle lanes
    xi, xj, xh = XL + 110, XR - 110, 296                       # inner lanes; the middle hairpin
    return [(XL, b2, 55), (XR, b2, 165), (XR, t1, 165), (XL, t1, 165), (XL, m2, 165), (xh, m2, 55), (xh, m1, 55),
            (xi, m1, 55), (xi, t2, 55), (xj, t2, 55), (xj, b1, 55), (XL, b1, 55)]

TRACKS = [
    dict(n=1, name="BREAKFAST AT TIFFANY'S", W=72, H=64, sy=416, lx=288, verts=None,
         kind='the track in the game: a rounded rectangle with a dip in the top straight'),
    dict(n=2, name='THE BREAKFAST CLUB', W=72, H=64, sy=64 * 8 - 72, lx=288, verts=track2_verts(),
         kind='twisty and technical: toast-rack switchbacks - three hairpins, then track 1\'s dip'),
    dict(n=3, name='BREAKFAST OF CHAMPIONS', W=72, H=84, sy=84 * 8 - 72, lx=288, verts=track3_verts(),
         kind='fast and flowing: four long straights, wide sweeping bends and one fast kink'),
    dict(n=4, name='THE DANISH GIRL', W=72, H=91, sy=91 * 8 - 72, lx=272, verts=track4_verts(),
         kind='the pastry swirl: spiral in on big sweeping curves, hairpin in the middle, spiral out'),
]
for t in TRACKS:
    t['path'] = track1_path() if t['verts'] is None else rounded(t['verts'])
    assert len(t['name']) <= 22 and t['name'] == t['name'].upper()

# ------------------------------------------------------------------ measuring a centre line
def lap_length(path): return sum(math.dist(path[i], path[(i + 1) % len(path)]) for i in range(len(path)))

def resample(path, step=2.0):
    """The closed centre line as points a fixed distance apart; returns (points, spacing)."""
    loop = path + [path[0]]
    seg = [math.dist(loop[i], loop[i + 1]) for i in range(len(path))]
    total = sum(seg); n = int(round(total / step)); out = []; i = 0; acc = 0.0
    for k in range(n):
        d = k * total / n
        while d > acc + seg[i] and i < len(seg) - 1: acc += seg[i]; i += 1
        u = (d - acc) / seg[i]
        out.append((loop[i][0] + (loop[i + 1][0] - loop[i][0]) * u, loop[i][1] + (loop[i + 1][1] - loop[i][1]) * u))
    return np.array(out), total / n

def self_crossings(path):
    """How many pairs of the centre line's segments (not neighbours) cross or touch."""
    P = np.array(path); Q = np.roll(P, -1, axis=0); n = len(P); count = 0
    def orient(a, b, c): return (b[..., 0] - a[..., 0]) * (c[..., 1] - a[..., 1]) - (b[..., 1] - a[..., 1]) * (c[..., 0] - a[..., 0])
    for i in range(n):
        j = np.arange(i + 2, n if i else n - 1)                # not itself, not its neighbours
        if not len(j): continue
        a, b, c, d = P[i], Q[i], P[j], Q[j]
        o1, o2, o3, o4 = orient(a, b, c), orient(a, b, d), orient(c, d, a), orient(c, d, b)
        count += int(((o1 * o2 <= 0) & (o3 * o4 <= 0) & ~((o1 == 0) & (o2 == 0))).sum())
    return count

ADJ = 160   # px along the track: two points further apart than this are "different sections"
            # (a half circle of the 96 px that two roads with 3 tiles between them need is 151 px)
def clearance(path):
    """The least cloth, in pixels, between two different sections of road (full width): the
    least distance between centre-line points more than ADJ apart along the lap, less ROAD."""
    S, sp = resample(path, 2.0); n = len(S); k = int(math.ceil(ADJ / sp)); best = 1e9
    idx = np.arange(n)
    for i in range(n):
        gap = np.abs(idx - i); gap = np.minimum(gap, n - gap)
        far = gap > k
        d = np.hypot(S[far, 0] - S[i, 0], S[far, 1] - S[i, 1]).min()
        best = min(best, d)
    return best - ROAD

def min_radius(path, arm=24.0):
    """The tightest corner: the least radius of the circle through three centre-line points
    'arm' px apart along the lap (so a sharp kink in a polyline gets a fair, finite figure)."""
    S, sp = resample(path, 1.0); k = int(round(arm / sp))
    A, B, C = np.roll(S, k, 0), S, np.roll(S, -k, 0)
    a, b, c = np.hypot(*(B - C).T), np.hypot(*(A - C).T), np.hypot(*(A - B).T)
    area = np.abs((B[:, 0] - A[:, 0]) * (C[:, 1] - A[:, 1]) - (B[:, 1] - A[:, 1]) * (C[:, 0] - A[:, 0])) / 2
    R = np.where(area > 1e-9, a * b * c / np.maximum(4 * area, 1e-12), 1e9)
    return float(R.min())

def start_straight(t):
    """The straight the start line is on: (x0, x1) of the stretch of centre line at y = sy."""
    S, _ = resample(t['path'], 1.0)
    on = S[np.abs(S[:, 1] - t['sy']) < 0.01][:, 0]
    x0 = x1 = float(t['lx'])
    while (np.abs(on - (x0 - 1)) < 1.5).any(): x0 -= 1
    while (np.abs(on - (x1 + 1)) < 1.5).any(): x1 += 1
    return x0, x1

# ------------------------------------------------------------------ the world, as make_world.py makes it
spec = importlib.util.spec_from_file_location('bf', os.path.join(HERE, 'make_breakfast.py'))
bf = importlib.util.module_from_spec(spec); spec.loader.exec_module(bf)
ITEMS = bf.ITEMS
O_RING = ["..####..", ".#.####.", "###..###", "##....##", "##....##", "###..###", ".######.", "..####.."]
_fa = open(os.path.join(HERE, 'face_art.txt')).read()
_nos = re.search(r'== NOS face ==\n((?:[X.]{16}\n){16})', _fa).group(1).split()
NOS_ART = [_nos[y][4:12] for y in range(16) if 'X' in _nos[y]]
OIL_ART = ['........', '..XXX...', '.X...XX.', 'XXXXXXXX', 'X......X', 'X.XXXX.X', 'X.X..X.X', 'X.XXXX.X', 'X......X', 'X......X', 'XXXXXXXX', '........']
T1_WANTED = [('plate', 32, 24), ('knife', 39, 24), ('fork', 30, 24), ('spoon', 41, 24),
             ('egg', 24, 21), ('toast', 25, 31), ('juice', 44, 32), ('bacon', 34, 33),
             ('juice', 3, 3), ('toast', 60, 3), ('egg', 63, 47), ('bacon', 3, 50), ('plate', 61, 22),
             ('egg', 2, 24), ('toast', 30, 1), ('fork', 66, 36), ('knife', 68, 36), ('juice', 45, 50),
             ('bacon', 14, 2), ('egg', 24, 49)]
T1_PLACED = ['plate', 'knife', 'fork', 'spoon', 'egg', 'toast', 'juice', 'bacon', 'toast', 'egg', 'juice', 'egg']   # the twelve track 1 has room for

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

def build_world(t):
    W, H, PATH, SY, LX = t['W'], t['H'], t['path'], t['sy'], t['lx']
    PW, PH = W * 8, H * 8
    def road_mask(width):
        im = Image.new('1', (PW, PH), 0)
        d = ImageDraw.Draw(im)
        pts = PATH + [PATH[0]]
        d.line(pts, fill=1, width=width, joint='curve')
        for x, y in pts:
            d.ellipse([x - width / 2, y - width / 2, x + width / 2, y + width / 2], fill=1)
        return im
    road_im = road_mask(ROAD); road = road_im.load()
    img = Image.new('1', (PW, PH), 0); px = img.load()
    # the cereal O's (place_os, copied)
    pts = PATH + [PATH[0]]
    seq = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0)))
        for i in range(n): seq.append((x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n))
    OS = []
    for side in (-1, 1):
        last = None
        for i in range(len(seq)):
            (xa, ya), (xb, yb) = seq[i - 2], seq[(i + 2) % len(seq)]
            d = math.hypot(xb - xa, yb - ya) or 1
            nx, ny = -(yb - ya) / d, (xb - xa) / d
            cx, cy = seq[i][0] + side * nx * (ROAD / 2 + 3), seq[i][1] + side * ny * (ROAD / 2 + 3)
            p = (int(round((cx - 4) / 8)) * 8, int(round((cy - 4) / 8)) * 8)
            if last is None or math.hypot(p[0] - last[0], p[1] - last[1]) >= 18:
                if all(math.hypot(p[0] - q[0], p[1] - q[1]) >= 15 for q in OS):
                    OS.append(p); last = p
    for ox, oy in OS:
        for j, r in enumerate(O_RING):
            for i, c in enumerate(r):
                if c == '#': px[ox + i, oy + j] = 1
    # the grid and the start line (track 1: the line at x = 288, the cars 40 .. 104 px behind it)
    LANE_A, LANE_B = SY - 14 - 8, SY + 14 - 8
    GRID = [(LX - 40, LANE_A), (LX - 56, LANE_B), (LX - 72, LANE_A), (LX - 88, LANE_B), (LX - 104, LANE_A)]
    grid_ok = True
    for gx, gy in GRID:
        for y in range(gy - 1, gy + 17):
            if road[gx - 3, y]: px[gx - 3, y] = 1
            else: grid_ok = False
        for x in range(gx - 3, gx + 4):
            for y in (gy - 1, gy + 16):
                if road[x, y]: px[x, y] = 1
        grid_ok = grid_ok and all(road[x, y] for x in (gx, gx + 19) for y in (gy, gy + 15))
    for y in range(SY - 60, SY + 60):
        for x in range(LX, LX + 8):
            if road[x, y] and not px[x, y] and ((x // 4) + (y // 4)) % 2 == 0:
                px[x, y] = 1
    # the breakfast things
    items_img = Image.new('1', (PW, PH), 0); ipx = items_img.load()
    far = np.array(road_mask(ROAD + 24), dtype=bool)
    tile_far = far.reshape(H, 8, W, 8).any(axis=(1, 3))       # a tile with any of the road's band in it
    taken = set()
    def free(tx, ty, w, h):
        for j in range(h):
            for i in range(w):
                if (tx + i, ty + j) in taken: return False
                if not (0 <= tx + i < W and 0 <= ty + j < H) or tile_far[ty + j, tx + i]: return False
        return True
    def place(shape, tx, ty):
        w, h = len(shape[0]) // 8, len(shape) // 8
        for j in range(h + 1):
            for i in range(w + 1): taken.add((tx + i, ty + j))
        for y, row in enumerate(shape):
            for x, c in enumerate(row):
                if c == '#': px[tx * 8 + x, ty * 8 + y] = 1; ipx[tx * 8 + x, ty * 8 + y] = 1
    placed = []; spots = []
    def settle(name, tx, ty):
        shape = ITEMS[name]; w, h = len(shape[0]) // 8, len(shape) // 8; best = None
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                if free(tx + dx, ty + dy, w, h):
                    k = (dark_tiles(shape, tx + dx, ty + dy), abs(dx) + abs(dy))
                    if best is None or k < best[0]: best = (k, tx + dx, ty + dy)
        if best:
            place(shape, best[1], best[2]); placed.append(name); spots.append((best[1] + w / 2, best[2] + h / 2))
    if t['n'] == 1:
        for name, tx, ty in T1_WANTED:
            tx, ty = (int(round(v / 8)) for v in tf1(tx * 8, ty * 8))
            settle(name, tx, ty)
    else:
        # a new track: the same twelve things, each where there is room, as far from the others as it can be
        for name in T1_PLACED:
            shape = ITEMS[name]; w, h = len(shape[0]) // 8, len(shape) // 8
            cand = [(tx, ty) for ty in range(1, H - h) for tx in range(1, W - w) if free(tx, ty, w, h)]
            if not cand: continue
            def spread(c):
                cx, cy = c[0] + w / 2, c[1] + h / 2
                dist = min([math.hypot(cx - sx, cy - sy) for sx, sy in spots] + [60])
                return (round(dist), -abs(cx - W / 2) - abs(cy - H / 2))
            tx, ty = max(cand, key=spread)
            settle(name, tx, ty)
    # the cans: NOS A just behind the grid, NOS B and the oil can C out on the lap
    def _can(cx, cy):
        top = int(round(cy)) - 6
        ty, dy = top // 8, top % 8
        if dy > 4: dy = 4
        return int(cx - 4) // 8, ty, dy
    if t['n'] == 1:
        _mid = [p for p in PATH if abs(p[0] - 288) < 80 and p[1] < SY - 100]
        _bx = sum(p[0] for p in _mid) / len(_mid); _by = max(p[1] for p in _mid)
        _left = min(PATH, key=lambda p: (abs(p[1] - (SY - 170)), p[0]))
        CANS = {'A': _can(156, SY), 'B': _can(_bx, _by),
                'C': _can(min(p[0] for p in PATH if abs(p[1] - _left[1]) < 20), _left[1])}
    else:
        S, _sp = resample(PATH, 1.0)
        i0 = int(np.argmin(np.hypot(S[:, 0] - LX, S[:, 1] - SY)))
        at = lambda f: S[(i0 + int(f * len(S))) % len(S)]
        CANS = {'A': _can(LX - 132, SY), 'B': _can(*at(0.45)), 'C': _can(*at(0.72))}
    for k, (tx, ty, dy) in CANS.items():
        for y, row in enumerate(OIL_ART if k == 'C' else NOS_ART):
            for x, c in enumerate(row):
                if c == 'X': px[tx * 8 + x, ty * 8 + dy + y] = 1; ipx[tx * 8 + x, ty * 8 + dy + y] = 1
    # the masks of the things that sit on the cloth
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
    # the cut into tiles
    ink_a = np.array(img, dtype=bool)
    yy, xx = np.mgrid[0:PH, 0:PW]
    cloth_on = ((((xx >> 5) + (yy >> 5)) & 1) == 1) & ((yy & 1) == 0) & ((xx & 3) == (yy & 2))
    def tbytes(a, tx, ty): return bytes(np.packbits(a[ty * 8:ty * 8 + 8, tx * 8:tx * 8 + 8], axis=1).ravel().tolist())
    cells = {}
    for ty in range(H):
        for tx in range(W):
            ink = tbytes(ink_a, tx, ty)
            sl = (slice(ty * 8, ty * 8 + 8), slice(tx * 8, tx * 8 + 8))
            msk = tbytes(imask, tx, ty) if (imask[sl] & cloth_on[sl]).any() else bytes(8)
            cells[(tx, ty)] = (ink, msk)
    plain = [bytes(8)] + sorted({ink for ink, m in cells.values() if not any(m) and any(ink)})
    masked = sorted({(ink, m) for ink, m in cells.values() if any(m)})
    tiles = len(plain) + len(masked)
    road_a = np.array(road_im, dtype=bool)
    road_tiles = int((road_a.reshape(H, 8, W, 8).sum(axis=(1, 3)) >= 32).sum())
    row_bytes = sum(1 + 2 * sum(1 for tx in range(W) if any(cells[(tx, ty)][0]) or any(cells[(tx, ty)][1])) for ty in range(H))
    # the waypoints
    loop = PATH + [PATH[0]]
    seglen = [math.dist(loop[i], loop[i + 1]) for i in range(len(PATH))]
    total = sum(seglen); NWP = round(total / WP_STEP); wps = []
    for k in range(NWP):
        dd = k * total / NWP; i = 0
        while dd > seglen[i]: dd -= seglen[i]; i += 1
        (x0, y0), (x1, y1) = loop[i], loop[i + 1]; u = dd / seglen[i]
        wps.append((round(x0 + (x1 - x0) * u), round(y0 + (y1 - y0) * u)))
    data = dict(rows=row_bytes, index=2 * H, surface=(W // 8) * H, omap=(W // 8) * H, waypoints=4 * NWP, tiles=8 * tiles)
    return dict(road=road_a, ink=ink_a, imask=imask, cloth_on=cloth_on, OS=OS, GRID=GRID, grid_ok=grid_ok, CANS=CANS,
                placed=placed, tiles=tiles, masked=len(masked), road_tiles=road_tiles, nwp=NWP, wps=wps,
                data=data, data_total=sum(data.values()))

# ------------------------------------------------------------------ the pictures
CYAN, BLUE, YELLOW, BLACK, RED, WHITE = (0, 215, 215), (0, 0, 215), (215, 215, 0), (0, 0, 0), (215, 0, 0), (255, 255, 255)
ROAD_PAPER, ROAD_DOT = (214, 246, 246), (150, 190, 240)        # the road, lightened so the design reads
def font(size): return ImageFont.load_default(size=size)

def world_image(w):
    """The world at 1 pixel = 1 pixel: the check cloth in the game's colours, the road on it
    (lightened - in the game the road is plain cloth between the O's), the O's and things in blue."""
    h_, w_ = w['road'].shape
    a = np.empty((h_, w_, 3), dtype=np.uint8); a[:] = CYAN
    a[w['cloth_on']] = BLUE
    a[w['road']] = ROAD_PAPER
    a[w['road'] & w['cloth_on']] = ROAD_DOT
    a[w['imask'] & ~w['road']] = CYAN
    a[w['imask'] & w['road']] = ROAD_PAPER
    a[w['ink']] = BLUE
    return Image.fromarray(a)

def overlay(d, t, w, s, ox, oy, labels=True):
    """Start line, direction arrows and the play window, drawn at scale s with the map at (ox, oy)."""
    S, sp = resample(t['path'], 1.0); n = len(S)
    i0 = int(np.argmin(np.hypot(S[:, 0] - t['lx'], S[:, 1] - t['sy'])))
    P = lambda x, y: (ox + x * s, oy + y * s)
    step = n // max(6, round(n / 230))
    for k in range(60, n - 40, step):                           # arrows along the lap, in racing order
        x, y = S[(i0 + k) % n]; x2, y2 = S[(i0 + k + 3) % n]
        ux, uy = x2 - x, y2 - y; l = math.hypot(ux, uy); ux, uy = ux / l, uy / l
        a = 11
        tri = [P(x + ux * a, y + uy * a), P(x - ux * a * 0.6 - uy * a * 0.75, y - uy * a * 0.6 + ux * a * 0.75),
               P(x - ux * a * 0.6 + uy * a * 0.75, y - uy * a * 0.6 - ux * a * 0.75)]
        d.polygon(tri, fill=RED, outline=BLACK)
    lx, sy = t['lx'], t['sy']                                   # the start line: a red bar beside the checker band
    d.rectangle([P(lx + 9, sy - 36), P(lx + 11, sy + 36)], fill=RED)
    if labels:
        f = font(int(11 * s))
        d.text(P(lx + 16, sy - 34), 'START', fill=RED, font=f, stroke_width=max(1, int(s)), stroke_fill=WHITE)
    # the play window, where it is at the start: centred on the pole car, kept inside the map
    gx, gy = w['GRID'][0]
    wx = min(max(gx + 10 - WIN_W // 2, 0), t['W'] * 8 - WIN_W); wy = min(max(gy + 10 - WIN_H // 2, 0), t['H'] * 8 - WIN_H)
    for k in range(max(2, int(2 * s))):
        d.rectangle([ox + wx * s + k, oy + wy * s + k, ox + (wx + WIN_W) * s - 1 - k, oy + (wy + WIN_H) * s - 1 - k], outline=YELLOW if k % 2 else BLACK)
    if labels:
        f = font(int(9 * s))
        d.text(P(wx + 4, wy + 3), 'PLAY WINDOW %d x %d px (to scale)' % (WIN_W, WIN_H), fill=BLACK, font=f, stroke_width=max(1, int(s)), stroke_fill=YELLOW)

def figures_line(t):
    return ('Map %d x %d tiles (%d x %d px)   Lap %d px = %.2f x track 1   Waypoints %d   Distinct tiles %d'
            % (t['W'], t['H'], t['W'] * 8, t['H'] * 8, round(t['lap']), t['mult'], t['w']['nwp'], t['w']['tiles']))

def track_picture(t, s=2):
    w = t['w']; PW, PH = t['W'] * 8, t['H'] * 8; pad, cap = 24, 150
    im = Image.new('RGB', (PW * s + 2 * pad, PH * s + pad + cap), YELLOW)
    im.paste(world_image(w).resize((PW * s, PH * s), Image.NEAREST), (pad, pad))
    d = ImageDraw.Draw(im)
    d.rectangle([pad - 3, pad - 3, pad + PW * s + 2, pad + PH * s + 2], outline=BLUE, width=3)
    overlay(d, t, w, s, pad, pad)
    y = pad + PH * s + 12
    d.text((pad, y), 'TRACK %d   %s' % (t['n'], t['name']), fill=BLACK, font=font(34))
    d.text((pad, y + 46), t['kind'][0].upper() + t['kind'][1:] + '.', fill=BLACK, font=font(19))
    d.text((pad, y + 74), figures_line(t), fill=BLACK, font=font(19))
    d.text((pad, y + 102), 'Red arrows: the way round. Road shown lighter than in the game. Design only - not in the game. Classification: Internal.',
           fill=(70, 70, 0), font=font(15))
    im.save(os.path.join(OUTDIR, 'track%d.png' % t['n']))

def overview_picture(tracks, s=1):
    pad, gap, head, cap = 28, 28, 64, 124
    wid = sum(t['W'] * 8 * s for t in tracks) + gap * (len(tracks) - 1) + 2 * pad
    tall = max(t['H'] * 8 * s for t in tracks)
    im = Image.new('RGB', (wid, head + tall + cap + pad), YELLOW); d = ImageDraw.Draw(im)
    d.text((pad, 14), 'BREAKFAST RUN - the track in the game and three longer designs, all at the same scale', fill=BLACK, font=font(30))
    x = pad
    for t in tracks:
        PW, PH = t['W'] * 8 * s, t['H'] * 8 * s; y0 = head + tall - PH       # stood on a common base line
        im.paste(world_image(t['w']).resize((PW, PH), Image.NEAREST), (x, y0))
        d.rectangle([x - 2, y0 - 2, x + PW + 1, y0 + PH + 1], outline=BLUE, width=2)
        overlay(d, t, t['w'], s, x, y0, labels=False)
        y = head + tall + 10
        d.text((x, y), '%d  %s' % (t['n'], t['name']), fill=BLACK, font=font(26))
        d.text((x, y + 34), 'Lap %d px  =  %.2f x track 1' % (round(t['lap']), t['mult']) if t['n'] > 1 else 'Lap %d px  (in the game)' % round(t['lap']), fill=BLACK, font=font(22))
        d.text((x, y + 62), 'Map %d x %d tiles, %d waypoints, %d tiles' % (t['W'], t['H'], t['w']['nwp'], t['w']['tiles']), fill=BLACK, font=font(18))
        x += PW + gap
    d.text((pad, head + tall + 98), 'Yellow box on each: the play window (%d x %d px) at the start. Red arrows: the way round. Design only. Classification: Internal.' % (WIN_W, WIN_H),
           fill=(70, 70, 0), font=font(16))
    im.save(os.path.join(OUTDIR, 'tracks_overview.png'))

# ------------------------------------------------------------------ measure, check, write
def main():
    os.makedirs(OUTDIR, exist_ok=True)
    base = lap_length(TRACKS[0]['path'])
    for t in TRACKS:
        p = t['path']; t['lap'] = lap_length(p); t['mult'] = t['lap'] / base
        t['w'] = build_world(t)
        xs, ys = [q[0] for q in p], [q[1] for q in p]
        t['margin'] = min(min(xs), t['W'] * 8 - max(xs), min(ys), t['H'] * 8 - max(ys))
        t['crossings'] = self_crossings(p)
        t['cloth'] = clearance(p)
        t['rmin'] = min_radius(p)
        t['rdesign'] = min(v[2] for v in t['verts']) if t['verts'] else 54.0     # track 1's arcs: 40 x 1.35
        loop = p + [p[0]]
        head = [math.atan2(loop[i + 1][1] - loop[i][1], loop[i + 1][0] - loop[i][0]) for i in range(len(p))]
        t['kink'] = max(abs(math.degrees((head[i] - head[i - 1] + math.pi) % (2 * math.pi) - math.pi)) for i in range(len(p)))
        t['straight'] = start_straight(t)
    t1 = TRACKS[0]
    # track 1 through this script must be make_world.py's track 1
    got = dict(os=len(t1['w']['OS']), nwp=t1['w']['nwp'], road_tiles=t1['w']['road_tiles'])
    assert got == EXPECT_T1, 'track 1 does not match make_world.py: %r' % got
    ok_all = True
    print('%-24s %-8s %8s %6s %4s %6s %5s %6s %6s %6s' % ('track', 'map', 'lap px', 'x', 'wp', 'tiles', "O's", 'rows', 'data', 'things'))
    for t in TRACKS:
        w = t['w']
        print('%d %-22s %-8s %8.1f %6.3f %4d %6d %5d %6d %6d %6d' % (t['n'], t['name'], '%dx%d' % (t['W'], t['H']), t['lap'], t['mult'],
              w['nwp'], w['tiles'], len(w['OS']), w['data']['rows'], w['data_total'], len(w['placed'])))
    print()
    for t in TRACKS:
        x0, x1 = t['straight']; lx = t['lx']
        checks = [
            ('closed (largest jump in direction between two segments, degrees)', t['kink'], t['kink'] <= 12),
            ('centre line crosses itself (count)', t['crossings'], t['crossings'] == 0),
            ('least cloth between two sections of road (px; want >= %d = %d tiles)' % (CLEAR_TILES * 8, CLEAR_TILES), t['cloth'], t['cloth'] >= CLEAR_TILES * 8 - 0.5),
            ('tightest corner, 3-point radius (px; track 1: %.1f)' % t1['rmin'], t['rmin'], t['rmin'] >= t1['rmin'] - 0.05),
            ('smallest arc radius as drawn (px; track 1: 54)', t['rdesign'], t['rdesign'] >= 54),
            ('centre line to the map edge (px; track 1: %.1f)' % t1['margin'], t['margin'], t['margin'] >= t1['margin'] - 0.05),
            ('start straight (px; behind the line %d, after it %d)' % (lx - x0, x1 - lx), x1 - x0, lx - x0 >= 140 and x1 - lx >= 48),
            ('five grid boxes all on the road', int(t['w']['grid_ok']), t['w']['grid_ok']),
            ('lap at least 1.4 x track 1', t['mult'], t['n'] == 1 or t['mult'] >= 1.4),
            ('distinct tiles within the game\'s 256', t['w']['tiles'], t['w']['tiles'] <= 256),
        ]
        t['checks'] = checks
        print('track %d  %s' % (t['n'], t['name']))
        for what, val, ok in checks:
            if t['n'] == 1 and not ok: mark = 'n/a '          # track 1 is the yardstick, not on trial
            else: mark = 'PASS' if ok else 'FAIL'; ok_all = ok_all and ok
            print('   %s  %-74s %s' % (mark, what, ('%.1f' % val) if isinstance(val, float) else val))
    for t in TRACKS[1:]: track_picture(t)
    overview_picture(TRACKS)
    json.dump([dict(track=t['n'], name=t['name'], map_tiles=[t['W'], t['H']], lap_px=round(t['lap'], 1), multiple=round(t['mult'], 3),
                    waypoints=t['w']['wps'], distinct_tiles=t['w']['tiles'], cereal_os=len(t['w']['OS']),
                    start_line_x=t['lx'], start_straight_y=t['sy'], grid=t['w']['GRID'],
                    corners_x_y_radius=t['verts'], data_bytes=t['w']['data'])
               for t in TRACKS], open(os.path.join(OUTDIR, 'tracks_data.json'), 'w'), indent=1)
    write_note(TRACKS)
    print('\nall checks passed' if ok_all else '\nSOME CHECKS FAILED')
    return 0 if ok_all else 1

HARD = {
    2: ["Fits the map the game has now (72 x 64 tiles) - no bigger map needed.",
        "The rows of road are close together (3 to 5 tiles of cloth between them), so there is little room for breakfast things between them, and a car that runs wide can reach the next row."],
    3: ["Needs a taller map: 84 rows instead of 64 (the same 72 wide). The game's row index, mini-map and camera limits are built for 64 rows and would need changing.",
        "The long straights run up and down the screen, where the window is shortest (152 px)."],
    4: ["Needs the tallest map: 91 rows instead of 64 (the same 72 wide), with the same changes as track 3.",
        "Two lanes run side by side in opposite directions all the way round (about 4 tiles of cloth between): the computer cars' waypoints and the wrong-way / lap-counting logic should be tested for a car that hops across to the other lane.",
        "The start straight is the shortest of the four: the grid fits, but the first bend comes sooner after the line than on track 1."],
}
def write_note(tracks):
    t1 = tracks[0]; L = []
    L += ['# Breakfast Run - three longer track designs', '',
          'Classification: Internal', '',
          'These are **designs only**. Nothing here is in the game yet, and the game was not changed.',
          'Made by `tools/make_track_designs.py` (run it again to redraw the pictures and this note).',
          'Pictures: `track2.png`, `track3.png`, `track4.png`, and all four side by side in `tracks_overview.png`.', '',
          '## The figures', '',
          '| | Name | Map (tiles) | Lap (pixels) | Times track 1 | Waypoints | Distinct tiles | Cereal O\'s | Map data (bytes, estimate) |',
          '|---|---|---|---|---|---|---|---|---|']
    for t in tracks:
        w = t['w']
        L.append('| %d | %s | %d x %d | %d | %s | %d | %d | %d | %d |' % (t['n'], t['name'], t['W'], t['H'], round(t['lap']),
                 '1.00 (in the game)' if t['n'] == 1 else '%.2f' % t['mult'], w['nwp'], w['tiles'], len(w['OS']), w['data_total']))
    L += ['',
          '- **Lap** is the length of the middle of the road, once round.',
          '- **Waypoints** are the points the computer cars steer by, one every 32 pixels as on track 1.',
          '- **Distinct tiles** is the number of different 8 x 8 pictures the map needs, counted the way `make_world.py` counts them ("tiles: N"). '
          'The game can hold 256. The count hardly changes with the length of the road, because the road itself is plain cloth: it is the breakfast things that use the tiles '
          '(each new design was given the same twelve things as track 1, wherever there was room: %s placed).' % ', '.join('track %d - %d' % (t['n'], len(t['w']['placed'])) for t in tracks[1:]),
          '- **Map data** is an estimate of the bytes the map itself takes in memory: the row lists, the row index, the road/off-road and O maps, the waypoints and the tile pictures. '
          'It is there to compare the tracks with each other, not as an exact count.', '',
          '## The tracks', '']
    for t in tracks[1:]:
        w = t['w']; x0, x1 = t['straight']
        L += ['### Track %d - %s' % (t['n'], t['name']), '',
              t['kind'][0].upper() + t['kind'][1:] + '.', '',
              '- Map: %d x %d tiles (%d x %d pixels). Track 1 is 72 x 64.' % (t['W'], t['H'], t['W'] * 8, t['H'] * 8),
              '- Lap: %d pixels, **%.2f times** track 1 (%d).' % (round(t['lap']), t['mult'], round(t1['lap'])),
              '- Waypoints: %d (track 1: %d). Cereal O\'s: %d (track 1: %d).' % (w['nwp'], t1['w']['nwp'], len(w['OS']), len(t1['w']['OS'])),
              '- Distinct tiles: %d (track 1: %d).' % (w['tiles'], t1['w']['tiles']),
              '- Map data: about %d bytes (track 1: about %d) - %+d.' % (w['data_total'], t1['w']['data_total'], w['data_total'] - t1['w']['data_total']),
              '- Tightest corner: %d pixel radius (track 1\'s arcs: 54; its dip is sharper). Start straight: %d pixels (track 1: %d).'
              % (round(t['rdesign']), round(x1 - x0), round(t1['straight'][1] - t1['straight'][0])),
              '- Least cloth between two stretches of road: %.1f tiles.' % (t['cloth'] / 8), '',
              'What would make it hard to put in the game:', ''] + ['- ' + s for s in HARD[t['n']]] + ['']
    L += ['## For all three', '',
          '- **Memory is the real obstacle.** The project notes say memory is full (well under 200 bytes free). A second track of any size needs room for its own map data '
          '(see the last column above), so room has to be found first - for example by loading one track at a time, or packing the map data.',
          '- All three keep the map 72 tiles wide, because the game\'s road-surface code is written for exactly 72 (it stops the build otherwise). Only the height grows.',
          '- All three use track 1\'s road width (72 pixels), start on a bottom straight heading right with the same five-car grid, and run the same way round (anticlockwise).',
          '- The game today builds one track straight into the program: choosing between tracks, and each track\'s name on screen, are new work.',
          '- The positions of the breakfast things and of the NOS and oil cans in the pictures are placeholders, put there by the script so the tile counts are fair. They are easy to move.', '',
          '## Checks the script ran', '',
          'For each new track: the middle line is closed and smooth; it never crosses itself; no two different stretches of road come closer than 3 tiles of cloth; '
          'no corner is tighter than track 1\'s; the road stays as far from the map\'s edge as track 1\'s does; the start straight holds the five-car grid; the lap is at least 1.4 times track 1.', '',
          '| Check | ' + ' | '.join('Track %d' % t['n'] for t in tracks) + ' |', '|---|' + '---|' * len(tracks)]
    for i, (what, _, _) in enumerate(tracks[1]['checks']):
        what = re.sub(r' \(.*\)$', '', what)
        row = []
        for t in tracks:
            _, val, ok = t['checks'][i]
            v = ('%.1f' % val) if isinstance(val, float) else str(val)
            row.append(v + (' (yardstick)' if t['n'] == 1 else (' - pass' if ok else ' - FAIL')))
        L.append('| %s | %s |' % (what, ' | '.join(row)))
    L += ['', 'Not checked: the tracks have not been driven - not built into the game, so nothing here says how they play, how fast a lap is, or whether the computer cars cope.', '']
    open(os.path.join(OUTDIR, 'TRACKS.md'), 'w').write('\n'.join(L))

if __name__ == '__main__':
    raise SystemExit(main())
