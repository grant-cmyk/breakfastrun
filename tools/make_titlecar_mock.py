"""Mock-ups: the title's cars in BLACK in front of the red and white checks (Grant, 15 Nov 2026: "the
cars are red now. Is it possible to make them black against the red and white?"). A cell has two
colours, and the checks use both, so black needs a give somewhere: each row here is one way.
The five cars are read from the built game (big_tab: mask and ink). Checked for colour clash.
Usage: python3 tools/make_titlecar_mock.py -> docs/design/titlecar_options.png"""
import os, sys, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SYM = {}
for l in open(os.path.join(ROOT, 'build', 'racer.sym')):
    p = l.split()
    if len(p) >= 3 and p[1] == 'EQU': SYM[p[0].lower()] = int(p[2].rstrip('H'), 16)
z = subprocess.Popen([os.path.join(ROOT, '..', 'zx-emulator', 'zxdev'), 'serve', '--stdio'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
def rpc(m, **p):
    z.stdin.write(json.dumps({'id': 1, 'method': m, 'params': p}) + '\n'); z.stdin.flush(); return json.loads(z.stdout.readline())['result']
rd = lambda a, n: bytes.fromhex(rpc('read', addr=a, len=n)['hex'])
rpc('load', path=os.path.join(ROOT, 'build', 'racer.tap')); rpc('run', frames=300)
CARS = []
for car in range(5):
    e = rd(SYM['big_tab'] + (car * 16 + 4) * 4, 4); ptr = e[0] | e[1] << 8; off, rows = e[2], e[3]
    d = rd(ptr, rows * 4); mask = [[0] * 16 for _ in range(off + rows)]; ink = [[0] * 16 for _ in range(off + rows)]
    for r in range(rows):
        m = d[r * 4] << 8 | d[r * 4 + 2]; i = d[r * 4 + 1] << 8 | d[r * 4 + 3]
        for x in range(16): mask[off + r][x] = m >> (15 - x) & 1; ink[off + r][x] = i >> (15 - x) & 1
    CARS.append((mask, ink))
z.kill()
R, W, K = (255, 0, 0), (255, 255, 255), (0, 0, 0)
STRIP_W, STRIP_H = 5 * 48 + 8, 24
def cloth(x, y): return R if (x // 8 + y // 8) % 2 == 0 else W
def strip(mode):
    im = Image.new('RGB', (STRIP_W, STRIP_H)); px = im.load()
    for y in range(STRIP_H):
        for x in range(STRIP_W): px[x, y] = cloth(x, y)
    for n, (mask, ink) in enumerate(CARS):
        x0, y0 = 12 + 48 * n + n, 4 - (n % 2)                 # (not on the cells' grid: as in the game)
        cells = set()
        for r, row in enumerate(mask):
            for x in range(16):
                if row[x] or ink[r][x]: cells.add(((x0 + x) // 8, (y0 + r) // 8))
        if mode == 'patch':
            for cx, cy in cells:
                for yy in range(8):
                    for xx in range(8):
                        if 0 <= cy * 8 + yy < STRIP_H: px[cx * 8 + xx, cy * 8 + yy] = W
        for r, row in enumerate(mask):
            for x in range(16):
                X, Y = x0 + x, y0 + r
                if not (0 <= Y < STRIP_H): continue
                m, i = row[x], ink[r][x]
                if mode == 'red': c = R if i else (W if m else None)
                elif mode == 'through': c = K if i else None
                elif mode == 'patch': c = K if i else None
                elif mode == 'solid': c = K if (m or i) else None
                elif mode == 'inverse': c = (None if i else K) if (m or i) else None
                if c: px[X, Y] = c
    bad = sum(1 for cy in range(STRIP_H // 8) for cx in range(STRIP_W // 8) if len(set(im.crop((cx * 8, cy * 8, cx * 8 + 8, cy * 8 + 8)).get_flattened_data())) > 2)
    return im, bad
ROWS = [('NOW  Red line, white mask', 'as built: a tight white shape, the car\'s lines in red', 'red'),
        ('A  Black line, see-through', 'black cars; the checks show inside them (how it was at first)', 'through'),
        ('B  Black line on a white patch', 'the cells under a car turn white: black car, no red inside - but the patch is square and jumps 8 pixels at a time', 'patch'),
        ('C  Solid black shape', 'the car\'s tight shape filled black: no detail inside', 'solid'),
        ('D  Black shape, cloth-coloured lines', 'filled black, the car\'s lines cut out of it: they show red or white as the cloth behind', 'inverse')]
Z = 5; f1 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20); f2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
out = Image.new('RGB', (STRIP_W * Z + 48, 70 + len(ROWS) * (STRIP_H * Z + 70)), (24, 26, 32)); d = ImageDraw.Draw(out)
d.text((24, 18), 'Breakfast Run - the title\'s five cars in front of the checks: ways to have them black', fill=(240, 240, 240), font=f1)
for k, (name, note, mode) in enumerate(ROWS):
    im, bad = strip(mode); y = 64 + k * (STRIP_H * Z + 70)
    out.paste(im.resize((STRIP_W * Z, STRIP_H * Z), Image.NEAREST), (24, y))
    d.text((24, y + STRIP_H * Z + 6), name, fill=(255, 220, 90), font=f1); d.text((24, y + STRIP_H * Z + 32), note, fill=(200, 200, 205), font=f2)
    print('%-38s %s' % (name, 'no colour clash' if not bad else '%d cells with three colours' % bad))
out.save(os.path.join(ROOT, 'docs', 'design', 'titlecar_options.png')); print('wrote titlecar_options.png', out.size)
