"""Breakfast-table scenery, straight top-down, 1-bit (one-bit-art skill):
key shapes and one value each - outlines for edges, SOLID for the darkest
parts (yolk, handles, crust), DITHER for a mid-tone material (juice, toasted
bread, bacon), PAPER for highlights and for the white of plate and egg.
Each item is a list of strings ('#' ink), sized in whole 8x8 tiles."""
import math
from PIL import Image, ImageDraw

def canvas(w, h):
    return [[0] * w for _ in range(h)]
def to_rows(g):
    return [''.join('#' if v else '.' for v in r) for r in g]
def ring(g, cx, cy, r):
    for y in range(len(g)):
        for x in range(len(g[0])):
            d = math.hypot(x + .5 - cx, y + .5 - cy)
            if r - 0.5 <= d < r + 0.5: g[y][x] = 1
def disc(g, cx, cy, r, val=1, cond=None):
    for y in range(len(g)):
        for x in range(len(g[0])):
            if math.hypot(x + .5 - cx, y + .5 - cy) < r and (cond is None or cond(x, y)): g[y][x] = val
def dith(x, y, level):        # 2 = 50% checker, 4 = 25%
    return (x + y) % 2 == 0 if level == 2 else (x % 2 == 0 and y % 2 == 0)

def plate():
    g = canvas(48, 48)
    ring(g, 24, 24, 23); ring(g, 24, 24, 16)                    # rim and well
    for a in range(0, 360, 45):                                  # a glint on the rim, top left
        pass
    return to_rows(g)

def egg():
    g = canvas(24, 24)
    blobs = [(12, 12, 8.0), (5.5, 8, 4.5), (18.5, 6.5, 4.5), (18, 17.5, 4.8), (6, 18, 4.2), (12, 20.5, 3.4), (12, 3.5, 3.0)]
    inside = lambda x, y: any(math.hypot(x + .5 - bx, y + .5 - by) < r for bx, by, r in blobs)
    for y in range(24):
        for x in range(24):
            if inside(x, y) and not all(inside(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                g[y][x] = 1                                      # the white's outline
    disc(g, 11.5, 11.5, 4.6)                                     # yolk, solid
    g[10][10] = 0; g[9][10] = 0                                  # shine
    return to_rows(g)

def toast():
    g = canvas(24, 24)
    def inside(x, y):
        if x < 1 or x > 22 or y > 22: return False
        if y < 7:                                                # the domed top of a slice
            return math.hypot(x + .5 - 6.5, y + .5 - 7) < 6 or math.hypot(x + .5 - 17.5, y + .5 - 7) < 6 or (5 < x < 18 and y > 2)
        return True
    for y in range(24):
        for x in range(24):
            if not inside(x, y): continue
            edge = not all(inside(x + dx, y + dy) for dx in (-2, 0, 2) for dy in (-2, 0, 2))
            g[y][x] = 1 if edge else (1 if dith(x, y, 4) else 0)    # crust solid, bread 25% dither
    return to_rows(g)

def juice():
    g = canvas(24, 24)
    ring(g, 12, 12, 11)                                          # the glass
    disc(g, 12, 12, 9, 1, lambda x, y: dith(x, y, 2))            # juice: 50% dither
    disc(g, 9, 9, 3.2, 0)                                        # highlight crescent: paper
    return to_rows(g)

def bacon():
    g = canvas(32, 16)
    for k, y0 in enumerate((3, 10)):
        for x in range(1, 31):
            yc = y0 + round(1.3 * math.sin((x + 4 * k) / 3.2))
            g[yc - 2][x] = 1; g[yc + 2][x] = 1                   # rasher edges
            if dith(x, yc, 2): g[yc][x] = 1                      # the meat stripe, dithered
        for y in range(16):                                      # square ends
            for x in (1, 30):
                yc = y0 + round(1.3 * math.sin((x + 4 * k) / 3.2))
                if yc - 2 <= y <= yc + 2: g[y][x] = 1
    return to_rows(g)

def cutlery(kind):
    g = canvas(8, 40)
    for y in range(24, 40):                                      # the handle: solid, rounded end
        for x in (2, 3, 4, 5): g[y][x] = 1
    g[39][2] = g[39][5] = 0
    if kind == 'knife':
        for y in range(2, 24):
            g[y][2] = 1; g[y][5 if y > 4 else 4] = 1             # blade outline
        g[1][3] = g[1][4] = 1; g[2][4] = 1
        for x in range(2, 6): g[23][x] = 1
    elif kind == 'fork':
        for y in range(1, 10):
            for x in (1, 3, 4, 6): g[y][x] = 1 if x in (1, 6) or y > 0 else 0
        for y in range(1, 10): g[y][3] = 1 if y > 3 else 0; g[y][4] = 0
        for y in range(1, 10): g[y][3] = 1                       # three tines + outer: 1,3,6
        for y in range(9, 13):
            for x in range(1, 7): g[y][x] = 1                    # tine root
        for y in range(13, 24): g[y][3] = g[y][4] = 1            # neck
    elif kind == 'spoon':
        disc(g, 4, 7, 3.9, 1)                                    # bowl
        disc(g, 4, 7, 2.6, 0)                                    # bowl hollow
        for y in range(11, 24): g[y][3] = g[y][4] = 1            # neck
    return to_rows(g)

ITEMS = {'plate': plate(), 'egg': egg(), 'toast': toast(), 'juice': juice(), 'bacon': bacon(),
         'knife': cutlery('knife'), 'fork': cutlery('fork'), 'spoon': cutlery('spoon')}

if __name__ == '__main__':
    S = 6
    order = list(ITEMS)
    W = sum(len(ITEMS[k][0]) + 8 for k in order) + 8
    img = Image.new('RGB', (W * S, 56 * S), (255, 255, 255))
    x0 = 8
    for k in order:
        for y, row in enumerate(ITEMS[k]):
            for x, c in enumerate(row):
                if c == '#':
                    for a in range(S):
                        for b in range(S): img.putpixel(((x0 + x) * S + a, (4 + y) * S + b), (0, 0, 0))
        x0 += len(ITEMS[k][0]) + 8
    img.save('/home/user/breakfastrun/build/breakfast_preview.png')
    small = img.resize((W * 2, 56 * 2), Image.NEAREST); small.save('/home/user/breakfastrun/build/breakfast_preview_2x.png')
    print('ok', {k: (len(v[0]), len(v)) for k, v in ITEMS.items()})
