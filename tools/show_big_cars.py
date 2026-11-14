"""Sheet of the big cars' three drawn headings (0, 22.5, 45) from a big-car art file: 8x with a
grid, and real size (shown 3x) on the cloth with the game's 1-px halo. Usage:
show_big_cars.py [art.txt] [out.png]"""
import os, re, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
from make_big_cars import pic, cloth, INK, PAP
def read(path):
    t = open(path).read()
    return {(m.group(1), m.group(2)): m.group(3).split() for m in re.finditer(r'== (\w+) big heading ([\d.]+) ==\n((?:[Xo.]{20}\n){20})', t)}
def sheet(art, out, order=('YOU', 'CYAN', 'WHITE', 'PINK', 'GREEN')):
    S = 8; W = 16 + 3 * (20 * S + 12) + 3 * 66 + 16; H = 16 + len(order) * (20 * S + 12)
    im = Image.new('RGB', (W, H), (17, 18, 22)); d = ImageDraw.Draw(im)
    for r, n in enumerate(order):
        for c, h in enumerate(('0', '22.5', '45')):
            g = art[(n, h)]; x, y = 16 + c * (20 * S + 12), 16 + r * (20 * S + 12)
            im.paste(pic(g, S, (40, 44, 52)), (x, y))
            for k in range(0, 21, 5): d.line([x + k * S, y, x + k * S, y + 20 * S], fill=(70, 74, 84)); d.line([x, y + k * S, x + 20 * S, y + k * S], fill=(70, 74, 84))
            st = cloth(22, 22); m = pic(g, 1, (0, 0, 0)); mk = Image.new('L', m.size, 0)
            mk.putdata([0 if p == (0, 0, 0) else 255 for p in m.getdata()]); st.paste(m, (1, 1), mk)
            im.paste(st.resize((66, 66), Image.NEAREST), (16 + 3 * (20 * S + 12) + c * 66, y + 40))
    im.save(out); print('wrote', out)
if __name__ == '__main__':
    a = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'big_car_art.txt')
    sheet(read(a), sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'docs', 'design', 'big_car_headings.png'))
