"""Title / attract screen DESIGN mock-ups - pictures only, nothing here is in the game.

Grant, 14 Nov 2026: "then we need a title/attract screen. The logo, keys customization option,
hi-score, 1 or 2 player. When the game starts, the player chooses a car and personality - we
need another 5 to choose from. So they choose a face/personality, then they choose a car ...
Each car has strengths and weaknesses which we will tweak as we go along. The game will later
on allow for two players to play"
and: "then please have another agent run to build the title/attract screen - open to ideas on
the design, but want the person to see they choose 1UP or 2UP to play, K to customize keys, have
the title screen have some kind of attract sequence showing the different drivers, maybe a face
and have that car skid around - open to ideas"

Every screen is built the way the earlier mock-ups were (tools/make_layout_review.py), so it can
really be drawn on a Spectrum: a 256 x 192 array of pixels (bits) and a 24 x 32 array of colour
cells (attrs: one ink and one paper per 8 x 8 cell, BRIGHT per cell, FLASH per cell), yellow
border. Letters are the ROM's own 8 x 8 font, plain or doubled. Anything that moves does so
inside ONE colour pair (blue on cyan cloth, or black on the yellow table), so nothing clashes.

Art used:   the logo (build/logo.txt), the faces (tools/face_art.txt: YOU; tools/new_cast_art.txt:
            BUN, SPECS2, CURLS, CAP, SHADES - first drafts), the game's small 16 x 16 cars with
            their real 16 headings (tools/make_data.py: all_frames), and the five new cars
            (tools/new_cast_art.txt: 20 x 20 first drafts, drawn facing up only - their other 15
            headings here are that drawing turned by make_data.bturn, the tool that turned the
            big cars; DRAFTS for Grant to redraw at 16 x 16).
Made up:    every name, one-liner and strength number; the lap record and who holds it; the
            second player's keys.

Writes, in docs/design/:
  title_options.png   three title layouts side by side (3x) with notes
  title_attract.gif   the recommended title (A) with the attract sequence, 12.5 frames a second
  title_flow.png      the keys screen, choose-driver, choose-car and the order of the screens
Usage: python3 tools/make_title_mockups.py"""
import math, os, re, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
from make_layout_review import render, FONT      # the Spectrum screen renderer and the ROM font
import make_data as M                            # the game's cars: 16 headings each
OUT = os.path.join(ROOT, 'docs', 'design')

# ---------------------------------------------------------------- colours (attribute bytes)
TABLE = 0x30        # black on yellow: the kitchen table (and the border is yellow)
CLOTH = 0x29        # blue on cyan: the cloth, as the game's play window
FRAME = 0x31        # blue on yellow: the slim frame round a cloth window
CARD = 0x78         # black on bright white
HEAD = 0x4F         # bright white on blue: headings
P1 = 0x57           # bright white on red: 1UP (your colour in the race)
P2 = 0x4F           # bright white on blue: 2UP
KEY = 0x47          # bright white on black: a key cap
RATE = (0x79, 0x7A, 0x7B)   # GRIP blue, SPEED red, ACCEL magenta - on a white card
FLASH = 0x80

# ---------------------------------------------------------------- the cast (ALL NAMES MADE UP)
def _faces():
    got = {}
    for fn in ('face_art.txt', 'new_cast_art.txt'):
        t = open(os.path.join(HERE, fn)).read()
        for m in re.finditer(r'== (\w+) face ==[^\n]*\n((?:[X.]{16}\n){16})', t):
            got[m.group(1)] = np.array([[c == 'X' for c in r] for r in m.group(2).split()], dtype=np.uint8)
    return got
FACES = _faces()
# face art, name (two short words), lady/man, tile colour, one-liner (two lines of 13), favourite car
DRIVERS = [
    ('YOU',    ('EGGS', 'BENNY'),   'man',  0x57, ('COOL HEAD,', 'SUNNY SIDE UP'), 0),
    ('BUN',    ('HONEY', 'BUN'),    'lady', 0x58, ('SWEET TALKER,', 'ROUGH DRIVER'), 3),
    ('CAP',    ('OLD', 'KIPPER'),   'man',  0x60, ('SLOW TO WAKE,', 'HARD TO PASS'), 5),
    ('SPECS2', ('MISS', 'MUESLI'),  'lady', 0x68, ('HAS DONE THE', 'MATHS ON YOU'), 2),
    ('SHADES', ('HARD', 'BOILED'),  'man',  0x38, ('NEVER CRACKS.', 'NEVER SMILES.'), 1),
    ('CURLS',  ('LOOPY', 'LOU'),    'lady', 0x70, ('FLAT OUT OR', 'NOT AT ALL'), 4),
]
# art, name, (GRIP, SPEED, ACCEL) each 1-5, a line about it
CARS = [
    ('YOU',       'TOASTER',     (3, 3, 3), 'GOOD AT EVERYTHING'),
    ('OFFROAD',   'MUD MUFFIN',  (5, 2, 2), 'STICKS LIKE JAM'),
    ('PICKUP',    'BUTTY TRUCK', (3, 4, 2), 'HEAVY, BUT IT SHIFTS'),
    ('BUGGY',     'BEAN BUGGY',  (2, 2, 5), 'OFF LIKE A SHOT'),
    ('HOTROD',    'ESPRESSO',    (2, 5, 2), 'FAST. SLIDES A LOT.'),
    ('MILKFLOAT', 'MILK FLOAT',  (4, 1, 4), 'STEADY. NEVER FAST.'),
]
RECORD = ('0:41.2', 'HONEY BUN')                 # made up
ICONS = {'grip':  [".XXXXX.", "XX...XX", "X..X..X", "XX...XX", ".XXXXX."],     # a tyre
         'speed': ["X...X..", ".X...X.", "..X...X", ".X...X.", "X...X.."],     # fast forward
         'accel': ["...XX..", "..XX...", ".XXXXX.", "...XX..", "..XX..."]}     # a bolt (as the race screen's)
