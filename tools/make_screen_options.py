"""Mock-ups of the WHOLE race screen (Grant, 14 Nov 2026): "mockup some options for a nicer display
that integrates the car strengths (the 3), shows the map and items with more integrated organised
feel, it feels like things are floating in the display, try to organise, condense, shape, put
borders around things - can you mockup some ideas to make the gameplay whole screen look snazzier
and prettier".

Three options, each built cell by cell on a REAL race screen (docs/design/mock_setup_racing.bin:
the 6912 bytes of screen memory from zxdev), so each keeps the Spectrum's rules: 256 x 192 pixels,
one ink and one paper colour per 8 x 8 cell, BRIGHT per cell. In every option the play window is
untouched (x 8-183, y 32-151, blue on cyan only), and the ideas Grant already approved are in:
the three car strengths as icon + five pips (tools/make_setup_mockup.py), and the NOS you hold as
small masked canisters in the window's bottom right corner.

  A  "Cards on the table"   - today's arrangement, but every group is a white card under a blue
                              title bar; one joined dashboard card under the window.
  B  "Arcade console"       - black everywhere, bright ink; ONE instrument column on the right
                              (race, car, map); the bottom is all pit radio.
  C  "Blue dashboard"       - the window sits on an L-shaped blue dashboard that holds you, the
                              car, the radio and the map; a TV-style banner on top.

The pieces (track name, place, lap, time, logo, race rows, map, radio words) are lifted from the
real screen and moved; the best-lap time shown is made up (the dump was taken before a lap ended).

Writes docs/design/screen_options.png (today, A, B, C with notes) and screen_option_a.png,
screen_option_b.png, screen_option_c.png (each alone, 3x, with the yellow border).
Usage: make_screen_options.py"""
import os, re, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
from make_layout_review import load, render, text, face
DESIGN = os.path.join(ROOT, 'docs', 'design')
src = open(os.path.join(HERE, 'make_strip_mockups.py')).read()
SMALL = eval(re.search(r'SMALL = (\{.*?\})', src, re.S).group(1))          # the 3 x 5 letters
SMALL.setdefault(':', "....X.....X....")
# the approved art (tools/make_setup_mockup.py): the three strengths as 7 x 5 icons, the NOS can
ICONS = {'grip':  [".XXXXX.", "XX...XX", "X..X..X", "XX...XX", ".XXXXX."],     # a tyre
         'speed': ["X...X..", ".X...X.", "..X...X", ".X...X.", "X...X.."],     # fast forward
         'accel': ["...XX..", "..XX...", ".XXXXX.", "...XX..", "..XX..."]}     # a bolt of power
CAN = ["..XXX..", "...X...", "..XXX..", ".XXXXX.", "X.....X", "XXXXXXX", "XXXXXXX", "X.....X", "X.....X", ".XXXXX."]
PARTS = ('grip', 'speed', 'accel'); LEVELS = (1, 2, 2); NOS = 2

# colours: attribute = BRIGHT 0x40 + paper * 8 + ink
TABLE = 0x30                                   # black on yellow: the kitchen table
CARD = 0x78                                    # black on bright white
HEAD = 0x4F                                    # bright white on blue: every heading
YOU = 0x57; CHIEF = 0x4F                       # your red panel, the chief's blue one

B0, A0 = load(os.path.join(DESIGN, 'mock_setup_racing.bin'))
def cut(y0, y1, x0, x1): return B0[y0:y1, x0:x1].copy()
NAME = cut(0, 8, 8, 184)                       # "BREAKFAST AT TIFFANY'S", 22 letters
PLACE = cut(8, 24, 8, 56)                      # "1ST", big
LAPW = cut(16, 24, 72, 96)                     # "LAP"
LAPN = cut(8, 24, 96, 144)                     # "1/3", big
TIME = cut(16, 24, 152, 184)                   # "0:04"
LOGO = cut(8, 24, 200, 256)                    # the logo, 7 x 2 cells
RACE = cut(40, 120, 200, 256); RACE_A = A0[5:15, 25:32].copy()   # 5 cars, 2 rows each
MAP = cut(142, 179, 204, 252)                  # the mini-map, 48 x 37
WORDS = cut(164, 182, 100, 153)                # the radio wave line and the chief's two lines
YOUF = np.array([[c == 'X' for c in r] for r in face('YOU')], dtype=np.uint8)
CREWF = np.array([[c == 'X' for c in r] for r in face('CREW')], dtype=np.uint8)

