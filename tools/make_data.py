"""Generate the car graphics and the thrust table. Writes src/data.asm.

Car art follows the one-bit-art skill (Grant's house style), scaled down from his
top-down Traverse USA cars to 16x16 so a car fits at every heading:
  key shape      value
  tyres          DITHER  (wheels are dithered)
  windscreen     PAPER   (glass is white)
  rear window    PAPER
  roof           SOLID, ringed by paper (open sides - negative space)
  nose           SOLID, with the car's identifying mark carved out in paper
  rear bumper    SOLID line
Identifying marks: player = notch in the nose; CPU A = paper racing stripe through
the roof; CPU B = open cockpit (no roof) with the driver's helmet as a dot.
Headings: never rotate pixels (rule T1). Each key shape is re-rasterised at the
angle (dither phase locked to the pixel grid so it stays a clean checker); the
cardinal frames are exact quarter-turns of the hand-checked upright frame.
Mask: every car pixel opaque, plus a 1px halo so the car reads over track lines."""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.join(HERE, '..', 'src', 'data.asm')
INK, PAPER, DITH, NONE = 1, 0, 2, -1

def car_value(x, y, kind):
    """Value at car-local point (x, y); nose toward -y; units = pixels.
    Body 6 wide x 13 long, tyres 1.5 wide either side."""
    ax = abs(x)
    if 3.0 <= ax <= 4.6 and (-5.0 <= y <= -1.6 or 1.6 <= y <= 5.0):
        return DITH                           # tyres
    if ax > 3.0 or abs(y) > 6.5:
        return NONE
    if y < -3.0:                              # nose
        if kind == 0 and ax < 1.0 and -5.5 <= y < -3.6:
            return PAPER                      # player's notch
        if kind == 3 and ax < 2.0 and -5.0 <= y < -4.0:
            return PAPER                      # CPU C: grille slot across the nose
        return INK
    if y < -1.0:                              # windscreen: glass between the pillars
        return PAPER if ax < 2.0 else INK
    if y < 2.0:                               # roof zone
        if kind == 2:                         # convertible: open cockpit + helmet
            if ax < 1.0 and -0.5 <= y < 1.5: return INK
            return PAPER if ax < 2.0 else INK
        if ax >= 2.0: return PAPER            # open sides ring the roof with paper
        if kind == 1 and ax < 0.75: return PAPER  # CPU A: racing stripe
        if kind == 4 and ax < 1.0 and -0.5 <= y < 1.0: return PAPER  # CPU D: sunroof
        return INK
    if y < 3.0:                               # rear window
        return PAPER if ax < 2.0 else INK
    return INK                                # rear body and bumper

def raster(angle_deg, kind):
    """One sample at each pixel centre: every pixel takes the value of the
    key shape it sits in. (Averaging several samples smeared the 1px glass
    and the roof ring into noise at the angled headings.)"""
    th = math.radians(angle_deg)
    g = [[NONE] * 16 for _ in range(16)]
    for py in range(16):
        for px in range(16):
            dx, dy = px + .5 - 8, py + .5 - 8
            lx = dx * math.cos(th) + dy * math.sin(th)
            ly = -dx * math.sin(th) + dy * math.cos(th)
            g[py][px] = car_value(lx, ly, kind)
    return g

def mirror_diag(g):
    """Reflect across the up-right diagonal: heading 22.5 becomes 67.5 exactly."""
    return [[g[15 - c][15 - r] for c in range(16)] for r in range(16)]

def rot90cw(g):
    return [[g[15 - c][r] for c in range(16)] for r in range(16)]

def frames_for(kind):
    # the 22.5 degree heading is drawn on a 2:1 slope (26.6 degrees): pixel lines
    # step evenly at 2:1, and 4 degrees cannot be seen at 16x16
    n, nne, ne = raster(0, kind), raster(math.degrees(math.atan2(1, 2)), kind), raster(45, kind)
    base = [n, nne, ne, mirror_diag(nne)]
    f = base[:]
    for k in range(4, 16):
        f.append(rot90cw(f[k - 4]))
    return f

