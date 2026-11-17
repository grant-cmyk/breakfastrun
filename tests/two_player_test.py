"""TWO PLAYERS IN ONE VIEW (src/twoplayer.asm; TWOP=1 with RACETRACK=1) - driven in zxdev on both players' keys.
  1. each car answers to its own keys only (and each player's NOS key to their own canisters)
  2. the view holds both cars, every picture of a race driven by two autopilots; laps count for both; the race ends
  3. the leash: one player stops - their car is put back legally (on the road's middle, inside the window, behind the
     leader, standing still, held for a moment) every time, all the way round; and the other way about
  4. one player (the title's 1) on the two-player tape is the one-player game: a scripted drive's car positions are
     the same, TV frame by TV frame, as on the same build without the switch
Usage: python3 tests/two_player_test.py [tape with TWOP=1] [the same build without it]   (names in build/, no .tap;
       default racer_2p and racer_tight_w56s_normal; build folders build/<BDIR>: 2PDIR, OFFDIR)"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from twop_lib import Game2, WIN_W, WIN_H
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
TAP2 = sys.argv[1] if len(sys.argv) > 1 else 'racer_2p'
TAP1 = sys.argv[2] if len(sys.argv) > 2 else 'racer_tight_w56s_normal'
SRC2 = os.path.join(ROOT, 'build', os.environ.get('2PDIR', 'racer_2p'), 'src')
SRC1 = os.path.join(ROOT, 'build', os.environ.get('OFFDIR', 'tight_w56s_normal'), 'src')
PASS = FAIL = 0
def check(ok, what):
    global PASS, FAIL
    PASS += bool(ok); FAIL += not ok
    print(('PASS  ' if ok else 'FAIL  ') + what); sys.stdout.flush()
def prog(g, i):
    """how far round car i is: laps x waypoints + waypoints passed since the line (as the game's own 'progress')"""
    r = g.rec(i); n = len(g.wps)
    return r[25] * n + (r[13] - g.sym['ws'] - 1) % n

# ---- 1. their own keys only ----
g = Game2(TAP2, SRC2); g.start(2, alone=True)
check(g.two() == 1, "the title's 2 starts a two-player race")
a0, a1 = g.car(0), g.car(1)
g.key('Q', True); g.key('P', True); g.run(40); g.key('Q', False); g.key('P', False)
b0, b1 = g.car(0), g.car(1)
check(b0[:2] != a0[:2] and b0[2] != a0[2] and b1 == a1, "Q and P move and turn player 1's car; player 2's does not stir (%s -> %s; %s)" % (a0, b0, b1))
g.run(60)                                               # (player 1's car rolls to a stop)
c0 = g.car(0)
g.key('0', True); g.key('6', True); g.run(40); g.key('0', False); g.key('6', False)
d0, d1 = g.car(0), g.car(1)
check(d1[:2] != b1[:2] and (b1[2] - d1[2]) % 64 in range(1, 32) and d0[2] == c0[2] and math.hypot(d0[0] - c0[0], d0[1] - c0[1]) < 3,
      "0 and 6 move player 2's car and turn it left; player 1's only rolls (%s -> %s; %s -> %s)" % (b1, d1, c0, d0))
e1 = g.car(1); g.key('7', True); g.run(10); g.key('7', False)
check((g.car(1)[2] - e1[2]) % 64 in range(1, 32), "7 turns player 2's car right")
g.run(80); s0 = g.car(1); g.key('0', True); g.run(30); v_go = math.hypot(g.car(1)[0] - s0[0], g.car(1)[1] - s0[1])
g.key('0', False); g.key('5', True); p0 = g.car(1); g.run(12); p1 = g.car(1); g.run(12); p2 = g.car(1); g.key('5', False)
check(v_go > 10 and math.hypot(p2[0] - p1[0], p2[1] - p1[1]) < math.hypot(p1[0] - p0[0], p1[1] - p0[1]), "5 brakes player 2's car")
S = g.sym
g.poke(S['inv'], [1, 0, 0]); g.poke(S['p2_inv'], [1])
g.rpc('press', keys='8', frames=3, after=2)
check(g.mem(S['p2_inv'], 1)[0] == 0 and g.mem(S['inv'], 3) == bytes([1, 0, 0]), "8 fires player 2's NOS canister, not player 1's")
g.run(60); g.poke(S['p2_inv'], [1])
g.rpc('press', keys='SPACE', frames=3, after=2)
check(g.mem(S['p2_inv'], 1)[0] == 1 and g.mem(S['inv'], 3) == bytes([0, 0, 0]), "SPACE fires player 1's, not player 2's")
g.close()

# ---- 2. two autopilots race: the view holds both, laps count for both, the race ends ----
g = Game2(TAP2, SRC2); g.start(2)
g.lift[1] = 0.93                                        # (player 2 a little slower, so that they are not always together)
worst = 0; laps = [[], []]; pictures = 0; leashes = 0; r0 = g.w16(S['renders']); over_at = None; last_t = 0
for f in range(6000):
    g.step()
    for i in (0, 1):
        if len(laps[i]) < g.laps(i): laps[i].append(f)
    t = g.mem(S['lsh_t'], 1)[0]
    if t > last_t: leashes += 1
    last_t = t
    r = g.w16(S['renders'])
    if r != r0:
        r0 = r; pictures += 1
        if g.laps(0) <= 3 and g.laps(1) <= 3:
            for i in (0, 1):
                (ok, (sx, sy)) = g.in_window(i)
                worst = max(worst, -sx, sx - (WIN_W - 16), -sy, sy - (WIN_H - 16))
    if g.mem(S['race_over'], 1)[0]: over_at = f; break
check(worst <= 8, "the view holds both cars: over %d pictures the worst is %d px of a car's 16 over the window's edge, read up to a picture's moving later (8 allowed)" % (pictures, max(worst, 0)))
check(len(laps[0]) == 4 and len(laps[1]) == 4, "laps count for both: the line crossed at frames %s (player 1), %s (player 2)" % (laps[0], laps[1]))
fin = g.mem(S['fin_at'], 5)
check(over_at is not None and fin[0] and fin[1], "the race ends with both in (frame %s; finishing places %s; the leash went %d times)" % (over_at, list(fin), leashes))
g.close()

# ---- 3. the leash ----
def leash_run(stopper, frames=2600):
    """the other player drives by autopilot; 'stopper' drives 150 frames and then lets go of everything"""
    g = Game2(TAP2, SRC2); g.start(2, alone=True)
    lead = 1 - stopper
    events = []; bad = []; last_t = 0; hold_moved = 0; held_from = None
    for f in range(frames):
        g.step(p1=(stopper != 0 or f < 150), p2=(stopper != 1 or f < 150))
        if f >= 150 and held_from is None:               # (once stopped, the stopper holds their accelerator down, to show the hold)
            pass
        tl = g.mem(S['lsh_t'], 2)
        if tl[0] > last_t:                               # the leash has just gone
            x, y, ang = g.car(stopper); lx, ly, _ = g.car(lead); r = g.rec(stopper)
            on_wp = min(math.hypot(x + 8 - wx, y + 8 - wy) for wx, wy in g.wps)
            aim = g.wps[r[13]]
            want = math.degrees(math.atan2(aim[0] - x - 8, -(aim[1] - y - 8))) % 360
            off = abs((ang * 360 / 64 - want + 540) % 360 - 180)
            inw, spot = g.in_window(stopper)
            ev = dict(f=f, car=tl[1], on_wp=on_wp, inw=inw, spot=spot, behind=prog(g, lead) - prog(g, stopper), far=math.hypot(lx - x, ly - y),
                      still=(r[6:10] == bytes(4)), off=off, fsh=None)
            events.append(ev)
            if not (tl[1] == stopper + 1 and on_wp < 1.5 and inw and 0 < ev['behind'] <= 4 and ev['far'] >= 24 and ev['still'] and off <= 45): bad.append(ev)
            held_from = (f, (x, y))
        last_t = tl[0]
        if held_from and f == held_from[0] + 8:          # 8 TV frames into the hold: it has not moved
            x, y, _ = g.car(stopper)
            hold_moved = max(hold_moved, math.hypot(x - held_from[1][0], y - held_from[1][1]))
        if held_from and f == held_from[0] + 30:         # and by now the ground under it has been looked at: road (3), not grass
            events[-1]['fsh'] = g.rec(stopper)[12]
            if events[-1]['fsh'] != 3: bad.append(events[-1])
            held_from = None
    out = (events, bad, hold_moved, g.laps(lead), g.laps(stopper))
    g.close(); return out
for stopper in (1, 0):
    events, bad, hold_moved, ll, sl = leash_run(stopper)
    who = 'player %d' % (stopper + 1)
    check(len(events) >= 8 and not bad, "%s stops: put back %d times round the track, each time on a waypoint (the road's middle, road under it), in the window, 1 to 4 waypoints behind the leader and 24 px or more from it, standing still, facing within 45 degrees of its next waypoint%s" %
          (who, len(events), '' if not bad else ' - NOT SO: %s' % bad[:3]))
    check(hold_moved < 1, "... and held still for the hold (it moved %.1f px in the first 8 frames)" % hold_moved)
    check(ll >= 3 and ll - sl in (0, 1), "... its lap count follows the leader's (leader on lap %d, it on lap %d)" % (ll, sl))
    print('      (nearest to the leader %.0f px, furthest %.0f; spots in the window %s ...)' % (min(e['far'] for e in events), max(e['far'] for e in events), [e['spot'] for e in events[:4]]))

# ---- 4. one player on the two-player tape = the game without the switch ----
SCRIPT = [(0, 'Q', 1), (60, 'P', 1), (75, 'P', 0), (140, 'O', 1), (150, 'O', 0), (260, 'Q', 0), (290, 'Q', 1), (300, 'SPACE', 1), (305, 'SPACE', 0),
          (420, 'O', 1), (452, 'O', 0), (600, 'A', 1), (620, 'A', 0), (700, 'P', 1), (716, 'P', 0), (900, 'O', 1), (930, 'O', 0)]
def scripted(tap, src, alone, frames=1100):
    g = Game2(tap, src); g.start(1, alone=alone)
    two = g.two() if 'two_p' in g.sym else 0
    path = []; other = []
    for f in range(frames):
        for (at, k, down) in SCRIPT:
            if at == f: g.key(k, bool(down))
        g.run(1); path.append(g.car(0)); other.append(g.car(1))
    g.close(); return two, path, other
for alone in (True, False):
    two, pa, oa = scripted(TAP2, SRC2, alone); _, pb, ob = scripted(TAP1, SRC1, alone)
    same = sum(1 for a, b in zip(pa, pb) if a == b)
    first = next((i for i, (a, b) in enumerate(zip(pa, pb)) if a != b), None)
    far = max(math.hypot(a[0] - b[0], a[1] - b[1]) for a, b in zip(pa, pb))
    check(two == 0 and same == len(pa), "one player, %s: a scripted drive's car is where it is on the tape without the switch, all %d TV frames%s" %
          ('alone' if alone else 'with the computer cars', len(pa), '' if same == len(pa) else ' - NOT SO: %d the same, first different at frame %s, furthest apart %.1f px' % (same, first, far)))
    if not alone:
        check(oa[-1] != oa[0] and oa == ob, "... and the second car is the computer's, where it is on that tape too%s" % ('' if oa == ob else ' - NOT SO (first different at frame %s)' % next(i for i, (a, b) in enumerate(zip(oa, ob)) if a != b)))
print('%d pass, %d fail' % (PASS, FAIL))
sys.exit(1 if FAIL else 0)
