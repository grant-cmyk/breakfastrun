"""Draft the 22.5 and 45 degree headings of a hand-drawn car from its heading-0
drawing (X ink, o paper, . empty), for Grant to check and touch up.
Each pixel takes the majority of 16 sample points of the drawing turned to the
angle (not a plain pixel rotation, which the one-bit-art skill warns turns
lines to mush); empty only if mostly empty, else ink unless paper clearly wins.
The 45 degree drawing is made exactly symmetric about the car's own line.
Usage: turn_car.py NAME < heading0.txt  ->  the three '== NAME heading ==' blocks"""
import math, sys
def raster_ss(g, deg, n=4):
    th = math.radians(deg); out = []
    for py in range(16):
        r = ''
        for px in range(16):
            cnt = {'X': 0, 'o': 0, '.': 0}
            for sy in range(n):
                for sx in range(n):
                    dx, dy = px + (sx + .5) / n - 8, py + (sy + .5) / n - 8
                    lx = dx * math.cos(th) + dy * math.sin(th); ly = -dx * math.sin(th) + dy * math.cos(th)
                    x, y = math.floor(lx + 8), math.floor(ly + 8)
                    cnt[g[y][x] if 0 <= x < 16 and 0 <= y < 16 else '.'] += 1
            if cnt['.'] > n * n // 2: r += '.'
            elif cnt['o'] > cnt['X']: r += 'o'
            else: r += 'X'
        out.append(r)
    return out
def sym45(g):
    g = [list(r) for r in g]
    for y in range(16):
        for x in range(16):
            a, b = g[y][x], g[15 - x][15 - y]
            if a != b:
                g[y][x] = g[15 - x][15 - y] = 'X' if 'X' in (a, b) else 'o'
    return [''.join(r) for r in g]
def blocks(name, g):
    assert len(g) == 16 and all(len(r) == 16 for r in g)
    a, b = raster_ss(g, math.degrees(math.atan2(1, 2))), sym45(raster_ss(g, 45))
    return ''.join('\n== %s heading %s ==\n' % (name, h) + '\n'.join(d) + '\n' for h, d in (('0', g), ('22.5', a), ('45', b)))
if __name__ == '__main__':
    print(blocks(sys.argv[1], sys.stdin.read().split()), end='')
