"""Mock-up: the driver strip under the window (Grant, 10 Nov 2026): the LAP / TIME /
BEST lines go; in their place your face on the left, your inventory (3 slots - you
start with one NOS canister), and a message box ("GREAT DRIVING!" when you
overtake, "SUPERB LAP!", "GET IT TOGETHER" when you hit the O's) - spoken by your
crew chief on the right (Grant: the messages come from the pits). Drawn on a real
race screen (docs/design/mock_screen.bin, from the game) with the Spectrum's own colours
and ROM letters. Writes docs/design/driver_strip.png; and (Grant: "a set of text that is smaller - like the
numbers - to make more space") the same with 3 x 5 letters: docs/design/driver_strip_small.png."""
import os, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
scr = open(os.path.join(ROOT, 'docs', 'design', 'mock_screen.bin'), 'rb').read()
import zx                                         # the ROM's letters, from the emulator's own ROM
font = open(os.path.join(os.path.dirname(zx.__file__), 'roms', 'Spectrum48.rom'), 'rb').read()[0x3D00:0x4000]
PAL = [(0, 0, 0), (0, 0, 215), (215, 0, 0), (215, 0, 215), (0, 215, 0), (0, 215, 215), (215, 215, 0), (215, 215, 215)]
PALB = [(0, 0, 0), (0, 0, 255), (255, 0, 0), (255, 0, 255), (0, 255, 0), (0, 255, 255), (255, 255, 0), (255, 255, 255)]
def load():
    bits = np.zeros((192, 256), np.uint8)
    for y in range(192):
        a = ((y & 0xC0) << 5) | ((y & 7) << 8) | ((y & 0x38) << 2)
        bits[y] = np.unpackbits(np.frombuffer(scr[a:a + 32], np.uint8))
    return bits, bytearray(scr[6144:6912])
def render(bits, attr, s):
    img = np.zeros((192, 256, 3), np.uint8)
    for r in range(24):
        for c in range(32):
            at = attr[r * 32 + c]; pal = PALB if at & 64 else PAL
            ink, pap = np.array(pal[at & 7]), np.array(pal[(at >> 3) & 7])
            cell = bits[r * 8:r * 8 + 8, c * 8:c * 8 + 8][..., None]
            img[r * 8:r * 8 + 8, c * 8:c * 8 + 8] = np.where(cell, ink, pap)
    return Image.fromarray(img).resize((256 * s, 192 * s), Image.NEAREST)
fa = open(os.path.join(ROOT, 'tools', 'face_art.txt')).read()
YOU = re.search(r'== YOU face ==\n((?:[X.]{16}\n){16})', fa).group(1).split()
NOS = ["....XXXX....",      # valve handle
       "......X.....",
       "....XXXX....",      # neck
       "...XXXXXX...",
       "..X......X..",      # shoulders, the body white
       "..X.X....X..",      # a highlight
       "..XXXXXXXX..",      # the label band
       "..XXXXXXXX..",
       "..XXXXXXXX..",
       "..X.X....X..",
       "..X.X....X..",
       "..X......X..",
       "...XXXXXX..."]
CREW = [".....######.....",    # the crew chief: a headset - the band over his
        "...##......##...",    # head, big ear cups, the microphone at his mouth
        "..#..######..#..",
        "..#.#......#.#..",
        ".##..........##.",
        "####.##..##.####",
        "####........####",
        "####...##...####",
        ".##..........##.",
        "..#.........#...",
        "..#..####..####.",
        "...#.......#....",
        "....#.....#.....",
        ".....#####......",
        "................",
        "................"]
def text(bits, s, col, row):
    for i, ch in enumerate(s):
        g = font[(ord(ch) - 32) * 8:(ord(ch) - 32) * 8 + 8]
        for j in range(8):
            bits[row * 8 + j, (col + i) * 8:(col + i + 1) * 8] = np.unpackbits(np.array([g[j]], np.uint8))
def face2x(bits, art, x0):
    for y in range(16):
        for x in range(16):
            if art[y][x] in 'X#': bits[160 + 2 * y:162 + 2 * y, x0 + 2 * x:x0 + 2 * x + 2] = 1
