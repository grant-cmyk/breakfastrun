"""A better driver than rt_lib's autopilot, to stand in for a good human lap on the race-track tapes (17 Nov 2026): it
aims at a point LOOK pixels further round the middle of the road than where it is (so it cuts the corners), and lifts off
Q only when that point is more than LIFT degrees off its nose. Usage (alone on the track, 3 laps):
  python3 tests/rt_ace.py <tape name in build/> <its src folder> [LOOK ...]      (no LOOK: tries 40 to 120 and prints each)
ace(g, look, lift) returns the steering function, for other tools."""
import sys, math
from rt_lib import *
def ace(g, look=72, lift=60, dead=6):
    pts = []
    w = g.wps
    for (x0, y0), (x1, y1) in zip(w, w[1:] + w[:1]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / 4))
        pts += [(x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n) for k in range(n)]
    N = len(pts); st = {'i': None, 'hist': [], 'back': 0}
    def steer():
        x, y, ang = g.car(); x += 8; y += 8
        # (22 Nov 2026, the breakfast-table race tape: the autopilot drove into a cereal O at the top chicane and pushed
        # against it for the rest of the race. A person backs off: so does it - not 6 px further on in a second (50 TV
        # frames) with Q held: A (back) and the wheel the other way for 25 frames)
        st['hist'].append((x, y)); del st['hist'][:-50]
        if st['back']:
            st['back'] -= 1; g.key('Q', False); g.key('A', True); g.key('O', st['bo']); g.key('P', not st['bo'])
            if not st['back']: g.key('A', False); st['hist'] = []
            return
        if len(st['hist']) == 50 and math.hypot(x - st['hist'][0][0], y - st['hist'][0][1]) < 6 and g.mem(g.sym['race_on'], 1)[0]:
            st['back'] = 25; st['bo'] = 'P' in g.held; return
        rng = range(N) if st['i'] is None else [(st['i'] + k) % N for k in range(-5, 30)]
        st['i'] = i = min(rng, key=lambda k: (pts[k][0] - x) ** 2 + (pts[k][1] - y) ** 2)
        tx, ty = pts[(i + look // 4) % N]
        diff = (math.degrees(math.atan2(tx - x, -(ty - y))) % 360 - ang * 360 / 64 + 540) % 360 - 180
        g.key('Q', abs(diff) < lift); g.key('O', diff < -dead); g.key('P', diff > dead)
    return steer
def laps(name, src, look, lift, alone=True, secs=70):
    g = Game(name, src); g.to_grid(); g.go(alone=alone)
    S = g.sym; surf = g.mem(S['surface_map'], 9 * S['maph']); steer = ace(g, look, lift)
    t = []; last = None; on = 0
    for f in range(secs * 50):
        steer(); g.run(1)
        c = g.mem(S['cars'], 26); tx, ty = (c[1] + 256 * c[2] + 8) >> 3, (c[4] + 256 * c[5] + 8) >> 3
        if len(t) <= S["laps"]: on += not (0 <= ty < S["maph"] and 0 <= tx < 72) or bool(surf[ty * 9 + (tx >> 3)] & (0x80 >> (tx & 7)))
        if last is not None and c[25] != last: t.append(f / 50)
        last = c[25]
        if len(t) > S['laps']: break
    g.close()
    return [round(b - a, 1) for a, b in zip(t, t[1:])], on
if __name__ == '__main__':
    name, src = sys.argv[1], sys.argv[2]
    for look in ([int(v) for v in sys.argv[3:]] or range(40, 121, 16)):
        for lift in (45, 70, 180):
            l, on = laps(name, src, look, lift)
            print('%s LOOK %3d LIFT %3d: laps %s (the first from the grid), %d TV frames on the grass' % (name, look, lift, l, on))
