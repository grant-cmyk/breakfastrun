"""Mock-ups: overall layout options for the race screen and the title screen (Grant, 15 Nov 2026:
"we're going to keep the play area the same size, Can you mockup again some overall design layout
options for the game and the title screen"). Each is a real 256 x 192 Spectrum screen made from
pieces of the game's own screens (docs/design/layout_src/*.png), checked for colour clash: no 8 x 8
cell has more than two colours. The play window is 192 x 152 in every race layout.
Usage: python3 tools/make_layout_options.py   -> docs/design/layout_game.png, layout_title.png"""
import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, '..', 'docs', 'design')
G = Image.open(os.path.join(D, 'layout_src', 'game.png')).convert('RGB')
GR = Image.open(os.path.join(D, 'layout_src', 'grid.png')).convert('RGB')
T = Image.open(os.path.join(D, 'layout_src', 'title.png')).convert('RGB')
ROM = open(os.path.join(HERE, '..', '..', 'zx-emulator', 'roms', '48.rom'), 'rb').read()
K = (0, 0, 0); B = (0, 0, 216); R = (216, 0, 0); M = (216, 0, 216); GN = (0, 216, 0); C = (0, 216, 216); Y = (216, 216, 0); W = (216, 216, 216)
BR = (255, 0, 0); BY = (255, 255, 0); BW = (255, 255, 255); BC = (0, 255, 255); BB = (0, 0, 255); BG = (0, 255, 0); BM = (255, 0, 255)
WIN = G.crop((0, 0, 208, 168)); LOGO = G.crop((72, 168, 128, 184)); MAP = G.crop((208, 0, 256, 40)); RACE = G.crop((208, 72, 256, 160))
FACES = [GR.crop((240, 80 + 16 * i, 256, 96 + 16 * i)) for i in range(5)]
LOGO2 = T.crop((8, 0, 120, 32)); STAGE = T.crop((8, 32, 136, 144)); CARD = T.crop((144, 40, 248, 136))
def recolour(im, pairs, box=None):
    im = im.copy(); px = im.load(); x0, y0, x1, y1 = box or (0, 0) + im.size
    for y in range(y0, y1):
        for x in range(x0, x1):
            for a, b in pairs:
                if px[x, y] == a: px[x, y] = b; break
    return im
