"""Mock-up (Grant, 14 Nov 2026): "If there is a NOS, it appears in the bottom right in game in a
masked or smaller box; this allows for the 3 car measures to fit in the bottom area. They must be
tighter - three rows one underneath each other - much more compact in a little box ... to the left
of the radio box." Built on two real game screens (docs/design/mock_setup_before.bin, _racing.bin:
screen memory from zxdev), cell by cell, so it keeps the Spectrum's rules. Writes
docs/design/setup_box_mockup.png: before the start and racing, then both strips close up."""
import os, re, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
from make_layout_review import load, render, PAL, PALB
src = open(os.path.join(HERE, 'make_strip_mockups.py')).read()
SMALL = eval(re.search(r'SMALL = (\{.*?\})', src, re.S).group(1))
def small(b, ch, x, y):
    for k, v in enumerate(SMALL[ch]):
        if v == 'X': b[y + k // 3, x + k % 3] = 1
# the three parts as icons, 7 x 5 (Grant, 14 Nov 2026: "don't use letters, use icons"):
ICONS = {'grip':  [".XXXXX.", "XX...XX", "X..X..X", "XX...XX", ".XXXXX."],     # a tyre
         'speed': ["X...X..", ".X...X.", "..X...X", ".X...X.", "X...X.."],     # fast forward
         'accel': ["...XX..", "..XX...", ".XXXXX.", "...XX..", "..XX..."]}     # a bolt of power
CAN = ["..XXX..", "...X...", "..XXX..", ".XXXXX.", "X.....X", "XXXXXXX", "XXXXXXX", "X.....X", "X.....X", ".XXXXX."]   # a NOS canister, 7 x 10
def stamp(b, art, x, y, masked=False):
    h, w = len(art), len(art[0])
    if masked:                                      # a 1-px gap of paper all round the ink
        for j in range(h):
            for i in range(w):
                if art[j][i] == 'X': b[y + j - 1:y + j + 2, x + i - 1:x + i + 2] = 0
    for j in range(h):
        for i in range(w):
            if art[j][i] == 'X': b[y + j, x + i] = 1
def mock(path, levels, keys, nos):
    b, a = load(path)
    b[160:192, 24:88] = 0; a[20:24, 3:11] = 0x30     # the inventory and the old set-up row go
    b[184:192, 0:192] = 0; a[23, 0:24] = 0x30
    # the set-up box: columns 6-9, rows 20-22 (x 48-79, y 160-183), black on bright white, rounded
    x0, x1, y0, y1 = 48, 79, 160, 183
    a[20:23, 6:10] = 0x78
    b[y0, x0 + 2:x1 - 1] = 1; b[y1, x0 + 2:x1 - 1] = 1; b[y0 + 2:y1 - 1, x0] = 1; b[y0 + 2:y1 - 1, x1] = 1
    for (x, y) in [(x0 + 1, y0 + 1), (x1 - 1, y0 + 1), (x0 + 1, y1 - 1), (x1 - 1, y1 - 1)]: b[y, x] = 1
    for i, (name, lv) in enumerate(zip(('grip', 'speed', 'accel'), levels)):
        y = 163 + 7 * i
        stamp(b, ICONS[name], 50, y)                # its icon (rows in key order: 1, 2, 3)
        for j in range(5):                          # 5 pips, 3 x 5: filled for a level you have
            x = 59 + 4 * j
            b[y:y + 5, x:x + 3] = 1
            if j >= lv: b[y + 1:y + 4, x + 1] = 0
    # the NOS: no box - a small canister for each one you hold, in the window's own blue on cyan,
    # masked (a 1-px gap round it), in the window's bottom right corner (window x 8-183, y 32-151)
    for k in range(nos):
        stamp(b, CAN, 175 - 9 * k, 140, masked=True)
    return b, a
shots = [('Before the start (SPEED 2, ACCEL 2)', mock(os.path.join(ROOT, 'docs', 'design', 'mock_setup_before.bin'), (1, 2, 2), True, 1)),
         ('Racing, holding two NOS', mock(os.path.join(ROOT, 'docs', 'design', 'mock_setup_racing.bin'), (1, 2, 2), False, 2))]
try: f = ImageFont.truetype('DejaVuSans-Bold.ttf', 18)
except OSError: f = ImageFont.load_default()
full = [render(b, a, s=2) for _, (b, a) in shots]
zoom = [render(b, a, border=6, s=6).crop(((32 + 0) * 6, (24 + 128) * 6, (32 + 192) * 6, (24 + 192) * 6)) for _, (b, a) in shots]
W = full[0].width * 2 + 48; H = 40 + full[0].height + 40 + zoom[0].height * 2 + 60
out = Image.new('RGB', (W, H), (17, 18, 22)); d = ImageDraw.Draw(out)
for i, (t, _) in enumerate(shots):
    x = 16 + i * (full[0].width + 16)
    d.text((x, 10), t, fill=(236, 235, 230), font=f); out.paste(full[i], (x, 36))
y = 36 + full[0].height + 16
for i, (t, _) in enumerate(shots):
    d.text((16, y), 'Close up - ' + t[0].lower() + t[1:], fill=(236, 235, 230), font=f); y += 26
    out.paste(zoom[i], (16, y)); y += zoom[i].height + 12
o = os.path.join(ROOT, 'docs', 'design', 'setup_box_mockup.png'); out.save(o); print('wrote', os.path.normpath(o), out.size)