def ink_of(g):
    # dither is drawn as a checker locked to the sprite grid
    return [[1 if v == INK or (v == DITH and (x + y) % 2 == 0) else 0
             for x, v in enumerate(row)] for y, row in enumerate(g)]

def mask_of(g):
    solid = [[v != NONE for v in row] for row in g]
    return [[1 if any(solid[y + j][x + i] for j in (-1, 0, 1) for i in (-1, 0, 1)
                      if 0 <= y + j < 16 and 0 <= x + i < 16) else 0
             for x in range(16)] for y in range(16)]

def rows_bytes(bits):
    out = []
    for row in bits:
        v = 0
        for b in row: v = v * 2 + b
        out.append((v >> 8, v & 255))
    return out

KINDS = ['player (notch in the nose)', 'CPU A (racing stripe)', 'CPU B (open cockpit)',
         'CPU C (grille slot in the nose)', 'CPU D (sunroof)']
NAMES = ['YOU', 'CYAN', 'GREEN', 'PINK', 'WHITE']
# CHOOSE=1 (the choose screen, tools/build_choose.sh): more cars to pick from, listed in tools/choose_cars.txt (today the
# two kept in tools/pool_art.txt - the six-wheeled TRUCK and SPECS's saloon). Their drawings: tools/car_art.txt,
# tools/pool_art.txt or tools/choose_car_art.txt. Their frames, table and names go above the screen-copy routine
# (src/cars_hp.asm). Adding a car is a drawing and a line in the list: no code.
CHOOSE = os.environ.get('CHOOSE') == '1'
SHOWN = {}
if CHOOSE:
    import re as _re
    _l = _re.findall(r'^car:\s*(\w+)\s+(.+?)\s*$', open(os.path.join(HERE, 'choose_cars.txt')).read(), _re.M)
    assert [a for a, _ in _l[:5]] == NAMES, 'tools/choose_cars.txt: the first five cars must be %s' % NAMES
    assert len(_l) <= 10, 'tools/choose_cars.txt: ten cars at most'
    for a, b in _l[5:]: KINDS.append('%s (the choose screen: %s)' % (a, b)); NAMES.append(a)
    SHOWN = {a: b.upper()[:12] for a, b in _l}
def hand_drawn():
    """Cars drawn by hand in tools/car_art.txt (the car editor's text): for each
    car named there, its three drawn headings replace the generated ones.
    X = ink, o = paper (the car's white body), . = empty."""
    import re
    path = os.path.join(HERE, 'car_art.txt')
    if not os.path.exists(path): return {}
    got = {}
    text = open(path).read()
    if CHOOSE:
        for f in ('pool_art.txt', 'choose_car_art.txt'):
            if os.path.exists(os.path.join(HERE, f)): text += open(os.path.join(HERE, f)).read()
    # SWAP_CAR=CYAN=TRUCK (Grant, 23 Nov 2026: "The six wheeler to replace Franks car" - his coupe looked like Max's racer): a
    # car's pictures from another drawing (tools/pool_art.txt); the driver, card and face are the same. Set on the breakfast
    # fast tapes only (tools/build_race.sh), so the other tapes keep their pictures.
    # STUDIO_ART=1 (Grant, 23 Nov 2026, "cars done" in the Car Studio): tools/car_art_studio.txt read on top - a car drawn again
    # there wins (the last drawing of a name and heading is the one kept). Set on the breakfast fast tapes only.
    studio = open(os.path.join(HERE, 'car_art_studio.txt')).read() if os.environ.get('STUDIO_ART') == '1' else ''
    text += studio
    swap = dict(a.split('=') for a in os.environ.get('SWAP_CAR', '').split(',') if a)
    if swap:
        pool = open(os.path.join(HERE, 'pool_art.txt')).read() + studio
        for to, frm in swap.items():
            assert to in NAMES and ('== %s heading 0 ==' % frm) in pool, 'SWAP_CAR: %s=%s' % (to, frm)
            text = re.sub(r'== %s heading ' % to, '== %s_OLD heading ' % to, text)
            text += re.sub(r'== %s heading ' % frm, '== %s heading ' % to, pool)
    for m in re.finditer(r'== (\w+) heading ([\d.]+) ==\n((?:[Xo.]{16}\n){16})', text):
        if m.group(1) not in NAMES: continue
        g = [[INK if c == 'X' else PAPER if c == 'o' else NONE for c in r] for r in m.group(3).split()]
        if m.group(2) not in ('0', '22.5', '45', '11.25', '33.75'): continue
        got.setdefault(NAMES.index(m.group(1)), {})[{'0': 0, '22.5': 1, '45': 2, '11.25': 3, '33.75': 4}[m.group(2)]] = g
    for k in range(5, len(NAMES)):               # (CHOOSE) a car drawn nose up only: its angled headings drafted from that (tools/turn_car.py)
        assert k in got and 0 in got[k], 'no "== %s heading 0 ==" drawing for the car in tools/choose_cars.txt' % NAMES[k]
        if len(got[k]) < 3:
            import turn_car
            a, b = turn_car.turned([''.join('X' if v == INK else 'o' if v == PAPER else '.' for v in r) for r in got[k][0]])
            for i, d in ((1, a), (2, b)): got[k].setdefault(i, [[INK if c == 'X' else PAPER if c == 'o' else NONE for c in r] for r in d])
    return got
