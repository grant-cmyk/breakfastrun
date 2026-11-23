"""CHOOSE YOUR CAR - a mock-up of the popup over the title (Grant, 23 Nov 2026: "when you click 1, a popup appears asking you
to choose your car. You press left and right to select cars ... show the strengths of each car. This is the grip,
acceleration, speed ... armour"). Not in the game: a picture, drawn on the real title screen (screenshot) with the ROM font
and the cars' own 16 x 16 drawings, kept to the Spectrum's 8 x 8 colour squares. Ratings are Grant's driver cards
(tools/driver_cards.txt). Writes docs/design/choose_popup/choose_popup_mock.png.
Usage: python3 tools/make_choose_popup_mock.py <title screenshot, 352 x 288 with border> <ROM font, 768 bytes>"""
import sys, os, re
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
title = Image.open(sys.argv[1]).convert('RGB'); font = open(sys.argv[2], 'rb').read()
B = 48                                                          # (the border in the screenshot)
N = [(0, 0, 0), (0, 0, 215), (215, 0, 0), (215, 0, 215), (0, 215, 0), (0, 215, 215), (215, 215, 0), (215, 215, 215)]
BR = [(0, 0, 0), (0, 0, 255), (255, 0, 0), (255, 0, 255), (0, 255, 0), (0, 255, 255), (255, 255, 0), (255, 255, 255)]
BLACK, BLUE, RED, MAG, GREEN, CYAN, YELLOW, WHITE = range(8)
def art(files, name):
    t = ''.join(open(os.path.join(HERE, f)).read() for f in files)
    return re.search(r'== %s heading 0 ==\n((?:[Xo.]{16}\n){16})' % name, t).group(1).split()
CARS = [  # name shown, drawing, its colour, ratings A S G R (driver_cards.txt), the line under it, good, poor
    ('RACER', art(['car_art.txt'], 'YOU'), RED, (5, 4, 4, 5), 'THE ALL-ROUNDER', 'NOTHING LETS IT DOWN', 'GRIP: ITS WEAK SPOT'),
    ('TANK', art(['car_art.txt'], 'PINK'), MAG, (4, 2, 8, 9), 'HEAVY AND SLOW', 'CORNERS, BUMPS', 'STARTS, STRAIGHTS'),
    ('DRAGSTER', art(['car_art.txt'], 'WHITE'), WHITE, (7, 8, 1, 2), 'FLIES ON STRAIGHTS', 'STRAIGHTS, NOS', 'CORNERS, OIL, BUMPS'),
    ('SALOON', art(['pool_art.txt'], 'SPECS'), YELLOW, (4, 5, 3, 5), 'A REAL CHALLENGER', 'QUICK ON STRAIGHTS', 'LOOSE IN CORNERS'),
]
def screen(car, idx, total):
    px = [[title.getpixel((B + x, B + y)) for x in range(256)] for y in range(192)]
    def cell(c, r, ink, paper, bits=None, bright=1):       # a colour square: 8 rows of bits (None: all paper)
        P = BR if bright else N
        for y in range(8):
            v = bits[y] if bits else 0
            for x in range(8): px[r * 8 + y][c * 8 + x] = P[ink] if v >> (7 - x) & 1 else P[paper]
    def text(c, r, s, ink=BLACK, paper=WHITE):
        for i, ch in enumerate(s): cell(c + i, r, ink, paper, font[(ord(ch) - 32) * 8:(ord(ch) - 32) * 8 + 8])
    def centre(r, s, ink=BLACK, paper=WHITE, c0=3, w=26): text(c0 + (w - len(s)) // 2, r, s, ink, paper)
    C0, C1, R0, R1 = 3, 28, 3, 22                            # the popup: columns 3-28, rows 3-22
    for r in range(R0, R1 + 1):
        for c in range(C0, C1 + 1): cell(c, r, BLACK, WHITE)
    for c in range(C0, C1 + 1):                                # its frame: a black line round it
        for x in range(8): px[R0 * 8][c * 8 + x] = BR[BLACK]; px[R1 * 8 + 7][c * 8 + x] = BR[BLACK]
    for r in range(R0, R1 + 1):
        for y in range(8): px[r * 8 + y][C0 * 8] = BR[BLACK]; px[r * 8 + y][C1 * 8 + 7] = BR[BLACK]
    for c in range(C0 + 1, C1): cell(c, R0 + 1, WHITE, RED)
    centre(R0 + 1, 'CHOOSE YOUR CAR', WHITE, RED)
    name, a, col, rat, line, good, poor = car
    for r in range(4):                                         # the car, twice the size, on its own colour
        for c in range(4):
            bits = []
            for y in range(8):
                v = 0
                for x in range(8):
                    sy, sx = (r * 8 + y) // 2, (c * 8 + x) // 2
                    v = v << 1 | (a[sy][sx] == 'X')
                bits.append(v)
            cell(14 + c, R0 + 3 + r, BLACK, col, bits, 0 if col == WHITE else 1)   # (Jane's white: not bright, to stand off the popup)
    text(12, R0 + 4, '<'); text(19, R0 + 4, '>')
    text(C1 - 4, R0 + 3, '%d/%d' % (idx, total), BLUE)
    centre(R0 + 7, name, BLACK)
    centre(R0 + 8, line, BLUE)
    COLS = (YELLOW, RED, GREEN, BLUE)
    for k, (lab, v) in enumerate(zip(('ACCEL', 'SPEED', 'GRIP', 'ARMOUR'), rat)):
        r = R0 + 10 + k
        text(5, r, lab)
        for i in range(10):                                    # ten squares: a lit one solid in the rating's colour, the rest an outline
            lit = i < v
            bits = [0x00] + ([0x7E] * 6 if lit else [0x7E] + [0x42] * 4 + [0x7E]) + [0x00]
            cell(12 + i, r, COLS[k] if lit else BLACK, WHITE, bits)
        text(23, r, str(v), BLACK)
    text(5, R0 + 15, '+ ' + good); cell(5, R0 + 15, WHITE, GREEN, font[(ord('+') - 32) * 8:(ord('+') - 32) * 8 + 8])
    text(5, R0 + 16, '- ' + poor); cell(5, R0 + 16, WHITE, RED, font[(ord('-') - 32) * 8:(ord('-') - 32) * 8 + 8])
    centre(R0 + 18, 'LEFT/RIGHT  FIRE TO RACE', BLUE)
    out = title.copy()
    for y in range(192):
        for x in range(256): out.putpixel((B + x, B + y), px[y][x])
    return out
shots = [screen(c, i + 1, 7) for i, c in enumerate(CARS)]
W, H = shots[0].size; Z = 2; G = 16
sheet = Image.new('RGB', (2 * W * Z + G, 2 * H * Z + G), (240, 240, 236))
for i, s in enumerate(shots):
    sheet.paste(s.resize((W * Z, H * Z), Image.NEAREST), ((i % 2) * (W * Z + G), (i // 2) * (H * Z + G)))
os.makedirs(os.path.join(ROOT, 'docs/design/choose_popup'), exist_ok=True)
sheet.save(os.path.join(ROOT, 'docs/design/choose_popup/choose_popup_mock.png'))
for i, s in enumerate(shots): s.resize((W * 2, H * 2), Image.NEAREST).save(os.path.join(ROOT, 'docs/design/choose_popup/popup_%d_%s.png' % (i + 1, CARS[i][0].lower())))
print('written docs/design/choose_popup/')
