"""Mock-up: your place on a small solid blue plate inside the game area (Grant's pick B, 14 Nov
2026: "I like B, but can we create smaller fonts, and so 2nd or 3rd shows a small nd or small
rd"). The figure is an ordinary letter; "st / nd / rd / th" is a small raised suffix in a 3 x 5
font; the lap, if shown, is in the same small font. On a real screen from the game.
Usage: python3 tools/make_ingame_plate.py -> docs/design/ingame_plate.png   (ZXDEV = zxdev)"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import make_ingame_info as mi                     # (reads a screen from the game; plate(), glyphs(), render)
mc, render = mi.mc, mi.render
SMALL = {'0': '111 101 101 101 111', '1': '010 110 010 010 111', '2': '111 001 111 100 111', '3': '111 001 111 001 111',
         '4': '101 101 111 001 001', '5': '111 100 111 001 111', '/': '001 001 010 100 100', ' ': '000 000 000 000 000',
         'L': '100 100 100 100 111', 'A': '010 101 111 101 101', 'P': '110 101 110 100 100', 'F': '111 100 110 100 100',
         'I': '111 010 010 010 111', 'N': '110 101 101 101 101', 'U': '101 101 101 101 111', 'O': '111 101 101 101 111',
         'E': '111 100 110 100 111', '!': '010 010 010 000 010',
         'n': '000 110 101 101 101', 'd': '001 001 011 101 011', 'r': '000 101 110 100 100', 's': '000 011 110 001 110',
         't': '010 111 010 010 011', 'h': '100 100 110 101 101'}
def small(s):
    g = np.zeros((5, 4 * len(s) - 1), dtype=np.uint8)
    for k, ch in enumerate(s):
        for j, row in enumerate(SMALL[ch].split()):
            for i, c in enumerate(row): g[j, 4 * k + i] = c == '1'
    return g
SUF = {1: 'st', 2: 'nd', 3: 'rd', 4: 'th', 5: 'th'}
def place_plate(n, lap=None):
    """The plate's pixels (1 = blue): solid, rounded, the figure and its small suffix cut out of it."""
    fig = mi.glyphs(str(n)); suf = small(SUF[n]); lp = small(lap) if lap else None
    w = max(8 + 1 + suf.shape[1], lp.shape[1] if lap else 0) + 6; h = 14 + (8 if lap else 0)
    txt = np.zeros((h, w), dtype=np.uint8); txt[3:11, 3:11] = fig; txt[3:8, 12:12 + suf.shape[1]] = suf
    if lap: txt[13:18, 3:3 + lp.shape[1]] = lp
    return mi.plate(w, h) & (1 - txt)
def put(b, m, x, y):
    halo = mc.grow(mc.grow(np.pad(m | 1, 2) * 0 + np.pad(mi.plate(m.shape[1], m.shape[0]), 2)))    # 2 clear pixels round the plate
    reg = b[y - 2:y + m.shape[0] + 2, x - 2:x + m.shape[1] + 2]; reg[halo == 1] = 0; b[y:y + m.shape[0], x:x + m.shape[1]] |= m
def msg_plate(s):
    g = small(s); w, h = g.shape[1] + 6, 11; txt = np.zeros((h, w), dtype=np.uint8); txt[3:8, 3:3 + g.shape[1]] = g
    return mi.plate(w, h) & (1 - txt)
def scene(kind):
    b, a = mi.bits0.copy(), mi.attrs0.copy(); R = 8 + 176
    if kind == 1: m = place_plate(2); put(b, m, R - 10 - m.shape[1], 17)
    if kind == 2: m = place_plate(2, 'LAP 2/3'); put(b, m, R - 10 - m.shape[1], 17)
    if kind == 3:
        m = place_plate(3, 'LAP 3/3'); put(b, m, R - 10 - m.shape[1], 17)
        g = msg_plate('FINAL LAP!'); put(b, g, R - 10 - g.shape[1], 17 + m.shape[0] + 4)
    return render(b, a, border=6, s=3)
if __name__ == '__main__':
    try: f = ImageFont.truetype('DejaVuSans-Bold.ttf', 22); fs = ImageFont.truetype('DejaVuSans.ttf', 17)
    except OSError: f = fs = ImageFont.load_default()
    BG, FG = (17, 18, 22), (236, 235, 230)
    caps = ['1. The place alone: an ordinary figure with a small raised nd (23 x 14 pixels).', '2. With the lap under it in the small letters (34 x 22).',
            '3. And a quick message as a second small plate under it, for 2 seconds.']
    ims = [scene(k) for k in (1, 2, 3)]; w, h = ims[0].size
    zoom = Image.new('RGB', (w, h), BG); zd = ImageDraw.Draw(zoom); zd.text((0, 0), 'Close up (7x): 1st to 5th, and with the lap', fill=FG, font=fs)
    def big(m, s=7):
        im = Image.new('RGB', (m.shape[1] + 4, m.shape[0] + 4), (0, 215, 215)); px = im.load()
        for y in range(m.shape[0]):
            for x in range(m.shape[1]):
                if m[y, x]: px[x + 2, y + 2] = (0, 0, 215)
        return im.resize((im.width * s, im.height * s), Image.NEAREST)
    x = 0
    for n in range(1, 6): im = big(place_plate(n)); zoom.paste(im, (x, 34)); x += im.width + 10
    x = 0
    for n, lap in ((1, 'LAP 1/3'), (2, 'LAP 2/3'), (4, 'LAP 3/3')): im = big(place_plate(n, lap)); zoom.paste(im, (x, 180)); x += im.width + 10
    im = big(msg_plate('FINAL LAP!')); zoom.paste(im, (0, 380)); im2 = big(msg_plate('UP ONE!')); zoom.paste(im2, (im.width + 10, 380))
    out = Image.new('RGB', (2 * w + 60, 2 * (h + 44) + 60), BG); d = ImageDraw.Draw(out)
    d.text((20, 12), 'Your place on a small blue plate inside the game area, with a small nd / rd (mock-up on a real screen)', fill=(255, 255, 255), font=f)
    for i, im in enumerate(ims + [zoom]):
        x, y = 20 + (i % 2) * (w + 20), 52 + (i // 2) * (h + 44)
        if i < 3: d.text((x, y), caps[i], fill=FG, font=fs)
        out.paste(im, (x, y + 24))
    p = os.path.join(HERE, '..', 'docs', 'design', 'ingame_plate.png'); out.save(p); print('wrote', os.path.normpath(p), out.size)
