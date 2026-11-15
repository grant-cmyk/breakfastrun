"""Mock-ups: FINAL LAP as a pit-crew message INSIDE the play area, at the bottom (Grant, 15 Nov 2026:
"when I'm on the final lap, have a display at the bottom - mockup a pit crew message in the play
area - 'final lap' and a small pitcrew face and speech bubble"; "the pitstop messages were not
visible as the player is focused on the game area - but maybe inside the game area at the bottom
will be more visible"). Over a race screen (docs/design/layout_src/race_now.png); checked for clash.
Usage: python3 tools/make_finallap_mock.py -> docs/design/finallap_options.png"""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_layout_options as L, make_podium_mock as P
from PIL import Image
K, B, BY, BW, BR, BB, C = L.K, L.B, L.BY, L.BW, L.BR, L.BB, L.C
RACE = Image.open(os.path.join(L.D, 'layout_src', 'race_now.png')).convert('RGB')
CREW = P._art('face_art.txt', 'face')['CREW']
def base():
    s = L.Scr(); s.paste(RACE, 0, 0); return s
def crew(s, cx, cy, ink, paper): s.fill(cx, cy, 2, 2, paper); P.face(s, CREW, cx, cy, ink, paper)
def bubble(s, cx, cy, w, h, paper, ink, tail_left=True):   # a speech bubble of whole cells: rounded corners, a tail to the face
    s.fill(cx, cy, w, h, paper)
    x0, y0, x1, y1 = cx * 8, cy * 8, (cx + w) * 8 - 1, (cy + h) * 8 - 1
    for (x, y) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        for dx in range(2):
            for dy in range(2 - dx):
                s.im.putpixel((x + (dx if x == x0 else -dx), y + (dy if y == y0 else -dy)), ink)
def a_bubble():                                  # the chief bottom left of the centre, a white bubble beside him
    s = base(); crew(s, 6, 17, K, BW); bubble(s, 8, 17, 10, 2, BW, K); s.text('FINAL LAP!', 8, 17, K, None, tall=True); return s
def b_small():                                   # the same in the small letters: half the height, a line more room
    s = base(); crew(s, 7, 17, K, BW); bubble(s, 9, 17, 8, 2, BW, K)
    P.smallc(s, 'FINAL LAP!', 9, 16, 138, K); P.smallc(s, 'BRING IT HOME', 9, 16, 145, K); return s
def c_band():                                    # a band across the foot of the window
    s = base(); s.fill(4, 18, 17, 2, B); crew(s, 4, 18, BW, B); s.text('FINAL LAP!', 8, 18, BY, None, tall=True); return s
def d_yellow():                                  # the podium's colours: a yellow bubble, the chief on blue
    s = base(); crew(s, 6, 17, BW, B); bubble(s, 8, 17, 10, 2, BY, K); s.text('FINAL LAP!', 8, 17, K, None, tall=True); return s
def e_corner():                                  # tucked beside the health bolt: small, out of the racing line
    s = base(); crew(s, 4, 18, K, BW); bubble(s, 6, 18, 7, 2, BW, K); P.smallc(s, 'FINAL', 6, 12, 146, K); P.smallc(s, 'LAP!', 6, 12, 153, K); return s
def f_red():                                     # urgent: white on red
    s = base(); crew(s, 6, 17, BW, BR); bubble(s, 8, 17, 10, 2, BR, BW); s.text('FINAL LAP!', 8, 17, BW, None, tall=True); return s
if __name__ == '__main__':
    L.sheet([('A  White bubble', 'the crew chief and a bubble, tall letters, bottom centre', a_bubble),
             ('B  Small letters', 'two short lines in the small letters', b_small),
             ('C  Blue band', 'a band across the foot of the play area, yellow letters', c_band),
             ('D  Yellow bubble', 'as A in the podium\'s colours', d_yellow),
             ('E  Corner', 'small, beside the health bolt, clear of the middle', e_corner),
             ('F  Red', 'as A, white on red', f_red)],
            'Breakfast Run - FINAL LAP: the crew chief\'s message inside the play area', 'finallap_options.png')
