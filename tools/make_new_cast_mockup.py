"""Mock-up (Grant, 14 Nov 2026): five more cars and five more drivers to choose from on the
title screen - "look for unique styles - the offroad, the pickup truck, the buggy - can get
creative. For personalities, need three ladies and three men". FIRST DRAFTS for Grant to redraw
in the car editor: 20 x 20 cars at heading 0 (left half + centre column, mirrored, like
make_big_cars.py), 16 x 16 faces (left half, mirrored). In this game's style: solid ink with
paper features (Grant's own big cars), each car one clear silhouette of its own.
Writes tools/new_cast_art.txt and docs/design/new_cast_mockup.png."""
import os, sys
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
from make_big_cars import pic, cloth
CARS = {
 'OFFROAD': ("the 4 x 4: bull bar, knobbly tyres, open cab with a roll bar, a spare wheel on the back", [
  "..........", "....XXXXXX", "....X..X..", ".XXXXXXXXX", ".X.XXXXXXX", ".XXXXXooXX", ".X.XXXXXXX", ".XXXXXXXXX", "....Xooooo", "....Xooooo",
  "....XXXXXX", "....XXoooX", "....XXoooX", ".XXXXXXXXX", ".X.XXXXXXX", ".XXXXXXooo", ".X.XXXXoXX", ".XXXXXXooo", ".....XXXXX", ".........."]),
 'PICKUP': ("the pickup truck: a cab up front, an open load bed with a crate in it", [
  "..........", ".....XXXXX", "..XXXXXXXX", "..XXXXXXXX", "..XXXXXXXX", "..XXXooooo", "....XXXXXX", "....XXXXXX", "....XXXXXX", "....XXoooo",
  "....XXXXXX", "....Xooooo", "..XXXooooo", "..XXXooXXo", "..XXXooXXo", "..XXXooooo", "....Xooooo", "....XXXXXX", "..........", ".........."]),
 'BUGGY': ("the dune buggy: a pointed nose, small front wheels out on arms, an open cockpit, fat rear tyres, the engine showing", [
  "..........", ".........X", "........XX", ".XX....XXX", ".XXXXXXXXX", ".XX....XXX", ".XX...XXXX", "......XXXX", ".....XXooo", ".....XooXX",
  ".....XooXX", ".....XXooo", "XXXX.XXXXX", "XXXX.XX.X.", "XXXXXXXX.X", "XXXXXXX.X.", "XXXX.XXX.X", "XXXX.XXXXX", "......XXXX", ".........."]),
 'HOTROD': ("the hot rod: engine pipes on show up front, thin front wheels, the cab right at the back between giant rear wheels", [
  "..........", "........XX", ".XX.....XX", ".XXXXXXXXX", ".XX...XoXo", ".XX...XoXo", "......XoXo", "......XoXo", "......XXXX", ".....XXXXX",
  ".....Xoooo", "XXXX.XXXXX", "XXXX.XXXXX", "XXXXXXXXXX", "XXXX.XXXXX", "XXXX.Xoooo", "XXXX.XXXXX", "XXXX..XXXX", "..........", ".........."]),
 'MILKFLOAT': ("the milk float (breakfast delivery): a boxy cab with a big windscreen, crates of bottles on the back", [
  "..........", "....XXXXXX", "...XXXXXXX", "...Xoooooo", "...Xoooooo", ".XXXXXXXXX", ".XXXXXXXXX", ".XXXXXXXXX", "...XXXXXXX", "...XooXooX",
  "...XooXooX", "...XXXXXXX", "...XooXooX", ".XXXooXooX", ".XXXXXXXXX", ".XXXooXooX", "...XooXooX", "...XXXXXXX", "..........", ".........."]),
}
FACES = {
 'BUN': ("lady: hair up in a bun, lashes, a smile", 0x58, [
  "......XX", ".....XXX", "...XXXXX", "..XXXXXX", ".XXX....", ".XX.....", ".XX.XX..", ".XX..X..", ".X......", ".X.....X", ".X......", ".XX..X..", "..X...XX", "...X....", "....XXXX", "........"]),
 'SPECS2': ("lady: a bob, round glasses", 0x68, [
  "........", "...XXXXX", "..XXXXXX", ".XXXXXXX", ".XXX....", ".XX.....", ".XX.XXX.", ".XX.X.XX", ".XX.XXX.", ".XX.....", ".XX....X", ".XX.....", ".XXX..XX", ".XXX....", "....XXXX", "........"]),
 'CURLS': ("lady: big curls", 0x70, [
  "..XX.XX.", ".XXXXXXX", "XXXXXXXX", "XXX.....", ".XX.....", "XXX.XX..", "XXX..X..", ".XX.....", "XXX....X", "XXX.....", ".XX.....", "XXX..XXX", "XXX...XX", ".XXX....", "...XXXXX", "........"]),
 'CAP': ("man: a flat cap, a moustache", 0x60, [
  "........", "....XXXX", "..XXXXXX", ".XXXXXXX", "XXXXXXXX", "..X.....", "..X.XX..", "..X..X..", "..X.....", "..X....X", "..X.XXXX", "..X.X...", "..X...XX", "...X....", "....XXXX", "........"]),
 'SHADES': ("man: bald, dark glasses, a beard", 0x78, [
  "........", "....XXXX", "..XX....", ".X......", ".X......", ".X......", "XXXXXXXX", ".XXXXXX.", ".X.XXX..", ".X.....X", ".XX.....", ".XXX.XXX", ".XXXX...", "..XXXXXX", "...XXXXX", ".....XXX"]),
}
PAL = [(0, 0, 0), (0, 0, 215), (215, 0, 0), (215, 0, 215), (0, 215, 0), (0, 215, 215), (215, 215, 0), (215, 215, 215)]
PALB = [(0, 0, 0), (0, 0, 255), (255, 0, 0), (255, 0, 255), (0, 255, 0), (0, 255, 255), (255, 255, 0), (255, 255, 255)]
car = lambda h: [r + r[:-1][::-1] + '.' for r in h]
face = lambda h: [r + r[::-1] for r in h]
def face_pic(g, attr, s):
    pal = PALB if attr & 64 else PAL; ink, pap = pal[attr & 7], pal[(attr >> 3) & 7]
    im = Image.new('RGB', (16 * s, 16 * s), pap); px = im.load()
    for y in range(16):
        for x in range(16):
            if g[y][x] == 'X':
                for a in range(s):
                    for b in range(s): px[x * s + a, y * s + b] = ink
    return im
