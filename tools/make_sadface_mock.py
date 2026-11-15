"""Mock-ups: you did not make the podium - your unhappy face (Grant, 15 Nov 2026: "if you did not get
on the podium, then your face shows somewhere (not sure where) with an unhappy face"). Over the
podium as built with YOU fourth (docs/design/layout_src/podium4.png); checked for clash.
Usage: python3 tools/make_sadface_mock.py -> docs/design/sadface_options.png"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_layout_options as L, make_podium_mock as P
from PIL import Image
K, B, BY, BW, BR, Y = L.K, L.B, L.BY, L.BW, L.BR, L.Y
POD = Image.open(os.path.join(L.D, 'layout_src', 'podium4.png')).convert('RGB')
SAD = P.SAD[0]
def base():
    s = L.Scr(); s.paste(POD, 0, 0); return s
def sad(s, cx, cy): s.fill(cx, cy, 2, 2, BR); P.face(s, SAD, cx, cy, BW, BR)
def a_card():                                   # on the card, in the yellow beside the podium
    s = base(); sad(s, 5, 11); P.small(s, 'YOU', 42, 106, K); P.small(s, '4TH', 42, 113, K); return s
def b_tower():                                  # in the race order: your own row shows your face
    s = base(); sad(s, 29, 16); return s
def c_under():                                  # under the window, left of the logo
    s = base(); sad(s, 1, 21); s.text('4TH', 4, 21, K); P.small(s, 'UNLUCKY', 32, 180, K); return s
def d_below():                                  # in the window, hanging under the card
    s = base(); s.fill(5, 18, 16, 2, BR); P.face(s, SAD, 5, 18, BW, BR); P.smallc(s, 'YOU FINISHED 4TH', 8, 20, 150, BW); return s
def e_laps():                                   # with your lap times, under the panel
    s = base(); sad(s, 24, 21); return s
def f_foot():                                   # the card's foot: your face and place in place of PRESS ANY KEY's row end
    s = base(); s.fill(5, 17, 16, 1, BR); P.smallc(s, 'YOU 4TH   PRESS ANY KEY', 5, 20, 137, BW); sad(s, 3, 16); return s
if __name__ == '__main__':
    L.sheet([('A  On the card', 'in the yellow beside the podium, with your place', a_card),
             ('B  In the race order', 'your own row on the right shows the face', b_tower),
             ('C  Under the window', 'left of the logo, with your place', c_under),
             ('D  Under the card', 'a red strip hanging below the podium', d_below),
             ('E  With your lap times', 'beside the three times under the panel', e_laps),
             ('F  At the card\'s corner', 'peeking in at the foot of the card', f_foot)],
            'Breakfast Run - not on the podium: where your unhappy face goes (YOU finished 4th)', 'sadface_options.png')
