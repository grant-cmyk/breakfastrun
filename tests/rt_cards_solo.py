"""The driver cards: EACH COMPUTER CAR ON ITS OWN (17 Nov 2026) - one car at a time laps the track with the others (and
you) left on the grid, so that its lap is the car and its driver and nothing else: no bumps, nobody in the way.
Usage: python3 tests/rt_cards_solo.py <tape name in build/> <its src folder> [laps to time, default 3]
Prints for each: its flying laps, its speed (px a TV frame) - the mean, the fastest, and the mean of the slowest quarter
of the lap (its corners) - the share of the lap spent sliding (going more than 20 degrees away from where it points),
and its time on the grass."""
import sys, math
from rt_lib import *
INFIELD = (240, 300)       # a patch of grass inside the tight track's lap, clear of the road
def solo(name, src, k, laps=3, seed=0):
    g = Game(name, src); g.to_grid()
    S = g.sym; CS = S['c_size']
    g.poke(S['seed'], [0x34 + 37 * seed, 0x12 + seed])
    g.go(alone=False); g.key('Q', False)
    for i in range(5):                   # (the others off the road, on the grass in the middle, with no throttle)
        if i != k:
            g.put(INFIELD[0] + 24 * i, INFIELD[1], i=i)
            if i: g.rpc('write', addr=S['cars'] + i * CS + 19, value=0)
    surf = g.mem(S['surface_map'], 9 * S['maph'])
    t = []; last = None; sp = []; slide = 0; on = 0; n = 0
    for f in range(120 * 50):
        g.run(1)
        r = g.mem(S['cars'] + k * CS, CS)
        s16 = lambda lo, hi: (lo + 256 * hi + 32768) % 65536 - 32768
        vx, vy = s16(r[6], r[7]), s16(r[8], r[9]); v = math.hypot(vx, vy)
        if last is not None and r[25] != last: t.append(f / 50)
        last = r[25]
        if len(t) >= 1:
            sp.append(v / 256); n += 1
            if v > 64: slide += abs((math.degrees(math.atan2(vx, -vy)) - r[10] * 5.625 + 540) % 360 - 180) > 20
            tx, ty = (r[1] + 256 * r[2] + 8) >> 3, (r[4] + 256 * r[5] + 8) >> 3
            on += bool(surf[ty * 9 + (tx >> 3)] & (0x80 >> (tx & 7)))
        if len(t) > laps: break
    g.close()
    sp.sort()
    return [round(b - a, 1) for a, b in zip(t, t[1:])], sum(sp) / max(n, 1), sp[-1] if sp else 0, sum(sp[:max(n // 4, 1)]) / max(n // 4, 1), 100.0 * slide / max(n, 1), 100.0 * on / max(n, 1)
if __name__ == '__main__':
    name, src = sys.argv[1], sys.argv[2]; laps = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    for k, who in enumerate(['CYAN', 'GREEN', 'PINK', 'WHITE'], 1):
        l, mean, top, slow, sl, on = solo(name, src, k, laps)
        print('%s %-6s alone: laps %s  speed mean %.2f, fastest %.2f, in its slowest quarter %.2f px a TV frame; sliding %.0f%% of the lap; on the grass %.1f%%' % (name, who, l, mean, top, slow, sl, on))
