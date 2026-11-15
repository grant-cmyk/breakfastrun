"""Mock-up: the podium's fastest-lap lines (Grant, 15 Nov 2026: "fastest lap - put the name underneath
that - show the fastest lap icon and the time"). Drawn over the podium as built
(docs/design/layout_src/podium.png); the card a row taller for the second line.
Usage: python3 tools/make_fastlap_mock.py -> docs/design/fastlap_options.png"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_layout_options as L, make_podium_mock as P
from PIL import Image
K, B, BY, BW = L.K, L.B, L.BY, L.BW
POD = Image.open(os.path.join(L.D, 'layout_src', 'podium.png')).convert('RGB')
CLOCK = [0b00111100, 0b01000010, 0b10001001, 0b10001001, 0b10001101, 0b10000001, 0b01000010, 0b00111100]
def clock(s, x, y, ink):
    for r, v in enumerate(CLOCK):
        for c in range(8):
            if v >> (7 - c) & 1: s.im.putpixel((x + c, y + r), ink)
def base():
    s = L.Scr(); s.paste(POD, 0, 0)
    s.fill(5, 14, 16, 2, BY); s.fill(5, 16, 16, 1, B)            # two lines of card, the foot a row lower
    P.smallc(s, 'PRESS ANY KEY', 5, 20, 129, BW); return s
def v_now():
    s = L.Scr(); s.paste(POD, 0, 0); return s
def v_a():                                        # FASTEST LAP, the clock and the time on one line; the name under it
    s = base(); P.small(s, 'FASTEST LAP', 52, 114, K); clock(s, 104, 112, K); P.small(s, '21.4', 116, 114, K)
    P.smallc(s, 'JANE', 5, 20, 122, K); return s
def v_b():                                        # FASTEST LAP alone; the clock, the time and the name under it
    s = base(); P.smallc(s, 'FASTEST LAP', 5, 20, 113, K)
    clock(s, 72, 120, K); P.small(s, '21.4', 84, 122, K); P.small(s, 'JANE', 108, 122, K); return s
def v_c():                                        # no words: the clock says "fastest lap" - clock and time, the name under
    s = base(); clock(s, 88, 112, K); P.small(s, '21.4', 100, 114, K); P.smallc(s, 'JANE', 5, 20, 122, K); return s
if __name__ == '__main__':
    L.sheet([('NOW', 'as built: FASTEST LAP, the name and the time on one line', v_now),
             ('A  Words, clock, time / name', 'FASTEST LAP with the clock and the time; the name underneath', v_a),
             ('B  Words / clock, time, name', 'FASTEST LAP alone; clock, time and name underneath', v_b),
             ('C  Clock and time / name', 'no words: the clock icon stands for fastest lap', v_c)],
            'Breakfast Run - the podium\'s fastest lap', 'fastlap_options.png')