HAND = hand_drawn()
def frames_of(k):
    f = frames_for(k)
    if k in HAND:
        assert all(i in HAND[k] for i in (0, 1, 2)), 'car %s needs all three headings drawn' % NAMES[k]
        n, nne, ne = HAND[k][0], HAND[k][1], HAND[k][2]
        f = [n, nne, ne, mirror_diag(nne)]
        for i in range(4, 16): f.append(rot90cw(f[i - 4]))
    return f
all_frames = [frames_of(k) for k in range(len(KINDS))]
# HEAD32=1 (Grant, 22 Nov 2026: "smoothness can be improved with more angles of drawing ... what if we compromised to 32?"):
# the racer (YOU - in RACE mode every car) is drawn at 32 headings, 11.25 degrees apart. Grant's 0, 22.5 and 45 drawings as
# before; the two between (11.25 and 33.75) from tools/car_art.txt if drawn there, else drafted from heading 0 by
# tools/turn_car.py (turned to the middle of the slopes either side: 13.3 and 35.8 degrees, as 22.5 is drawn on a 2:1 slope).
HEAD32 = os.environ.get('HEAD32') in ('1', 'all')
H32K = range(len(KINDS)) if os.environ.get('HEAD32') == 'all' else [0]    # (HEAD32=all, the race-only tape: every car at 32)
def frames32_of(k):
    import turn_car
    n, nne, ne = HAND[k][0], HAND[k][1], HAND[k][2]
    up = [''.join('X' if v == INK else 'o' if v == PAPER else '.' for v in r) for r in n]
    tg = lambda d: [[INK if c == 'X' else PAPER if c == 'o' else NONE for c in r] for r in turn_car.raster_ss(up, d)]
    a = HAND[k].get(3) or tg(13.28); b = HAND[k].get(4) or tg(35.78)
    f = [n, a, nne, b, ne, mirror_diag(b), mirror_diag(nne), mirror_diag(a)]
    for i in range(8, 32): f.append(rot90cw(f[i - 8]))
    return f

