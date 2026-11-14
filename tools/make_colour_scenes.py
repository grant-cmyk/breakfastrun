"""Coloured objects IN PLAY: whole game screens with several objects placed beside the track
(Grant, 14 Nov 2026: "mockups for different coloured objects and how they would look in gameplay
- cleverly working around colour clash - clever use of colours and object sizes to make it feel
like there are more colours allowed than there are"). A mock-up: the game does not draw these yet.

The screens are real ones, read from the game in zxdev during an autopilot lap; the objects (from
tools/make_colour_objects.py) are placed on the WORLD - off the road, clear of the cereal O's and
of each other - and put into each screen's window where the camera sees them, cars on top.
compose() checks every cell: one ink colour, one paper colour.
Usage: python3 tools/make_colour_scenes.py   -> docs/design/colour_scenes.png   (ZXDEV = zxdev)"""
import os, sys, json, math, subprocess, re, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
import make_colour_objects as mc
from make_layout_review import render
src = open(os.path.join(ROOT, 'tests', 'drive_test.py')).read()
src = src[:src.index('with Racer(headless=True)')].replace("os.path.dirname(os.path.abspath(__file__))", repr(os.path.join(ROOT, 'tests')))
exec(src)                                                     # world, wmask, cloth(), surf, MAPW, MAPH, SYM
top = open(os.path.join(ROOT, 'src', 'omap.asm')).read()
orows = [l.split('defb')[1] for l in top[top.index('omap_src:'):].splitlines()[1:] if 'defb' in l][:MAPH]
obits = np.array([[int(c) for b in r.split(',') for c in b.strip().lstrip('%')] for r in orows], dtype=np.uint8)
road = np.array(surf[:MAPW * MAPH], dtype=np.uint8).reshape(MAPH, MAPW)
wps = [tuple(int(v) for v in l.split('dw')[1].split(',')) for l in open(os.path.join(ROOT, 'src', 'waypoints.asm')).read().split('waypoints:')[1].splitlines() if 'dw' in l]
if road[wps[0][1] // 8, wps[0][0] // 8] == 0: road = 1 - road   # (1 = road, whichever way the map has it)
busy = np.kron(road | obits | (np.array(wmask).reshape(MAPH, 8, MAPW, 8).any(axis=(1, 3))), np.ones((8, 8), dtype=np.uint8))   # per pixel: road, an O, a breakfast thing
by = {o.name.split(',')[0]: o for o in mc.OBJECTS}; bl = {o.name.split(',')[0]: o for o in mc.BLENDED}
# the cast, biggest first: (object, blended?) - a spread of colours and sizes
CAST = [(by['Place mat and plate'], 0), (by['Black coffee on a saucer'], 0), (by['Bowl of cereal'], 0), (by['Butter on its dish'], 0), (bl['Fried egg'], 1),
        (by['Jam jar lid'], 0), (bl['Banana'], 1), (by['Waffle'], 0), (by['Mug of tea'], 0), (by['Glass of milk'], 0), (bl['Spilt milk'], 1),
        (by['Slice of toast'], 0), (bl['Strawberry'], 1), (by['Sugar cubes'], 0)]
random.seed(11); placed = []; taken = busy.copy()
def fits(o, x, y, gap):
    if x < 8 or y < 8 or x + o.w > MAPW * 8 - 8 or y + o.h > MAPH * 8 - 8: return False
    return not taken[max(0, y - gap):y + o.h + gap, max(0, x - gap):x + o.w + gap].any()
used = {}
for n in range(len(wps)):                                     # along the lap, both sides of the line, up to two deep:
    (x0, y0), (x1, y1) = wps[n], wps[(n + 1) % len(wps)]; d = math.hypot(x1 - x0, y1 - y0); nx, ny = -(y1 - y0) / d, (x1 - x0) / d
    for side in (1, -1):                                      # whichever of the cast fits there, so sizes and colours mix
        for rep in range(2):
            for o, blend in sorted(CAST, key=lambda c: (used.get(c[0].name, 0), -c[0].w * c[0].h)):   # the least used first, then the biggest
                gap = 12 if blend else 3; done = False
                for dist in range(30, 110, 3):
                    x, y = int(x0 + side * nx * dist - o.w / 2), int(y0 + side * ny * dist - o.h / 2)
                    if fits(o, x, y, gap):
                        g = 12 if blend else 2
                        placed.append((o, x, y)); taken[y - g:y + o.h + g, x - g:x + o.w + g] = 1; used[o.name] = used.get(o.name, 0) + 1; done = True; break
                if done: break
print('placed', len(placed), 'objects on the table')
# ---- real screens from the game ----
ZXDEV = os.environ.get('ZXDEV', os.path.join(ROOT, '..', 'zx-emulator', 'zxdev'))
z = subprocess.Popen([ZXDEV, 'serve', '--stdio'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
def rpc(method, **params):
    z.stdin.write(json.dumps({'id': 1, 'method': method, 'params': params}) + '\n'); z.stdin.flush()
    r = json.loads(z.stdout.readline())
    if 'error' in r: raise SystemExit('%s: %s' % (method, r['error']))
    return r['result']
def mem(addr, n):
    out = b''
    while n:
        r = rpc('read', addr=addr, len=min(n, 1024)); c = bytes.fromhex(r['hex']) if 'hex' in r else bytes(r['bytes']); out += c; addr += len(c); n -= len(c)
    return out
w16 = lambda a: int.from_bytes(mem(a, 2), 'little')
held = set()
def key(kk, down):
    if down and kk not in held: rpc('key_down', keys=kk); held.add(kk)
    if not down and kk in held: rpc('key_up', keys=kk); held.discard(kk)
rpc('load', path=os.path.join(ROOT, 'build', 'racer.tap')); rpc('random', pin=True)
while w16(SYM['renders']) == 0: rpc('run', frames=5)
key('Q', True)
while mem(SYM['race_on'], 1)[0] == 0: rpc('run', frames=1)
x0 = w16(CARS + 1); wp = 0
while wps[wp][0] < x0 + 30: wp += 1
shots = []
for fr in range(1100):
    c = mem(CARS, 11); x, y, ang = c[1] + 256 * c[2] + 8, c[4] + 256 * c[5] + 8, c[10]
    tx, ty = wps[wp]
    if math.hypot(tx - x, ty - y) < 28: wp = (wp + 1) % len(wps)
    diff = (math.degrees(math.atan2(tx - x, -(ty - y))) % 360 - ang * 360 / 64 + 540) % 360 - 180
    key('Q', abs(diff) < 70); key('O', diff < -8); key('P', diff > 8)
    rpc('run', frames=1)
    if fr % 12 == 6: shots.append((mem(0x4000, 6912), w16(SYM['camx']), w16(SYM['camy'])))
z.kill()
def bits_of(m):
    b = np.zeros((192, 256), dtype=np.uint8)
    for yy in range(192):
        a = ((yy & 0xC0) << 5) | ((yy & 7) << 8) | ((yy & 0x38) << 2)
        b[yy] = np.unpackbits(np.frombuffer(m[a:a + 32], dtype=np.uint8))
    return b, np.frombuffer(m[6144:6912], dtype=np.uint8).reshape(24, 32).copy()
def want(cx, cy): return world[cy:cy + WH, cx:cx + 176] | (cloth(cx, cy) & ~wmask[cy:cy + WH, cx:cx + 176])
scenes = []
for m, cx, cy in shots:
    sb, sa = bits_of(m); win = sb[WY:WY + WH, 8:184]
    best = None                                               # the camera the picture was really drawn with
    for dy in range(-8, 9):
        for dx in range(-8, 9):
            if 0 <= cx + dx <= MAPW * 8 - 176 and 0 <= cy + dy <= MAPH * 8 - WH:
                e = int((win != want(cx + dx, cy + dy)).sum())
                if best is None or e < best[0]: best = (e, cx + dx, cy + dy)
    e, cx, cy = best
    if e > 900: continue
    cars = mc.grow((win != want(cx, cy)).astype(np.uint8))    # what is not table: the cars (and lights, canisters)
    things = [(o, x - cx, y - cy) for o, x, y in placed if x - cx < 176 and y - cy < WH and x - cx + o.w > 0 and y - cy + o.h > 0]
    seen = sum(1 for o, x, y in things if 8 <= x + o.w // 2 < 168 and 8 <= y + o.h // 2 < WH - 8)
    try: b, a = mc.compose(win.copy(), things, sprites=(cars, win))
    except AssertionError: continue
    scenes.append((seen, len({o.name for o, _, _ in things}), cx, cy, sb, sa, b, a, things))
print(len(scenes), 'screens without a clash, of', len(shots))
scenes.sort(key=lambda s: (-s[1], -s[0])); pick = []
for s in scenes:                                              # the fullest, from different parts of the lap
    if all(math.hypot(s[2] - p[2], s[3] - p[3]) > 150 for p in pick): pick.append(s)
    if len(pick) == 6: break
try: f = ImageFont.truetype('DejaVuSans-Bold.ttf', 24); fs = ImageFont.truetype('DejaVuSans.ttf', 18)
except OSError: f = fs = ImageFont.load_default()
BG, FG = (17, 18, 22), (236, 235, 230); tiles = []
for seen, kinds, cx, cy, sb, sa, b, a, things in pick:
    sb = sb.copy(); sa = sa.copy(); sb[WY:WY + WH, 8:184] = b; sa[WY // 8:(WY + WH) // 8, 1:23] = a
    im = render(sb, sa, border=6, s=3); t = Image.new('RGB', (im.width, im.height + 34), BG)
    ImageDraw.Draw(t).text((0, 4), ', '.join(sorted({o.name.split(',')[0] for o, _, _ in things})), fill=FG, font=fs); t.paste(im, (0, 34)); tiles.append(t)
cols = 2; rows = (len(tiles) + 1) // 2; W = tiles[0].width * cols + 20 * (cols + 1); notes = [
    'HOW THE COLOUR IS DONE WITHOUT CLASH (checked for every cell of every screen here):',
    '- Big objects with a thick blue edge carry a block of colour inside: the edge soaks up the join with the cloth.',
    '- Soft objects (egg, banana, strawberry, spilt milk) are drawn in their own colour straight on the cloth, with a plain margin round them.',
    '- A second colour inside an object (yolk, butter pat, seeds, the green mat) sits 8 pixels in, so it never shares a cell with the first.',
    '- Different colours stand next to each other as separate objects: the eye reads one busy, many-coloured table.',
    '- Everything is beside the road, clear of the O\'s. Cars are blue; one that leaves the road and crosses a soft object turns its colour.']
out = Image.new('RGB', (W, 60 + rows * (tiles[0].height + 20) + 30 * len(notes) + 30), BG); d = ImageDraw.Draw(out)
d.text((20, 14), 'Coloured objects in play: real game screens with %d objects placed round the track (mock-up)' % len(placed), fill=(255, 255, 255), font=f)
for i, t in enumerate(tiles): out.paste(t, (20 + (i % cols) * (t.width + 20), 60 + (i // cols) * (t.height + 20)))
for i, n in enumerate(notes): d.text((20, 60 + rows * (tiles[0].height + 20) + 30 * i), n, fill=FG, font=fs)
p = os.path.join(ROOT, 'docs', 'design', 'colour_scenes.png'); out.save(p); print('wrote', os.path.normpath(p), out.size)
