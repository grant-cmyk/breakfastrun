"""The big cars exactly as the game has them (the bytes make_data.py writes: frames 24 wide, the
1-px halo, every car at all 16 headings), on the game's cloth: at real size, and 4x.
Writes docs/design/big_cars_16_headings.png. Usage: show_game_cars.py"""
import os, sys
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
import make_data as M
from make_big_cars import cloth
INK, PAP = (0, 0, 215), (0, 215, 215); CW = 30
def strip():
    st = cloth(16 * CW + 8, 5 * CW + 4); px = st.load()
    for k in range(5):
        for h in range(16):
            first, rows = M.big_bytes(M.big_all[k][h]); x0 = 4 + h * CW + 3; y0 = 2 + k * CW
            for j, r in enumerate(rows):
                for b in range(3):
                    m, i = r[2 * b], r[2 * b + 1]
                    for bit in range(8):
                        if m >> (7 - bit) & 1: px[x0 + b * 8 + bit, y0 + first + j] = INK if i >> (7 - bit) & 1 else PAP
    return st
if __name__ == '__main__':
    st = strip(); f = ImageFont.truetype('DejaVuSans-Bold.ttf', 17)
    big = st.resize((st.width * 4, st.height * 4), Image.NEAREST)
    o = Image.new('RGB', (big.width + 32, st.height + big.height + 110), (17, 18, 22)); d = ImageDraw.Draw(o)
    d.text((16, 10), 'The cars in the game now, REAL SIZE (one screen pixel each): YOU, CYAN, GREEN, PINK, WHITE - 16 headings each', fill=(236, 235, 230), font=f)
    o.paste(st, (16, 38))
    d.text((16, 52 + st.height), 'The same, 4x (blue = ink, cyan inside the car = paper; the thin cyan edge is the halo that keeps a car clear of what is behind it)', fill=(236, 235, 230), font=f)
    o.paste(big, (16, 80 + st.height))
    p = os.path.join(ROOT, 'docs', 'design', 'big_cars_16_headings.png'); o.save(p); print('wrote', os.path.normpath(p), o.size)
