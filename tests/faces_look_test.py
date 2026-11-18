"""The race order's faces look left and right before the race (Grant, 18 Nov 2026: "at the start of the games I want the
faces animated looking left and right - as per our sprites"). From the first picture of the race screen until the lights
go green, each row's face (character rows TOWER_Y + 2 x place and the one below, columns 30-31) must change between at
least two looks - the everyday face and its "eyes" look (src/faces_mood.asm) - and every picture of it on the screen must
be one of those two, exactly; the rows must not all move together. Once racing, no face is left in the rows.
  python3 tests/faces_look_test.py [tape name [its src folder]]     (default racer_armour_grip1, build/<name>/src)
Prints PASS/FAIL lines and RESULT."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rt_lib import *
NAME = sys.argv[1] if len(sys.argv) > 1 else 'racer_armour_grip1'
fails = 0
def ok(c, m):
    global fails
    print('PASS' if c else 'FAIL', m); fails += 0 if c else 1
g = Game(NAME, sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'build', NAME, 'src')); S = g.sym
TY = 6                                                   # TOWER_Y (src/hud.asm)
NC = S.get('ncars', 5)
def face_on_screen(p):
    """the 16 rows x 2 bytes in the face's squares of row p, as on the screen"""
    scr = g.mem(0x4000, 6144); out = []
    for r in range(16):
        y = (TY + 2 * p) * 8 + r
        a = ((y & 0xC0) << 5) | ((y & 7) << 8) | ((y & 0x38) << 2)
        out.append((scr[a + 30], scr[a + 31]))
    return tuple(out)
def looks(car):
    """the car's everyday face and its eyes look, as 16 rows x 2 bytes each"""
    f = g.mem(S['faces'] + 32 * car, 32)
    day = [(f[2 * r], f[2 * r + 1]) if r < 8 else (f[16 + 2 * (r - 8)], f[17 + 2 * (r - 8)]) for r in range(16)]
    m = g.mem(S['faces_mood'], 600); i = 0
    for k in range(3 * car):                             # the car's three lists: eyes, happy, sad - skip to its eyes
        while m[i] != 0xFF: i += 3
        i += 1
    eyes = list(day)
    while m[i] != 0xFF:
        eyes[m[i]] = (m[i + 1], m[i + 2]); i += 3
    return tuple(day), tuple(eyes)
g.to_grid()
order = list(g.mem(S['shown_order'], NC))
seen = [dict() for _ in range(NC)]; wrong = [0] * NC; apart = 0; frames = 0
want = [looks(c) if c < NC else None for c in order]
while frames < 400:
    g.run(2); frames += 2
    g.rpc('run', until_pc=S['snd_picture'], max_frames=40)   # (read between pictures, as the other tests do: a face caught half-redrawn
                                                          #  for one TV frame is not a look - 18 Nov 2026, the looks now come from slower memory)
    now = []
    for p in range(NC):
        o = g.mem(S['shown_order'] + p, 1)[0]
        if o >= NC: now.append(None); continue
        if want[p] is None or order[p] != o: order[p] = o; want[p] = looks(o)
        f = face_on_screen(p)
        if f == want[p][0]: k = 'everyday'
        elif f == want[p][1]: k = 'eyes'
        else: k = None; wrong[p] += 1
        seen[p][k] = seen[p].get(k, 0) + 1; now.append(k)
    if len(set(k for k in now if k)) > 1: apart += 1
for p in range(NC):
    ok(seen[p].get('everyday', 0) > 10 and seen[p].get('eyes', 0) > 10 and wrong[p] == 0,
       'before the race, row %d (car %d): the face changes between its two looks - everyday %d, eyes %d of %d samples; %d not one of them' % (p + 1, order[p], seen[p].get('everyday', 0), seen[p].get('eyes', 0), frames // 2, wrong[p]))
ok(apart > 20, 'the rows are not in lock-step: in %d of %d samples some rows looked one way and some the other' % (apart, frames // 2))
g.go()
g.run(150)
left = [p for p in range(NC) if g.mem(S['shown_order'] + p, 1)[0] < 0xFF and face_on_screen(p) in looks(g.mem(S['shown_order'] + p, 1)[0] & 7)]
ok(not left and g.mem(S['race_on'], 1)[0], 'racing (3 s after green): no face left in any row (rows still showing one: %s)' % left)
g.close()
print('RESULT:', 'PASS' if fails == 0 else '%d FAIL' % fails)
