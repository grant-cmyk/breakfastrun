"""Rebuild the big cars' 22.5 and 45 degree headings from PARTS, not from turned pixels
(Grant, 14 Nov 2026: "I did the straight up images and Claude did the rest - could you see if
you could improve on those"). The first drafts (tools/turn_car.py) turned the pixels of his
heading-0 drawings, which is what the one-bit-art skill warns against (T1): 1-px lines, wheel
centres and numbers turned to mush, and the corners were cut off by the 20 x 20 frame.
Here each car is described once as its key shapes, read off Grant's drawing - body blocks,
wheels, paper insets, the gaps between wheel and body, the number - and each shape is redrawn
at the angle: blocks as clean-edged polygons, gaps and thin paper lines as evenly stepping
lines, and the race number UPRIGHT (so it still reads), in a solid plate.
The turned car is drawn at 0.9 size, so its corners stay inside the frame.
Usage: turn_big_car.py            -> prints the 22.5 and 45 blocks for every car
       turn_big_car.py --write    -> also replaces them in tools/big_car_art.txt"""
import math, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
C = 9.5                                              # the middle of the 19 x 19 the cars are drawn in
def R(v, x0, y0, x1, y1): return ('rect', v, x0, y0, x1 + 1, y1 + 1)       # pixels x0..x1, y0..y1
def G(xa, ya, xb, yb): return ('line', '.', xa, ya, xb, yb)                # a gap: pixel centres
def PL(xa, ya, xb, yb): return ('line', 'o', xa, ya, xb, yb)               # a paper line
def IL(xa, ya, xb, yb): return ('line', 'X', xa, ya, xb, yb)               # an ink line
def ST(cx, cy, rows): return ('stamp', cx, cy, rows)                       # upright, centred there
def mirror(parts):                                   # the right-hand twin of left-hand parts
    out = []
    for p in parts:
        if p[0] == 'rect': out.append(('rect', p[1], 19 - p[4], p[3], 19 - p[2], p[5]))
        elif p[0] == 'line': out.append(('line', p[1], 19 - p[2], p[3], 19 - p[4], p[5]))
    return parts + out
D = {'1': [".o.", "oo.", ".o.", ".o.", "ooo"], '2': ["oo.", "..o", ".o.", "o..", "ooo"], '3': ["oo.", "..o", ".o.", "..o", "oo."],
     '4': ["o.o", "o.o", "ooo", "..o", "..o"], '5': ["ooo", "o..", "oo.", "..o", "oo."]}
def plate(d): return ["XXXXX"] + ['X' + r.replace('.', 'X') + 'X' for r in D[d]] + ["XXXXX"]
def F(v, x0, y0, x1, y1): return ('rect', v, x0, y0, x1, y1)                # edges, not pixels
# The cars AS TURNED: simpler than the upright drawings, because nothing 1 px thick survives a
# turn (the skill's T4). Wheels keep a paper centre only where it is 2 px or more; the gap
# between a wheel and the body is opened to 1.5 px; the tank's treads are 3 wider gaps, not 5.
CARS = {
 # YOU: the racing car. Nose, a wide front with its wheels, waist, a paper cockpit, hollow rear
 # wheels (big enough to keep their paper centres) clear of the rear deck, the wing.
 'YOU': [F('X', 8, 0.6, 11, 3), F('X', 5.5, 3, 13.5, 8), F('X', 6.5, 8, 12.5, 10.5), F('X', 5, 10.5, 14, 13), F('X', 6.4, 13, 12.6, 19)]
        + mirror([F('X', 2.4, 3.2, 5.5, 7.8), F('X', 0.6, 12.4, 5, 18.4), F('o', 1.9, 13.8, 3.7, 17), F('X', 5, 14.8, 6.4, 16.4)])
        + [F('o', 7.6, 11.4, 11.4, 14.6), ST(9.5, 5.4, plate('1'))],
 # CYAN: the six-wheeler. A long body, three solid wheels a side, each on a stub axle, with a
 # clear gap between wheel and body; a paper cockpit.
 'CYAN': [F('X', 7.5, 0, 11.5, 2), F('X', 5.8, 1.4, 13.2, 18), F('X', 7, 18, 12, 19)]
        + mirror([F('X', 0.8, 1.6, 3.9, 6), F('X', 0.8, 7.8, 3.9, 12.2), F('X', 0.8, 14, 3.9, 19),
                  F('X', 3.9, 3, 5.8, 4.6), F('X', 3.9, 9.2, 5.8, 10.8), F('X', 3.9, 15.7, 5.8, 17.3)])
        + [F('o', 7.6, 11.6, 11.4, 15), ST(9.5, 5.6, plate('2'))],
 # WHITE (Slim Jane): the open-wheeler. A thin nose between two small front wheels on an axle,
 # a slim body, two big rear wheels on an axle (the axles 1.6 px, so they hold together).
 'WHITE': [F('X', 8, 0.6, 11, 7), F('X', 7, 7, 12, 10), F('X', 6.2, 10, 12.8, 18.6)]
        + mirror([F('X', 3.4, 0.8, 6, 6), F('X', 1.2, 12.4, 4.6, 19), F('X', 5.8, 2.7, 8, 4.3), F('X', 4.6, 15.2, 6.2, 16.8)])
        + [ST(9.5, 13.5, plate('3'))],
 # PINK: the tank. Two tracks with 3 treads each, cut in from the outside, the hull between, the gun.
 'PINK': [F('X', 5.5, 7, 13.5, 17.6), F('X', 8, 0.6, 11, 7.2)]
        + mirror([F('X', 0.6, 5.4, 5.5, 18.6), F('.', 0, 7.6, 3.6, 9.2), F('.', 0, 11.2, 3.6, 12.8), F('.', 0, 14.8, 3.6, 16.4)])
        + [ST(9.5, 12.5, plate('4'))],
 # GREEN: the clown car. A round body, small front wheels and big rear ones on stub axles, a
 # band of paper (the windscreen) ahead of the number.
 'GREEN': [F('X', 7, 2, 12, 3), F('X', 5.8, 3, 13.2, 6), F('X', 4.4, 6, 14.6, 7), F('X', 3.4, 7, 15.6, 8), F('X', 2.6, 8, 16.4, 12), F('X', 3.4, 12, 15.6, 13),
           F('X', 4.4, 13, 14.6, 14), F('X', 6, 14, 13, 18.6)]
        + mirror([F('X', 0.8, 1.6, 3.9, 5.6), F('X', 0, 14, 4, 19), F('X', 3.9, 3, 5.8, 4.5), F('X', 4, 15.8, 6, 17.4)])
        + [F('o', 6.8, 4.5, 12.2, 6.1), ST(9.5, 10.6, plate('5'))],
}
def bres(x0, y0, x1, y1):
    dx, dy = abs(x1 - x0), -abs(y1 - y0); sx = 1 if x0 < x1 else -1; sy = 1 if y0 < y1 else -1; e = dx + dy; out = []
    while True:
        out.append((x0, y0))
        if (x0, y0) == (x1, y1): return out
        e2 = 2 * e
        if e2 >= dy: e += dy; x0 += sx
        if e2 <= dx: e += dx; y0 += sy