class Scr:
    def __init__(s, paper=Y): s.im = Image.new('RGB', (256, 192), paper); s.d = ImageDraw.Draw(s.im)
    def fill(s, cx, cy, w, h, col): s.d.rectangle((cx * 8, cy * 8, (cx + w) * 8 - 1, (cy + h) * 8 - 1), fill=col)
    def paste(s, im, cx, cy): s.im.paste(im, (cx * 8, cy * 8))
    def text(s, t, cx, cy, ink=K, paper=None, tall=False):
        for i, ch in enumerate(t):
            g = ROM[0x3D00 + (ord(ch) - 32) * 8:][:8]
            for y in range(16 if tall else 8):
                row = g[y // 2 if tall else y]
                for x in range(8):
                    on = row >> (7 - x) & 1
                    if on or paper: s.im.putpixel(((cx + i) * 8 + x, cy * 8 + y), ink if on else paper)
    def check(s, name):
        bad = [(cx, cy) for cy in range(24) for cx in range(32) if len(set(s.im.crop((cx * 8, cy * 8, cx * 8 + 8, cy * 8 + 8)).get_flattened_data())) > 2]
        print('%-34s %s' % (name, 'no colour clash' if not bad else 'CLASH in cells %s' % bad[:8])); return s.im
def gingham(s, cx, cy, w, h, a=BR, b=BW):
    for y in range(h):
        for x in range(w): s.fill(cx + x, cy + y, 1, 1, a if (x + y) % 2 == 0 else b)
# ---------------------------------------------------------------- the race screen
def g_now():
    s = Scr(); s.paste(G, 0, 0); return s
def g_full_panel():                 # A: the panel filled top to bottom, the foot of the screen used
    s = Scr(); s.paste(WIN, 0, 0); s.paste(MAP, 26, 0)
    s.paste(RACE, 26, 5)
    s.text('RECORD', 26, 17, BW, B); s.text('0:21.4', 26, 18)
    s.text(' BEST ', 26, 20, BW, B); s.text('0:22.0', 26, 21)
    s.paste(LOGO, 0, 21); s.text("BREAKFAST AT", 9, 21); s.text("TIFFANY'S   TRACK 1", 9, 22)
    return s
def g_mirror():                     # B: the panel on the left, the window against the right edge
    s = Scr(); s.paste(WIN, 6, 0); s.paste(MAP, 0, 0); s.paste(RACE, 0, 5)
    s.text('RECORD', 0, 17, BW, B); s.text('0:21.4', 0, 18)
    s.paste(LOGO, 15, 21); return s
def g_banner():                     # C: a banner along the top, the window under it
    s = Scr(); s.fill(0, 0, 32, 2, BW)
    s.paste(recolour(LOGO, [(Y, BW)], (0, 0, 56, 8)), 0, 0)
    s.text("BREAKFAST AT TIFFANY'S", 8, 0, K); s.text("TRACK 1    RECORD 0:21.4", 8, 1, B)
    gingham(s, 0, 2, 32, 1)
    s.paste(WIN, 0, 3); s.paste(MAP, 26, 3); s.paste(RACE, 26, 9)
    s.text('RECORD', 26, 21, BW, B); s.text('0:21.4', 26, 22); return s
def g_night():                      # D: the surround black - a dashboard; the window is the only bright thing
    s = Scr(K)
    w = recolour(WIN, [(Y, K), (B, BW)], (0, 0, 208, 8)); w = recolour(w, [(Y, K), (B, BW)], (0, 160, 208, 168))
    w = recolour(w, [(Y, K), (B, BW)], (0, 0, 8, 168)); w = recolour(w, [(Y, K), (B, BW)], (200, 0, 208, 168))
    s.paste(w, 0, 0); s.paste(recolour(MAP, [(Y, K), (K, BY)]), 26, 0); s.paste(RACE, 26, 6)
    lg = recolour(LOGO, [(Y, K), (K, BW)], (0, 0, 56, 8)); lg = recolour(lg, [(Y, K), (BY, K)], (0, 8, 32, 16))
    s.paste(lg, 9, 21)
    s.text('RECORD', 26, 18, BY); s.text('0:21.4', 26, 19, BW)
    return s
def g_gingham():                    # E: a tablecloth trim - red and white checks frame the foot and the panel's head
    s = Scr(); s.paste(WIN, 0, 0)
    gingham(s, 26, 0, 6, 1); s.paste(MAP, 26, 1); gingham(s, 26, 6, 6, 1)
    s.paste(RACE, 26, 7); s.text('RECORD', 26, 18, BW, B); s.text('0:21.4', 26, 19)
    gingham(s, 0, 21, 9, 3); gingham(s, 16, 21, 16, 3); s.fill(9, 21, 7, 3, Y); s.paste(LOGO, 9, 21)
    return s
# ---------------------------------------------------------------- the title screen
def keys(s, cx, cy, ink=K):
    s.text('1 - ONE PLAYER', cx, cy, ink); s.text('2 - TWO PLAYERS', cx, cy + 1, ink); s.text('K - KEYS', cx, cy + 2, ink)
def t_now():
    s = Scr(); s.paste(T, 0, 0); return s
def t_centre():                     # A: the logo centred and alone at the top, the stage and card under it as a pair
    s = Scr(); s.paste(LOGO2, 9, 0); gingham(s, 0, 4, 32, 1)
    s.paste(STAGE, 0, 5); s.paste(CARD, 17, 6)
    keys(s, 8, 19); s.text(' LAP RECORD  0:21.4 ', 6, 22, BW, B)
    s.text('PRESS 1 OR 2 TO START', 5, 23, BY, K); return s
def t_menu():                       # B: a breakfast menu card
    s = Scr(BR); gingham(s, 0, 0, 32, 24)
    s.fill(3, 1, 26, 22, BW)
    s.paste(recolour(LOGO2, [(Y, BW)], (0, 0, 112, 16)), 9, 2)
    s.text("TODAY'S MENU", 10, 7, R); s.text('--------------------', 6, 8, K)
    s.text('1  ONE PLAYER ......', 6, 10, K); s.text('2  TWO PLAYERS .....', 6, 12, K); s.text('K  CHOOSE KEYS .....', 6, 14, K)
    s.text('--------------------', 6, 16, K)
    for i, f in enumerate(FACES): s.paste(f, 7 + 4 * i, 17)
    s.text('LAP RECORD   0:21.4', 6, 20, B); s.text('PRESS 1 OR 2 TO START', 5, 22, BW, K); return s
def t_night():                      # C: black, the five drivers in a row, the stage wide
    s = Scr(K)
    lg = recolour(LOGO2, [(Y, K), (K, BW)], (0, 0, 112, 16)); lg = recolour(lg, [(Y, K), (BY, K)], (0, 16, 64, 32)); s.paste(lg, 9, 0)
    st = recolour(STAGE, [(Y, K)]); s.paste(st, 8, 4)
    for i, f in enumerate(FACES):
        s.paste(f, 3 + 6 * i, 18); n = ['YOU', 'CYAN', 'SLIM', 'PINK', 'GREEN'][i]; s.text(n, 4 + 6 * i - (len(n) + 1) // 2, 20, BW)
    keys(s, 9, 21, BY); return s
def t_poster():                     # D: a race poster: the logo huge across the top on white, the stage full width
    s = Scr(); s.fill(0, 0, 32, 5, BW); s.paste(recolour(LOGO2, [(Y, BW)], (0, 0, 112, 16)), 1, 0)
    s.text('THE KITCHEN-TABLE', 15, 1, R); s.text('GRAND PRIX', 15, 2, K)
    gingham(s, 0, 4, 32, 1)
    s.paste(STAGE, 1, 5); s.paste(CARD, 18, 6)
    keys(s, 2, 20); s.text('RECORD 0:21.4', 18, 20, B); s.text('PRESS 1 OR 2 TO START', 5, 23, BY, K); return s
def sheet(items, title, out):
    SC = 2; PADX, PADY, CAP = 24, 24, 46; cols = 2; rows = (len(items) + 1) // 2
    Wd = PADX + cols * (256 * SC + PADX); Ht = 60 + rows * (192 * SC + CAP + PADY)
    im = Image.new('RGB', (Wd, Ht), (24, 26, 32)); d = ImageDraw.Draw(im)
    try: f1 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20); f2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
    except Exception: f1 = f2 = ImageFont.load_default()
    d.text((PADX, 18), title, fill=(240, 240, 240), font=f1)
    for i, (name, note, fn) in enumerate(items):
        x = PADX + (i % cols) * (256 * SC + PADX); y = 60 + (i // cols) * (192 * SC + CAP + PADY)
        scr = fn().check(name)
        im.paste(scr.resize((256 * SC, 192 * SC), Image.NEAREST), (x, y))
        d.text((x, y + 192 * SC + 6), name, fill=(255, 220, 90), font=f1); d.text((x, y + 192 * SC + 28), note, fill=(200, 200, 205), font=f2)
    im.save(os.path.join(D, out)); print('wrote', out, im.size)
if __name__ == '__main__':
    sheet([('NOW', 'as it is today, for comparison', g_now),
           ('A  Full panel', 'panel filled top to bottom; track name and times at the foot', g_full_panel),
           ('B  Mirror', 'panel on the left, play area against the right edge', g_mirror),
           ('C  Banner', 'white title banner with a check trim; everything moves down', g_banner),
           ('D  Night', 'black surround like a dashboard; the play area is the bright thing', g_night),
           ('E  Tablecloth', 'red-and-white check trim round the panel and the foot', g_gingham)],
          'Breakfast Run - race screen layouts (play area 192 x 152 in all)', 'layout_game.png')
    sheet([('NOW', 'as it is today, for comparison', t_now),
           ('A  Centred', 'logo alone and centred; stage and driver card as a pair', t_centre),
           ('B  Menu card', 'a breakfast menu on a check tablecloth; the five drivers in a row', t_menu),
           ('C  Night', 'black, the stage in the middle, the five drivers along the foot', t_night),
           ('D  Poster', 'a race poster: white header with a strapline, check trim', t_poster)],
          'Breakfast Run - title screen layouts', 'layout_title.png')