PARTS = ('grip', 'speed', 'accel'); LABELS = ('GRIP', 'SPEED', 'ACCEL')

# ---------------------------------------------------------------- the cars: sprites for 16 headings
def _sprites():
    """For each of the six cars: 16 headings of (ink, mask, size). The game's car: 16 x 16, the real
    frames. A new car: its 20 x 20 draft on make_data's 27 x 27 grid, turned by make_data.bturn."""
    out = []
    for art, _, _, _ in CARS:
        if art in M.NAMES:
            fr = M.all_frames[M.NAMES.index(art)]
            out.append([(np.array(M.ink_of(g), dtype=np.uint8), np.array(M.mask_of(g), dtype=np.uint8)) for g in fr])
            continue
        t = open(os.path.join(HERE, 'new_cast_art.txt')).read()
        rows = re.search(r'== %s big heading 0 ==[^\n]*\n((?:[Xo.]{20}\n){20})' % art, t).group(1).split()
        g = [[M.NONE] * M.GN for _ in range(M.GN)]
        for y in range(M.BN):
            for x in range(M.BN): g[y + M.GO][x + M.GO] = M.HC[rows[y][x]]
        f = [g, M.bturn(g, M.BIG_ANG[1]), M.bsym45(M.bturn(g, 45))]; f.append(M.bmdiag(f[1]))
        for i in range(4, 16): f.append(M.brot(f[i - 4]))
        sp = []
        for q in f:
            q = np.array(q); ink = (q == M.INK).astype(np.uint8); solid = np.pad(q != M.NONE, 1)
            mask = np.zeros_like(ink)
            for j in range(3):
                for i in range(3): mask |= solid[j:j + M.GN, i:i + M.GN]
            sp.append((ink, mask))
        out.append(sp)
    return out
SPR = _sprites()

# ---------------------------------------------------------------- drawing on the Spectrum screen
def new(paper=TABLE):
    return np.zeros((192, 256), dtype=np.uint8), np.full((24, 32), paper, dtype=np.uint8)
def fill(a, c0, r0, w, h, at): a[r0:r0 + h, c0:c0 + w] = at
def glyph(ch):
    g = FONT[(ord(ch) - 32) * 8:(ord(ch) - 32) * 8 + 8]
    return np.array([[(v >> (7 - i)) & 1 for i in range(8)] for v in g], dtype=np.uint8)
def rom(b, s, x, y, k=1):                        # ROM letters at pixel (x, y), k times the size
    for n, ch in enumerate(s):
        b[y:y + 8 * k, x + 8 * k * n:x + 8 * k * (n + 1)] = np.kron(glyph(ch), np.ones((k, k), dtype=np.uint8))
