"""Option G of the whole-screen mock-ups (Grant, 14 Nov 2026): "I like the e design but still in
yellow. So what i like in E is the border changes around the gameplay area. I like what you did
with the car three ratings and the display for the player bottom left".

So this is option E (tools/make_screen_options2.py) laid out as it was - the slim frame round the
play window, the instrument column (logo, RACE, best lap, CAR with one rating per cell row and one
pip per cell, MAP), the scoreboard bottom left (your face and the big place in ONE red block, the
lap line that becomes FINAL LAP / FINISHED!, TIME), the radio bubble and the chief, the three
start lights in the window - but on the yellow table, with a yellow border. Two ways to do it:

  G1  "dark panels on the table" - the best-lap line, the CAR rows, the MAP and the TIME line keep
                                   E's black backgrounds and bright ink, as dark cards on the
                                   yellow; the window's slim frame is black.
  G2  "all on yellow"            - no black panels: the ratings in blue, red and magenta straight
                                   on the table (yellow and green do not read on yellow), the map
                                   black on yellow as in the game today, the slim frame in blue.

Built cell by cell on the real screens, as before (the window x 8-183, y 16-151, blue on cyan
only apart from the light blocks; one ink and one paper per cell). Unlike E, the face and the big
place now sit on the cell grid (face cols 1-2, place cols 4-9, rows 20-21). Made up: the best-lap
time, the times in the FINAL LAP / FINISHED pictures, the window's top 8 lines (see options2).

Writes docs/design/screen_options3.png (G1 and G2: the race screen 3x, the five start-light
pictures, the two messages, notes) and screen_option_g1.png, screen_option_g2.png.
Usage: make_screen_options3.py"""
import os, sys
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
from make_layout_review import render
from make_screen_options import (put, fill, small, rom, outline, heading, tail, strengths,
                                 YOUF, CREWF, TABLE, CARD, HEAD, YOU, CHIEF)
from make_screen_options2 import start, race, big, centre, check, DESIGN

def option_g(state, dark):
    DARK = 0x47                                  # bright white on black: G1's dark cards
    d, b, a, place, lap, time = start(state, TABLE, TABLE if dark else 0x31)   # the frame: black / blue ink
    # the slim frame: a 2-px rounded line and a gap of table, in the old bezel's cells
    keep = b[16:152, 8:184].copy(); b[8:160, 0:192] = 0; b[16:152, 8:184] = keep
    for k in (0, 1): outline(b, 3 + k, 11 + k, 188 - k, 156 - k)
    b[13, 5] = 1; b[13, 186] = 1; b[154, 5] = 1; b[154, 186] = 1
    put(b, d.name, 8, 0)
    # the instrument column: logo, RACE, best lap, CAR, MAP
    put(b, d.logo, 200, 0); a[1, 25:30] = 0x72; a[1, 30:32] = 0x77
    heading(b, a, 'RACE', 25, 2, 7); race(b, a, d, 25, 3)
    fill(a, 25, 13, 7, 1, DARK if dark else TABLE); small(b, 'BEST 0:41.2', 206, 106)
    heading(b, a, 'CAR', 25, 14, 7)
    for i, at in enumerate((0x44, 0x45, 0x46) if dark else (0x31, 0x32, 0x33)):   # green, cyan, yellow / blue, red, magenta
        fill(a, 25, 15 + i, 7, 1, at)
    strengths(b, 201, 121, 8, 217, 6, 8)
    heading(b, a, 'MAP', 25, 18, 7)
    fill(a, 25, 19, 7, 5, 0x46 if dark else TABLE); put(b, d.map, 204, 154)
    # the scoreboard: your face and your place in ONE red block (on the cell grid); lap, then time
    fill(a, 1, 20, 9, 2, YOU); put(b, YOUF, 8, 160); big(b, place, 32, 160)
    fill(a, 1, 22, 9, 1, CARD)
    rom(b, {'final': 'FINAL LAP', 'finish': 'FINISHED!'}.get(state, ' LAP ' + lap), 8, 176)
    fill(a, 1, 23, 9, 1, DARK if dark else TABLE); rom(b, 'TIME ' + time, 8, 184)
    # the pit radio: the bubble, its point going into the chief's blue panel
    fill(a, 11, 20, 10, 4, CARD); outline(b, 88, 160, 167, 191)
    centre(b, d.words, 89, 166, 167)
    fill(a, 21, 21, 2, 2, CHIEF); put(b, CREWF, 168, 168); tail(b, 168, 172)
    return b, a
