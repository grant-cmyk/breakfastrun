"""The choose screen's new art on one sheet, at real size and enlarged: docs/design/choose/new_art_sheet.png -
the two new drivers (SPECS, DOT: everyday, eyes, happy, sad) and the two extra cars (SALOON, TRUCK: headings 0, 22.5,
45 as drawn, and 90, a quarter turn of heading 0). Also writes docs/design/choose/new_faces.txt: the new faces as
text in the form tools/import_faces.py reads (NAME now|eyes|happy|sad, then 16 rows of # and .), to paste into the
faces editor or edit by hand.   Usage: python3 tools/make_choose_sheet.py"""
import os, re
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
D = os.path.join(ROOT, 'docs', 'design', 'choose'); os.makedirs(D, exist_ok=True)
fa = open(os.path.join(HERE, 'face_art.txt')).read(); fm = open(os.path.join(HERE, 'face_moods.txt')).read()
F = {}
for m in re.finditer(r'== (\w+) face ==\n((?:[X.]{16}\n){16})', fa): F[(m.group(1), 'now')] = m.group(2).split()
for m in re.finditer(r'== (\w+) (eyes|happy|sad) ==\n((?:[X.]{16}\n){16})', fm): F[(m.group(1), m.group(2))] = m.group(3).split()
pool = open(os.path.join(HERE, 'pool_art.txt')).read()
C = {(m.group(1), m.group(2)): m.group(3).split() for m in re.finditer(r'== (\w+) heading ([\d.]+) ==\n((?:[Xo.]{16}\n){16})', pool)}
for n in ('SPECS', 'TRUCK'): C[(n, '90')] = [''.join(C[(n, '0')][15 - c][r] for c in range(16)) for r in range(16)]
with open(os.path.join(D, 'new_faces.txt'), 'w') as f:
    f.write("Classification: Internal\n\nThe choose screen's two new drivers, as tools/import_faces.py reads them (python3 tools/import_faces.py this-file, then\npython3 tools/make_faces.py and bash tools/build_choose.sh). # is ink.\n\n")
    for n in ('SPECS', 'DOT'):
        for mood in ('now', 'eyes', 'happy', 'sad'): f.write('%s %s\n%s\n\n' % (n, mood, '\n'.join(r.replace('X', '#') for r in F[(n, mood)])))
S = 6; PAD = 14; CW = 16 * S + 16 + PAD * 2 + 8
W = PAD + 4 * CW; H = 4 * (16 * S + 34) + 40
img = Image.new('RGB', (W, H), (255, 255, 255)); dr = ImageDraw.Draw(img)
def put(g, x, y, band, car=False):
    for s, ox in ((1, 0), (S, 16 + 8)):
        for j in range(16):
            for i in range(16):
                ch = g[j][i]
                col = (0, 0, 0) if ch == 'X' else ((255, 255, 255) if ch == 'o' else band)
                dr.rectangle([x + ox + i * s, y + j * s, x + ox + i * s + s - 1, y + j * s + s - 1], fill=col)
rows = [('SPECS', False), ('DOT', False), ('SPECS', True), ('TRUCK', True)]
label = {('SPECS', False): 'SPECS (new driver)', ('DOT', False): 'DOT (new driver)', ('SPECS', True): 'SALOON (extra car, from the pool)', ('TRUCK', True): 'TRUCK (extra car, from the pool)'}
dr.text((PAD, 8), 'Breakfast Run - the choose screen\'s new drivers and extra cars: real size, and 6 times', fill=(0, 0, 0))
for r, (n, car) in enumerate(rows):
    y = 34 + r * (16 * S + 34)
    dr.text((PAD, y), label[(n, car)], fill=(0, 0, 0))
    for c, k in enumerate(['0', '22.5', '45', '90'] if car else ['now', 'eyes', 'happy', 'sad']):
        x = PAD + c * CW
        put((C if car else F)[(n, k)], x, y + 14, (0, 200, 200) if car else (255, 255, 255), car)
        dr.text((x + 24, y + 14 + 16 * S + 2), ('heading ' + k) if car else k, fill=(90, 90, 90))
img.save(os.path.join(D, 'new_art_sheet.png')); print('wrote', os.path.join(D, 'new_art_sheet.png'), 'and new_faces.txt')
