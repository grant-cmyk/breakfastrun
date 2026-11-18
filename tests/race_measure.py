"""RACE mode's competitiveness, measured (18 Nov 2026; Grant: "the idea is to make it competitive so you don't run away
with it"). Races of 3 laps on a RACE tape (tools/build_race.sh), you starting last, each with a different run of luck;
YOUR car driven by a stand-in for a person:
  good      rt_ace.py's corner-cutting autopilot (LOOK 104, LIFT 30: about the quickest clean lap on MAX's card at 70%)
  careful   rt_lib's autopilot (it aims at the middle of the road: an average driver)
Usage: python3 tests/race_measure.py <tape name in build/> [good|careful] [races, default 5] [try=...] [jobs=5]
  try=  the RACE drivers' numbers poked in before the lights (no tape need be built), all four cars the same:
        reach,line,half,ease,fuss,err,brake - e.g. try=48,3,2,2,2,4,61  (brake: the speed it brakes down to for a corner,
        cd_race's third byte, quarter-pixels a frame; - for any number to leave it as built), and an eighth, slide: the
        speed above which the car slides when it steers (cd_race's first word, 256 = 1 px a frame) - MAX's card's grip
Prints a line a race - the finishing order (Y you, C cyan, G yellow, P magenta, W white), your place, the gaps at the flag to
the winner (seconds), how many times the order changed (and how many of those moved YOU), each car's flying laps - and a
summary: your wins, your mean place, your mean gap to the winner when not winning, the slowest car's mean flying lap
against the quickest's."""
import sys, os
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rt_lib import *
import rt_ace
WHO = 'YCGPW'
def one(args):
    name, driver, race, tune = args
    g = Game(name, os.path.join(ROOT, 'build', name, 'src')); g.to_grid()
    S = g.sym; CS = S['c_size']
    g.poke(S['seed'], [(0x34 + 37 * race) & 255, 0x12 + race])
    g.go()
    if tune:
        reach, line, half, ease, fuss, err, brake = tune[:7]
        slide = tune[7] if len(tune) > 7 else None
        for k in range(4):
            cur = list(g.mem(S['ai_race'] + 5 * k, 5))
            new = [v if v is not None else c for v, c in zip((reach, line, half, ease, fuss), cur)]
            g.poke(S['ai_race'] + 5 * k, new)
            if err is not None: g.poke(S['cars'] + (k + 1) * CS + 21, [err])
            if brake is not None: g.poke(S['cd_race'] + 8 * k + 2, [brake])
            if slide is not None: g.poke(S['cd_race'] + 8 * k, [slide & 255, slide >> 8])
    steer = rt_ace.ace(g, 104, 30) if driver == 'good' else g.steer
    t = [[] for _ in range(5)]; last = [None] * 5; prev = None; changes = you_moves = 0
    skid = [0] * 5; moving = [0] * 5             # (18 Nov 2026, Grant: "the computer cars need to skid a bit more": the share of the time
                                                 #  a computer car is in its slide - turning faster than its card's slide speed: racer.asm skid)
    s16 = lambda lo, hi: (lo + 256 * hi + 32768) % 65536 - 32768
    for f in range(int(os.environ.get('RACE_SECS', '160')) * 50):
        steer(); g.run(1)
        c = g.mem(S['cars'], CS * 5)
        for i in range(5):
            if len(t[i]) > S['laps']: continue
            lap = c[i * CS + 25]
            if last[i] is not None and lap != last[i]: t[i].append(f / 50)
            last[i] = lap
        sl = [None] + [g.mem(S['cd_race'] + 8 * k, 2) for k in range(4)]
        for i in range(1, 5):
            vx, vy = abs(s16(c[i * CS + 6], c[i * CS + 7])), abs(s16(c[i * CS + 8], c[i * CS + 9]))
            sp = max(vx, vy) + min(vx, vy) // 2
            if sp > 128:
                moving[i] += 1; skid[i] += bool(c[i * CS + S['c_ctrl']] & 3) and sp >= sl[i][0] + 256 * sl[i][1]
        o = list(g.mem(S['order'], 5))
        if prev is not None and o != prev:
            changes += 1; you_moves += o.index(0) != prev.index(0)
        prev = o
        if all(len(t[i]) > S['laps'] for i in range(5)): break
    g.close()
    fin = [x[-1] if len(x) > S['laps'] else 9999 for x in t]
    order = sorted(range(5), key=lambda i: fin[i])
    laps = [[round(b - a, 2) for a, b in zip(x, x[1:])] for x in t]
    return dict(order=order, fin=fin, place=order.index(0) + 1, gaps=[round(fin[i] - fin[order[0]], 1) for i in range(5)],
                changes=changes, you_moves=you_moves, skid=[round(100 * skid[i] / max(1, moving[i])) for i in range(5)], fly=[l[1:] for l in laps], first=[l[:1] for l in laps])
def measure(name, driver='good', races=5, tune=None, jobs=5):
    with Pool(min(jobs, races)) as p:
        res = p.map(one, [(name, driver, r, tune) for r in range(races)])
    return res
def report(name, driver, res):
    print('%s, %s driver, %d races of 3 laps, you from the back of the grid' % (name, driver, len(res)))
    for r, x in enumerate(res):
        print('  race %d: %s  you %d%s  gaps to the winner %s  order changes %d (you %d)  flying laps %s' % (
            r + 1, ''.join(WHO[i] for i in x['order']), x['place'], {1: 'st', 2: 'nd', 3: 'rd'}.get(x['place'], 'th'),
            ' '.join('%s %.1f' % (WHO[i], x['gaps'][i]) for i in x['order'][1:]), x['changes'], x['you_moves'],
            ' '.join('%s %s' % (WHO[i], '/'.join('%.1f' % v for v in x['fly'][i])) for i in range(5))))
    wins = sum(x['place'] == 1 for x in res)
    lost = [x['gaps'][0] for x in res if x['place'] > 1]
    mean = [sum(sum(x['fly'][i]) for x in res) / max(1, sum(len(x['fly'][i]) for x in res)) for i in range(5)]
    print('  YOU: %d wins of %d, mean place %.1f, mean gap to the winner when not winning %s; order changes a race %.1f; '
          'mean flying lap %s; slowest car %.0f%% off the quickest' % (
              wins, len(res), sum(x['place'] for x in res) / len(res), ('%.1f s' % (sum(lost) / len(lost))) if lost else '-',
              sum(x['changes'] for x in res) / len(res), ' '.join('%s %.2f' % (WHO[i], mean[i]) for i in range(5)),
              100.0 * (max(mean) / min(mean) - 1)))
    print('  COMPUTER CARS IN A SLIDE (%% of the time moving: turning faster than their slide speed): %s' % ' '.join('%s %.0f%%' % (WHO[i], sum(x['skid'][i] for x in res) / len(res)) for i in range(1, 5)))
if __name__ == '__main__':
    a = sys.argv[1:]
    name = a[0]; driver = ([v for v in a if v in ('good', 'careful')] or ['good'])[0]
    races = ([int(v) for v in a[1:] if v.isdigit()] or [5])[0]
    tune = ([[None if x == '-' else int(x) for x in v[4:].split(',')] for v in a if v.startswith('try=')] or [None])[0]
    jobs = ([int(v[5:]) for v in a if v.startswith('jobs=')] or [5])[0]
    report(name, driver, measure(name, driver, races, tune, jobs))