def put(b, art, x, y): b[y:y + art.shape[0], x:x + art.shape[1]] = art
def fill(a, c0, r0, w, h, at): a[r0:r0 + h, c0:c0 + w] = at
def small(b, s, x, y):
    for n, ch in enumerate(s):
        for k, v in enumerate(SMALL[ch]):
            if v == 'X': b[y + k // 3, x + 4 * n + k % 3] = 1
def rom(b, s, x, y):                           # ROM letters at any pixel (inside one colour)
    t = np.zeros((8, 8 * len(s) + 8), dtype=np.uint8); text(t, s, 0, 0)
    b[y:y + 8, x:x + 8 * len(s)] = t[:, :8 * len(s)]
def stamp(b, art, x, y, masked=False):
    h, w = len(art), len(art[0])
    if masked:
        for j in range(h):
            for i in range(w):
                if art[j][i] == 'X': b[y + j - 1:y + j + 2, x + i - 1:x + i + 2] = 0
    for j in range(h):
        for i in range(w):
            if art[j][i] == 'X': b[y + j, x + i] = 1
def outline(b, x0, y0, x1, y1, sides='tblr', solid=False):
    """A 1-px rounded frame (the style of the approved speech bubble). solid: the corner pixel
    outside the curve is ink too, so a card on a dark background has no light corner dot."""
    if 't' in sides: b[y0, x0 + 2:x1 - 1] = 1
    if 'b' in sides: b[y1, x0 + 2:x1 - 1] = 1
    if 'l' in sides: b[y0 + 2:y1 - 1, x0] = 1
    if 'r' in sides: b[y0 + 2:y1 - 1, x1] = 1
    for cs, (x, y, dx, dy) in {'tl': (x0, y0, 1, 1), 'tr': (x1, y0, -1, 1), 'bl': (x0, y1, 1, -1), 'br': (x1, y1, -1, -1)}.items():
        if cs[0] in sides and cs[1] in sides:
            b[y + dy, x + dx] = 1
            if solid: b[y, x] = 1; b[y + dy, x] = 1; b[y, x + dx] = 1
        else:                                  # an open end: the line runs straight to the edge
            if cs[0] in sides: b[y, x:x + 2 * dx:dx] = 1
            if cs[1] in sides: b[y:y + 2 * dy:dy, x] = 1
def heading(b, a, s, c0, r, w, at=HEAD):       # a title bar: ROM letters, centred on its cells
    fill(a, c0, r, w, 1, at); rom(b, s, c0 * 8 + (w * 8 - 8 * len(s)) // 2, r * 8)
def strengths(b, x, y, pitch, px, pw, pstep):
    """The three rows: icon at x, then five pips pw wide from px. A pip you have is solid, one
    you do not have is hollow."""
    for i, (name, lv) in enumerate(zip(PARTS, LEVELS)):
        yy = y + pitch * i
        stamp(b, ICONS[name], x, yy)
        for j in range(5):
            xx = px + pstep * j
            b[yy:yy + 5, xx:xx + pw] = 1
            if j >= lv: b[yy + 1:yy + 4, xx + 1:xx + pw - 1] = 0
def tail(b, x, y):                             # the bubble's point, 4 x 8, towards the chief
    for k, w in enumerate([1, 2, 3, 4, 4, 3, 2, 1]): b[y + k, x:x + w] = 1
def nos(b):
    for k in range(NOS): stamp(b, CAN, 175 - 9 * k, 140, masked=True)
def blank(paper):
    """The real screen with everything but the play window and its bezel wiped to one colour."""
    b, a = B0.copy(), A0.copy()
    keep_b = b[24:160, 0:192].copy(); keep_a = a[3:20, 0:24].copy()
    b[:] = 0; a[:] = paper
    b[24:160, 0:192] = keep_b; a[3:20, 0:24] = keep_a
    nos(b)
    return b, a
def race(b, a, c0, r0):
    put(b, RACE, c0 * 8, r0 * 8); a[r0:r0 + 10, c0:c0 + 7] = RACE_A

# ---- today (the unchanged screen, with the approved strengths box and NOS)
def today():
    b, a = B0.copy(), A0.copy()
    b[160:192, 24:88] = 0; a[20:24, 3:11] = TABLE
    b[184:192, 0:192] = 0; a[23, 0:24] = TABLE
    fill(a, 6, 20, 4, 3, CARD); outline(b, 48, 160, 79, 183)
    strengths(b, 50, 163, 7, 59, 3, 4)
    nos(b)
    return b, a

# ---- A: cards on the table
def option_a():
    b, a = blank(TABLE)
    # the header card, docked on the window: a blue title bar, then place / lap / time on white
    fill(a, 0, 0, 24, 1, HEAD); put(b, NAME, 8, 0)
    fill(a, 0, 1, 24, 2, CARD)
    put(b, PLACE, 8, 8); fill(a, 1, 1, 6, 2, YOU)
    put(b, LAPW, 72, 16); put(b, LAPN, 96, 8); fill(a, 12, 1, 6, 2, 0x70)
    small(b, 'TIME', 160, 10); put(b, TIME, 152, 16)
    b[8:24, 0] = 1; b[8:24, 191] = 1
    # the right-hand column: logo, RACE card, MAP card
    put(b, LOGO, 200, 0); a[1, 25:30] = 0x72; a[1, 30:32] = 0x77
    heading(b, a, 'RACE', 25, 3, 7); race(b, a, 25, 4)
    fill(a, 25, 14, 7, 2, CARD); small(b, 'BEST LAP', 212, 114); rom(b, '0:41.2', 204, 119)
    outline(b, 200, 110, 255, 127, 'blr')
    heading(b, a, 'MAP', 25, 17, 7)
    fill(a, 25, 18, 7, 6, CARD); put(b, MAP, 204, 149); outline(b, 200, 142, 255, 191, 'blr')
    # the dashboard card under the window: YOU | CAR | RADIO, one blue title bar over all three
    fill(a, 0, 20, 24, 1, HEAD); rom(b, 'YOU', 0, 160); rom(b, 'CAR', 36, 160); rom(b, 'RADIO', 100, 160)
    fill(a, 0, 21, 3, 3, YOU); put(b, YOUF, 4, 172)
    fill(a, 3, 21, 18, 3, CARD)
    strengths(b, 28, 171, 6, 38, 5, 6)
    b[168:192, 72] = 1                           # the divider between CAR and RADIO
    b[191, 24:168] = 1
    put(b, WORDS, 94, 171)
    fill(a, 21, 21, 3, 3, CHIEF); put(b, CREWF, 172, 172); tail(b, 168, 176)
    return b, a

# ---- B: the arcade console
def option_b():
    INK = 0x47                                   # bright white on black
    b, a = blank(0x07)
    # the window's bezel becomes a thin bright line with a black gap (same cells as the bezel)
    b[24:160, 0:192] = 0; b[32:152, 8:184] = B0[32:152, 8:184]; nos(b)
    a[3, 0:24] = 0x45; a[19, 0:24] = 0x45; a[3:20, 0] = 0x45; a[3:20, 23] = 0x45
    for k in (0, 1): outline(b, 3 + k, 27 + k, 188 - k, 156 - k)
    b[29, 5] = 1; b[29, 186] = 1; b[154, 5] = 1; b[154, 186] = 1
    # top: track name, place, lap, time
    fill(a, 0, 0, 24, 1, 0x46); put(b, NAME, 8, 0)
    put(b, PLACE, 8, 8); fill(a, 1, 1, 6, 2, YOU)
    fill(a, 7, 1, 17, 2, INK); put(b, LAPW, 72, 16); put(b, LAPN, 96, 8); fill(a, 12, 1, 6, 2, 0x70)
    small(b, 'TIME', 160, 10); put(b, TIME, 152, 16); fill(a, 19, 1, 4, 1, 0x45)
    # ONE instrument column: logo badge, RACE, CAR, MAP - each under the same blue bar
    put(b, LOGO, 200, 0); a[0, 25:32] = 0x70; a[1, 25:30] = 0x72; a[1, 30:32] = 0x77
    heading(b, a, 'RACE', 25, 2, 7); race(b, a, 25, 3)
    fill(a, 25, 13, 7, 1, INK); small(b, 'BEST 0:41.2', 206, 106)
    heading(b, a, 'CAR', 25, 14, 7)
    for i, at in enumerate((0x44, 0x45, 0x46)): fill(a, 25, 15 + i, 7, 1, at)   # green, cyan, yellow
    strengths(b, 201, 121, 8, 217, 6, 8)         # one strength per cell row, one pip per cell
    heading(b, a, 'MAP', 25, 18, 7)
    fill(a, 25, 19, 7, 5, 0x46); put(b, MAP, 204, 154)
    # bottom: the pit radio - you, a long bubble, the chief
    fill(a, 1, 21, 2, 2, YOU); put(b, YOUF, 8, 168)
    fill(a, 4, 20, 16, 4, CARD); outline(b, 32, 160, 159, 191, solid=True)
    put(b, WORDS, 70, 167)
    fill(a, 20, 21, 1, 2, INK); tail(b, 160, 172)
    fill(a, 21, 21, 2, 2, CHIEF); put(b, CREWF, 168, 168)
    return b, a

# ---- C: the blue dashboard
def option_c():
    DASH = 0x4F; LABEL = 0x4E                    # bright white / bright yellow on blue
    b, a = blank(TABLE)
    # top: a blue stripe with the track name, then a TV banner of three blocks that touch
    fill(a, 0, 0, 24, 1, HEAD); put(b, NAME, 8, 0)
    fill(a, 0, 1, 8, 2, YOU); put(b, PLACE, 8, 8)
    fill(a, 8, 1, 10, 2, CARD); put(b, LAPW, 66, 16); put(b, LAPN, 94, 8)
    fill(a, 18, 1, 6, 2, 0x47); small(b, 'TIME', 160, 10); put(b, TIME, 152, 16)
    # the right-hand column: logo and the race tower, as today, with a best-lap foot
    put(b, LOGO, 200, 8); a[2, 25:30] = 0x72; a[2, 30:32] = 0x77
    heading(b, a, 'RACE', 25, 4, 7); race(b, a, 25, 5)
    fill(a, 25, 15, 7, 1, CARD); small(b, 'BEST 0:41.2', 206, 121); outline(b, 200, 118, 255, 127, 'blr')
    # the dashboard: rows 20-23 right across, turning up the right-hand side for the map
    fill(a, 0, 20, 32, 4, DASH); fill(a, 24, 17, 8, 3, DASH)
    a[19, 0:24] = 0x48; a[17:20, 23] = 0x48      # the bezel's foot stands on the dashboard
    fill(a, 0, 20, 20, 1, LABEL); rom(b, 'YOU', 4, 160); rom(b, 'CAR', 44, 160); rom(b, 'RADIO', 104, 160)
    fill(a, 1, 21, 2, 2, YOU); put(b, YOUF, 8, 168)
    fill(a, 5, 21, 5, 3, LABEL)                  # the pips in yellow, one per cell
    strengths(b, 32, 169, 8, 42, 5, 8)
    fill(a, 11, 21, 9, 3, CARD); outline(b, 88, 168, 159, 191, solid=True)
    put(b, WORDS, 98, 171)
    tail(b, 160, 172)
    fill(a, 21, 21, 2, 2, CHIEF); put(b, CREWF, 168, 168)
    b[168:184, 167] = 1; b[168:184, 184] = 1; b[167, 168:184] = 1; b[184, 168:184] = 1   # a white frame round the chief
    fill(a, 24, 17, 8, 1, LABEL); rom(b, 'MAP', 216, 136)
    put(b, MAP, 204, 146); outline(b, 200, 144, 255, 184)
    return b, a

def check(name, b, a):
    """The promises: the window's pixels and colours are the real ones (plus the NOS), and the
    arrays are a legal screen by construction."""
    t, _ = B0.copy(), None; nos(t)
    assert (b[32:152, 8:184] == t[32:152, 8:184]).all(), name + ': play window pixels changed'
    assert (a[4:19, 1:23] == 0x29).all(), name + ': play window colours changed'

OPTIONS = [('Today (with the approved strengths box and NOS)', today,
            ['Things sit loose on the yellow table.', 'The strengths box, faces and bubble do not line up with anything.']),
           ('A - Cards on the table', option_a,
            ['Same places as today, but every group is a white card under a blue title bar.',
             'Under the window: ONE joined dashboard card - YOU | CAR | RADIO - with bigger pips.',
             'Header card docks onto the window; RACE and MAP cards match it on the right.']),
           ('B - Arcade console', option_b,
            ['Black everywhere with bright ink; the window gets a thin glowing frame.',
             'ONE instrument column: RACE, CAR (strengths, a colour each, one pip per cell), MAP.',
             'The bottom is all pit radio: you, a long bubble (room for longer lines), the chief.']),
           ('C - Blue dashboard', option_c,
            ['The window stands on an L-shaped blue dashboard: YOU, CAR, RADIO and the MAP in it.',
             'TV-style banner on top: place, lap and time as three blocks that touch.',
             'Yellow table kept above; the race tower stays where it is today.'])]

if __name__ == '__main__':
    try:
        f = ImageFont.truetype('DejaVuSans-Bold.ttf', 26); fs = ImageFont.truetype('DejaVuSans.ttf', 19)
    except OSError: f = fs = ImageFont.load_default()
    shots = []
    for title, fn, notes in OPTIONS:
        b, a = fn(); check(title, b, a)
        im = render(b, a, s=3); shots.append((title, im, notes))
        if title[1:3] == ' -':
            o = os.path.join(DESIGN, 'screen_option_%s.png' % title[0].lower()); im.save(o); print('wrote', os.path.normpath(o), im.size)
    w, h = shots[0][1].size; gap, top, foot = 24, 46, 96
    out = Image.new('RGB', (2 * w + 3 * gap, 2 * (top + h + foot) + gap), (17, 18, 22)); d = ImageDraw.Draw(out)
    for n, (title, im, notes) in enumerate(shots):
        x = gap + (n % 2) * (w + gap); y = gap // 2 + (n // 2) * (top + h + foot)
        d.text((x, y + 6), title, fill=(255, 255, 255), font=f); out.paste(im, (x, y + top))
        for k, t in enumerate(notes): d.text((x + 4, y + top + h + 8 + 26 * k), '- ' + t, fill=(222, 221, 214), font=fs)
    o = os.path.join(DESIGN, 'screen_options.png'); out.save(o); print('wrote', os.path.normpath(o), out.size)
