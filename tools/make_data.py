"""Generate the car graphics and the thrust table. Writes src/data.asm.

Car art follows the one-bit-art skill (Grant's house style), scaled down from his
top-down Traverse USA cars to 16x16 so a car fits at every heading:
  key shape      value
  tyres          DITHER  (wheels are dithered)
  windscreen     PAPER   (glass is white)
  rear window    PAPER
  roof           SOLID, ringed by paper (open sides - negative space)
  nose           SOLID, with the car's identifying mark carved out in paper
  rear bumper    SOLID line
Identifying marks: player = notch in the nose; CPU A = paper racing stripe through
the roof; CPU B = open cockpit (no roof) with the driver's helmet as a dot.
Headings: never rotate pixels (rule T1). Each key shape is re-rasterised at the
angle (dither phase locked to the pixel grid so it stays a clean checker); the
cardinal frames are exact quarter-turns of the hand-checked upright frame.
Mask: every car pixel opaque, plus a 1px halo so the car reads over track lines."""
import math, os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'src', 'data.asm')
INK, PAPER, DITH, NONE = 1, 0, 2, -1

def car_value(x, y, kind):
    """Value at car-local point (x, y); nose toward -y; units = pixels.
    Body 6 wide x 13 long, tyres 1.5 wide either side."""
    ax = abs(x)
    if 3.0 <= ax <= 4.6 and (-5.0 <= y <= -1.6 or 1.6 <= y <= 5.0):
        return DITH                           # tyres
    if ax > 3.0 or abs(y) > 6.5:
        return NONE
    if y < -3.0:                              # nose
        if kind == 0 and ax < 1.0 and -5.5 <= y < -3.6:
            return PAPER                      # player's notch
        if kind == 3 and ax < 2.0 and -5.0 <= y < -4.0:
            return PAPER                      # CPU C: grille slot across the nose
        return INK
    if y < -1.0:                              # windscreen: glass between the pillars
        return PAPER if ax < 2.0 else INK
    if y < 2.0:                               # roof zone
        if kind == 2:                         # convertible: open cockpit + helmet
            if ax < 1.0 and -0.5 <= y < 1.5: return INK
            return PAPER if ax < 2.0 else INK
        if ax >= 2.0: return PAPER            # open sides ring the roof with paper
        if kind == 1 and ax < 0.75: return PAPER  # CPU A: racing stripe
        if kind == 4 and ax < 1.0 and -0.5 <= y < 1.0: return PAPER  # CPU D: sunroof
        return INK
    if y < 3.0:                               # rear window
        return PAPER if ax < 2.0 else INK
    return INK                                # rear body and bumper

def raster(angle_deg, kind):
    """One sample at each pixel centre: every pixel takes the value of the
    key shape it sits in. (Averaging several samples smeared the 1px glass
    and the roof ring into noise at the angled headings.)"""
    th = math.radians(angle_deg)
    g = [[NONE] * 16 for _ in range(16)]
    for py in range(16):
        for px in range(16):
            dx, dy = px + .5 - 8, py + .5 - 8
            lx = dx * math.cos(th) + dy * math.sin(th)
            ly = -dx * math.sin(th) + dy * math.cos(th)
            g[py][px] = car_value(lx, ly, kind)
    return g

def mirror_diag(g):
    """Reflect across the up-right diagonal: heading 22.5 becomes 67.5 exactly."""
    return [[g[15 - c][15 - r] for c in range(16)] for r in range(16)]

def rot90cw(g):
    return [[g[15 - c][r] for c in range(16)] for r in range(16)]

def frames_for(kind):
    # the 22.5 degree heading is drawn on a 2:1 slope (26.6 degrees): pixel lines
    # step evenly at 2:1, and 4 degrees cannot be seen at 16x16
    n, nne, ne = raster(0, kind), raster(math.degrees(math.atan2(1, 2)), kind), raster(45, kind)
    base = [n, nne, ne, mirror_diag(nne)]
    f = base[:]
    for k in range(4, 16):
        f.append(rot90cw(f[k - 4]))
    return f

def ink_of(g):
    # dither is drawn as a checker locked to the sprite grid
    return [[1 if v == INK or (v == DITH and (x + y) % 2 == 0) else 0
             for x, v in enumerate(row)] for y, row in enumerate(g)]

def mask_of(g):
    solid = [[v != NONE for v in row] for row in g]
    return [[1 if any(solid[y + j][x + i] for j in (-1, 0, 1) for i in (-1, 0, 1)
                      if 0 <= y + j < 16 and 0 <= x + i < 16) else 0
             for x in range(16)] for y in range(16)]

def rows_bytes(bits):
    out = []
    for row in bits:
        v = 0
        for b in row: v = v * 2 + b
        out.append((v >> 8, v & 255))
    return out

KINDS = ['player (notch in the nose)', 'CPU A (racing stripe)', 'CPU B (open cockpit)',
         'CPU C (grille slot in the nose)', 'CPU D (sunroof)']