def option_g1(state): return option_g(state, True)
def option_g2(state): return option_g(state, False)
for fn in (option_g1, option_g2): fn.border = 6; fn.msg = (0, 152, 192, 192)

OPTIONS = [('G1 - E on the yellow table: dark panels (yellow border)', option_g1, 'g1',
            ['The slim window frame is a black line. Best lap, CAR, MAP and TIME stay as black cards with bright ink.',
             'CAR: green, cyan and yellow on black, exactly as in E. The map is yellow on black.',
             'Scoreboard: face and big place in one red block, now on the cell grid; the lap line is a white strip.']),
           ('G2 - E on the yellow table: all on yellow (yellow border)', option_g2, 'g2',
            ['No black panels. The slim window frame is blue, to go with the blue title bars.',
             'CAR: blue, red and magenta straight on the table (yellow and green do not read on yellow).',
             'Best lap, MAP and TIME are black on the table, as the map is in the game today.'])]

if __name__ == '__main__':
    try:
        f = ImageFont.truetype('DejaVuSans-Bold.ttf', 26); fs = ImageFont.truetype('DejaVuSans.ttf', 19); fl = ImageFont.truetype('DejaVuSans-Bold.ttf', 16)
    except OSError: f = fs = fl = ImageFont.load_default()
    BG, FG = (17, 18, 22), (236, 235, 230)
    def crop(fn, state, box, s):
        b, a = fn(state); im = render(b, a, border=fn.border, s=s)
        return im.crop(((32 + box[0]) * s, (24 + box[1]) * s, (32 + box[2]) * s, (24 + box[3]) * s))
    rows = []
    for title, fn, tag, notes in OPTIONS:
        check(title, fn)
        b, a = fn('race'); main = render(b, a, border=fn.border, s=3)
        o = os.path.join(DESIGN, 'screen_option_%s.png' % tag); main.save(o); print('wrote', os.path.normpath(o), main.size)
        strip = [crop(fn, s, (0, 8, 192, 160), 2) for s in ('off', 'r1', 'r2', 'r3', 'go')]
        msgs = [(t, crop(fn, s, fn.msg, 2)) for s, t in (('final', 'Last lap'), ('finish', 'At the flag'))]
        rows.append((title, main, strip, msgs, notes))
    gap = 24; mw, mh = rows[0][1].size; cw, ch = rows[0][2][0].size
    rh = 46 + mh + 92
    out = Image.new('RGB', (gap + mw + gap + 3 * cw + 3 * gap, rh * len(rows) + gap), BG); d = ImageDraw.Draw(out)
    for n, (title, main, strip, msgs, notes) in enumerate(rows):
        y = gap // 2 + n * rh; x2 = gap + mw + gap
        d.text((gap, y + 6), title, fill=(255, 255, 255), font=f); out.paste(main, (gap, y + 46))
        d.text((x2, y + 12), 'The start lights in the window: unlit, red, red red, red red red, all green (go), then gone', fill=FG, font=fl)
        for k, im in enumerate(strip): out.paste(im, (x2 + (k % 3) * (cw + gap), y + 46 + (k // 3) * (ch + 12)))
        xm = x2 + 2 * (cw + gap); ym = y + 46 + ch + 12
        for t, im in msgs:
            d.text((xm, ym), t, fill=FG, font=fl); out.paste(im, (xm, ym + 22)); ym += 22 + im.height + 14
        for k, t in enumerate(notes): d.text((gap + 4, y + 46 + mh + 8 + 26 * k), '- ' + t, fill=(222, 221, 214), font=fs)
    o = os.path.join(DESIGN, 'screen_options3.png'); out.save(o); print('wrote', os.path.normpath(o), out.size)
