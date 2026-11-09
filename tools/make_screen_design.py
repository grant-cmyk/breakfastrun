"""Screen designs for the Claude Design canvas, as real Spectrum screens
(bitmap + one attribute per 8x8 cell, ROM font, real race frame, real cars,
the 1-bit logo). Writes PNGs to the folder given as argv[1]."""
import sys, os, json, numpy as np
from PIL import Image, ImageDraw
OUT = sys.argv[1]; S = os.environ['S']
sys.argv = [sys.argv[0]]
exec(open('/home/user/breakfastrun/tools/make_hud_mockups.py').read().split('# A - bottom strip')[0])
LOGO = [[1 if c == '#' else 0 for c in l.strip()] for l in open('/home/user/breakfastrun/build/logo.txt')]
def logo(s, r, c):
    for y, row in enumerate(LOGO):
        s.bm[r * 8 + y, c * 8:c * 8 + 56] = row
    s.cells(r, c, r, c + 6, BLACK, YEL, 0)
    s.cells(r + 1, c, r + 2, c + 4, RED, YEL, 1)
    s.cells(r + 1, c + 5, r + 2, c + 6, WHITE, YEL, 1)
PAPER = {0: RED, 1: CYAN, 2: GREEN, 3: MAG, 4: WHITE}
def panel(s, order, lap, time, best):
    logo(s, 1, 25)
    s.text(5, 25, ' RACE  '[:7], WHITE, BLUE, 1)
    for i, k in enumerate(order):
        r = 6 + 2 * i
        pk, ik = (RED, WHITE) if k == 0 else (PAPER[k], BLACK)
        s.cells(r, 25, r + 1, 31, ik, pk, 1)
        s.text(r, 25, str(i + 1), ik, pk, 1)
        s.car(r * 8, 27 * 8, k)
        s.text(r + 1, 30, 'YOU'[:0])
    s.text(17, 25, 'LAP'); s.big(18, 25, str(lap), WHITE, BLUE, 1); s.text(19, 27, '/3')
    s.text(21, 25, 'TIME'); s.text(22, 25, time)
    if best: s.text(17, 29, 'BEST'[:3]); s.text(18, 29, best[:3])
def progress(s, marks):
    # lap-progress strip under the window: a line from the start line round to it again
    y = 22 * 8 + 3
    s.bm[y:y + 2, 8:24 * 8] = 1
    for i in range(0, 8, 2): s.bm[y - 3 + i:y - 1 + i, 23 * 8 + 4:23 * 8 + 6] = 1   # finish flag stub
    for k, frac in marks:
        x = 8 + int(frac * (22 * 8 - 6))
        s.bm[y - 3:y + 5, x:x + 4] = 1
        s.bm[y - 2:y + 4, x + 1:x + 3] = 0 if k else 1
        if k == 0:
            s.cells(22, x // 8, 22, x // 8, RED, YEL, 1)
            s.text(21, max(1, x // 8 - 1), 'YOU', RED, YEL, 1)
def base(msg=None, msg_big=False, msg_col=None):
    s = Screen(); s.window(4, 1, 23)
    if msg:
        if msg_big: s.big(1, msg_col if msg_col is not None else 1, msg, WHITE, RED, 1)
        else: s.text(1, msg_col if msg_col is not None else 1, msg)
    return s
order = [1, 3, 0, 2, 4]
# mid race
m = base('FINAL LAP!', True, 2)
panel(m, order, 3, '0:42.6', '')
progress(m, [(1, .78), (3, .70), (0, .62), (2, .55), (4, .31)])
m.png(OUT + '/race_mid.png')
# start: lights
st = base()
for i, col in enumerate((RED, RED, RED)):
    st.cells(1, 2 + 3 * i, 2, 3 + 3 * i, col, BLACK, 1)
    st.big(1, 2 + 3 * i, 'O'.replace('O', '\x7f') if False else 'O', col, BLACK, 1)
st.text(1, 12, 'GET READY'); st.text(2, 12, 'PRESS Q')
panel(st, [0, 1, 2, 3, 4], 1, '0:00.0', '')
progress(st, [(k, .02) for k in (1, 3, 2, 4)] + [(0, .02)])
st.png(OUT + '/race_start.png')
# finish
fi = base('FINISHED 2ND', True, 0)
panel(fi, [1, 0, 3, 2, 4], 3, '0:58.4', '')
fi.text(21, 1, 'BEST LAP 0:18.9'); fi.text(22, 1, 'PRESS Q TO RACE AGAIN')
fi.png(OUT + '/race_finish.png')
# cell map: what every cell is for
cm = base('FINAL LAP!', True, 2); panel(cm, order, 3, '0:42.6', ''); progress(cm, [(1, .78), (3, .70), (0, .62), (2, .55), (4, .31)])
cm.png(OUT + '/cells_raw.png', scale=3)
im = Image.open(OUT + '/cells_raw.png').convert('RGBA'); ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
def box(c0, r0, c1, r1, col):
    d.rectangle([(32 + c0 * 8) * 3, (24 + r0 * 8) * 3, (32 + (c1 + 1) * 8) * 3 - 1, (24 + (r1 + 1) * 8) * 3 - 1], fill=col + (70,), outline=col + (255,), width=3)
box(1, 4, 23, 19, (0, 120, 255)); box(25, 1, 31, 3, (255, 140, 0)); box(25, 5, 31, 15, (200, 0, 200))
box(25, 17, 31, 22, (0, 170, 90)); box(0, 0, 23, 2, (230, 40, 40)); box(0, 21, 23, 23, (120, 120, 120))
for c in range(33): d.line([((32 + c * 8) * 3, 24 * 3), ((32 + c * 8) * 3, (24 + 192) * 3)], fill=(0, 0, 0, 40))
for r in range(25): d.line([(32 * 3, (24 + r * 8) * 3), ((32 + 256) * 3, (24 + r * 8) * 3)], fill=(0, 0, 0, 40))
Image.alpha_composite(im, ov).convert('RGB').save(OUT + '/cells_map.png'); os.remove(OUT + '/cells_raw.png')
# logo sheet: colour at 8x, and at real size (1x, 2x) on the yellow
lg = Screen(); logo(lg, 0, 0)
full = np.zeros((24, 56, 3), np.uint8)
for r in range(3):
    for c in range(7):
        ink, paper, br = lg.attr[r][c]; pal = PALB if br else PAL
        blk = lg.bm[r * 8:r * 8 + 8, c * 8:c * 8 + 8]
        full[r * 8:r * 8 + 8, c * 8:c * 8 + 8] = np.where(blk[..., None] == 1, pal[ink], pal[paper])
L = Image.fromarray(full)
sheet = Image.new('RGB', (56 * 8 + 24 + 56 * 2 + 24 + 56 + 24, 24 * 8 + 24), PAL[YEL])
sheet.paste(L.resize((56 * 8, 24 * 8), Image.NEAREST), (12, 12))
sheet.paste(L.resize((112, 48), Image.NEAREST), (56 * 8 + 36, 12)); sheet.paste(L, (56 * 8 + 36 + 112 + 24, 12))
dd = ImageDraw.Draw(sheet)
for c in range(8): dd.line([(12 + c * 64, 12), (12 + c * 64, 12 + 192)], fill=(0, 0, 0), width=1)
for r in range(4): dd.line([(12, 12 + r * 64), (12 + 448, 12 + r * 64)], fill=(0, 0, 0), width=1)
sheet.save(OUT + '/logo_sheet.png')
print(sorted(os.listdir(OUT)))
