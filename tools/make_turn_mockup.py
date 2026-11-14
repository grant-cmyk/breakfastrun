"""Mock-up (Grant, 14 Nov 2026): "If the cars turning need more pixels can you mock up the turning
cars with the extra pixels ... The car primary shape should remain intact ... its side and core
components should more or less be maintained, e.g. wheels and overall size. In some of these the
turning car is noticeably a smaller shape."
A 17 x 18 car turned 45 degrees is 25 pixels across, so the 20 x 20 frame clips it or the car has
to shrink. Here the angled headings get a 26 x 26 frame and the car stays FULL SIZE:
  row 1  in the game now (20 x 20, corners clipped)
  row 2  Grant's own drawing turned at full size in 26 x 26 (nothing clipped), the number upright
  row 3  each car rebuilt from its parts at full size in 26 x 26 (clean wheels and edges)
Under each angled car: its size (ink + paper pixels) against the upright drawing's.
Writes docs/design/turn_bigger_frame_mockup.png and tools/big_car_art_26.txt (rows 2 and 3)."""
import os, re, sys, math
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
from make_big_cars import pic, cloth
import turn_big_car as T
from turn_car import raster_ss
N = 26; PAD = (N - 20) // 2
t = open(os.path.join(HERE, 'big_car_art.txt')).read()
ART = {(m.group(1), m.group(2)): m.group(3).split() for m in re.finditer(r'== (\w+) big heading ([\d.]+) ==\n((?:[Xo.]{20}\n){20})', t)}
NAMES = ['YOU', 'CYAN', 'WHITE', 'PINK', 'GREEN']
def pad(g): return ['.' * N] * PAD + ['.' * PAD + r + '.' * (N - 20 - PAD) for r in g] + ['.' * N] * (N - 20 - PAD)
def turned(name, h):                                   # row 2: the drawing itself, turned about the car's middle
    big = pad(ART[(name, '0')])                        # (the car's middle, 9.5, lands on 12.5; raster_ss turns about 13)
    big = ['.' + r[:-1] for r in ['.' * N] + big[:-1]] # so move it half a pixel: 1 px down-right, near enough
    g = [list(r) for r in raster_ss(big, T.ANG[h])]
    st = [p for p in T.CARS[name] if p[0] == 'stamp'][0]
    th = math.radians(T.ANG[h]); c, s = math.cos(th), math.sin(th); O = N / 2
    cx = O + (st[1] - T.C) * c - (st[2] - T.C) * s; cy = O + (st[1] - T.C) * s + (st[2] - T.C) * c
    rows = [r[1:-1] for r in st[3][1:-1]]              # the 3 x 5 digit only, in ink
    x0, y0 = round(cx - 1.5), round(cy - 2.5)
    for j in range(-1, 6):
        for i in range(-1, 4):
            if g[y0 + j][x0 + i] != '.': g[y0 + j][x0 + i] = rows[j][i] if 0 <= j < 5 and 0 <= i < 3 else 'X'
    return [''.join(r) for r in g]
def rebuilt(name, h): return T.draw(T.CARS[name], T.ANG[h], scale=1.0, n=N + 1, O=N / 2)[:N]
area = lambda g: sum(c != '.' for r in g for c in r)
def paste(st, g, x, y):
    m = pic(g, 1, (0, 0, 0)); mk = Image.new('L', m.size, 0); mk.putdata([0 if p == (0, 0, 0) else 255 for p in m.get_flattened_data()]); st.paste(m, (x, y), mk)
if __name__ == '__main__':
    Z = 5; CW = 30; rows = [('In the game now: 20 x 20 frame - the turned car is clipped at its corners', lambda n, h: ART[(n, h)], 20),
                             ("26 x 26 frame: Grant's drawing turned at full size, nothing clipped, number upright", turned, N),
                             ('26 x 26 frame: rebuilt from parts at full size - clean wheels and edges, number upright', rebuilt, N)]
    f = ImageFont.truetype('DejaVuSans-Bold.ttf', 17); fs = ImageFont.truetype('DejaVuSans.ttf', 12)
    W = (len(NAMES) * 3 * CW + 8) * Z + 32; H = len(rows) * ((CW + 2) * Z + 62) + 12
    out = Image.new('RGB', (W, H), (17, 18, 22)); d = ImageDraw.Draw(out); y = 10; txt = ''
    for title, fn, n in rows:
        d.text((16, y), title + '   (each car: 0, 22.5, 45 degrees; 5x)', fill=(236, 235, 230), font=f)
        st = cloth(len(NAMES) * 3 * CW + 8, CW + 2)
        for i, nm in enumerate(NAMES):
            a0 = area(ART[(nm, '0')])
            for j, h in enumerate(('0', '22.5', '45')):
                g = ART[(nm, '0')] if h == '0' else fn(nm, h); k = 20 if h == '0' else n
                x = 4 + (i * 3 + j) * CW + (CW - k) // 2
                paste(st, g, x, 1 + (CW - k) // 2)
                if h != '0':
                    d.text((16 + (4 + (i * 3 + j) * CW + 4) * Z, y + 28 + (CW + 2) * Z + 2), '%d%% size' % round(100 * area(g) / a0), fill=(160, 165, 175), font=fs)
                    if n == N: txt += '== %s %s heading %s (26 x 26) ==\n' % (nm, 'turned' if fn is turned else 'rebuilt', h) + '\n'.join(g) + '\n\n'
        out.paste(st.resize((st.width * Z, st.height * Z), Image.NEAREST), (16, y + 28)); y += (CW + 2) * Z + 62
    p = os.path.join(ROOT, 'docs', 'design', 'turn_bigger_frame_mockup.png'); out.save(p); print('wrote', os.path.normpath(p), out.size)
    open(os.path.join(HERE, 'big_car_art_26.txt'), 'w').write("BREAKFAST RUN - MOCK-UP: the angled headings in a 26 x 26 frame, full size (tools/make_turn_mockup.py). Not in the game.\n\n" + txt)
