"""Mock-ups: the frame round the play window (Grant, 15 Nov 2026: "make some variations on the border
rectangle area surrounding the gameplay - some mockups - it doesn't quite work for me"). The frame
is the ring of cells round the 24 x 19 window: columns 0 and 25, rows 0 and 20. Real screens,
checked for colour clash. Usage: python3 tools/make_frame_options.py -> docs/design/frame_options.png"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_layout_options as L
K, B, R, Y, W, BR, BY, BW, C = L.K, L.B, L.R, L.Y, L.W, L.BR, L.BY, L.BW, L.C
INNER = L.G.crop((8, 8, 200, 160))
RING = [(x, y) for x in range(26) for y in range(21) if x in (0, 25) or y in (0, 20)]
def base(table=Y):
    s = L.Scr(); s.paste(L.G, 0, 0)
    for x, y in RING: s.fill(x, y, 1, 1, table)
    s.paste(INNER, 1, 1); return s
def f_now():
    s = L.Scr(); s.paste(L.G, 0, 0); return s
def f_none(): return base()
def line(s, inset, col, w=1):                 # a rectangle of w pixels, its outside inset pixels in from the ring's outer edge
    x0, y0, x1, y1 = inset, inset, 207 - inset, 167 - inset
    for k in range(w): s.d.rectangle((x0 + k, y0 + k, x1 - k, y1 - k), outline=col)
def f_hair():
    s = base(); line(s, 7, K, 1); return s
def f_thick():
    s = base(); line(s, 4, B, 4); return s
def f_solid():
    s = base()
    for x, y in RING: s.fill(x, y, 1, 1, B)
    return s
def f_gingham():
    s = base()
    for x, y in RING: s.fill(x, y, 1, 1, BR if (x + y) % 2 == 0 else BW)
    return s
def f_mat():                                  # a white place mat under the window, a shadow under and to the right of it
    s = base()
    for x, y in RING: s.fill(x, y, 1, 1, BW)
    s.d.rectangle((204, 4, 207, 167), fill=K); s.d.rectangle((4, 164, 207, 167), fill=K)
    s.d.rectangle((204, 0, 207, 3), fill=BW); s.d.rectangle((0, 164, 3, 167), fill=BW); return s
def f_double():
    s = base(); line(s, 2, B, 1); line(s, 5, B, 2); return s
def f_black():
    s = base()
    for x, y in RING: s.fill(x, y, 1, 1, K)
    line(s, 3, BY, 1); return s
if __name__ == '__main__':
    L.sheet([('NOW', 'slim blue line, rounded corners, a gap of table inside it', f_now),
             ('A  None', 'no frame: the cloth sits straight on the table', f_none),
             ('B  Hairline', 'one black pixel hugging the cloth', f_hair),
             ('C  Thick', 'a 4-pixel blue band, table either side', f_thick),
             ('D  Solid', 'the whole ring blue: a heavy picture frame', f_solid),
             ('E  Tablecloth', 'red-and-white checks, as the title screen', f_gingham),
             ('F  Place mat', 'white mat with a shadow under and right', f_mat),
             ('G  Double', 'a thin line outside a thicker one', f_double),
             ('H  Black', 'black ring with a yellow pinstripe', f_black)],
            'Breakfast Run - the frame round the play area', 'frame_options.png')