def strip(msg):
    bits, attr = load()
    bits[160:192, 0:192] = 0                       # the old LAP / TIME / BEST lines
    for r in range(20, 24):
        for c in range(24): attr[r * 32 + c] = 0x30
    face2x(bits, YOU, 0)                           # you, twice size, on your red: cols 0-3
    for r in range(20, 24):
        for c in range(0, 4): attr[r * 32 + c] = 0x57
    for k in range(3):                             # the inventory: 3 slots, cols 4-9
        x0 = 32 + k * 16
        for r in (21, 22):
            for c in (4 + 2 * k, 5 + 2 * k): attr[r * 32 + c] = 0x78
        bits[168, x0 + 1:x0 + 15] = 1; bits[183, x0 + 1:x0 + 15] = 1
        bits[169:183, x0] = 1; bits[169:183, x0 + 15] = 1
    for y, row in enumerate(NOS):                  # slot 1: the NOS canister you start with
        for x, v in enumerate(row):
            if v == 'X': bits[169 + 1 + y, 32 + 2 + x] = 1
    x0, x1, y0, y1 = 88, 151, 160, 191             # the message box, cols 11-18: white, rounded
    for r in range(20, 24):
        for c in range(11, 19): attr[r * 32 + c] = 0x78
    bits[y0, x0 + 2:x1 - 1] = 1; bits[y1, x0 + 2:x1 - 1] = 1
    bits[y0 + 2:y1 - 1, x0] = 1; bits[y0 + 2:y1 - 1, x1] = 1
    for (x, y) in ((x0 + 1, y0 + 1), (x1 - 1, y0 + 1), (x0 + 1, y1 - 1), (x1 - 1, y1 - 1)): bits[y, x] = 1
    bits[y0 + 13:y0 + 19, x1] = 0                  # a speech tail out to the crew chief
    for i in range(4):
        bits[y0 + 12 + i, x1 + 1 + i] = 1; bits[y0 + 19 - i, x1 + 1 + i] = 1
    bits[y0 + 15:y0 + 17, x1 + 5] = 1
    face2x(bits, CREW, 160)                        # the crew chief, cols 20-23, on blue
    for r in range(20, 24):
        for c in range(20, 24): attr[r * 32 + c] = 0x4F
    for i, line in enumerate(msg): text(bits, line, 11 + (8 - len(line)) // 2, 21 + i)
    return bits, attr
MSGS = [('GREAT', 'DRIVING!'), ('SUPERB', 'LAP!'), ('GET IT', 'TOGETHER')]
b, a = strip(MSGS[0])
full = render(b, a, 2)
strips = [render(*strip(m), 3).crop((0, 152 * 3, 196 * 3, 192 * 3)) for m in MSGS]
W = max(full.width, strips[0].width) + 32
H = 40 + full.height + 24 + sum(s.height + 16 for s in strips)
out = Image.new('RGB', (W, H), (17, 18, 22)); d = ImageDraw.Draw(out); fnt = ImageFont.load_default()
d.text((16, 12), 'The driver strip: you, your inventory (3), the message, your crew chief  -  the whole screen (2x), then the strip (3x)', fill=(236, 235, 230), font=fnt)
out.paste(full, (16, 36)); y = 36 + full.height + 24
for s in strips: out.paste(s, (16, y)); y += s.height + 16
o = os.path.join(ROOT, 'docs', 'design', 'driver_strip.png'); out.save(o); print('wrote', os.path.normpath(o))

# ---- small letters, 3 x 5 like the race order's numbers (4 px a letter, 6 a line)
SMALL = {'A': ".X.X.XXXXX.XX.X", 'B': "XX.X.XXX.X.XXX.", 'C': ".XXX..X..X...XX", 'D': "XX.X.XX.XX.XXX.",
         'E': "XXXX..XX.X..XXX", 'F': "XXXX..XX.X..X..", 'G': ".XXX..X.XX.X.XX", 'H': "X.XX.XXXXX.XX.X",
         'I': "XXX.X..X..X.XXX", 'J': "..X..X..XX.X.X.", 'K': "X.XX.XXX.X.XX.X", 'L': "X..X..X..X..XXX",
         'M': "X.XXXXXXXX.XX.X", 'N': "XX.X.XX.XX.XX.X", 'O': ".X.X.XX.XX.X.X.", 'P': "XX.X.XXX.X..X..",
         'Q': ".X.X.XX.XXX..XX", 'R': "XX.X.XXX.X.XX.X", 'S': ".XXX...X...XXX.", 'T': "XXX.X..X..X..X.",
         'U': "X.XX.XX.XX.XXXX", 'V': "X.XX.XX.XX.X.X.", 'W': "X.XX.XXXXXXXX.X", 'X': "X.XX.X.X.X.XX.X",
         'Y': "X.XX.X.X..X..X.", 'Z': "XXX..X.X.X..XXX", '!': ".X..X..X.....X.", ' ': "...............",
         '.': ".............X.", '-': "......XXX......", "'": ".X..X..........", '0': "XXXX.XX.XX.XXXX",
         '1': ".X.XX..X..X.XXX", '2': "XX...X.X.X..XXX", '3': "XX...X.X...XXX.", '4': "X.XX.XXXX..X..X",
         '5': "XXXX..XX...XXX.", '6': ".XXX..XXXX.XXXX", '7': "XXX..X.X..X..X.", '8': "XXXX.XXXXX.XXXX",
         '9': "XXXX.XXXX..XXX."}
def stext(bits, s, x, y):
    for i, ch in enumerate(s):
        g = SMALL[ch]
        for j in range(5):
            for k in range(3):
                if g[j * 3 + k] == 'X': bits[y + j, x + i * 4 + k] = 1
def strip_small(lines):
    bits, attr = strip(())
    x0, x1 = 88, 151                                # the box's inside: 62 px, 15 letters
    top = 160 + (32 - (len(lines) * 7 - 2)) // 2
    for i, line in enumerate(lines):
        w = len(line) * 4 - 1
        stext(bits, line, x0 + 1 + (62 - w) // 2, top + i * 7)
    return bits, attr
SMSGS = [('GREAT DRIVING!', 'YOU PASSED', 'JANE.'), ('SUPERB LAP!', '13.5 - BEST', 'SO FAR'), ('GET IT', 'TOGETHER!', 'MIND THE OS')]
b, a = strip_small(SMSGS[0])
full = render(b, a, 2)
strips = [render(*strip_small(m), 3).crop((0, 152 * 3, 196 * 3, 192 * 3)) for m in SMSGS]
W = max(full.width, strips[0].width) + 32
H = 40 + full.height + 24 + sum(s.height + 16 for s in strips)
out = Image.new('RGB', (W, H), (17, 18, 22)); d = ImageDraw.Draw(out)
d.text((16, 12), 'The driver strip with small letters (3 x 5, like the numbers): 3 lines of up to 15  -  the whole screen (2x), then the strip (3x)', fill=(236, 235, 230), font=fnt)
out.paste(full, (16, 36)); y = 36 + full.height + 24
for s in strips: out.paste(s, (16, y)); y += s.height + 16
o = os.path.join(ROOT, 'docs', 'design', 'driver_strip_small.png'); out.save(o); print('wrote', os.path.normpath(o))
