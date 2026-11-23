"""BIGGER PLACE NUMBER - mock-ups (Grant, 23 Nov 2026: "I'd also like a mockup of a bigger position number in the top right").
Drawn on a real race screen (the group C tape, 1x screenshot) at the place plate (top right of the window), in its colours: the
plate solid blue ink, its writing the cloth's cyan showing through. ROM letters (8 x 8, twice or three times the size) and the
game's 3 x 5 small figures. Usage: python3 tools/make_place_mock.py <race screenshot 352x288> <ROM font 768 bytes>
Writes docs/design/place_number_mockups.png."""
import sys, os
from PIL import Image, ImageDraw
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
base = Image.open(sys.argv[1]).convert('RGB'); font = open(sys.argv[2], 'rb').read()
INK = (0, 0, 215); CY = (0, 215, 215)
SM = {'0': '111101101101111', '1': '010110010010111', '2': '111001111100111', '3': '111001111001111', '4': '101101111001001',
      '5': '111100111001111', '6': '111100111101111', '7': '111001001001001', '8': '111101111101111', '9': '111101111001111',
      ':': '000010000010000', '.': '000000000000010', '/': '001001010100100', 'P': '111101111100100', 'N': '101111111111101',
      'D': '110101101101110', 'L': '100100100100111', 'A': '010101111101101', 'S': '111100111001111', 'T': '111010010010010',
      'R': '110101110101101', 'H': '101101111101101', ' ': '000000000000000'}
def box(im, x, y, w, h):
    d = ImageDraw.Draw(im); d.rectangle([x + 1, y, x + w - 2, y + h - 1], fill=INK); d.rectangle([x, y + 1, x + w - 1, y + h - 2], fill=INK)
def small(im, x, y, s):
    for i, ch in enumerate(s):
        g = SM[ch]
        for r in range(5):
            for c in range(3):
                if g[r * 3 + c] == '1': im.putpixel((x + i * 4 + c, y + r), CY)
def rom(im, x, y, ch, z):
    o = (ord(ch) - 32) * 8
    for r in range(8):
        for c in range(8):
            if font[o + r] >> (7 - c) & 1:
                for a in range(z):
                    for b in range(z): im.putpixel((x + c * z + a, y + r * z + b), CY)
X0, Y0 = 48 + 160, 48 + 8          # (the window's top right: the plate's corner region, screen x 160-207 + border)
def clean(im):                      # the plate's old place, the cloth put back (copied from a clear patch beside it)
    patch = base.crop((48 + 112, Y0, 48 + 160, Y0 + 40)); im.paste(patch, (X0, Y0)); return im
opts = []
im = base.copy(); opts.append(('Today', 'The plate as it is: place and lap in the ROM letters, the lap time small.', im))
im = clean(base.copy()); box(im, X0 - 4, Y0 + 2, 40, 28)
rom(im, X0 + -2, Y0 + 4, '2', 2); small(im, X0 + 16, Y0 + 5, 'ND'); small(im, X0 + 16, Y0 + 13, '1/3'); small(im, X0 + -1, Y0 + 22, '0:10.8')
opts.append(('A  Big place on the plate', 'The place twice the size with ND beside it; the lap and the time in the small figures.', im))
im = base.copy(); box(im, X0 - 26, Y0 + 2, 28, 28); rom(im, X0 - 24, Y0 + 4, '2', 3)
opts.append(('B  A big number beside the plate', 'A box of its own, the place three times the size; the plate as today.', im))
im = clean(base.copy()); box(im, X0 - 4, Y0 + 2, 40, 28)
rom(im, X0 + -2, Y0 + 4, '2', 2); small(im, X0 + 16, Y0 + 9, '/5'); small(im, X0 + -1, Y0 + 22, '1/3 10.8')
opts.append(('C  Place out of five', 'The place twice the size and "/5"; under it the lap and the lap time.', im))
Z = 3; cw, ch = 110, 60
sheet = Image.new('RGB', (len(opts) * (cw * Z + 12), ch * Z + 50 + 296), (244, 246, 248)); d = ImageDraw.Draw(sheet)
for i, (t, desc, im) in enumerate(opts):
    x = i * (cw * Z + 12)
    d.text((x + 4, 4), t, fill=(20, 26, 43)); d.text((x + 4, 18), desc[:58], fill=(90, 99, 120)); d.text((x + 4, 28), desc[58:], fill=(90, 99, 120))
    sheet.paste(im.crop((X0 - 60, Y0 - 6, X0 - 60 + cw, Y0 - 6 + ch)).resize((cw * Z, ch * Z), Image.NEAREST), (x, 44))
    sheet.paste(im.resize((im.width, im.height)), (x + 8, ch * Z + 50))
sheet.save(os.path.join(ROOT, 'docs/design/place_number_mockups.png')); print('written')
