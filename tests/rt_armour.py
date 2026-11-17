"""The armour and weapons trial's race reports (17 Nov 2026): whole races from the lights to the flag on a race-track
tape, your car by the corner-cutting autopilot, and what happened in each.
Usage: python3 tests/rt_armour.py <tape name in build/> <its src folder> [races, default 5] [ace=104,30] [late=3] [shot=folder]
For each race: the finishing order, each car's laps, and - on a tape built with ARMOUR=1 - shells fired and shells that
hit, times the clown's wheels came out and cars they hit, how often each car was spun, each car's armour at the flag
(pieces of 6), and who limped (had none left) and from when. A tape without ARMOUR gives the orders and laps only, to
set beside it. The races run side by side (one emulator each), each with its own run of luck.
late=N: your car sits on the grid N seconds after the green light and then chases - a race spent in the pack, not in front.
shot=folder: a screenshot there every second of race 1."""
import sys, os
from concurrent.futures import ProcessPoolExecutor
from rt_lib import *
import rt_ace
WHO = ['YOU', 'FRANK', 'SPIKE', 'BRUNO', 'JANE']
def one(args):
    name, src, race, look, lift, shot, late = args
    g = Game(name, src); g.to_grid(); S = g.sym; CS = S['c_size']
    g.poke(S['seed'], [(0x34 + 37 * race) & 255, 0x12 + race])
    g.go(); steer = rt_ace.ace(g, look, lift)
    arm = 'arm_tab' in S
    last = [None] * 5; t = [[] for _ in range(5)]; limp = [None] * 5; f = 0
    for f in range(100 * 50):
        if f < late * 50: g.key('Q', False); g.key('O', False); g.key('P', False)
        else: steer()
        g.run(1)
        c = g.mem(S['cars'], CS * 5)
        for i in range(5):
            r = c[i * CS:(i + 1) * CS]
            if last[i] is not None and r[25] != last[i] and len(t[i]) <= S['laps']: t[i].append(f / 50)
            last[i] = r[25]
        if arm and f % 10 == 0:
            a = g.mem(S['arm_tab'], 40)
            for i in range(5):
                if a[i * 8 + 1] == 0 and limp[i] is None and len(t[i]) <= S['laps']: limp[i] = f / 50
        if shot and race == 0 and f % 50 == 0: g.shot(os.path.join(shot, 'race_%03d.png' % (f // 50)), 2)
        if all(len(t[i]) > S['laps'] for i in range(5)): break
    res = dict(race=race, laps=[[round(b - a, 1) for a, b in zip(x, x[1:])] for x in t], end=[x[-1] if len(x) > S['laps'] else None for x in t],
               order=''.join(WHO[i][0] for i in sorted(range(5), key=lambda i: t[i][-1] if len(t[i]) > S['laps'] else 999)), limp=limp,
               bumps=g.w16(S['bumps']))
    if arm:
        a = g.mem(S['arm_tab'], 40); k = g.mem(S['sh_fired'], 4)
        res.update(pieces=[a[i * 8 + 1] for i in range(5)], spins=[a[i * 8 + 7] for i in range(5)], fired=k[0], hits=k[1], outs=k[2], whits=k[3])
    g.close(); return res
def report(name, src, races=5, look=104, lift=30, shot=None, late=0):
    with ProcessPoolExecutor(min(races, 6)) as ex: rs = list(ex.map(one, [(name, src, r, look, lift, shot, late) for r in range(races)]))
    print('%s: %d races, you by the autopilot (LOOK %d, LIFT %d)%s. Orders (Y you, F Frank, S Spike, B Bruno, J Jane): %s' % (name, races, look, lift, ', starting %.0f s late' % late if late else '', ' '.join(r['order'] for r in rs)))
    for r in rs:
        print(' race %d: %s  bumps %d  finished at %s' % (r['race'] + 1, r['order'], r['bumps'], ' '.join('%s %s' % (WHO[i][0], ('%.1f' % r['end'][i]) if r['end'][i] else 'NOT IN') for i in range(5))))
        if 'pieces' in r:
            print('    shells fired %d, hit %d; wheels out %d times, hit %d; spins %s; armour at the flag %s; limped %s' % (
                r['fired'], r['hits'], r['outs'], r['whits'], ' '.join('%s %d' % (WHO[i][0], r['spins'][i]) for i in range(5)),
                ' '.join('%s %d' % (WHO[i][0], r['pieces'][i]) for i in range(5)), ', '.join('%s from %.0f s' % (WHO[i], r['limp'][i]) for i in range(5) if r['limp'][i] is not None) or 'nobody'))
    for i in range(5):
        fl = [x for r in rs for x in r['laps'][i][1:]]
        print('  %-6s flying laps mean %.1f (best %.1f, worst %.1f); all laps %s' % (WHO[i], sum(fl) / max(len(fl), 1), min(fl or [0]), max(fl or [0]), ' / '.join(' '.join('%.1f' % x for x in r['laps'][i]) for r in rs)))
    if 'pieces' in rs[0]:
        n = len(rs)
        print('  a race, on average: %.1f shells fired, %.1f hit; wheels out %.1f times, %.1f hits; spins %s; armour left %s; bumps %.0f' % (
            sum(r['fired'] for r in rs) / n, sum(r['hits'] for r in rs) / n, sum(r['outs'] for r in rs) / n, sum(r['whits'] for r in rs) / n,
            ' '.join('%s %.1f' % (WHO[i][0], sum(r['spins'][i] for r in rs) / n) for i in range(5)),
            ' '.join('%s %.1f' % (WHO[i][0], sum(r['pieces'][i] for r in rs) / n) for i in range(5)), sum(r['bumps'] for r in rs) / n))
    return rs
if __name__ == '__main__':
    a = sys.argv[3:]
    look, lift = ([[int(x) for x in (v[4:] + ',30').split(',')[:2]] for v in a if v.startswith('ace=')] or [[104, 30]])[0]
    report(sys.argv[1], sys.argv[2], ([int(v) for v in a if v.isdigit()] or [5])[0], look, lift, ([v[5:] for v in a if v.startswith('shot=')] or [None])[0], ([float(v[5:]) for v in a if v.startswith('late=')] or [0])[0])
