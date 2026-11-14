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
def mock(path, levels, keys, nos):
    b, a = load(path)
    slot = b[168:184, 32:48].copy()                 # the first inventory slot, with its canister
    b[160:192, 24:88] = 0; a[20:24, 3:11] = 0x30     # the inventory and the old set-up row go
    b[184:192, 0:192] = 0; a[23, 0:24] = 0x30
    # the set-up box: columns 6-9, rows 20-22 (x 48-79, y 160-183), black on bright white, rounded
    x0, x1, y0, y1 = 48, 79, 160, 183
    a[20:23, 6:10] = 0x78
    b[y0, x0 + 2:x1 - 1] = 1; b[y1, x0 + 2:x1 - 1] = 1; b[y0 + 2:y1 - 1, x0] = 1; b[y0 + 2:y1 - 1, x1] = 1
    for (x, y) in [(x0 + 1, y0 + 1), (x1 - 1, y0 + 1), (x0 + 1, y1 - 1), (x1 - 1, y1 - 1)]: b[y, x] = 1
    for i, (name, lv) in enumerate(zip('GSA', levels)):
        y = 163 + 7 * i
        if keys: small(b, '123'[i], 50, y)          # its key, only before the start
        small(b, name, 54, y)
        for j in range(5):                          # 5 pips, 3 x 5: filled for a level you have
            x = 59 + 4 * j
            b[y:y + 5, x:x + 3] = 1
            if j >= lv: b[y + 1:y + 4, x + 1] = 0
    # the NOS: a 2 x 2 cell panel in the window's bottom right corner (columns 21-22, rows 17-18),
    # only while you hold one; its count beside the canister when you hold more than one
    if nos:
        b[136:152, 168:184] = slot; a[17:19, 21:23] = 0x78
        if nos > 1:
            b[137:151, 169:183] = 0
            b[137:151, 169:179] = slot[1:15, 3:13]
            small(b, str(nos), 179, 144)
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
