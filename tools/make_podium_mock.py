"""Mock-ups: the race-finished display (Grant, 15 Nov 2026: "Once all players are finished, there is
a winner display in the centre of the gameplay area (can be a different colour so overlays on the
blue/cyan). Maybe a podium with their faces, 1st, 2nd, 3rd, then also show fastest lap. Winner
must have a graphic showing them smiling"). Real 256 x 192 screens over the game's own race
screen, checked for colour clash. WIN holds a smiling 16 x 16 face for each driver, drafted here.
Usage: python3 tools/make_podium_mock.py -> docs/design/podium_options.png, podium_faces.png"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_layout_options as L
from PIL import Image, ImageDraw
K, B, R, M, GN, C, Y, W, BR, BY, BW, BC, BB, BG, BM = L.K, L.B, L.R, L.M, L.GN, L.C, L.Y, L.W, L.BR, L.BY, L.BW, L.BC, L.BB, L.BG, L.BM
NAMES = ['YOU', 'CYAN', 'SLIM', 'PINK', 'GREEN']; COL = [BR, BC, BW, BM, BG]
def bits(im):
    bg = im.getpixel((0, 0)); return [''.join('#' if im.getpixel((x, y)) != bg else '.' for x in range(16)) for y in range(16)]
FACE = [bits(f) for f in L.FACES]
def edit(face, rows):
    f = list(face)
    for y, r in rows.items(): f[y] = r
    return f
WIN = [edit(FACE[0], {4: '...##########...', 5: '...#........#...', 6: '...#.##..##.#...', 7: '...#........#...', 8: '...#.#....#.#...', 9: '...#.######.#...', 10: '....#.#..#.#....', 11: '....#..##..#....'}),
       edit(FACE[1], {9: '...#........#...', 10: '...#.######.#...', 11: '....#.#..#.#....', 12: '....##.##.##....'}),
       edit(FACE[2], {7: '....#......#....', 8: '...#.#....#.#...', 9: '..###.####.###..'}),
       edit(FACE[3], {9: '..#..........#..', 10: '...#.#....#.#...', 11: '...#.######.#...', 12: '....#.#..#.#....', 13: '.....#.##.#.....'}),
       edit(FACE[4], {9: '..#..........#..', 10: '...#.#....#.#...', 11: '...#.######.#...', 12: '....#.#..#.#....', 13: '.....#.##.#.....'})]
SAD = [edit(FACE[0], {4: '...##########...', 5: '...#..#..#..#...', 6: '...#.##..##.#...', 7: '...#.#......#...', 8: '...#........#...', 9: '...#..####..#...', 10: '....##....##....', 11: '....#......#....'}),
       edit(FACE[1], {9: '...#........#...', 10: '...#..####..#...', 11: '....##....##....', 12: '....#......#....'}),
       edit(FACE[2], {7: '....#.#....#....', 8: '...#...##...#...', 9: '..###.#..#.###..'}),
       edit(FACE[3], {9: '..#...#......#..', 10: '...#........#...', 11: '...#..####..#...', 12: '....##....##....'}),
       edit(FACE[4], {9: '..#...#......#..', 10: '...#........#...', 11: '...#..####..#...', 12: '....##....##....'})]
def face(s, art, cx, cy, ink, paper, scale=1):
    for y, r in enumerate(art):
        for x, ch in enumerate(r):
            s.d.rectangle((cx * 8 + x * scale, cy * 8 + y * scale, cx * 8 + x * scale + scale - 1, cy * 8 + y * scale + scale - 1), fill=ink if ch == '#' else paper)
def big_digit(s, ch, cx, cy, ink, paper):      # the ROM's digit twice the size
    g = L.ROM[0x3D00 + (ord(ch) - 32) * 8:][:8]
    for y in range(16):
        for x in range(16): s.im.putpixel((cx * 8 + x, cy * 8 + y), ink if g[y // 2] >> (7 - x // 2) & 1 else paper)
_src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'make_strip_mockups.py')).read()
_ns = {'__file__': 'make_strip_mockups.py'}; exec(_src[_src.index('# ---- small letters'):_src.index('def stext')], _ns)
SMALL = dict(_ns['SMALL'])                      # the game's own 3 x 5 letters (A-Z ! . - '), and its figures
SMALL.update({'0': '111 101 101 101 111', '1': '010 110 010 010 111', '2': '111 001 111 100 111', '3': '111 001 111 001 111', '4': '101 101 111 001 001',
              '5': '111 100 111 001 111', '6': '111 100 111 101 111', '7': '111 001 010 010 010', '8': '111 101 111 101 111', '9': '111 101 111 001 111',
              ':': '000 010 000 010 000', ' ': '000 000 000 000 000'})
def small(s, t, x, y, ink):                     # small letters, 4 pixels apart, top-left at pixel (x, y)
    for i, ch in enumerate(t):
        g = SMALL[ch]; g = g.split() if ' ' in g else [g[k:k + 3] for k in range(0, 15, 3)]
        for r, row in enumerate(g):
            for c, b in enumerate(row):
                if b in '1#X': s.im.putpixel((x + 4 * i + c, y + r), ink)
def smallc(s, t, cx0, cx1, y, ink): small(s, t, (cx0 * 8 + cx1 * 8 + 8 - (4 * len(t) - 1)) // 2, y, ink)   # centred over cells cx0..cx1
def tight(s, panel=BW, text=K, bar=B, bar_ink=BW, steps=(BY, C, M)):
    w, a, b = ORDER
    s.fill(6, 3, 14, 13, panel)
    s.fill(6, 3, 14, 1, bar); smallc(s, 'CHEQUERED FLAG', 6, 19, 25, bar_ink)
    s.fill(11, 4, 4, 4, COL[w]); face(s, WIN[w], 11, 4, K, COL[w], 2)
    smallc(s, 'WINNER', 6, 10, 41, R if panel != K else BY); smallc(s, 'WINNER', 15, 19, 41, R if panel != K else BY)
    s.fill(10, 8, 6, 5, steps[0]); big_digit(s, '1', 12, 8, K, steps[0]); smallc(s, NAMES[w], 10, 15, 90, K)
    s.fill(7, 7, 2, 2, COL[a]); face(s, FACE[a], 7, 7, K, COL[a])
    s.fill(6, 9, 4, 4, steps[1]); big_digit(s, '2', 7, 9, K, steps[1]); smallc(s, NAMES[a], 6, 9, 90, K)
    s.fill(17, 8, 2, 2, COL[b]); face(s, FACE[b], 17, 8, K, COL[b])
    s.fill(16, 10, 4, 3, steps[2]); big_digit(s, '3', 17, 10, K, steps[2]); smallc(s, NAMES[b], 16, 19, 98, K)
    smallc(s, 'FASTEST LAP', 6, 19, 106, text); smallc(s, '%s 0:21.4' % NAMES[FAST[0]], 6, 19, 114, text)
    s.fill(6, 15, 14, 1, bar); smallc(s, 'PRESS ANY KEY', 6, 19, 121, bar_ink)
def p_tight():
    s = base(); tight(s); return s
def p_tight_n():
    s = base(); tight(s, steps=(BY, BW, BW)); return s
def base():
    s = L.Scr(); s.paste(L.G, 0, 0); return s
ORDER = [1, 0, 3]; FAST = (1, '0:21.4')        # a sample result: CYAN wins, YOU second, PINK third; CYAN has the fastest lap
def podium(s, panel, text, step, head_ink, head_paper):
    s.fill(4, 2, 18, 16, panel)
    s.text('   CHEQUERED FLAG   '[1:19], 4, 2, head_ink, head_paper)
    w, a, b = ORDER
    s.text('WINNER', 5, 4, text); s.text(NAMES[w], 5, 5, text)
    s.text('*', 16, 6, BY if panel == K else R); s.text('*', 15, 5, BY if panel == K else R); s.text('*', 15, 3, BY if panel == K else R)
    s.fill(11, 4, 4, 4, COL[w]); face(s, WIN[w], 11, 4, K, COL[w], 2)
    s.fill(10, 8, 6, 6, step[0]); big_digit(s, '1', 12, 9, K if step[0] != B else BW, step[0])
    s.fill(6, 7, 2, 2, COL[a]); face(s, FACE[a], 6, 7, K, COL[a])
    s.fill(5, 9, 5, 5, step[1]); big_digit(s, '2', 6, 10, BW if step[1] in (B, K, R) else K, step[1]); s.text(NAMES[a], 5, 12, BW if step[1] in (B, K, R) else K)
    s.fill(17, 8, 2, 2, COL[b]); face(s, FACE[b], 17, 8, K, COL[b])
    s.fill(16, 10, 5, 4, step[2]); big_digit(s, '3', 17, 11, BW if step[2] in (B, K, R) else K, step[2]); s.text(NAMES[b], 16, 13, BW if step[2] in (B, K, R) else K)
    s.text('FASTEST LAP', 5, 15, text); s.text('%s  %s' % (NAMES[FAST[0]], FAST[1]), 7, 16, text)
    s.text('PRESS ANY KEY', 6, 17, head_ink, head_paper)
def p_card():
    s = base(); podium(s, BW, K, (BY, C, M), BW, B); return s
def p_night():
    s = base(); podium(s, K, BW, (BY, BC, BM), K, BY); return s
def p_table():
    s = base(); podium(s, Y, K, (BW, BW, BW), BW, R); return s
def p_strip():                                 # less of the window covered: a band across the middle
    s = base(); w, a, b = ORDER
    s.fill(1, 6, 24, 8, BW); s.text('     CHEQUERED FLAG     ', 1, 6, BW, B)
    s.fill(2, 8, 4, 4, COL[w]); face(s, WIN[w], 2, 8, K, COL[w], 2); s.text('WINNER', 7, 8, R); s.text(NAMES[w], 7, 9, K)
    for i, d in enumerate((a, b)):
        s.fill(14, 8 + 2 * i, 2, 2, COL[d]); face(s, FACE[d], 14, 8 + 2 * i, K, COL[d]); s.text('%s %s' % ('2ND 3RD'.split()[i], NAMES[d]), 17, 8 + 2 * i, K)
    s.text('FASTEST LAP %s %s' % (FAST[1], NAMES[FAST[0]]), 2, 12, B)
    s.text('    PRESS ANY KEY       ', 1, 13, K, BY); return s
def faces_sheet():
    Z = 12; im = Image.new('RGB', (40 + 5 * (16 * Z + 24), 70 + 3 * (16 * Z + 40)), (24, 26, 32)); d = ImageDraw.Draw(im)
    from PIL import ImageFont
    f1 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
    d.text((24, 16), 'Breakfast Run - each driver: as now, happy (won), sad', fill=(240, 240, 240), font=f1)
    for i in range(5):
        for k, art in enumerate((FACE[i], WIN[i], SAD[i])):
            x0 = 24 + i * (16 * Z + 24); y0 = 60 + k * (16 * Z + 40)
            d.rectangle((x0, y0, x0 + 16 * Z - 1, y0 + 16 * Z - 1), fill=COL[i])
            for y, r in enumerate(art):
                for x, ch in enumerate(r):
                    if ch == '#': d.rectangle((x0 + x * Z, y0 + y * Z, x0 + x * Z + Z - 1, y0 + y * Z + Z - 1), fill=K)
            d.text((x0, y0 + 16 * Z + 6), NAMES[i] + ('', ' - HAPPY', ' - SAD')[k], fill=(255, 220, 90), font=f1)
    im.save(os.path.join(L.D, 'podium_faces.png')); print('wrote podium_faces.png', im.size)
if __name__ == '__main__':
    L.sheet([('A2  Podium card, tight', 'A drawn tighter: small letters, everything centred; 14 x 13 cells', p_tight),
             ('A3  The same, plain steps', 'as A2 with white steps for 2nd and 3rd: the faces carry the colour', p_tight_n)],
            'Breakfast Run - the winner display, tightened (sample result: CYAN wins, YOU 2nd, PINK 3rd)', 'podium_tight.png')
    L.sheet([('A  Podium card', 'white card over the cloth; yellow, cyan and pink steps', p_card),
             ('B  Podium, night', 'black card: the brightest thing on the screen', p_night),
             ('C  Podium, table', 'the table\'s yellow, white steps, red heading', p_table),
             ('D  Results band', 'a band across the middle: more of the track still shows', p_strip)],
            'Breakfast Run - race finished: the winner display (sample result: CYAN wins, YOU 2nd, PINK 3rd)', 'podium_options.png')
    faces_sheet()