def draw(parts, deg, scale=0.88, n=20, O=None):
    """O: the middle of the frame the car is drawn into (default: the 19 x 19's, as in the game)."""
    O = C if O is None else O
    th = math.radians(deg); c, s = math.cos(th), math.sin(th)
    fwd = lambda x, y: (O + scale * ((x - C) * c - (y - C) * s), O + scale * ((x - C) * s + (y - C) * c))    # clockwise on screen
    g = [['.'] * n for _ in range(n)]
    for py in range(n):                              # the blocks: the last one over a pixel's middle wins
        for px in range(n):
            dx, dy = (px + .5 - O) / scale, (py + .5 - O) / scale
            x, y = C + dx * c + dy * s, C - dx * s + dy * c
            for p in parts:
                if p[0] == 'rect' and p[2] <= x < p[4] and p[3] <= y < p[5]: g[py][px] = p[1]
    def put(x, y, v):
        if 0 <= x < n - 1 and 0 <= y < n - 1: g[y][x] = v
    for p in parts:                                  # then the lines, stepping evenly
        if p[0] == 'line':
            (xa, ya), (xb, yb) = fwd(p[2], p[3]), fwd(p[4], p[5])
            for x, y in bres(math.floor(xa), math.floor(ya), math.floor(xb), math.floor(yb)): put(x, y, p[1])
    keep = set()
    for p in parts:                                  # then the number, upright
        if p[0] == 'stamp':
            cx, cy = fwd(p[1], p[2]); rows = p[3]; x0 = round(cx - len(rows[0]) / 2); y0 = round(cy - len(rows) / 2)
            for j, r in enumerate(rows):
                for i, v in enumerate(r): put(x0 + i, y0 + j, v); keep.add((x0 + i, y0 + j))
    for y in range(n):                               # row 19 and column 19 stay empty (the game's frame)
        g[y][n - 1] = '.'; g[n - 1][y] = '.'
    at = lambda x, y: g[y][x] if 0 <= x < n and 0 <= y < n else '.'
    orth = lambda x, y: [at(x + 1, y), at(x - 1, y), at(x, y + 1), at(x, y - 1)]
    for _ in range(2):                               # tidy (never the number's plate):
        for y in range(n - 1):
            for x in range(n - 1):
                if (x, y) in keep: continue
                o = orth(x, y); v = g[y][x]
                if v == '.' and sum(c != '.' for c in o) == 4: g[y][x] = 'X'          # a pinhole: filled
                elif v == 'X' and sum(c != '.' for c in o) <= 1: g[y][x] = '.'        # a spur: off
                elif v == 'o' and ('.' in o or 'o' not in o): g[y][x] = 'X'           # paper on the edge, or a lone speck
    return [''.join(r) for r in g]
ANG = {'22.5': math.degrees(math.atan2(1, 2)), '45': 45.0}     # 22.5 is drawn on a 2:1 slope, as before
def blocks(name):
    return {h: draw(CARS[name], a) for h, a in ANG.items()}
if __name__ == '__main__':
    p = os.path.join(HERE, 'big_car_art.txt'); t = open(p).read()
    for name in CARS:
        for h, g in blocks(name).items():
            blk = '== %s big heading %s ==\n' % (name, h) + '\n'.join(g) + '\n'
            print(blk)
            t, k = re.subn(r'== %s big heading %s ==\n(?:[Xo.]{20}\n){20}' % (name, re.escape(h)), blk, t); assert k == 1, (name, h)
    if '--write' in sys.argv: open(p, 'w').write(t); print('wrote', p)
    else: open(os.environ.get('OUT', '/dev/null'), 'w').write(t)
