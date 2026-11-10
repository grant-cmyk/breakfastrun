"""Little cartoon faces for the race order: one per car, 16 x 16, 1-bit.
One-bit-art skill: line, not mass; open contours; paper doing the work. Each
face says its driver's way of driving (Grant, 10 Nov 2026):
  YOU    a racing helmet, visor down, a stripe over the top
  CYAN   the racer: shades, angry brows, gritted teeth
  GREEN  the slow truck: asleep - a cap, eyes shut, a snoring o, a z
  PINK   the tank commander: a steel helmet with a star, stern brows, a moustache
  WHITE  Slim Jane: long hair, a fringe, lashes, a smile
  (pool) SPECS  the steady one: round glasses, a straight mouth
Shown ink on the car's colour band. Writes src/faces.asm (16 rows x 2 bytes a
face, kept in TOPMEM) and build/faces/*.txt for one_bit_review.py."""
import os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
HEAD = ["................",
        ".....######.....",
        "...##......##...",
        "..#..........#..",
        ".#............#.",
        ".#............#.",
        "#..............#",
        "#..............#",
        "#..............#",
        "#..............#",
        ".#............#.",
        ".#............#.",
        "..#..........#..",
        "...##......##...",
        ".....######.....",
        "................"]
def face(ink=(), paper=(), base=HEAD):
    g = [list(r) for r in base]
    for x, y in ink: g[y][x] = '#'
    for x, y in paper: g[y][x] = '.'
    return [''.join(r) for r in g]
def line(x0, x1, y): return [(x, y) for x in range(x0, x1 + 1)]
def box(x0, y0, x1, y1): return [(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)]
F = {}
# YOU: helmet - the top half solid with a paper stripe, a visor band with eye slits
F['YOU'] = face(ink=box(3, 2, 12, 4) + line(2, 13, 3) + line(1, 14, 4) + line(1, 14, 5) + box(2, 7, 13, 8),
                paper=[(7, 1), (8, 1), (7, 2), (8, 2), (7, 3), (8, 3), (7, 4), (8, 4), (4, 7), (5, 7), (10, 7), (11, 7)]
                      + line(5, 10, 11))
F['YOU'][11] = F['YOU'][11][:5] + '######' + F['YOU'][11][11:]       # a firm mouth
# CYAN: shades - and angry (Grant, 10 Nov 2026): brows slanting down to the
# middle, the lenses' inner tops lower, teeth gritted
F['CYAN'] = ["................",
             ".....######.....",
             "...##......##...",
             "..#..........#..",
             ".#.##......##.#.",
             ".#...##..##...#.",
             "#.####....####.#",
             "#.#####..#####.#",
             "#..####..####..#",
             "#..............#",
             ".#..########..#.",
             ".#..#.#..#.#..#.",
             "..#.########.#..",
             "...##......##...",
             ".....######.....",
             "................"]
# GREEN: the slow truck - asleep (Grant, 10 Nov 2026): the cap, eyes shut, a
# snoring o, and a z floating up beside it
F['GREEN'] = [".............###",
              "....######....#.",
              "...########..###",
              "..##########....",
              ".#............#.",
              ".#............#.",
              "#..............#",
              "#..####..####..#",
              "#..............#",
              "#..............#",
              ".#............#.",
              ".#.....##.....#.",
              "..#...#..#...#..",
              "...##..##..##...",
              ".....######.....",
              "................"]
# PINK: drives the tracked car - a tank commander (Grant, 10 Nov 2026): a steel
# helmet (solid dome, a paper star badge, a wide brim), stern brows, a moustache
F['PINK'] = ["................",
             ".....######.....",
             "...####..####...",
             "..####....####..",
             "..#####..#####..",
             "################",
             "..#..........#..",
             "..#.###..###.#..",
             "..#..#....#..#..",
             "..#..........#..",
             "..#..######..#..",
             "..#....##....#..",
             "...#........#...",
             "....##....##....",
             "......####......",
             "................"]
# WHITE: Slim Jane (Grant, 10 Nov 2026: "need a girl in the race") - long hair
# framing her face, a fringe, lashes over the eyes, a smile
F['WHITE'] = ["................",
              "....########....",
              "..############..",
              ".##############.",
              ".####......####.",
              "###..........###",
              "##..#.#..#.#..##",
              "##..##....##..##",
              "##............##",
              "##............##",
              "##...#....#...##",
              "##....####....##",
              "##.#........#.##",
              "##..##....##..##",
              "##....####....##",
              "................"]
# The pool: drivers kept for later races, not in the game yet (tools/pool_art.txt)
POOL = {}
# SPECS (WHITE until 10 Nov 2026): a side parting, round glasses joined by a bridge, a straight mouth
POOL['SPECS'] = face(ink=line(5, 12, 2) + [(4, 3), (3, 4)] + [(3, 5), (4, 5), (5, 5), (2, 6), (6, 6), (2, 7), (6, 7), (3, 8), (4, 8), (5, 8),
                       (10, 5), (11, 5), (12, 5), (9, 6), (13, 6), (9, 7), (13, 7), (10, 8), (11, 8), (12, 8), (7, 6), (8, 6), (4, 7), (11, 7)]
                       + line(5, 10, 11))
ORDER = ['YOU', 'CYAN', 'GREEN', 'PINK', 'WHITE']
os.makedirs(os.path.join(ROOT, 'build', 'faces'), exist_ok=True)
with open(os.path.join(ROOT, 'src', 'faces.asm'), 'w') as f:
    f.write('; GENERATED by tools/make_faces.py - a 16 x 16 face per car (kept in TOPMEM)\n')
    f.write('; by car: you, cyan, green, pink, white; 16 rows x 2 bytes\nfaces_src:\n')
    for name in ORDER:
        g = F[name]
        assert len(g) == 16 and all(len(r) == 16 for r in g), name
        open(os.path.join(ROOT, 'build', 'faces', name.lower() + '.txt'), 'w').write('\n'.join(g) + '\n')
        f.write('; %s\n' % name)
        for r in g:
            f.write('        defb %%%s,%%%s\n' % (r[:8].replace('#', '1').replace('.', '0'), r[8:].replace('#', '1').replace('.', '0')))
for name in POOL:
    open(os.path.join(ROOT, 'build', 'faces', name.lower() + '.txt'), 'w').write('\n'.join(POOL[name]) + '\n')
for name in ORDER:
    print(name); print('\n'.join(F[name])); print()
