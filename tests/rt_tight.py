"""The tighter-track trial's measurements (17 Nov 2026): lap times and time on the grass, car by car, on a race-track tape.
Usage: python3 tests/rt_tight.py <tape name in build/> <its src folder> [races, default 3] [alone] [ace=88] [try=...] [late=3]
  in the pack: your car by autopilot with the four computer cars;  alone: the computer cars stay on the grid.
  The autopilot is rt_lib's (it aims at the middle of the road: a careful lap) unless ace=LOOK is given: then rt_ace.py's,
  which cuts the corners the way a good driver does (LOOK 88 to 104 is about the quickest clean lap).
  ace=LOOK,LIFT: it lifts off when its aim is more than LIFT degrees off its nose (60 unless given; a car with poor grip
  wants 30 to 45 - the driver cards' tape).
  late= you sit on the grid that many seconds after the green light, then chase: can the cars be caught and passed?
  try=  to try the computer cars' settings WITHOUT building a tape: the four cars (CYAN, GREEN, PINK, WHITE), each
        reach,line,half,ease,fuss,pace,react,err - e.g. try=40,3,2,0,2,16,0,3/36,3,2,1,2,15,0,6/... (- leaves a car as built)
A car is "on the grass" when the middle of it is over a tile the game's own surface map calls grass (what slows it).
Each race is run to the flag from the lights with a different run of luck. Prints, for each car: its first laps (from
the grid), its flying laps and their mean, and the share of its time on the grass."""
import sys
from rt_lib import *
import rt_ace
def measure(name, src, races=3, alone=False, look=None, tune=None, quiet=False, late=0, lift=60):
    who = ['YOU (autopilot)', 'CYAN', 'GREEN', 'PINK', 'WHITE']; n = 1 if alone else 5
    first = [[] for _ in range(5)]; fly = [[] for _ in range(5)]; on = [0] * 5; visits = [0] * 5; total = [0] * 5; order = []
    for race in range(races):
        g = Game(name, src); g.to_grid()
        S = g.sym; CS = S['c_size']
        g.poke(S["seed"], [(0x34 + 37 * race) & 255, 0x12 + race])     # a different run of luck (the cars' lines and mistakes) each race
        for k, t in enumerate(tune or []):
            if t is None: continue
            g.poke(S['ai_styles'] + 5 * k, t[:5]); g.poke(S['cars'] + (k + 1) * CS + 19, [t[5], t[6], t[7]])
            if len(t) > 8: g.poke(S['ai_lift'] + k, [t[8]])
        g.go(alone=alone)
        steer = rt_ace.ace(g, look, lift) if look else g.steer
        surf = g.mem(S['surface_map'], 9 * S['maph'])
        def grass(x, y):
            tx, ty = (x + 8) >> 3, (y + 8) >> 3
            return not (0 <= tx < 72 and 0 <= ty < S['maph']) or bool(surf[ty * 9 + (tx >> 3)] & (0x80 >> (tx & 7)))
        last = [None] * 5; t = [[] for _ in range(5)]; was = [False] * 5
        for f in range(80 * 50):
            if f < late * 50: g.key('Q', False); g.key('O', False); g.key('P', False)   # (late=: you sit on the grid while the others go)
            else: steer()
            g.run(1)
            c = g.mem(S['cars'], CS * 5)
            for i in range(n):
                r = c[i * CS:(i + 1) * CS]
                if len(t[i]) > S['laps']: continue                 # (it has finished)
                gr = grass(r[1] + 256 * r[2], r[4] + 256 * r[5])
                on[i] += gr; visits[i] += gr and not was[i]; was[i] = gr; total[i] += 1
                if last[i] is not None and r[25] != last[i]: t[i].append(f / 50)
                last[i] = r[25]
            if all(len(t[i]) > S['laps'] for i in range(n)): break
        for i in range(n):
            laps = [round(b - a, 1) for a, b in zip(t[i], t[i][1:])]
            first[i] += laps[:1]; fly[i] += laps[1:]
        order.append(''.join(who[i][0] for i in sorted(range(n), key=lambda i: t[i][-1] if len(t[i]) > S['laps'] else 999)))
        g.close()
    mean = [sum(fly[i]) / len(fly[i]) if fly[i] else 0 for i in range(n)]
    if not quiet:
        print('%s, %s, %d races of %d laps%s%s' % (name, 'alone' if alone else 'in the pack', races, S['laps'], ', you by the corner-cutting autopilot (LOOK %d, LIFT %d)' % (look, lift) if look else '', '' if alone else '; finishing orders ' + ' '.join(order)))
        for i in range(n):
            print('  %-16s first laps %s  flying laps %s  mean %.2f  best %.1f  worst %.1f  grass %.1f%% of the time, %d visits' % (who[i], first[i], fly[i], mean[i], min(fly[i] or [0]), max(fly[i] or [0]), 100.0 * on[i] / max(total[i], 1), visits[i]))
    return dict(mean=mean, fly=fly, first=first, grass=[100.0 * on[i] / max(total[i], 1) for i in range(n)], visits=visits, order=order)
if __name__ == '__main__':
    a = sys.argv[3:]
    look, lift = ([[int(x) for x in (v[4:] + ',60').split(',')[:2]] for v in a if v.startswith('ace=')] or [[None, 60]])[0]
    tune = ([[None if c == '-' else [int(x) for x in c.split(',')] for c in v[4:].split('/')] for v in a if v.startswith('try=')] or [None])[0]
    measure(sys.argv[1], sys.argv[2], ([int(v) for v in a if v.isdigit()] or [3])[0], 'alone' in a, look, tune, late=([float(v[5:]) for v in a if v.startswith('late=')] or [0])[0], lift=lift)
