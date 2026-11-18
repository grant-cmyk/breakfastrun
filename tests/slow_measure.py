"""THE SLOWER GAME's measurements (Grant, 18 Nov 2026: "slower and smoother", "a maximum jump of 4 pixels or even less"):
how far your car and the view move from one picture to the next, on a race-track tape.
Usage: python3 tests/slow_measure.py <tape name in build/> [its src folder, default build/<tape name>/src] [secs=25]
  1. IN THE PACK: from the green light, your car by the corner-cutting autopilot (ace 104,30: the tidy one) with the four
     computer cars, for secs seconds. For every picture: the TV frames it took, and how far your car (in the world), the
     view (the camera) and your car on the screen moved since the last picture.
  2. NOS: alone on the track, the same autopilot; the canister you start with fired once your car is at its top speed
     (95% of its card's, for 5 TV frames); the same sums while it burns.
Prints for each: your top speed (px a TV frame), pictures a second, the share of pictures of 5 TV frames or more, and the
jumps (largest, and the typical - the middle one of the pictures at speed - in px; a jump is the larger of across and
down, the way the eye sees a step on the TV, with the straight-line distance beside it)."""
import sys, math
from rt_lib import *
import rt_ace
def drive(g, secs, alone, nos_at=None):
    """Each picture is measured where it has just gone to the screen (snd_picture, the next thing the game does): where
    your car and the camera are then, and the TV frames since the last (the game's own count, ticks)."""
    S = g.sym
    g.go(alone=alone); steer = rt_ace.ace(g, 104, 30)
    rows = []; vmax = 0; fired = False; f = 0; t0 = g.w16(S['ticks'])
    while f < secs * 50:
        r = g.w16(S['renders'])
        while g.w16(S['renders']) == r and f < secs * 50:       # (the rest of this picture: the autopilot, a TV frame at a time)
            steer()
            if nos_at is not None and fired is False and f >= nos_at(g, f): g.key('SPACE', True); fired = f
            if fired is not False and f == fired + 8: g.key('SPACE', False)   # (held 8 TV frames: the key is looked at once a picture)
            g.run(1); f += 1
            c = g.mem(S['cars'], 10); v = math.hypot(int.from_bytes(c[6:8], 'little', signed=True), int.from_bytes(c[8:10], 'little', signed=True)) / 256
            if fired is False: vmax = max(vmax, v)              # (the top speed: before any NOS)
        g.rpc('run', until_pc=S['snd_picture'], max_frames=10)
        x, y, _ = g.car(); cx, cy = g.cam(); f = g.w16(S['ticks']) - t0
        rows.append(dict(f=g.w16(S['ticks']), x=x, y=y, cx=cx, cy=cy, v=v, boost=g.mem(S['boost_t'], 1)[0]))
    return rows, vmax
def jumps(rows, pick=lambda a, b: True):
    out = []
    for a, b in zip(rows, rows[1:]):
        if not pick(a, b) or b['f'] == a['f']: continue
        dx, dy = b['x'] - a['x'], b['y'] - a['y']; cx, cy = b['cx'] - a['cx'], b['cy'] - a['cy']; sx, sy = dx - cx, dy - cy
        out.append(dict(fr=b['f'] - a['f'], car=max(abs(dx), abs(dy)), card=math.hypot(dx, dy), cam=max(abs(cx), abs(cy)),
                        scr=max(abs(sx), abs(sy)), v=b['v']))
    return out
def report(title, J, secs=None):
    if not J: print('  %s: no pictures' % title); return
    fast = [j for j in J if j['v'] > 0.8 * max(j['v'] for j in J)] or J
    med = lambda k, L: sorted(j[k] for j in L)[len(L) // 2]
    n5 = sum(j['fr'] >= 5 for j in J)
    print('  %s: %d pictures, %.2f a second, %.1f TV frames each; %d%% took 5 or more (%s)' % (
        title, len(J), 50.0 * len(J) / sum(j['fr'] for j in J), sum(j['fr'] for j in J) / len(J), round(100.0 * n5 / len(J)),
        ', '.join('%d: %d' % (k, sum(j['fr'] == k for j in J)) for k in sorted(set(j['fr'] for j in J)))))
    p95 = lambda k: sorted(j[k] for j in J)[int(len(J) * 0.95)]
    for k, what in (('car', 'your car in the world: '), ('cam', 'the view (camera):     '), ('scr', 'your car on the screen:')):
        print('    %s largest %2d px, 1 picture in 20 over %2d, typical at speed %d (at speed: %s)%s' % (what, max(j[k] for j in J), p95(k), med(k, fast),
              ', '.join('%d px %d%%' % (v, round(100.0 * sum(j[k] == v for j in fast) / len(fast))) for v in sorted(set(j[k] for j in fast))),
              ' (straight line: largest %.1f)' % max(j['card'] for j in J) if k == 'car' else ''))
if __name__ == '__main__':
    name = sys.argv[1]; a = sys.argv[2:]
    src = ([v for v in a if '=' not in v] or [os.path.join(ROOT, 'build', name, 'src')])[0]
    secs = float(([v[5:] for v in a if v.startswith('secs=')] or [25])[0])
    print(name)
    g = Game(name, src); g.to_grid(); rows, vmax = drive(g, secs, False); g.close()
    print('  your top speed in the pack %.2f px a TV frame' % vmax)
    report('IN THE PACK, %d s' % secs, jumps(rows[2:]))
    # NOS: fired once the car is at its top speed (alone, so nothing is in the way)
    st = {'n': 0}
    def nos_at(g, f):                   # (at 95% of the card's top speed for 5 TV frames running; at 8 s whatever happens)
        c = g.mem(g.sym['cars'], 10); v = math.hypot(int.from_bytes(c[6:8], 'little', signed=True), int.from_bytes(c[8:10], 'little', signed=True))
        st['n'] = st['n'] + 1 if v > 0.95 * g.sym['cd_top'] else 0
        return f if st['n'] >= 5 or f >= 400 else 10 ** 9
    g = Game(name, src); g.to_grid(); rows, v0 = drive(g, 12, True, nos_at)
    vb = max(r['v'] for r in rows if r['boost'])
    print('  NOS: top speed %.2f px a TV frame before, %.2f while it burns (%.2f times); it burned %d TV frames' % (v0, vb, vb / v0, sum(r['boost'] > 0 for r in rows) and max(r['boost'] for r in rows) + 1))
    report('WITH NOS BURNING', jumps(rows, lambda a, b: b['boost'] > 0))
    g.close()
