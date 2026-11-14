"""Second round of whole-screen mock-ups (Grant, 14 Nov 2026): "I would like updated mockups that
take into account those two rows added to gameplay at the top, have the start sequence a brief
3 2 1 countdown using blocked shapes different colours (blocked to avoid colour clash). So start
sequence normally at the top shifted to ingame. The background colour of the screen - that border
area outside of the zx spectrum with limited control where you can basically only set a colour,
make it consistent with the surround colour of the game - so yellow and yellow. Please do some
more mockup options for overall game look and design".

Three new options, D, E, F, built cell by cell on the REAL screens of the build with the taller
window (docs/design/mock_128_racing.bin and mock_128_before.bin: screen memory from zxdev). In
every one:
  - the play window takes BOTH former message rows: x 8-183, y 16-151 (cells cols 1-22, rows 2-18,
    176 x 136), blue on cyan only; the bezel's top band is in row 1. The dumps have the window from
    y 24, so the top 8 lines are worked out from the cloth itself (it repeats every 32 pixels on
    the diagonal: each pixel is the majority of the pixels one or more checks below it);
  - there is no message bar: place, lap and time live in the dashboard or the side column, and
    FINAL LAP / FINISHED have a named home;
  - the start is a 3, 2, 1, GO countdown IN the window, each figure made of whole 8 x 8 cells of
    one solid colour (the cell's paper AND ink are set to that colour, so whatever is under it is
    hidden and nothing can clash; no pixels are drawn - taking it away is putting the cells back
    to blue on cyan);
  - the border (the game can only give it one colour, and never a BRIGHT one) matches the
    surround: yellow, black or blue - so a blue surround uses the Spectrum's plain blue;
  - kept: race order in the cars' colours, mini-map, your face, crew chief and bubble, the three
    strengths as icon + pips, NOS as masked canisters in the window's corner, the logo.

  D  "Breakfast table"  - yellow. Place / lap / time head ONE joined column on the right (then
                          RACE, then MAP); one joined dashboard card under the window; the blue
                          bar on top carries the track name and turns into the message banner.
  E  "Night race"       - black. A scoreboard block bottom left: your face and your place in one
                          red block, lap and time under it; the instrument column of option B.
  F  "Blue broadcast"   - blue. A TV banner docked under the window (place | lap | time) that
                          turns into the message; your red panel hangs from your place.

Made up for the pictures: the best-lap time, the times in the FINAL LAP / FINISHED pictures, and
the top 8 lines of the window (see above). Everything else is lifted from the real screens.

Writes docs/design/screen_options2.png (D, E, F: the race screen 3x, the countdown as four
pictures, the two messages, notes) and screen_option_d.png, _e.png, _f.png (the race screen 3x).
Usage: make_screen_options2.py"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
from make_layout_review import load, render, PAL
from make_screen_options import (put, fill, small, rom, stamp, outline, heading, tail, strengths, nos,
                                 YOUF, CREWF, TABLE, CARD, HEAD, YOU, CHIEF)
DESIGN = os.path.join(ROOT, 'docs', 'design')
WIN = 0x29                                     # the play window: blue on cyan

def cloth_top(b):
    """The window's 8 new lines (y 16-23). The cloth is 32-px checks, so a pixel is the same as
    the one 32 across and 32 down (or 64 down ...): take the majority, which leaves out any car
    or O that happens to be on one of them."""
    top = np.zeros((8, 176), dtype=np.uint8)
    for y in range(16, 24):
        for x in range(8, 184):
            v = [b[y + 32 * j, x + 32 * i] for j in range(1, 5) for i in range(-5, 6)
                 if (i + j) % 2 == 0 and 8 <= x + 32 * i < 184 and y + 32 * j < 152]
            top[y - 16, x - 8] = sum(v) * 2 > len(v)
    return top

class Dump:
    """One real screen, and the pieces lifted from it."""
    def __init__(self, name):
        self.b, self.a = load(os.path.join(DESIGN, name))
        b = self.b
        self.name = b[0:8, 8:184].copy()                       # the track name, 22 letters
        self.logo = b[8:24, 200:256].copy()                    # 7 x 2 cells
        self.race = b[40:120, 200:256].copy(); self.race_a = self.a[5:15, 25:32].copy()
        self.map = b[142:179, 204:252].copy()                  # 48 x 37
        w = b[163:182, 90:165]                                 # the wave line and the chief's words
        ys, xs = np.nonzero(w); self.words = w[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
        # the window and its bezel, moved to the new shape: the band up a row, 8 new cloth lines
        f = np.zeros((152, 192), dtype=np.uint8)               # screen y 8-159
        f[16:152] = b[24:160, 0:192]                           # sides, window from y 24, the foot
        f[8:16] = b[24:32, 0:192]                              # the side bars carry on up
        f[1:8] = b[17:24, 0:192]                               # the top band, now y 9-15
        f[8:16, 8:184] = cloth_top(b)
        for x in range(8, 176):                                # an O the old window edge cut in half
            if list(b[24, x:x + 8]) == [1, 1, 1, 0, 0, 1, 1, 1] and list(b[25, x:x + 8]) == [1, 1, 0, 0, 0, 0, 1, 1]:
                f[14, x:x + 8] = [0, 1, 1, 1, 1, 0, 0, 0]      # gets its top two lines back
                f[15, x:x + 8] = [1, 0, 1, 1, 1, 1, 0, 0]
        self.frame = f
RACING = Dump('mock_128_racing.bin'); BEFORE = Dump('mock_128_before.bin')

# the countdown figures: one letter here is one whole cell
FIG = {'3': ["XXXXXX", "XXXXXX", "....XX", "..XXXX", "..XXXX", "....XX", "....XX", "XXXXXX", "XXXXXX"],
       '2': ["XXXXXX", "XXXXXX", "....XX", "XXXXXX", "XXXXXX", "XX....", "XX....", "XXXXXX", "XXXXXX"],
       '1': ["..XX..", ".XXX..", "XXXX..", "..XX..", "..XX..", "..XX..", "..XX..", "XXXXXX", "XXXXXX"],
       'G': ["XXXXXX", "XXXXXX", "XX....", "XX....", "XX.XXX", "XX.XXX", "XX..XX", "XXXXXX", "XXXXXX"],
       'O': ["XXXXXX", "XXXXXX", "XX..XX", "XX..XX", "XX..XX", "XX..XX", "XX..XX", "XXXXXX", "XXXXXX"]}
SOLID = {'red': 0x52, 'yellow': 0x76, 'green': 0x64, 'white': 0x7F}    # paper = ink, BRIGHT
COUNT = {'3': [('3', 9, 'red')], '2': [('2', 9, 'yellow')], '1': [('1', 9, 'green')],
         'GO': [('G', 5, 'green'), ('O', 13, 'white')]}
def countdown(a, state):
    for fig, c0, col in COUNT.get(state, []):
        for j, row in enumerate(FIG[fig]):
            for i, v in enumerate(row):
                if v == 'X': a[6 + j, c0 + i] = SOLID[col]

def big(b, s, x, y):                           # ROM letters twice size
    t = np.zeros((8, 8 * len(s)), dtype=np.uint8); rom(t, s, 0, 0)
    b[y:y + 16, x:x + 16 * len(s)] = np.kron(t, np.ones((2, 2), dtype=np.uint8))
def centre(b, art, x0, x1, y): put(b, art, x0 + (x1 - x0 + 1 - art.shape[1]) // 2, y)
def start(state, surround, ring):
    """A clean screen in one colour with the new window and bezel; returns the dump in use and
    the words for place, lap and time in this picture."""
    d = BEFORE if state in COUNT else RACING
    b = np.zeros((192, 256), dtype=np.uint8); a = np.full((24, 32), surround, dtype=np.uint8)
    b[8:160, 0:192] = d.frame
    a[1:20, 0:24] = ring; a[2:19, 1:23] = WIN
    nos(b); countdown(a, state)
    lap, time = {'final': ('3/3', '1:23'), 'finish': ('3/3', '2:05')}.get(state, ('1/3', '0:00' if state in COUNT else '0:04'))
    return d, b, a, '1ST', lap, time
def race(b, a, d, c0, r0): put(b, d.race, c0 * 8, r0 * 8); a[r0:r0 + 10, c0:c0 + 7] = d.race_a

# ---- D: the breakfast table (yellow)
def option_d(state):
    d, b, a, place, lap, time = start(state, TABLE, TABLE)
    # the blue bar on the window: the track name - and the message banner when there is one
    if state == 'final': fill(a, 0, 0, 24, 1, 0x70); rom(b, 'FINAL LAP', 60, 0)
    elif state == 'finish': fill(a, 0, 0, 24, 1, YOU); rom(b, 'FINISHED ' + place, 48, 0)
    else: fill(a, 0, 0, 24, 1, HEAD); put(b, d.name, 8, 0)
    # ONE joined column: logo, your place, lap and time, RACE, MAP
    put(b, d.logo, 200, 0); a[1, 25:30] = 0x72; a[1, 30:32] = 0x77
    fill(a, 25, 3, 7, 2, YOU); big(b, place, 204, 24)
    fill(a, 25, 5, 7, 1, 0x70); rom(b, 'LAP ' + lap, 200, 40)
    fill(a, 25, 6, 7, 1, CARD); small(b, 'TIME', 202, 50); rom(b, time, 220, 48)
    heading(b, a, 'RACE', 25, 7, 7); race(b, a, d, 25, 8)
    heading(b, a, 'MAP', 25, 18, 7)
    fill(a, 25, 19, 7, 5, CARD); put(b, d.map, 204, 153); outline(b, 200, 150, 255, 191, 'blr')
    # the dashboard card under the window: YOU | CAR | RADIO under one blue title bar
    fill(a, 0, 20, 24, 1, HEAD); rom(b, 'YOU', 0, 160); rom(b, 'CAR', 36, 160); rom(b, 'RADIO', 100, 160)
    fill(a, 0, 21, 3, 3, YOU); put(b, YOUF, 4, 172)
    fill(a, 3, 21, 18, 3, CARD)
    strengths(b, 28, 171, 6, 38, 5, 6)
    b[168:192, 72] = 1; b[191, 24:168] = 1
    centre(b, d.words, 73, 167, 171)
    fill(a, 21, 21, 3, 3, CHIEF); put(b, CREWF, 172, 172); tail(b, 168, 176)
    return b, a
option_d.border = 6; option_d.msg = (0, 0, 192, 24)

# ---- E: the night race (black)
def option_e(state):
    INK = 0x47
    d, b, a, place, lap, time = start(state, 0x07, 0x45)
    # the bezel is a thin bright double line with a black gap (in the bezel's own cells)
    keep = b[16:152, 8:184].copy(); b[8:160, 0:192] = 0; b[16:152, 8:184] = keep
    for k in (0, 1): outline(b, 3 + k, 11 + k, 188 - k, 156 - k)
    b[13, 5] = 1; b[13, 186] = 1; b[154, 5] = 1; b[154, 186] = 1
    fill(a, 0, 0, 24, 1, 0x46); put(b, d.name, 8, 0)
    # the instrument column: logo badge, RACE, CAR, MAP
    put(b, d.logo, 200, 0); a[0, 25:32] = 0x70; a[1, 25:30] = 0x72; a[1, 30:32] = 0x77
    heading(b, a, 'RACE', 25, 2, 7); race(b, a, d, 25, 3)
    fill(a, 25, 13, 7, 1, INK); small(b, 'BEST 0:41.2', 206, 106)
    heading(b, a, 'CAR', 25, 14, 7)
    for i, at in enumerate((0x44, 0x45, 0x46)): fill(a, 25, 15 + i, 7, 1, at)
    strengths(b, 201, 121, 8, 217, 6, 8)
    heading(b, a, 'MAP', 25, 18, 7)
    fill(a, 25, 19, 7, 5, 0x46); put(b, d.map, 204, 154)
    # the scoreboard: your face and your place in ONE red block; lap (or the message), then time
    fill(a, 0, 20, 9, 2, YOU); put(b, YOUF, 3, 160); big(b, place, 22, 160)
    fill(a, 0, 22, 9, 1, 0x70)
    rom(b, {'final': 'FINAL LAP', 'finish': 'FINISHED!'}.get(state, ' LAP ' + lap), 0, 176)
    fill(a, 0, 23, 9, 1, INK); rom(b, 'TIME ' + time, 0, 184)
    # the pit radio
    fill(a, 10, 20, 10, 4, CARD); outline(b, 80, 160, 159, 191, solid=True)
    centre(b, d.words, 81, 158, 167)
    fill(a, 20, 21, 1, 2, INK); tail(b, 160, 172)
    fill(a, 21, 21, 2, 2, CHIEF); put(b, CREWF, 168, 168)
    return b, a
option_e.border = 0; option_e.msg = (0, 152, 192, 192)

# ---- F: the blue broadcast (blue)
def option_f(state):
    SUR = 0x0F; PIP = 0x0E; BAR = 0x70           # white on blue; yellow on blue; black on bright yellow
    d, b, a, place, lap, time = start(state, SUR, 0x08)
    put(b, d.name, 8, 0)
    # the banner docked under the window: place | lap | time - or the message, right across
    if state == 'final': fill(a, 0, 20, 24, 1, BAR); rom(b, 'FINAL LAP', 60, 160)
    elif state == 'finish': fill(a, 0, 20, 24, 1, YOU); rom(b, 'FINISHED ' + place, 48, 160)
    else:
        fill(a, 0, 20, 5, 1, YOU); rom(b, place, 8, 160)
        fill(a, 5, 20, 9, 1, BAR); rom(b, 'LAP ' + lap, 48, 160)
        fill(a, 14, 20, 10, 1, 0x47); rom(b, 'TIME ' + time, 116, 160)
    # under it: your red panel (it hangs from your place), the car, the radio, the chief
    fill(a, 0, 21, 3, 3, YOU); put(b, YOUF, 4, 172)
    fill(a, 5, 21, 5, 3, PIP); strengths(b, 32, 170, 8, 42, 5, 8)
    fill(a, 11, 21, 10, 3, CARD); outline(b, 88, 168, 167, 191, solid=True)
    centre(b, d.words, 89, 166, 171)
    fill(a, 21, 21, 3, 3, CHIEF); put(b, CREWF, 172, 172); tail(b, 168, 176)
    # the right-hand column: logo badge, RACE, best lap, MAP - yellow bars
    put(b, d.logo, 200, 0); a[0, 25:32] = 0x70; a[1, 25:30] = 0x72; a[1, 30:32] = 0x77
    heading(b, a, 'RACE', 25, 3, 7, BAR); race(b, a, d, 25, 4)
    small(b, 'BEST 0:41.2', 206, 114)
    heading(b, a, 'MAP', 25, 16, 7, BAR)
    put(b, d.map, 204, 146); outline(b, 200, 139, 255, 190)
    return b, a
option_f.border = 1; option_f.msg = (0, 152, 192, 192)

def check(name, fn):
    """The promises: racing, the window's pixels from y 24 are the real ones (plus the NOS) and
    every window cell is blue on cyan; in the countdown only whole cells change colour."""
    b, a = fn('race'); t = RACING.b.copy(); nos(t)
    assert (b[24:152, 8:184] == t[24:152, 8:184]).all(), name + ': play window pixels changed'
    assert (a[2:19, 1:23] == WIN).all(), name + ': play window colours changed'
    b3, a3 = fn('3'); t = BEFORE.b.copy(); nos(t)
    assert (b3[24:152, 8:184] == t[24:152, 8:184]).all(), name + ': the countdown drew pixels'

OPTIONS = [('D - Breakfast table (yellow border)', option_d,
            ['Place, lap and time head ONE joined column on the right: place, LAP, TIME, RACE, MAP - no gaps.',
             'Under the window: one joined dashboard card, YOU | CAR | RADIO, under a blue title bar.',
             'Messages: the blue track-name bar on top of the window turns into the banner (FINAL LAP, FINISHED 1ST).']),
           ('E - Night race (black border)', option_e,
            ['Scoreboard bottom left: your face and your place in ONE red block; lap and time under it.',
             'Instrument column on the right: RACE, CAR (a colour each, one pip per cell), MAP. Thin glowing window frame.',
             "Messages: the scoreboard's yellow lap line says FINAL LAP / FINISHED! under the big place."]),
           ('F - Blue broadcast (blue border)', option_f,
            ['A TV banner docked under the window: place | lap | time as three blocks that touch.',
             'Your red panel hangs from your place; car, radio bubble and chief sit along the same line.',
             'Messages: the whole banner becomes FINAL LAP or FINISHED 1ST. Plain (not BRIGHT) blue, to match the border.'])]

if __name__ == '__main__':
    try:
        f = ImageFont.truetype('DejaVuSans-Bold.ttf', 26); fs = ImageFont.truetype('DejaVuSans.ttf', 19); fl = ImageFont.truetype('DejaVuSans-Bold.ttf', 16)
    except OSError: f = fs = fl = ImageFont.load_default()
    BG, FG = (17, 18, 22), (236, 235, 230)
    def crop(fn, state, box, s):                 # a piece of the screen (screen pixels), s times size
        b, a = fn(state); im = render(b, a, border=fn.border, s=s)
        return im.crop(((32 + box[0]) * s, (24 + box[1]) * s, (32 + box[2]) * s, (24 + box[3]) * s))
    rows = []
    for title, fn, notes in OPTIONS:
        check(title, fn)
        b, a = fn('race'); main = render(b, a, border=fn.border, s=3)
        o = os.path.join(DESIGN, 'screen_option_%s.png' % title[0].lower()); main.save(o); print('wrote', os.path.normpath(o), main.size)
        strip = [(s if s != 'GO' else 'GO!', crop(fn, s, (0, 8, 192, 160), 2)) for s in ('3', '2', '1', 'GO')]
        msgs = [(t, crop(fn, s, fn.msg, 2)) for s, t in (('final', 'Last lap'), ('finish', 'At the flag'))]
        rows.append((title, main, strip, msgs, notes))
    gap = 24; mw, mh = rows[0][1].size; cw, ch = rows[0][2][0][1].size
    W = gap + mw + gap + 2 * cw + gap + gap
    rh = 46 + max(mh, 2 * (ch + 24) + 24 + max(m[1].height for r in rows for m in r[3])) + 92
    out = Image.new('RGB', (W, rh * len(rows) + gap), BG); d = ImageDraw.Draw(out)
    for n, (title, main, strip, msgs, notes) in enumerate(rows):
        y = gap // 2 + n * rh; x = gap
        d.text((x, y + 6), title, fill=(255, 255, 255), font=f); out.paste(main, (x, y + 46))
        x2 = gap + mw + gap
        d.text((x2, y + 12), 'The start: 3, 2, 1, GO in the window (whole cells of one colour)', fill=FG, font=fl)
        for k, (t, im) in enumerate(strip):
            out.paste(im, (x2 + (k % 2) * (cw + gap), y + 46 + (k // 2) * (ch + 12)))
        ym = y + 46 + 2 * (ch + 12)
        for k, (t, im) in enumerate(msgs):
            d.text((x2 + k * (cw + gap), ym), t, fill=FG, font=fl); out.paste(im, (x2 + k * (cw + gap), ym + 22))
        for k, t in enumerate(notes): d.text((gap + 4, y + 46 + mh + 8 + 26 * k), '- ' + t, fill=(222, 221, 214), font=fs)
    o = os.path.join(DESIGN, 'screen_options2.png'); out.save(o); print('wrote', os.path.normpath(o), out.size)