if __name__ == '__main__':
    with open(os.path.join(HERE, 'new_cast_art.txt'), 'w') as f:
        f.write("BREAKFAST RUN NEW CAST v1 - CLAUDE'S FIRST DRAFTS, not in the game (tools/make_new_cast_mockup.py)\n"
                "Five more cars (20 x 20, heading 0: X ink, o paper, . empty) and five more drivers (16 x 16: X ink)\n"
                "for the title screen's choice of driver and car. For Grant to redraw in the car editor.\n\n")
        for n, (d, h) in CARS.items(): f.write('== %s big heading 0 ==   (%s)\n' % (n, d) + '\n'.join(car(h)) + '\n\n')
        for n, (d, a, h) in FACES.items(): f.write('== %s face ==   (%s)\n' % (n, d) + '\n'.join(face(h)) + '\n\n')
    try: fb = ImageFont.truetype('DejaVuSans-Bold.ttf', 17); fs = ImageFont.truetype('DejaVuSans.ttf', 13)
    except OSError: fb = fs = ImageFont.load_default()
    S = 8; cw = 20 * S + 76; W = 32 + 5 * cw; H = 60 + 20 * S + 120 + 16 * S + 90
    out = Image.new('RGB', (W, H), (17, 18, 22)); d = ImageDraw.Draw(out)
    d.text((16, 10), 'Five more cars - first drafts, heading 0 (8x, and real size on the cloth shown 3x)', fill=(236, 235, 230), font=fb)
    for i, (n, (desc, h)) in enumerate(CARS.items()):
        x = 16 + i * cw; g = car(h)
        out.paste(pic(g, S, (40, 44, 52)), (x, 40))
        st = cloth(22, 22); m = pic(g, 1, (0, 0, 0)); mk = Image.new('L', m.size, 0)
        mk.putdata([0 if p == (0, 0, 0) else 255 for p in m.get_flattened_data()]); st.paste(m, (1, 1), mk)
        out.paste(st.resize((66, 66), Image.NEAREST), (x + 20 * S + 4, 40))
        d.text((x, 44 + 20 * S), n, fill=(236, 235, 230), font=fb)
        words = desc.split(); line = ''; yy = 66 + 20 * S
        for w in words:
            if d.textlength(line + ' ' + w, font=fs) > cw - 12: d.text((x, yy), line, fill=(160, 165, 175), font=fs); yy += 16; line = w
            else: line = (line + ' ' + w).strip()
        d.text((x, yy), line, fill=(160, 165, 175), font=fs)
    y0 = 60 + 20 * S + 120
    d.text((16, y0 - 28), 'Five more drivers - first drafts (8x, and real size shown 3x): three ladies, two men', fill=(236, 235, 230), font=fb)
    for i, (n, (desc, a, h)) in enumerate(FACES.items()):
        x = 16 + i * cw; g = face(h)
        out.paste(face_pic(g, a, S), (x, y0)); out.paste(face_pic(g, a, 3), (x + 16 * S + 8, y0))
        d.text((x, y0 + 16 * S + 4), n, fill=(236, 235, 230), font=fb); d.text((x, y0 + 16 * S + 26), desc, fill=(160, 165, 175), font=fs)
    p = os.path.join(ROOT, 'docs', 'design', 'new_cast_mockup.png'); out.save(p); print('wrote', os.path.normpath(p), out.size)