def txt(b, s, c, r, k=1): rom(b, s, c * 8, r * 8, k)
def ctr(b, s, c0, w, r, k=1): rom(b, s, c0 * 8 + (w * 8 - 8 * k * len(s)) // 2, r * 8, k)   # centred on w cells
def bar(b, a, s, c0, r, w, at=HEAD): fill(a, c0, r, w, 1, at); ctr(b, s, c0, w, r)
def put(b, art, x, y, k=1):
    art = np.kron(art, np.ones((k, k), dtype=np.uint8)); b[y:y + art.shape[0], x:x + art.shape[1]] = art
def stamp(b, rows, x, y):
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch == 'X': b[y + j, x + i] = 1
def box(b, x0, y0, x1, y1, t=1):                 # a rounded frame t pixels thick
    for k in range(t):
        b[y0 + k, x0 + 2:x1 - 1] = 1; b[y1 - k, x0 + 2:x1 - 1] = 1
        b[y0 + 2:y1 - 1, x0 + k] = 1; b[y0 + 2:y1 - 1, x1 - k] = 1
    for (x, y) in ((x0 + 1, y0 + 1), (x1 - 1, y0 + 1), (x0 + 1, y1 - 1), (x1 - 1, y1 - 1)): b[y, x] = 1
    if t > 1:
        for (x, y) in ((x0 + 2, y0 + 2), (x1 - 2, y0 + 2), (x0 + 2, y1 - 2), (x1 - 2, y1 - 2)): b[y, x] = 1
LOGO = np.array([[c == '#' for c in r] for r in open(os.path.join(ROOT, 'build', 'logo.txt')).read().split()], dtype=np.uint8)
def logo(b, a, c, r, k=1):
    """The game's logo, k times the size (56 x 16: 7 x 2 cells; its colours fall on cells at any k):
    BREAKFAST black on the table, RUN red, the egg white."""
    put(b, LOGO, c * 8, r * 8, k)
    fill(a, c, r, 7 * k, k, TABLE); fill(a, c, r + k, 5 * k, k, 0x72); fill(a, c + 5 * k, r + k, 2 * k, k, 0x77)
def cloth(b, a, c0, r0, w, h, frame=True):
    """A cloth window on whole cells: the game's 32-pixel checks (dark ones dotted), blue on cyan,
    and its slim blue frame, which lies in the ring of table cells round it."""
    for y in range(r0 * 8, (r0 + h) * 8):
        for x in range(c0 * 8, (c0 + w) * 8):
            u, v = x - c0 * 8, y - r0 * 8
            b[y, x] = ((u // 32 + v // 32) % 2 == 1) and ((v % 4 == 0 and u % 4 == 2) or (v % 4 == 2 and u % 4 == 0))
    fill(a, c0, r0, w, h, CLOTH)
    if frame:
        a[r0 - 1, c0 - 1:c0 + w + 1] = FRAME; a[r0 + h, c0 - 1:c0 + w + 1] = FRAME
        a[r0 - 1:r0 + h + 1, c0 - 1] = FRAME; a[r0 - 1:r0 + h + 1, c0 + w] = FRAME
        box(b, c0 * 8 - 5, r0 * 8 - 5, (c0 + w) * 8 + 4, (r0 + h) * 8 + 4, 2)
def face(b, a, key, c, r, k=2, at=None):         # a driver's face in its colour tile, k x 16 pixels
    put(b, FACES[DRIVERS[key][0]], c * 8, r * 8, k); fill(a, c, r, 2 * k, 2 * k, DRIVERS[key][3] if at is None else at)
def cap(b, a, s, c, r, k=1):                     # a key cap: white on black
    txt(b, s, c, r, k); fill(a, c, r, len(s) * k, k, KEY)
def pips(b, a, lv, c, r, i, wide=1):             # five pips, one per cell (or two cells wide)
    for j in range(5):
        x, y = (c + j * wide) * 8, r * 8
        b[y + 1:y + 7, x + 1:x + wide * 8 - 1] = 1
        if j >= lv: b[y + 2:y + 6, x + 2:x + wide * 8 - 2] = 0
    fill(a, c, r, 5 * wide, 1, RATE[i])
def rating_rows(b, a, lv, c, r, label=True, wide=1, step=1):
    """GRIP, SPEED, ACCEL: icon, word, five pips - one cell row each, one colour each."""
    for i in range(3):
        y = r + i * step
        stamp(b, ICONS[PARTS[i]], c * 8, y * 8 + 1); a[y, c] = RATE[i]
        if label: txt(b, LABELS[i], c + 1, y); fill(a, c + 1, y, 6, 1, RATE[i])
        pips(b, a, lv[i], c + (7 if label else 2), y, i, wide)
def mini_ratings(b, a, lv, c, r):
    """The race screen's little set-up box (4 x 3 cells): three rows of icon + five 3 x 5 pips."""
    x0, y0 = c * 8, r * 8; fill(a, c, r, 4, 3, CARD); box(b, x0, y0, x0 + 31, y0 + 23)
    for i in range(3):
        y = y0 + 3 + 7 * i; stamp(b, ICONS[PARTS[i]], x0 + 2, y)
        for j in range(5):
            x = x0 + 11 + 4 * j; b[y:y + 5, x:x + 3] = 1
            if j >= lv[i]: b[y + 1:y + 4, x + 1] = 0
def draw_car(b, car, h, cx, cy, clip, k=1):
    """Car `car` at heading h (0 = up, clockwise, 16 to the turn), its middle at (cx, cy), masked
    (a 1-pixel clear edge) and cut off at the window's edge: clip = (x0, y0, x1, y1)."""
    ink, mask = SPR[car][h % 16]
    if k > 1: ink = np.kron(ink, np.ones((k, k), dtype=np.uint8)); mask = np.kron(mask, np.ones((k, k), dtype=np.uint8))
    n = ink.shape[0]; x0, y0 = int(round(cx - n / 2)), int(round(cy - n / 2))
    for j in range(n):
        for i in range(n):
            x, y = x0 + i, y0 + j
            if mask[j, i] and clip[0] <= x < clip[2] and clip[1] <= y < clip[3]: b[y, x] = ink[j, i]

# ---------------------------------------------------------------- the attract sequence: one car's skid
SS = 16                                          # the skid marks are worked out 16 times a frame
def _resample(pts, n):                           # n + 1 points, evenly spaced along the line
    d = [0.0]
    for p, q in zip(pts, pts[1:]): d.append(d[-1] + math.hypot(q[0] - p[0], q[1] - p[1]))
    out = []; j = 0
    for i in range(n + 1):
        s = d[-1] * i / n
        while j < len(d) - 2 and d[j + 1] < s: j += 1
        t = (s - d[j]) / max(d[j + 1] - d[j], 1e-9)
        out.append((pts[j][0] + t * (pts[j + 1][0] - pts[j][0]), pts[j][1] + t * (pts[j + 1][1] - pts[j][1])))
    return out
def _line(p, q, n=20): return [(p[0] + (q[0] - p[0]) * i / n, p[1] + (q[1] - p[1]) * i / n) for i in range(n + 1)]
def path_circle(w, h, R, ccw=True):              # in along the bottom, once round, out the far side
    cx, cy = w / 2, h / 2; s = 1 if ccw else -1
    arc = [(cx + s * R * math.sin(t), cy + R * math.cos(t)) for t in [2 * math.pi * i / 80 for i in range(81)]]
    return _line((cx - s * (w / 2 + 16), cy + R), (cx, cy + R)) + arc + _line((cx, cy + R), (cx + s * (w / 2 + 16), cy + R))
def path_eight(w, h, A, B):                      # in from the left, a figure of eight, out to the right
    cx, cy = w / 2, h / 2
    e = [(cx + A * math.sin(t), cy - B * math.sin(2 * t)) for t in [2 * math.pi * i / 120 for i in range(121)]]
    return _line((-16, cy + 2 * B), (cx - A * .5, cy + B * .9), 12)[:-1] + _line((cx - A * .5, cy + B * .9), (cx, cy), 8)[:-1] + e + _line((cx, cy), (cx + A * .6, cy - B)) [1:] + _line((cx + A * .6, cy - B), (w + 16, cy - B))[1:]
def skid(path, frames, gain=1.6, spin=None, wheel=(5, 3)):
    """A car driven along `path` in `frames` frames. It DRIFTS: the nose points into the bend, ahead
    of the way it is going, by more the tighter the bend (up to 60 degrees). spin = (first, last,
    turns): it also spins that many whole turns between those frames. Returns, per frame, the middle
    (x, y), the heading 0-15 and the skid-mark pixels laid since the frame before (the two rear
    wheels, while it slides)."""
    n = frames * SS; P = _resample(path, n)
    phi = [math.atan2(P[min(i + 1, n)][0] - P[max(i - 1, 0)][0], -(P[min(i + 1, n)][1] - P[max(i - 1, 0)][1])) for i in range(n + 1)]
    for i in range(1, n + 1):                    # unwrap
        while phi[i] - phi[i - 1] > math.pi: phi[i] -= 2 * math.pi
        while phi[i] - phi[i - 1] < -math.pi: phi[i] += 2 * math.pi
    slide = [0.0] * (n + 1)
    for i in range(n + 1):
        lo, hi = max(i - SS, 0), min(i + SS, n)
        rate = (phi[hi] - phi[lo]) / (hi - lo) * SS            # the turn per frame
        slide[i] = max(-1.05, min(1.05, rate * gain))
    for _ in range(3):                           # ease the slide in and out
        slide = [sum(slide[max(i - SS, 0):i + SS + 1]) / len(slide[max(i - SS, 0):i + SS + 1]) for i in range(n + 1)]
    out = []
    for f in range(frames + 1):
        marks = []
        for i in range(max((f - 1) * SS, 0), f * SS + 1):
            th = phi[i] + slide[i]; sl = abs(slide[i])
            if spin and spin[0] * SS <= i <= spin[1] * SS:
                u = (i - spin[0] * SS) / ((spin[1] - spin[0]) * SS)
                th += 2 * math.pi * spin[2] * (u * u * (3 - 2 * u)); sl = 1
            if sl > 0.3:
                fx, fy = math.sin(th), -math.cos(th)
                for sgn in (-1, 1):
                    marks.append((int(P[i][0] - wheel[0] * fx + sgn * wheel[1] * fy), int(P[i][1] - wheel[0] * fy - sgn * wheel[1] * fx)))
        out.append((P[f * SS][0], P[f * SS][1], int(round(th / (math.pi / 8))) % 16, marks))
    return out
def stage(b, run, f, car, x0, y0, w, h):         # the stage at frame f: the marks so far, then the car
    for g in range(min(f, len(run) - 1) + 1):
        for (x, y) in run[g][3]:
            if 0 <= x < w and 0 <= y < h: b[y0 + y, x0 + x] = 1
    x, y, hd, _ = run[min(f, len(run) - 1)]
    draw_car(b, car, hd, x0 + x, y0 + y, (x0, y0, x0 + w, y0 + h))

# ---------------------------------------------------------------- TITLE, option A (recommended)
A_STAGE = (2, 5, 14, 12)                         # the cloth window: cells (col, row, wide, high)
def menu(b, a, r):
    """1UP / 2UP / KEYS as three big buttons, each with the key that picks it as a key cap."""
    cap(b, a, '1', 1, r, 2); txt(b, '1UP', 3, r, 2); fill(a, 3, r, 6, 2, P1); txt(b, '1 PLAYER', 1, r + 2)
    cap(b, a, '2', 11, r, 2); txt(b, '2UP', 13, r, 2); fill(a, 13, r, 6, 2, P2); txt(b, '2 PLAYERS', 11, r + 2)
    cap(b, a, 'K', 21, r, 2); txt(b, 'KEYS', 23, r, 2); fill(a, 23, r, 8, 2, CARD); txt(b, 'REDEFINE', 23, r + 2)
def record(b, a, c, r, w=14):
    bar(b, a, 'LAP RECORD', c, r, w); ctr(b, RECORD[0], c, w, r + 1, 2); ctr(b, 'BY ' + RECORD[1], c, w, r + 3)
def driver_card(b, a, d, c, r):
    """13 x 12 cells: who it is (face twice the size, name, one-liner) and the car they like best
    with its three strengths."""
    key, name, _, tile, line, car = DRIVERS[d]
    fill(a, c, r, 13, 12, CARD); bar(b, a, 'DRIVER %d OF %d' % (d + 1, len(DRIVERS)), c, r, 13)
    face(b, a, d, c, r + 1); txt(b, name[0], c + 5, r + 2); txt(b, name[1], c + 5, r + 3)
    ctr(b, line[0], c, 13, r + 5); ctr(b, line[1], c, 13, r + 6)
    bar(b, a, CARS[car][1], c, r + 8, 13, 0x07 | 0x40)
    rating_rows(b, a, CARS[car][2], c, r + 9)
def title_a(d=1, run=None, f=0):
    b, a = new()
    logo(b, a, 1, 0, 2); record(b, a, 17, 0)
    c, r, w, h = A_STAGE; cloth(b, a, c, r, w, h)
    if run: stage(b, run, f, DRIVERS[d][5], c * 8, r * 8, w * 8, h * 8)
    driver_card(b, a, d, 18, 5)
    menu(b, a, 19)
    txt(b, 'PRESS 1 OR 2 TO START', 5, 23); fill(a, 5, 23, 21, 1, TABLE | FLASH)
    return b, a
def runs_a():                                    # a different party trick for each driver
    w, h = A_STAGE[2] * 8, A_STAGE[3] * 8
    return {0: skid(path_circle(w, h, 30), 33),
            1: skid(path_eight(w, h, 34, 20), 33, gain=1.3),
            2: skid(path_circle(w, h, 26, ccw=False), 33, wheel=(7, 5)),
            3: skid(path_eight(w, h, 30, 22), 33, gain=1.3, wheel=(7, 5)),
            4: skid(_line((-16, h / 2 + 14), (w + 16, h / 2 - 14), 60), 33, spin=(9, 25, 2), wheel=(6, 5)),
            5: skid(path_circle(w, h, 32), 33, wheel=(8, 5))}

# ---------------------------------------------------------------- TITLE, option B: big logo, wide stage
def title_b(d=5, f=19):
    b, a = new(); key, name, _, tile, line, car = DRIVERS[d]
    logo(b, a, 5, 0, 3)                          # three times the size: 21 x 6 cells
    cap(b, a, '1', 27, 1); txt(b, '1UP', 28, 1); fill(a, 28, 1, 3, 1, P1)
    cap(b, a, '2', 27, 3); txt(b, '2UP', 28, 3); fill(a, 28, 3, 3, 1, P2)
    cap(b, a, 'K', 0, 1); txt(b, 'KEYS', 1, 1); fill(a, 1, 1, 4, 1, CARD)
    cloth(b, a, 1, 8, 30, 8)
    run = skid(path_eight(240, 64, 80, 20), 34, gain=2.2, wheel=(7, 5))
    stage(b, run, f, car, 8, 64, 240, 64)
    fill(a, 1, 17, 30, 4, CARD)
    face(b, a, d, 1, 17); txt(b, ' '.join(name), 6, 17); txt(b, line[0], 6, 18); txt(b, line[1], 6, 19)
    fill(a, 6, 20, 12, 1, 0x47); txt(b, CARS[car][1], 6, 20)
    rating_rows(b, a, CARS[car][2], 19, 17)
    txt(b, 'BEST ' + RECORD[0], 19, 20)
    txt(b, 'PRESS 1 OR 2 TO START', 5, 23); fill(a, 5, 23, 21, 1, TABLE | FLASH)
    return b, a

# ---------------------------------------------------------------- TITLE, option C: the line-up
def cursor(b, a, c, r, at, size=4):
    """Round a size x size tile at cell (c, r): a 2-pixel frame in the ring of table cells round it,
    in the player's colour (`at` is the player's block colour: its paper is the frame's ink)."""
    ink = 0x30 | ((at >> 3) & 7)
    fill(a, c - 1, r - 1, size + 2, 1, ink); fill(a, c - 1, r + size, size + 2, 1, ink)
    fill(a, c - 1, r, 1, size, ink); fill(a, c + size, r, 1, size, ink)
    box(b, c * 8 - 4, r * 8 - 4, (c + size) * 8 + 3, (r + size) * 8 + 3, 2)
def title_c(d=3, f=22):
    b, a = new(); key, name, _, tile, line, car = DRIVERS[d]
    logo(b, a, 9, 0, 2)
    txt(b, 'LAP', 2, 0); txt(b, 'RECORD', 2, 1); txt(b, RECORD[0], 2, 2); fill(a, 2, 2, 6, 1, CARD)
    txt(b, 'HELD BY', 24, 0); txt(b, 'HONEY', 24, 1); txt(b, 'BUN', 24, 2); fill(a, 24, 1, 5, 2, CARD)
    for i in range(6): face(b, a, i, 2 + 5 * i, 6)
    cursor(b, a, 2 + 5 * d, 6, HEAD)
    ctr(b, ' '.join(name) + ' - ' + CARS[car][1], 0, 32, 11)
    ctr(b, line[0] + ' ' + line[1], 0, 32, 12)
    for i in range(3):                            # the three strengths in one line
        c = 4 + 9 * i; stamp(b, ICONS[PARTS[i]], c * 8, 13 * 8 + 1); pips(b, a, CARS[car][2][i], c + 1, 13, i)
        a[13, c:c + 6] = (RATE[i] & 7) | 0x30
    run = skid(_line((-16, 22), (272, 10), 60), 34, spin=(8, 26, 3), wheel=(7, 5))   # a spin along the bare table
    stage(b, run, f, car, 0, 112, 256, 32)
    menu(b, a, 19)
    txt(b, 'PRESS 1 OR 2 TO START', 5, 23); fill(a, 5, 23, 21, 1, TABLE | FLASH)
    return b, a

# ---------------------------------------------------------------- KEYS, CHOOSE DRIVER, CHOOSE CAR
def keys_screen():
    b, a = new()
    cap(b, a, 'K', 1, 0, 2); txt(b, 'KEYS', 4, 0, 2); logo(b, a, 24, 0)
    acts = ('LEFT', 'RIGHT', 'ACCELERATE', 'BRAKE', 'NOS')
    for p, (c, at, tag, ks, now) in enumerate(((1, P1, '1UP', ('Z', 'X', '?', ' ', ' '), 2), (17, P2, '2UP', ('6', '7', '9', '8', '0'), None))):
        fill(a, c, 3, 14, 12, CARD); bar(b, a, tag, c, 3, 14, at)
        for i, (act, k) in enumerate(zip(acts, ks)):
            r = 5 + 2 * i; txt(b, act, c + 1, r)
            cap(b, a, k, c + 13 - len(k), r)
            if now == i:                         # the key being set: its row lit, the cap flashing
                fill(a, c, r, 14, 1, 0x70); a[r, c + 12] = KEY | FLASH
    txt(b, 'SINCLAIR STICK', 17, 15)
    ctr(b, '1UP: PRESS THE KEY FOR', 0, 32, 17)
    ctr(b, 'ACCELERATE', 0, 32, 18, 2); fill(a, 6, 18, 20, 2, P1)
    txt(b, '1', 3, 21); a[21, 3] = KEY; txt(b, '1UP KEYS', 5, 21)
    txt(b, '2', 15, 21); a[21, 15] = KEY; txt(b, '2UP KEYS', 17, 21)
    cap(b, a, 'ENTER', 3, 23); txt(b, 'BACK TO THE TITLE', 9, 23)
    return b, a
def prompt(b, a, r, who='1UP'):
    cap(b, a, 'O', 3, r); cap(b, a, 'P', 5, r); txt(b, 'CHOOSE', 7, r)
    cap(b, a, 'Q', 16, r); txt(b, 'THAT ONE!', 18, r)
def driver_screen(sel=1, who=0, taken=None):
    b, a = new(); at, tag = ((P1, '1UP'), (P2, '2UP'))[who]
    txt(b, tag, 1, 0, 2); fill(a, 1, 0, 6, 2, at); txt(b, 'DRIVER?', 8, 0, 2); logo(b, a, 24, 0)
    for i in range(6): face(b, a, i, 2 + 5 * i, 4)
    if taken is not None: cursor(b, a, 2 + 5 * taken, 4, P1)
    cursor(b, a, 2 + 5 * sel, 4, at)
    key, name, sex, tile, line, car = DRIVERS[sel]
    fill(a, 1, 10, 30, 8, CARD); face(b, a, sel, 2, 11, 3)
    txt(b, ' '.join(name), 9, 11, 2); txt(b, line[0], 9, 13); txt(b, line[1], 9, 14)
    txt(b, 'LIKES THE ' + CARS[car][1], 9, 16); fill(a, 9, 16, 21, 1, 0x79)
    prompt(b, a, 20)
    return b, a
def car_screen(sel=3, who=0, drv=1, taken=None):
    b, a = new(); at, tag = ((P1, '1UP'), (P2, '2UP'))[who]
    txt(b, tag, 1, 0, 2); fill(a, 1, 0, 6, 2, at); txt(b, 'CAR?', 8, 0, 2); face(b, a, drv, 17, 0, 1); logo(b, a, 24, 0)
    for i in range(6):
        c = 2 + 5 * i; cloth(b, a, c, 4, 4, 4, frame=False)
        draw_car(b, i, 0, c * 8 + 16, 48, (c * 8, 32, c * 8 + 32, 64))
        mini_ratings(b, a, CARS[i][2], c, 9)
    if taken is not None: cursor(b, a, 2 + 5 * taken, 4, P1)
    cursor(b, a, 2 + 5 * sel, 4, at)
    art, name, lv, about = CARS[sel]
    fill(a, 1, 13, 30, 9, CARD); cloth(b, a, 2, 14, 6, 6, frame=False)
    draw_car(b, sel, 2, 40, 136, (16, 112, 64, 160), 2)       # twice the size, turning on the spot
    txt(b, name, 9, 14, 2); txt(b, about, 9, 16)
    rating_rows(b, a, lv, 9, 18, wide=2)
    prompt(b, a, 23)
    return b, a

# ---------------------------------------------------------------- the sheets
def font(n, bold=True):
    try: return ImageFont.truetype('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf', n)
    except OSError: return ImageFont.load_default()
BG, FG, DIM = (17, 18, 22), (236, 235, 230), (165, 170, 180)
def para(d, x, y, s, f, width, fill=DIM, gap=4):
    for block in s.split('\n'):
        line = ''
        for w in block.split():
            if d.textlength((line + ' ' + w).strip(), font=f) > width: d.text((x, y), line, fill=fill, font=f); y += f.size + gap; line = w
            else: line = (line + ' ' + w).strip()
        d.text((x, y), line, fill=fill, font=f); y += f.size + gap + 4
    return y
def flash_on(a):                                 # the picture with the FLASH cells in their other state
    a = a.copy(); m = (a & FLASH) > 0
    a[m] = (a[m] & 0xC0) | ((a[m] & 7) << 3) | ((a[m] >> 3) & 7)
    return a

def make_options():
    runs = runs_a()
    shots = [('A  "The stage and the card"  (recommended)', title_a(1, runs[1], 21),
              'Laid out like the race screen: a cloth window on the left where the featured driver\'s car drives in, drifts a circle, a figure of eight or a spin (leaving skid marks) and drives off; beside it that driver\'s card - face at twice the size, name, one-liner, favourite car and its GRIP / SPEED / ACCEL. Logo twice the size top left, lap record top right.\n'
              '1UP, 2UP and KEYS are three big buttons, each with the key that picks it. PRESS 1 OR 2 TO START flashes (the Spectrum does that for free).'),
             ('B  "Big logo, wide table"', title_b(),
              'The logo three times the size across the top, with the keys tucked in the corners. A cloth strip the full width of the screen: room for long slides and a wide figure of eight. The driver\'s card is one white band underneath.\n'
              'Loudest logo, but the 1UP / 2UP / KEYS choices are small and the card is cramped.'),
             ('C  "The line-up"', title_c(),
              'All six drivers shown at once in a row; a frame hops along them and the line below names the one it is on. That driver\'s car spins along a strip of bare table (black marks on yellow - no cloth).\n'
              'Shows the whole cast at a glance and doubles as a preview of the choose-driver screen, but the skid has less room and the screen is busier.')]
    ims = [render(b, a, border=6, s=3) for _, (b, a), _ in shots]
    w, h = ims[0].size; pad = 24
    out = Image.new('RGB', (pad + 3 * (w + pad), 70 + h + 190), BG); d = ImageDraw.Draw(out)
    d.text((pad, 14), 'Breakfast Run - title screen, three layouts (design mock-ups; real Spectrum pixels and colour cells, shown 3x)', fill=FG, font=font(26))
    for i, ((t, _, note), im) in enumerate(zip(shots, ims)):
        x = pad + i * (w + pad); out.paste(im, (x, 60))
        d.text((x, 70 + h), t, fill=FG, font=font(24)); para(d, x, 108 + h, note, font(18, False), w - 10)
    out.save(os.path.join(OUT, 'title_options.png')); print('wrote title_options.png', out.size)
    for n, im in zip('abc', ims): im.save(os.path.join(OUT, 'title_option_%s.png' % n))

def make_gif(order=(0, 3, 2, 1), s=3):
    runs = runs_a(); frames = []
    for d in order:
        for f in range(34):
            b, a = title_a(d, runs[d], f)            # (FLASH changes every 16 TV frames: every 4 here)
            frames.append(render(b, flash_on(a) if (len(frames) // 4) % 2 else a, border=6, s=s))
    pal = frames[0].quantize(colors=32, method=Image.Quantize.MEDIANCUT)
    allc = Image.new('RGB', (16, 2))
    from make_layout_review import PAL, PALB
    allc.putdata(PAL + PALB + [PAL[0]] * 16); pal = allc.quantize(colors=16, dither=Image.Dither.NONE)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    p = os.path.join(OUT, 'title_attract.gif')
    q[0].save(p, save_all=True, append_images=q[1:], duration=80, loop=0, optimize=False)
    print('wrote title_attract.gif', len(q), 'frames,', os.path.getsize(p) // 1024, 'KB')
    return frames

def make_flow():
    shots = [('1  KEYS  (K on the title)', keys_screen()), ('2  CHOOSE YOUR DRIVER', driver_screen()),
             ('3  CHOOSE YOUR CAR', car_screen()), ('3b  ...then 2UP has a turn (two players)', car_screen(sel=1, who=1, drv=4, taken=3))]
    ims = [render(b, flash_on(a) if i == 0 else a, border=6, s=2) for i, (_, (b, a)) in enumerate(shots)]
    w, h = ims[0].size; pad = 24; fw = 560
    out = Image.new('RGB', (pad + 2 * (w + pad) + fw + pad, 60 + 2 * (h + 150)), BG); d = ImageDraw.Draw(out)
    d.text((pad, 14), 'Breakfast Run - keys, choose driver, choose car (design mock-ups, shown 2x)', fill=FG, font=font(24))
    notes = ['Press 1 or 2 here to set that player\'s five keys in turn: the row being set lights up, its key cap flashes and the big line names it. A key already used is refused. 2UP starts on 6 7 8 9 0, which is also a Sinclair joystick.',
             'Six faces, three ladies and three men. Left / right moves the frame (red for 1UP, blue for 2UP); accelerate picks. The card shows the face three times the size, the name, the one-liner and the car they like best (which the next screen starts on).',
             'Six cars on cloth tiles, each with its three strengths in the race screen\'s own little box, so they can be compared at a glance. The card shows the chosen car twice the size (turning slowly in the game) and its strengths as big bars.',
             'Two players: 1UP picks driver and car, then the header turns blue and 2UP picks. 1UP\'s pick keeps its red frame. A driver can be picked once; both may drive the same car (which also saves memory).']
    for i, ((t, _), im) in enumerate(zip(shots, ims)):
        x = pad + (i % 2) * (w + pad); y = 60 + (i // 2) * (h + 150)
        out.paste(im, (x, y)); d.text((x, y + h + 8), t, fill=FG, font=font(20)); para(d, x, y + h + 38, notes[i], font(15, False), w - 8)
    x = pad + 2 * (w + pad); y = 60
    d.text((x, y), 'The order of the screens', fill=FG, font=font(22)); y += 44
    steps = [('TITLE + ATTRACT', 'Logo, lap record, 1UP / 2UP / KEYS. The drivers take turns on the cloth, a few seconds each, round and round until a key is pressed.', (215, 215, 0)),
             ('K: KEYS', 'Only if K is pressed. Set 1UP\'s keys (and 2UP\'s), ENTER goes back to the title.', (215, 215, 215)),
             ('1 or 2: 1UP CHOOSES A DRIVER', 'Six faces.', (255, 60, 60)),
             ('1UP CHOOSES A CAR', 'Six cars with their strengths.', (255, 60, 60)),
             ('2UP CHOOSES DRIVER, THEN CAR', 'Only if 2 was pressed on the title.', (80, 120, 255)),
             ('THE RACE', 'The game as it is today: only the choices (players, drivers, cars, keys) are handed over. The four computer cars are drawn from the drivers and cars not picked.', (0, 215, 215)),
             ('BACK TO THE TITLE', 'After the finish, with the lap record (and who set it) updated.', (215, 215, 0))]
    for i, (t, note, col) in enumerate(steps):
        d.rounded_rectangle([x, y, x + fw - 20, y + 34], radius=8, fill=col)
        d.text((x + 12, y + 6), t, fill=(0, 0, 0), font=font(18))
        y2 = para(d, x + 12, y + 42, note, font(15, False), fw - 50)
        if i < len(steps) - 1:
            d.line([x + 30, y2, x + 30, y2 + 16], fill=FG, width=3); d.polygon([(x + 23, y2 + 14), (x + 37, y2 + 14), (x + 30, y2 + 24)], fill=FG)
        y = y2 + 30
    y += 10; d.text((x, y), 'Made up or draft in these pictures', fill=FG, font=font(20)); y += 36
    para(d, x, y, 'All names, one-liners and strength numbers; the lap record; 2UP\'s keys.\n'
                  'The five new faces and five new cars are first drafts for Grant to redraw. The new cars are 20 x 20 and drawn facing up only (the game\'s cars are 16 x 16 with 16 headings): their turned pictures were made by the tool, not by hand.\n'
                  'Only the first car (TOASTER - your car today) and the first face (EGGS BENNY - your face today) are the game\'s own art.\n'
                  'When 1UP\'s and 2UP\'s frames sit on neighbouring tiles they share a column of colour cells, so that side shows one colour only.', font(15, False), fw - 40)
    out.save(os.path.join(OUT, 'title_flow.png')); print('wrote title_flow.png', out.size)
    for n, im in zip(('keys', 'driver', 'car', 'car_2up'), ims): im.save(os.path.join(OUT, 'title_screen_%s.png' % n))

if __name__ == '__main__':
    make_options(); make_gif(); make_flow()