NAMES = ['YOU', 'CYAN', 'GREEN', 'PINK', 'WHITE']
def hand_drawn():
    """Cars drawn by hand in tools/car_art.txt (the car editor's text): for each
    car named there, its three drawn headings replace the generated ones.
    X = ink, o = paper (the car's white body), . = empty."""
    import re
    path = os.path.join(HERE, 'car_art.txt')
    if not os.path.exists(path): return {}
    got = {}
    for m in re.finditer(r'== (\w+) heading ([\d.]+) ==\n((?:[Xo.]{16}\n){16})', open(path).read()):
        g = [[INK if c == 'X' else PAPER if c == 'o' else NONE for c in r] for r in m.group(3).split()]
        got.setdefault(NAMES.index(m.group(1)), {})[['0', '22.5', '45'].index(m.group(2))] = g
    return got
HAND = hand_drawn()
def frames_of(k):
    f = frames_for(k)
    if k in HAND:
        assert len(HAND[k]) == 3, 'car %s needs all three headings drawn' % NAMES[k]
        n, nne, ne = HAND[k][0], HAND[k][1], HAND[k][2]
        f = [n, nne, ne, mirror_diag(nne)]
        for i in range(4, 16): f.append(rot90cw(f[i - 4]))
    return f
all_frames = [frames_of(k) for k in range(len(KINDS))]

if __name__ == '__main__':
    with open(OUT, 'w') as f:
        f.write('; GENERATED by tools/make_data.py - do not edit by hand\n\n')
        f.write('; thrust per frame for each of 16 headings: dx, dy in 8.8 fixed point\nthrust_tab:\n')
        for n in range(16):
            th = n * 2 * math.pi / 16
            dx, dy = round(64 * math.sin(th)), round(-64 * math.cos(th))
            f.write('        dw 0x%04X,0x%04X\n' % (dx & 0xFFFF, dy & 0xFFFF))
        f.write('\n; car pictures: %d cars x 16 headings' % len(KINDS) + ' x 16 rows x 4 bytes:\n')
        f.write('; mask left, ink left, mask right, ink right (mask 1 = opaque, with a\n')
        f.write('; 1px halo). One stream, so the draw reads it with one pointer.\n')
        f.write('; heading 0 = facing up, clockwise in 22.5 degree steps\ncar_data:\n')
        for k in range(len(KINDS)):
            f.write('; --- car %d: %s ---\n' % (k, KINDS[k]))
            for n, g in enumerate(all_frames[k]):
                f.write('; heading %d\n' % n)
                for (a, b), (ma, mb) in zip(rows_bytes(ink_of(g)), rows_bytes(mask_of(g))):
                    f.write('        defb %%%s,%%%s,%%%s,%%%s\n' % tuple(format(v, '08b') for v in (ma, a, mb, b)))
    with open(OUT, 'a') as f:
        f.write('\n; the rows of each heading that are not empty: first row, how many\n')
        f.write('; (over every car, as hand-drawn cars can differ in shape)\ncar_rows:\n')
        for n in range(16):
            used = [y for y in range(16) if any(any(mask_of(all_frames[k][n])[y]) for k in range(len(KINDS)))]
            f.write('        defb %d,%d   ; heading %d\n' % (used[0], used[-1] - used[0] + 1, n))
    with open(os.path.join(HERE, '..', 'src', 'sq4.asm'), 'w') as f:
        f.write('; GENERATED by tools/make_data.py - do not edit by hand\n')
        f.write('\n; quarter squares: n*n/4 for n = 0..127, low bytes then high bytes,\n')
        f.write('; so a*b = sq4(a+b) - sq4(a-b) needs two look-ups instead of a loop\n')
        f.write('        defs (256 - ($ & 255)) & 255\nsq4:\n')
        q = [n * n // 4 for n in range(128)]
        for i in range(0, 128, 16):
            f.write('        defb ' + ','.join(str(v & 255) for v in q[i:i + 16]) + '\n')
        for i in range(0, 128, 16):
            f.write('        defb ' + ','.join(str(v >> 8) for v in q[i:i + 16]) + '\n')
    # preview sheet: rows = cars, columns = headings 0-3 at 1x, 2x and 6x, on a busy track
    from PIL import Image
    S = 6
    img = Image.new('RGB', (16 * 18 * S, len(KINDS) * 18 * S + 20), (255, 255, 255))
    for k in range(len(KINDS)):
        for n in range(16):
            g = all_frames[k][n]; ink = ink_of(g); m = mask_of(g)
            for y in range(16):
                for x in range(16):
                    bg = (210, 210, 210) if m[y][x] == 0 else (255, 255, 255)
                    c = (0, 0, 0) if ink[y][x] else bg
                    for a in range(S):
                        for b in range(S):
                            img.putpixel(((n * 18 + 1 + x) * S + a, (k * 18 + 1 + y) * S + b), c)
    img.save(os.path.join(HERE, '..', 'build', 'cars_preview.png'))
    print('wrote', os.path.normpath(OUT))
