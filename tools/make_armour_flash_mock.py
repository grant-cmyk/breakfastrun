"""Mock-up, MOVING: armour in the race-order panel as five pips (B) or as a vertical bar at the row's right edge (V),
the piece that is lost FLASHING before it goes (Grant, 17 Nov 2026: "B looks good because its quite visible, but
possibly a vertical bar is more efficient. In B, if the damage changes, then a bar flashes and then disappears -
the flashing makes it more visible"). Drawn on a real screen. Usage: python3 tools/make_armour_flash_mock.py <shot 352x288>
Writes docs/design/racetrack/armour_flash.gif. Nothing here is in the game."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
src = np.array(Image.open(sys.argv[1]).convert('RGB'))
X0, Y0, RW, RH = 256, 96, 48, 16
K, WHT = (0, 0, 0), (255, 255, 255)
def cols(a, r):
    c = tuple(int(v) for v in a[Y0 + r * RH + 1, X0 + 1]); return c, (WHT if c[0] > 200 and c[1] < 60 and c[2] < 60 else K)
def pips(levels, flash, on):                           # B: five pips; levels 0-5 a row; flash = (row, pip) blinking
    a = src.copy()
    for r, n in enumerate(levels):
        c, ink = cols(a, r); a[Y0 + r * RH + 2:Y0 + r * RH + 14, X0 + 26:X0 + RW] = c
        for p in range(5):
            x = X0 + 27 + p * 4; y = Y0 + r * RH + 4; lit = p < n or (flash == (r, p) and on)
            a[y:y + 8, x:x + 3] = ink
            if not lit: a[y + 1:y + 7, x + 1:x + 2] = c
    return a
def vbar(levels, flash, on):                           # V: a bar 3 px wide, six 2-px pieces, at the row's right edge; the gap time stays
    a = src.copy()
    for r, n in enumerate(levels):
        c, ink = cols(a, r); y0 = Y0 + r * RH
        a[y0:y0 + RH, X0 + 24:X0 + RW - 4] = a[y0:y0 + RH, X0 + 27:X0 + RW - 1].copy(); a[y0:y0 + RH, X0 + RW - 5:X0 + RW] = c
        for p in range(6):                             # piece 0 at the foot
            y = y0 + 13 - p * 2; lit = p < n or (flash == (r, p) and on)
            if lit: a[y - 1:y + 1, X0 + RW - 4:X0 + RW - 1] = ink
            else: a[y, X0 + RW - 3] = ink              # a lost piece: one dot, so the bar's full height still reads
    return a
S = 4; fnt = ImageFont.load_default()
crop = lambda a: Image.fromarray(a).crop((244, 84, 316, 180)).resize((72 * S, 96 * S), Image.NEAREST)
B0, V0 = [2, 4, 5, 3, 4], [2, 5, 6, 3, 5]
frames = []
def frame(b, v, note):
    sh = Image.new('RGB', (2 * (72 * S + 16) + 16, 96 * S + 62), (40, 42, 48)); d = ImageDraw.Draw(sh)
    d.text((16, 8), 'B: five pips, the gap time gives way', fill=(236, 235, 230), font=fnt); sh.paste(crop(b), (16, 28))
    d.text((72 * S + 32, 8), 'V: a bar up the right edge, the gap time stays', fill=(236, 235, 230), font=fnt); sh.paste(crop(v), (72 * S + 32, 28))
    d.text((16, 96 * S + 38), note, fill=(255, 212, 0), font=fnt); return sh
for i in range(10): frames.append(frame(pips(B0, None, 0), vbar(V0, None, 0), 'the race as it stands'))
b1, v1 = B0[:], V0[:]; b1[0] -= 1; v1[0] -= 1          # the dragster (top row) is hit: its top piece blinks, then goes
for i in range(12): frames.append(frame(pips(b1, (0, b1[0]), i % 2 == 0), vbar(v1, (0, v1[0]), i % 2 == 0), 'the dragster is hit: the piece it loses flashes ...'))
for i in range(10): frames.append(frame(pips(b1, None, 0), vbar(v1, None, 0), '... and is gone'))
b2, v2 = b1[:], v1[:]; b2[3] -= 1; v2[3] -= 1
for i in range(12): frames.append(frame(pips(b2, (3, b2[3]), i % 2 == 0), vbar(v2, (3, v2[3]), i % 2 == 0), 'the clown car is hit'))
for i in range(12): frames.append(frame(pips(b2, None, 0), vbar(v2, None, 0), ''))
out = os.path.join(ROOT, 'docs', 'design', 'racetrack', 'armour_flash.gif')
frames[0].save(out, save_all=True, append_images=frames[1:], duration=120, loop=0); frames[12].save(out.replace('.gif', '.png')); print('wrote', out)
