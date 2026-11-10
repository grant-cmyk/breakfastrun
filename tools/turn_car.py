"""Draft the 22.5 and 45 degree headings of a hand-drawn car from its heading-0
drawing (X ink, o paper, . empty), for Grant to check and touch up.
Each pixel takes the majority of 16 sample points of the drawing turned to the
angle (not a plain pixel rotation, which the one-bit-art skill warns turns
lines to mush); empty only if mostly empty, else ink unless paper clearly wins.
The 45 degree drawing is made exactly symmetric about the car's own line.
Usage: turn_car.py NAME < heading0.txt  ->  the three '== NAME heading ==' blocks"""
import math, sys
def raster_ss(g, deg, n=4):
    N = len(g); c = N / 2                      # any square grid, turned about its middle
    th = math.radians(deg); out = []
    for py in range(N):
        r = ''
        for px in range(N):
            cnt = {'X': 0, 'o': 0, '.': 0}
            for sy in range(n):
                for sx in range(n):
                    dx, dy = px + (sx + .5) / n - c, py + (sy + .5) / n - c
                    lx = dx * math.cos(th) + dy * math.sin(th); ly = -dx * math.sin(th) + dy * math.cos(th)
                    x, y = math.floor(lx + c), math.floor(ly + c)
                    cnt[g[y][x] if 0 <= x < N and 0 <= y < N else '.'] += 1
            if cnt['.'] > n * n // 2: r += '.'
            elif cnt['o'] > cnt['X']: r += 'o'
            else: r += 'X'
        out.append(r)
    return out
def sym45(g):
    g = [list(r) for r in g]; M = len(g) - 1
    for y in range(M + 1):
        for x in range(M + 1):
            a, b = g[y][x], g[M - x][M - y]
            if a != b:
                g[y][x] = g[M - x][M - y] = 'X' if 'X' in (a, b) else 'o'
    return [''.join(r) for r in g]
def turned(g):
    """The 22.5 (drawn on a 2:1 slope) and 45 degree drafts of heading-0 drawing g."""
    return raster_ss(g, math.degrees(math.atan2(1, 2))), sym45(raster_ss(g, 45))
def blocks(name, g):
    assert len(g) == 16 and all(len(r) == 16 for r in g)
    a, b = raster_ss(g, math.degrees(math.atan2(1, 2))), sym45(raster_ss(g, 45))
    return ''.join('\n== %s heading %s ==\n' % (name, h) + '\n'.join(d) + '\n' for h, d in (('0', g), ('22.5', a), ('45', b)))
if __name__ == '__main__':
    print(blocks(sys.argv[1], sys.stdin.read().split()), end='')
