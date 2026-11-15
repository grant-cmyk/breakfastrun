"""Mock-ups: the right-hand panel rearranged (Grant, 15 Nov 2026: "Put the cars 1-5 further up the
screen, so just under the map. Then my result and laptimes goes under the cars"). Over the podium
as built with YOU fourth (docs/design/layout_src/podium4.png); checked for clash.
Usage: python3 tools/make_panel_mock.py -> docs/design/panel_options.png"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_layout_options as L, make_podium_mock as P
from PIL import Image
K, B, BY, BW, BR, Y, BB = L.K, L.B, L.BY, L.BW, L.BR, L.Y, L.BB
POD = Image.open(os.path.join(L.D, 'layout_src', 'podium4.png')).convert('RGB')
RACE = POD.crop((208, 72, 256, 160)); MAP = POD.crop((208, 0, 256, 40))
LAPS = ['22.2', '21.4', '22.6']
def base(top=5):                                # the map, then RACE and the five cars straight under it
    s = L.Scr(); s.paste(POD, 0, 0); s.fill(26, 5, 6, 19, Y); s.paste(RACE, 26, top); return s
def laps(s, row, ink=K, n=3):
    for i in range(n):
        P.small(s, str(i + 1), 211, row * 8 + 1 + 8 * i, ink); P.small(s, LAPS[i], 224, row * 8 + 1 + 8 * i, ink)
def v_now():
    s = L.Scr(); s.paste(POD, 0, 0); return s
def v_a():                                      # a red bar - YOU 4TH - then your laps
    s = base(); s.fill(26, 17, 6, 1, BR); P.smallc(s, 'YOU 4TH', 26, 31, 137, BW); laps(s, 18); return s
def v_b():                                      # your face (unhappy: off the podium) and your place large, then your laps
    s = base(); s.fill(26, 17, 2, 2, BR); P.face(s, P.SAD[0], 26, 17, BW, BR)
    P.big_digit(s, '4', 28, 17, K, Y); P.small(s, 'TH', 245, 143, K); laps(s, 20); return s
def v_c():                                      # headed YOUR RACE, the place and the laps, then the best lap picked out
    s = base(); s.fill(26, 17, 6, 1, B); P.smallc(s, 'YOUR RACE', 26, 31, 137, BW)
    P.smallc(s, 'FINISHED 4TH', 26, 31, 146, K); laps(s, 19)
    s.fill(26, 20, 6, 1, BY); laps(s, 19); return s
def v_d():                                      # during the race: the laps fill in as you finish them
    s = L.Scr(); s.paste(L.G, 0, 0); s.fill(26, 5, 6, 19, Y); s.paste(L.G.crop((208, 72, 256, 160)), 26, 5)
    s.fill(26, 17, 6, 1, BR); P.smallc(s, 'YOU', 26, 31, 137, BW); laps(s, 18, n=1); return s
if __name__ == '__main__':
    L.sheet([('NOW', 'the cars low in the panel, your lap times below it', v_now),
             ('A  Red bar, then laps', 'cars under the map; YOU 4TH on your red; your three laps', v_a),
             ('B  Face and place, then laps', 'your face (unhappy off the podium), a large 4TH, your laps', v_b),
             ('C  YOUR RACE', 'a headed block: place, laps, your best lap picked out in yellow', v_c),
             ('D  During the race', 'the same block mid-race: laps fill in as you finish them', v_d)],
            'Breakfast Run - the panel: cars just under the map, your result and lap times under the cars', 'panel_options.png')
