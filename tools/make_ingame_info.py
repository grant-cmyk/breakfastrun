"""Mock-up: position and quick "bite" messages INSIDE the game area (Grant, 14 Nov 2026: "I would
like to get some positional information into the game area, its easier for the player to see.
Would be good to have quick bite messages appear in a part of the in game" - "position inside the
game area - maybe top right, masked display to minimise impact to viewing area"). A real screen
from the game (read in zxdev), with the tag and the messages drawn over it four ways. The tag is
"masked" like the health gauge: only the letters and 1 pixel round them cover the table.
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
def scene(kind):
    b, a = bits0.copy(), attrs0.copy()
    R = 8 + 176                                                   # the window's right edge (x); its top is y 8
    if kind == 'A':     # the place alone, big, masked, top right
        stamp(b, glyphs('2', 2), R - 34, 11); stamp(b, glyphs('ND'), R - 18, 11)
    if kind == 'B':     # place and lap
        stamp(b, glyphs('2', 2), R - 34, 11); stamp(b, glyphs('ND'), R - 18, 11); stamp(b, glyphs('L2'), R - 18, 20)
    if kind == 'C':     # place, and a bite under it for 2 seconds
        stamp(b, glyphs('2', 2), R - 34, 11); stamp(b, glyphs('ND'), R - 18, 11); stamp(b, glyphs('L2'), R - 18, 20)
        stamp(b, glyphs('UP ONE!'), R - 58, 32)
    if kind == 'D':     # place in colour (its cells do not scroll, so they can have colours) and a bite across the top
        a[1:3, 19:23] = 0x57; b[8:24, 152:184] = 0                 # white on red, bright
        b[8:24, 152:168] |= glyphs('2', 2); b[8:16, 168:184] |= glyphs('ND'); b[16:24, 168:184] |= glyphs('L2')
        a[1, 7:17] = 0x70; b[8:16, 56:136] = 0; b[8:16, 56:136] |= glyphs('FINAL LAP!')
    return render(b, a, border=6, s=3)
try: f = ImageFont.truetype('DejaVuSans-Bold.ttf', 22); fs = ImageFont.truetype('DejaVuSans.ttf', 17)
except OSError: f = fs = ImageFont.load_default()
BG, FG = (17, 18, 22), (236, 235, 230)
caps = [('A', 'A. Your place, top right: a big figure with small letters, masked (1 clear pixel round each letter).'),
        ('B', 'B. The same with the lap under the letters (L2 = lap 2).'),
        ('C', 'C. B, and a quick message under it for 2 seconds: UP ONE! / DOWN ONE / FINAL LAP / NOS! / OIL OUT'),
        ('D', 'D. In colour: these cells do not scroll, so the place can be white on red and a message black on yellow. A solid block, not masked.')]
ims = [scene(k) for k, _ in caps]; w, h = ims[0].size
out = Image.new('RGB', (2 * w + 60, 2 * (h + 44) + 60), BG); d = ImageDraw.Draw(out)
d.text((20, 12), 'Position and quick messages inside the game area (mock-up on a real screen)', fill=(255, 255, 255), font=f)
for i, (im, (k, cap)) in enumerate(zip(ims, caps)):
    x, y = 20 + (i % 2) * (w + 20), 52 + (i // 2) * (h + 44); d.text((x, y), cap[:118], fill=FG, font=fs); out.paste(im, (x, y + 24))
p = os.path.join(ROOT, 'docs', 'design', 'ingame_info.png'); out.save(p); print('wrote', os.path.normpath(p), out.size)
