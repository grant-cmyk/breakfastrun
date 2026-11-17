"""Mock-up: the corner arrow made clearer on the race-track look (Grant, 17 Nov 2026: "the yellow arrow needs mask or
outline to be clearer"). Today its 1-pixel black outline vanishes over grass: in a square that is all grass the
cleared pixels show the square's green, so the arrow is yellow on green. Three ways out, each obeying the
two-colours-a-square rule, drawn on real screens (one over road, one over grass).
Usage: python3 tools/make_arrow_clear_mock.py <screen over road> <screen over grass>
Writes docs/design/racetrack/arrow_clear_options.png. Nothing here is in the game."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
K, G, Y = np.array((0, 0, 0)), np.array((0, 215, 0)), np.array((215, 215, 0))
def load(p):
    im = np.array(Image.open(p).convert('RGB')).astype(int); bx, by = (im.shape[1] - 256) // 2, (im.shape[0] - 192) // 2
    return im[by:by + 192, bx:bx + 256]
WX, WY = 8 + 80, 8 + 104                                  # the arrow's 3 x 3 squares on the screen (window x 80, line 104)
def shape(sc):
    reg = sc[WY:WY + 24, WX:WX + 24]
    return (reg[..., 0] > 150) & (reg[..., 1] > 150) & (reg[..., 2] < 90)
def grow(m, n):
    for _ in range(n):
        g = m.copy(); g[1:] |= m[:-1]; g[:-1] |= m[1:]; g[:, 1:] |= m[:, :-1]; g[:, :-1] |= m[:, 1:]; m = g
    return m
def grass_of(sc):                                         # what is grass in the arrow's squares, as the scenery has it
    reg = sc[WY:WY + 24, WX:WX + 24]; g = (reg[..., 1] > 150) & (reg[..., 0] < 90)
    return g & ~ARROW if sc is ROAD else g
ARROW = None; ROAD = None
def opt(sc, arrow, how):
    if how == 'now': return sc                            # (today: the real screen as it is)
    out = sc.copy(); reg = out[WY:WY + 24, WX:WX + 24]; gr = grass_of(sc) & ~grow(arrow, 1)
    for qy in range(3):
        for qx in range(3):
            s = (slice(qy * 8, qy * 8 + 8), slice(qx * 8, qx * 8 + 8)); a = arrow[s]; g = gr[s]
            if how == 'now':
                allg = (grass_of(sc)[s] | grow(arrow, 1)[s]).all() and g.any()
                if allg: reg[s] = np.where(a[..., None], Y, G)
                elif g.any(): reg[s] = np.where((a | g)[..., None], G, K)
                else: reg[s] = np.where(a[..., None], Y, K)
            elif how == 'box':                            # A: the 3 x 3 squares a black box, the arrow yellow in it
                reg[s] = np.where(a[..., None], Y, K)
            elif how == 'thick':                          # B: yellow on black, a 3-pixel black outline; grass kept outside it
                o = grow(arrow, 3)[s]; keep_g = g & ~o
                if keep_g.any() and not a.any(): reg[s] = np.where(keep_g[..., None], G, K)
                else: reg[s] = np.where(a[..., None], Y, K)   # (a square with arrow in it: yellow ink, so grass there goes black)
            elif how == 'black':                          # C: over grass the arrow is BLACK with a green edge; over road yellow as now
                if g.any() or grass_of(sc)[s].any(): reg[s] = np.where((g & ~a)[..., None], G, K)
                else: reg[s] = np.where(a[..., None], Y, K)
    return out
S = 4; fnt = ImageFont.load_default()
road, grass = load(sys.argv[1]), load(sys.argv[2]); ROAD = road
ar_g = shape(grass); ar_r = ar_g; ARROW = ar_g            # (both screens show the 'up' arrow; over the road part of it is green today, so its shape is read from the grass one)
OPTS = [('NOW', 'yellow on green over grass', 'now'), ('A', 'a black box behind it', 'box'),
        ('B', 'a thick black outline', 'thick'), ('C', 'black arrow over grass', 'black')]
crop = lambda sc: Image.fromarray(sc[WY - 16:WY + 40, WX - 24:WX + 48].astype(np.uint8)).resize((72 * S, 56 * S), Image.NEAREST)
sheet = Image.new('RGB', (len(OPTS) * (72 * S + 12) + 12, 2 * (56 * S + 10) + 30), (40, 42, 48)); d = ImageDraw.Draw(sheet)
for i, (tag, what, how) in enumerate(OPTS):
    ox = 12 + i * (72 * S + 12); d.text((ox, 8), tag + ': ' + what, fill=(236, 235, 230), font=fnt)
    sheet.paste(crop(opt(road, ar_r, how)), (ox, 26)); sheet.paste(crop(opt(grass, ar_g, how)), (ox, 26 + 56 * S + 10))
out = os.path.join(ROOT, 'docs', 'design', 'racetrack', 'arrow_clear_options.png'); sheet.save(out); print('wrote', out)