# ---- the big cars. Grant draws each car once, facing up, 20 x 20 (tools/big_car_art.txt: its
# 19 x 19 top-left part is used). The angled headings are that drawing TURNED AT FULL SIZE in a
# bigger frame (Grant, 14 Nov 2026: "the car primary shape should remain intact ... wheels and
# overall size"; "go with 26"): a 17 x 18 car turned 45 degrees is 25 pixels across, and the old
# 20 x 20 frame cut its corners off. Everything is worked out on a 27 x 27 grid with the car's
# middle on the grid's middle; the game's frame is that grid's columns 2..25 - 24 wide, so a row
# is still 3 bytes (26 would be 4 bytes a row and 13 KB of pictures: there is not the memory) -
# and as many rows as the heading needs, with the 1-px halo. A 24-wide frame loses nothing but
# a pixel or two at the far tips of the two widest cars. Each frame keeps only its rows in use:
# big_tab gives every car's every heading its address, first row and row count.
# tools/big_car_art_27.txt holds the 22.5 and 45 degree drawings (made here from the upright
# one the first time; edit them there - they are read back, never overwritten).
BN = 19; GN = 27; GO = 4; FW = 24; FX = 2
CH = {INK: 'X', PAPER: 'o', NONE: '.'}; HC = {'X': INK, 'o': PAPER, '.': NONE}
BIG_ANG = [0.0, math.degrees(math.atan2(1, 2)), 45.0, 90 - math.degrees(math.atan2(1, 2))]   # 22.5 is drawn on a 2:1 slope
PLATE = {'YOU': ('1', 9.5, 5.5), 'CYAN': ('2', 9.5, 5.5), 'WHITE': ('3', 9.5, 13.5), 'PINK': ('4', 9.5, 12.5), 'GREEN': ('5', 9.5, 10.5)}
DIGIT = {'1': [".o.", "oo.", ".o.", ".o.", "ooo"], '2': ["oo.", "..o", ".o.", "o..", "ooo"], '3': ["oo.", "..o", ".o.", "..o", "oo."],
         '4': ["o.o", "o.o", "ooo", "..o", "..o"], '5': ["ooo", "o..", "oo.", "..o", "oo."]}
def big_art():
    import re
    t = open(os.path.join(HERE, 'big_car_art.txt')).read(); got = {}
    for m in re.finditer(r'== (\w+) big heading 0 ==\n((?:[Xo.]{20}\n){20})', t):
        rows = m.group(2).split()
        assert rows[19] == '.' * 20 and all(r[19] == '.' for r in rows), m.group(1)
        g = [[NONE] * GN for _ in range(GN)]
        for y in range(BN):
            for x in range(BN): g[y + GO][x + GO] = HC[rows[y][x]]
        got[NAMES.index(m.group(1))] = g
    return got
