"""Mock-up: position and quick "bite" messages INSIDE the game area (Grant, 14 Nov 2026: "I would
like to get some positional information into the game area, its easier for the player to see.
Would be good to have quick bite messages appear in a part of the in game" - "position inside the
game area - maybe top right, masked display to minimise impact to viewing area"). A real screen
from the game (read in zxdev), with the tag and the messages drawn over it four ways. The tag is
a small rounded plate with ordinary-size letters, set in from the window's edges so the game shows
all round it (Grant: "smaller fonts - not double sized but in a smaller square that has slightly
rounded edges, with the game around it - better than feeling like something is wedged to the side").
Usage: python3 tools/make_ingame_info.py -> docs/design/ingame_info.png   (ZXDEV = zxdev)"""
import os, sys, json, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..'); sys.path.insert(0, HERE)
from make_layout_review import render, FONT
import make_colour_objects as mc
SYM = {}
for l in open(os.path.join(ROOT, 'build', 'racer.sym')):
    p = l.split()
    if len(p) >= 3 and p[1] == 'EQU': SYM[p[0].lower()] = int(p[2].rstrip('H'), 16)
z = subprocess.Popen([os.environ.get('ZXDEV', os.path.join(ROOT, '..', 'zx-emulator', 'zxdev')), 'serve', '--stdio'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
def rpc(m, **p):
    z.stdin.write(json.dumps({'id': 1, 'method': m, 'params': p}) + '\n'); z.stdin.flush(); r = json.loads(z.stdout.readline())
    if 'error' in r: raise SystemExit('%s: %s' % (m, r['error']))
    return r['result']
rpc('load', path=os.path.join(ROOT, 'build', 'racer.tap')); rpc('run', frames=300); rpc('key_down', keys='1'); rpc('run', frames=10); rpc('key_up', keys='1'); rpc('run', frames=100)
rpc('key_down', keys='Q'); rpc('run', frames=330); rpc('write', addr=SYM['dmg'], value=3); rpc('run', frames=20)
m = b''
while len(m) < 6912:
    r = rpc('read', addr=0x4000 + len(m), len=min(1024, 6912 - len(m))); m += bytes.fromhex(r['hex']) if 'hex' in r else bytes(r['bytes'])
z.kill()
bits0 = np.zeros((192, 256), dtype=np.uint8)
for y in range(192):
    a = ((y & 0xC0) << 5) | ((y & 7) << 8) | ((y & 0x38) << 2); bits0[y] = np.unpackbits(np.frombuffer(m[a:a + 32], dtype=np.uint8))
attrs0 = np.frombuffer(m[6144:6912], dtype=np.uint8).reshape(24, 32).copy()
def glyphs(s, scale=1):
    g = np.zeros((8 * scale, 8 * scale * len(s)), dtype=np.uint8)
    for k, ch in enumerate(s):
        f = FONT[(ord(ch) - 32) * 8:(ord(ch) - 32) * 8 + 8]
        for j in range(8):
            for i in range(8):
                if (f[j] >> (7 - i)) & 1: g[j * scale:(j + 1) * scale, (8 * k + i) * scale:(8 * k + i + 1) * scale] = 1
    return g
def stamp(bits, g, x, y, halo=1, box=False):
    """Letters on the table with `halo` clear pixels round them (an invisible mask) - or, box: a whole clear rectangle."""
    h, w = g.shape; clear = np.ones((h + 2 * halo, w + 2 * halo), dtype=np.uint8) if box else None
    if clear is None:
        clear = np.zeros((h + 2 * halo, w + 2 * halo), dtype=np.uint8); clear[halo:halo + h, halo:halo + w] = g
        for _ in range(halo): clear = mc.grow(clear)
    reg = bits[y - halo:y + h + halo, x - halo:x + w + halo]; reg[clear == 1] = 0; bits[y:y + h, x:x + w] |= g
def plate(w, h, r=3):
    """A w x h block with rounded corners (1 = inside)."""
    m = np.ones((h, w), dtype=np.uint8)
    for y in range(r):
        for x in range(r):
            if (r - x - 0.5) ** 2 + (r - y - 0.5) ** 2 > r * r + 0.5: m[y, x] = m[y, w - 1 - x] = m[h - 1 - y, x] = m[h - 1 - y, w - 1 - x] = 0
    return m
def chip(b, a, lines, x, y, style, attr=None):
    """A small rounded plate INSIDE the game area, the game showing all round it; ordinary-size letters.
    style 'line': a blue outline, clear inside. 'solid': a solid plate, the letters cut out of it.
    attr: the plate in a colour of its own - then the cells it sits in are cleared and coloured."""
    w = 8 * max(len(l) for l in lines) + 6; h = 9 * len(lines) + 4; m = plate(w, h)
    if attr is not None:
        c0, c1, r0, r1 = x // 8, (x + w - 1) // 8, y // 8, (y + h - 1) // 8
        b[r0 * 8:r1 * 8 + 8, c0 * 8:c1 * 8 + 8] = 0; a[r0:r1 + 1, c0:c1 + 1] = attr
    else:
        halo = mc.grow(mc.grow(np.pad(m, 2))); reg = b[y - 2:y + h + 2, x - 2:x + w + 2]; reg[halo == 1] = 0
    txt = np.zeros((h, w), dtype=np.uint8)
    for k, l in enumerate(lines):
        g = glyphs(l); txt[3 + 9 * k:3 + 9 * k + 8, 3:3 + g.shape[1]] = g
    if style == 'line':
        inner = np.zeros_like(m); inner[1:-1, 1:-1] = plate(w - 2, h - 2, 2); b[y:y + h, x:x + w] |= (m & (1 - inner)) | txt
    else:
        b[y:y + h, x:x + w] |= m & (1 - txt)
def scene(kind):
    b, a = bits0.copy(), attrs0.copy()
    X, Y = 138, 17                                                 # the plate's top left: a cell and more in from the window's top and right
    if kind == 'A': chip(b, a, ['2ND', 'L2/3'], X, Y, 'line')
    if kind == 'B': chip(b, a, ['2ND', 'L2/3'], X, Y, 'solid')
    if kind == 'C': chip(b, a, ['2ND', 'L2/3'], X, Y, 'solid', attr=0x28)          # a black plate, the letters in the table's cyan
    if kind == 'D':
        chip(b, a, ['2ND', 'L2/3'], X, Y, 'solid', attr=0x2A)                      # a red plate
        chip(b, a, ['FINAL LAP!'], 50, 17, 'solid', attr=0x2A)                     # and a quick message, the same way, for 2 seconds
    if kind == 'E':
        chip(b, a, ['2ND'], X + 8, Y, 'solid', attr=0x28)                          # the place alone: the smallest
    if kind == 'F':
        chip(b, a, ['2ND', 'L2/3'], X, Y, 'solid', attr=0x28); chip(b, a, ['UP ONE!'], X - 24, Y + 28, 'line')
    return render(b, a, border=6, s=3)
try: f = ImageFont.truetype('DejaVuSans-Bold.ttf', 22); fs = ImageFont.truetype('DejaVuSans.ttf', 17)
except OSError: f = fs = ImageFont.load_default()
BG, FG = (17, 18, 22), (236, 235, 230)
caps = [('A', 'A. A small rounded plate inside the game area: blue outline, clear inside, ordinary letters.'),
        ('B', 'B. The same as a solid blue plate, the letters cut out of it.'),
        ('C', 'C. A black plate (that corner does not scroll, so it can have a colour), letters in the table\'s cyan.'),
        ('D', 'D. A red plate, and a quick message as another plate, top middle, for 2 seconds.'),
        ('E', 'E. The smallest: the place alone on a black plate.'),
        ('F', 'F. Black plate, with a quick message under it as an outline plate.')]
ims = [scene(k) for k, _ in caps]; w, h = ims[0].size
out = Image.new('RGB', (2 * w + 60, 3 * (h + 44) + 60), BG); d = ImageDraw.Draw(out)
d.text((20, 12), 'Position inside the game area: a small rounded plate with the game all round it (mock-up on a real screen)', fill=(255, 255, 255), font=f)
for i, (im, (k, cap)) in enumerate(zip(ims, caps)):
    x, y = 20 + (i % 2) * (w + 20), 52 + (i // 2) * (h + 44); d.text((x, y), cap[:118], fill=FG, font=fs); out.paste(im, (x, y + 24))
p = os.path.join(ROOT, 'docs', 'design', 'ingame_info.png'); out.save(p); print('wrote', os.path.normpath(p), out.size)