def bturn(g, deg, n=4):
    """Each pixel the majority of 16 sample points of the drawing turned about the grid's middle:
    empty only if mostly empty, else ink unless paper clearly wins (as tools/turn_car.py)."""
    c = GN / 2; th = math.radians(deg); out = []
    for py in range(GN):
        r = []
        for px in range(GN):
            cnt = {INK: 0, PAPER: 0, NONE: 0}
            for sy in range(n):
                for sx in range(n):
                    dx, dy = px + (sx + .5) / n - c, py + (sy + .5) / n - c
                    lx = dx * math.cos(th) + dy * math.sin(th); ly = -dx * math.sin(th) + dy * math.cos(th)
                    x, y = math.floor(lx + c), math.floor(ly + c)
                    cnt[g[y][x] if 0 <= x < GN and 0 <= y < GN else NONE] += 1
            r.append(NONE if cnt[NONE] > n * n // 2 else PAPER if cnt[PAPER] > cnt[INK] else INK)
        out.append(r)
    return out
def bsym45(g):                                  # the 45 degree drawing: the same either side of the car's own line
    g = [r[:] for r in g]; M = GN - 1
    for y in range(GN):
        for x in range(GN):
            a, b = g[y][x], g[M - x][M - y]
            if a != b: g[y][x] = g[M - x][M - y] = INK if INK in (a, b) else PAPER
    return g
def bmdiag(g): return [[g[GN - 1 - c][GN - 1 - r] for c in range(GN)] for r in range(GN)]
def brot(g): return [[g[GN - 1 - c][r] for c in range(GN)] for r in range(GN)]
def big_turned():
    """The 22.5 and 45 degree drawings on the 27 x 27 grid: read from big_car_art_27.txt, which
    is written from the upright drawings if it is not there yet."""
    import re
    p = os.path.join(HERE, 'big_car_art_27.txt'); up = big_art()
    if not os.path.exists(p):
        with open(p, 'w') as f:
            f.write("BREAKFAST RUN BIG CAR ART, ANGLED - 27 x 27, the car's middle on the grid's middle (row 13, column 13)\n"
                    "X = ink   o = paper   . = empty. Made by tools/make_data.py from Grant's upright drawings in\n"
                    "tools/big_car_art.txt, turned at FULL SIZE (14 Nov 2026). The game shows columns 2-25 (24 wide).\n"
                    "Edit these by hand to touch them up: make_data.py reads this file and never overwrites it\n"
                    "(delete it to have it made afresh). The race number turns with the car.\n\n")
            for k in sorted(up):
                for h, g in (('22.5', bturn(up[k], BIG_ANG[1])), ('45', bsym45(bturn(up[k], 45)))):
                    f.write('== %s big27 heading %s ==\n' % (NAMES[k], h) + '\n'.join(''.join(CH[v] for v in r) for r in g) + '\n\n')
    t = open(p).read(); got = {}
    for m in re.finditer(r'== (\w+) big27 heading ([\d.]+) ==\n((?:[Xo.]{27}\n){27})', t):
        got.setdefault(NAMES.index(m.group(1)), {})[m.group(2)] = [[HC[c] for c in r] for r in m.group(3).split()]
    return up, got
def stamp(g, k, h):
    """The race number upright on an angled heading (turned, a 3 x 5 number is mush): its plate's
    middle turned with the car, a solid block round it wherever the car is."""
    d, px, py = PLATE[NAMES[k]]; th = math.radians(BIG_ANG[h % 4] + 90 * (h // 4)); c = GN / 2
    dx, dy = px + GO - c, py + GO - c
    x0 = round(c + dx * math.cos(th) - dy * math.sin(th) - 1.5); y0 = round(c + dx * math.sin(th) + dy * math.cos(th) - 2.5)
    g = [r[:] for r in g]
    for j in range(-1, 6):
        for i in range(-1, 4):
            if g[y0 + j][x0 + i] != NONE:
                g[y0 + j][x0 + i] = PAPER if 0 <= j < 5 and 0 <= i < 3 and DIGIT[d][j][i] == 'o' else INK
    return g
BIG0, BIGT = big_turned()
def big_frames(k):
    n, nne, ne = BIG0[k], BIGT[k]['22.5'], BIGT[k]['45']
    f = [n, nne, ne, bmdiag(nne)]
    for i in range(4, 16): f.append(brot(f[i - 4]))
    return f                                   # (the number turns with the car - Grant, 14 Nov 2026: "I am not
                                               # concerned that the numbers don't show properly when cars are
                                               # turning"; stamp() would redraw it upright)
# The SMALL cars (Grant, 14 Nov 2026: "keep the ability to have two car options - the smaller cars
# and the bigger cars. We may end up going with smaller cars"): the 16 x 16 cars of tools/car_art.txt,
# which the race order on the right uses. CARS=small in the environment puts them in the game: each
# heading goes on the same grid, in the frame's first 16 columns - so a row is 2 bytes of picture
# and an empty third, which the draw routine skips (a third faster) - and the game draws the frame
# at the car's own x (CAR_U in src/options.asm). The price: no 1-pixel clear edge to the car's left
# and right (it keeps the one above and below). Frames, table and draw routine are otherwise the same.
SMALL_CARS = os.environ.get('CARS', 'big') == 'small'
def small_frames(k):
    out = []
    for g in (frames32_of(k) if HEAD32 and k in H32K else all_frames[k]):
        G = [[NONE] * GN for _ in range(GN)]
        for y in range(16):
            for x in range(16):
                v = g[y][x]
                G[y + 5][x + FX] = (INK if (x + y) % 2 == 0 else PAPER) if v == DITH else v
        out.append(G)
    return out
big_all = [small_frames(k) if SMALL_CARS else big_frames(k) for k in range(len(KINDS))]
assert not HEAD32 or (SMALL_CARS and not CHOOSE), 'HEAD32 is for the small cars, without the choose screen'
# MIRROR=1 (22 Nov 2026, room for HEAD32): a computer car's heading that is another's frame turned left for right (or that,
# upside down too) is not kept either - draw_car makes it from the other, mirrored, into a small buffer (dc_mirror, bit 6 of
# the rows). Not YOUR car (kind 0): in RACE mode every car is yours, so RACE never pays for the mirroring.
MIRROR = os.environ.get('MIRROR') in ('1', 'all')
MIRK = (lambda k: True) if os.environ.get('MIRROR') == 'all' else (lambda k: k > 0)
REV = [int('{:08b}'.format(v)[::-1], 2) for v in range(256)]
def mir(r): return [REV[r[2]], REV[r[3]], REV[r[0]], REV[r[1]]]
FLIP = os.environ.get('FLIP') == '1'            # FLIP=1 bash build.sh: headings that are another heading upside down are not kept (draw_car reads the rows last to first)
FLIP_OF = {5: 3, 6: 2, 7: 1, 8: 0, 9: 15, 10: 14, 11: 13}
assert not MIRROR or (SMALL_CARS and FLIP), 'MIRROR is for the small cars, with FLIP'
ROWB = 4 if SMALL_CARS else 6                  # bytes a frame row: a small car's third pair is always empty, so it is not kept (14 Nov 2026)
def big_bytes(g):
    """The frame: grid columns 2..25 (24 wide), grid row r is frame row r + 1 (room for the halo
    above row 0). Returns (first row in use, the rows' bytes: mask0, ink0, mask1, ink1, mask2, ink2)."""
    H = GN + 2
    solid = [[0 <= y - 1 < GN and g[y - 1][x + FX] != NONE for x in range(FW)] for y in range(H)]
    rows = []
    for y in range(H):
        m = [1 if any(solid[y + j][x + i] for j in (-1, 0, 1) for i in (-1, 0, 1) if 0 <= y + j < H and 0 <= x + i < FW) else 0 for x in range(FW)]
        if SMALL_CARS: m[16:] = [0] * (FW - 16)       # (the small cars: 2 bytes a row)
        k = [1 if 0 <= y - 1 < GN and g[y - 1][x + FX] == INK else 0 for x in range(FW)]
        rows.append((any(m), [int(''.join(map(str, v[b * 8:b * 8 + 8])), 2) for b in range(ROWB // 2) for v in (m, k)]))
    used = [y for y in range(H) if rows[y][0]]
    return used[0], [rows[y][1] for y in range(used[0], used[-1] + 1)]
BIG_LO = 0x2100                                # room below the program for the big cars (0x5F00-0x7FFF)
def big_layout():
    """Every frame's bytes, in order; those that fit below the program go there, the rest above."""
    lo, hi, tab, room = [], [], [], BIG_LO - (256 + 4 * 17 if MIRROR else 0)
    if os.environ.get('BIG_LO_ROOM'): room = int(os.environ['BIG_LO_ROOM'])     # (HEAD32=all, 22 Nov 2026: only this many bytes of frames under 0x8000 - the rest go in the program)
    for k in range(len(KINDS)):
        fr = [big_bytes(g) for g in big_all[k]]
        N = len(big_all[k]); kept = set()
        for h, g in enumerate(big_all[k]):
            first, rows = fr[h]; n = ROWB * len(rows)
            src = FLIP_OF.get(h) if FLIP and N == 16 and not (MIRROR and MIRK(k)) else None
            if FLIP and (N == 32 or (MIRROR and MIRK(k))):      # (HEAD32 / MIRROR: any kept heading it is upside down, mirrored, or both)
                last = lambda s: 'bf_%d_%d+%d' % (k, s, ROWB * (len(fr[s][1]) - 1))
                for s in sorted(kept):
                    rs = fr[s][1]
                    if rs[::-1] == rows: tab.append((k, h, first, len(rows) | 0x80, last(s))); break
                    if MIRROR and MIRK(k) and [mir(r) for r in rs] == rows: tab.append((k, h, first, len(rows) | 0x40, 'bf_%d_%d' % (k, s))); break
                    if MIRROR and MIRK(k) and [mir(r) for r in rs[::-1]] == rows: tab.append((k, h, first, len(rows) | 0xC0, last(s))); break
                else: src = None; kept.add(h)
                if h not in kept: continue
            elif src is not None and fr[src][1][::-1] == rows:      # FLIP=1: this heading is heading `src` upside down, pixel for pixel:
                tab.append((k, h, first, len(rows) | 0x80, 'bf_%d_%d+%d' % (k, src, ROWB * (len(rows) - 1)))); continue   # not kept - drawn from src's last row up
            if k >= 5: hi.append((k, h, rows)); tab.append((k, h, first, len(rows), 'bf_%d_%d' % (k, h))); continue   # (CHOOSE: the two extra cars)
            dest = lo if n <= room else hi
            if dest is lo: room -= n
            dest.append((k, h, rows)); tab.append((k, h, first, len(rows), 'bf_%d_%d' % (k, h)))
    return lo, hi, tab
def write_frames(f, frames):
    for k, h, rows in frames:
        f.write('bf_%d_%d:                        ; %s, heading %d: %d rows\n' % (k, h, NAMES[k], h, len(rows)))
        for r in rows: f.write('        defb ' + ','.join('0x%02X' % v for v in r) + '\n')


if __name__ == '__main__':
    with open(OUT, 'w') as f:
        f.write('; GENERATED by tools/make_data.py - do not edit by hand\n\n')
        with open(os.path.join(HERE, '..', 'src', 'thrust.asm'), 'w') as t:   # (kept in the buffer's
            t.write('; GENERATED by tools/make_data.py - do not edit by hand\n')  # bottom rows: BUFD)
            t.write('; thrust per frame for each of 16 headings: dx, dy in 8.8 fixed point\nthrust_tab_src:\n')
            for n in range(16):
                th = n * 2 * math.pi / 16
                dx, dy = round(64 * math.sin(th)), round(-64 * math.cos(th))
                t.write('        dw 0x%04X,0x%04X\n' % (dx & 0xFFFF, dy & 0xFFFF))
        f.write('\n; the race order\'s car pictures: each car facing right (its heading 4) at 16 x 16,\n')
        f.write('; 16 rows of mask left, ink left, mask right, ink right (64 bytes a car)\n        if 1-OPT_TOWERF         ; (BRIDGE, track 5: drawn from the frames instead - tower_b, hud.asm)\ntower_cars:\n')
        for k in range(len(KINDS)):
            g = all_frames[k][4]
            for (a, b), (ma, mb) in zip(rows_bytes(ink_of(g)), rows_bytes(mask_of(g))):
                f.write('        defb %%%s,%%%s,%%%s,%%%s\n' % tuple(format(v, '08b') for v in (ma, a, mb, b)))
        f.write('        endif\n')
        lo, hi, tab = big_layout()
        f.write('\n; BIG_TAB: each car\'s 16 headings: the frame\'s address, its first row, its rows\n')
        f.write('; (frames are 24 wide - 3 (mask, ink) byte pairs a row - and only the rows in use are kept)\nbig_tab:\n')
        for k, h, first, n, lab in tab:
            if k < 5: f.write('        dw %s\n        db %d,%d\n' % (lab, first, n))
        f.write('\n; the big-car frames that did not fit below the program (%d bytes)\n' % sum(ROWB * len(r) for _, _, r in hi))
        write_frames(f, [v for v in hi if v[0] < 5])
    if CHOOSE:
        with open(os.path.join(HERE, '..', 'src', 'cars_hp.asm'), 'w') as f:
            f.write('; GENERATED by tools/make_data.py (CHOOSE=1) - the choose screen\'s two extra cars: their part of the\n')
            f.write('; cars\' table (as big_tab: 16 headings a car), then their frames. Kept above the screen-copy routine (src/hp.asm).\ncar_tab2:\n')
            for k, h, first, n, lab in tab:
                if k >= 5: f.write('        dw %s\n        db %d,%d\n' % (lab, first, n))
            write_frames(f, [v for v in hi if v[0] >= 5])
            f.write('car_names:                      ; every car\'s name, as the choose screen shows it\n')
            for n in NAMES: f.write('        db "%s",0\n' % SHOWN[n])
            f.write('NCAR    equ %d                  ; cars to choose from\n' % len(NAMES))
        for k in range(5, len(NAMES)):
            print('CHOOSE: extra car %s (%s): %d bytes of frames (%d of 16 headings kept), 64 of table, %d of name' % (
                NAMES[k], SHOWN[NAMES[k]], sum(ROWB * len(r) for kk, _, r in hi if kk == k), sum(1 for kk, _, r in hi if kk == k), len(SHOWN[NAMES[k]]) + 1))
    with open(os.path.join(HERE, '..', 'src', 'bigcars.asm'), 'w') as f:
        f.write('; GENERATED by tools/make_data.py - do not edit by hand\n')
        f.write('; the big-car frames, below the program (0x5F00-0x7FFF): %d bytes of %d\n' % (sum(ROWB * len(r) for _, _, r in lo), BIG_LO))
        if MIRROR:
            f.write('rev_tab:                        ; MIRROR: each byte with its bits the other way round (dc_mirror; at 0x5F00, on its own page)\n')
            for i in range(0, 256, 16): f.write('        defb ' + ','.join('0x%02X' % v for v in REV[i:i + 16]) + '\n')
            f.write('dm_buf:  defs 4*17                ; MIRROR: the mirrored frame, made by dc_mirror\n')
        write_frames(f, lo)
    print(('SMALL' if SMALL_CARS else 'big') + ' cars: %d bytes below the program, %d above, table %d; tallest frame %d rows' % (
        sum(ROWB * len(r) for _, _, r in lo), sum(ROWB * len(r) for k, _, r in hi if k < 5), 4 * len([v for v in tab if v[0] < 5]), max(n & 0x3F for _, _, _, n, _ in tab)))
    with open(os.path.join(HERE, '..', 'src', 'sqtab.asm'), 'w') as f:
        f.write('; GENERATED by tools/make_data.py - do not edit by hand\n')
        f.write('; quarter squares / 32: n * n / 128 for n = 0..383, 2 bytes each (grip.asm:\n')
        f.write('; a * b / 32 = sq(a + b) - sq(|a - b|), a up to 255, b up to 128)\nsqtab:\n')
        q = [round(n * n / 128) for n in range(384)]
        for i in range(0, 384, 12):
            f.write('        dw ' + ','.join(str(v) for v in q[i:i + 12]) + '\n')
    with open(os.path.join(HERE, '..', 'src', 'sq4.asm'), 'w') as f:
        f.write('; GENERATED by tools/make_data.py - do not edit by hand\n')
        f.write('\n; quarter squares: n*n/4 for n = 0..127, low bytes then high bytes,\n')
        f.write('; so a*b = sq4(a+b) - sq4(a-b) needs two look-ups instead of a loop\n')
        f.write('        defs (256 - ($ & 255)) & 255\nsq4:\n')
        q = [n * n // 4 for n in range(128)]
        for i in range(0, 128, 16):
            f.write('        defb ' + ','.join(str(v & 255) for v in q[i:i + 16]) + '\n')
        for i in range(0, 128, 16):
            f.write('        defb ' + ','.join(str(v >> 8) for v in q[i:i + 16]) + '\n')
    # preview sheet: rows = cars, columns = headings 0-3 at 1x, 2x and 6x, on a busy track
    from PIL import Image
    S = 6
    img = Image.new('RGB', (16 * 18 * S, len(KINDS) * 18 * S + 20), (255, 255, 255))
    for k in range(len(KINDS)):
        for n in range(16):
            g = all_frames[k][n]; ink = ink_of(g); m = mask_of(g)
            for y in range(16):
                for x in range(16):
                    bg = (210, 210, 210) if m[y][x] == 0 else (255, 255, 255)
                    c = (0, 0, 0) if ink[y][x] else bg
                    for a in range(S):
                        for b in range(S):
                            img.putpixel(((n * 18 + 1 + x) * S + a, (k * 18 + 1 + y) * S + b), c)
    img.save(os.path.join(HERE, '..', 'build', 'cars_preview.png'))
    print('wrote', os.path.normpath(OUT))
