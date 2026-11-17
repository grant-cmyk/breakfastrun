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
g.key('0', True); g.key('6', True); g.run(10); g.key('6', False); g.run(30); g.key('0', False)
d0, d1 = g.car(0), g.car(1)
check(d1[:2] != b1[:2] and (b1[2] - d1[2]) % 64 in range(1, 32) and d0[2] == c0[2] and math.hypot(d0[0] - c0[0], d0[1] - c0[1]) < 3,
      "0 and 6 move player 2's car and turn it left; player 1's only rolls (%s -> %s; %s -> %s)" % (b1, d1, c0, d0))
e1 = g.car(1); g.key('7', True); g.run(10); g.key('7', False)
check((g.car(1)[2] - e1[2]) % 64 in range(1, 32), "7 turns player 2's car right")
g.run(20); g.key('5', True); g.run(10); k0, k1 = g.rec(0)[11], g.rec(1)[11]; g.key('5', False)
check(k1 == 8 and k0 == 0, "5 is player 2's brake (their car's buttons read %d, player 1's %d)" % (k1, k0))
S = g.sym
g.poke(S['inv'], [1, 0, 0]); g.poke(S['p2_inv'], [1])
g.key('8', True); g.run(10); g.key('8', False); g.run(2)
check(g.mem(S['p2_inv'], 1)[0] == 0 and g.mem(S['inv'], 3) == bytes([1, 0, 0]), "8 fires player 2's NOS canister, not player 1's")
g.run(60); g.poke(S['p2_inv'], [1])
g.key('SPACE', True); g.run(10); g.key('SPACE', False); g.run(2)
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
# (The game reads the keys and moves the cars in a burst at the start of each picture - as many TV frames' worth as the last
# picture took - so WHEN a key is seen, and how far a computer car has got, depend on how long the pictures take; and the
# tape with the switch spends a few more T-states a picture testing "two players?". To compare the game's RULES and not its
# speed, both tapes are stopped at the same instruction every picture (dt_ok, where the burst's length is set), the length
# is made 5 TV frames, the keys are changed there, and the cars are read there. Both start from the same state at the green
# light: the cars as they stood on the grid, the counters at 0.)
SCRIPT = [(0, 'Q', 1), (12, 'P', 1), (15, 'P', 0), (28, 'O', 1), (30, 'O', 0), (52, 'Q', 0), (58, 'Q', 1), (60, 'SPACE', 1), (62, 'SPACE', 0),
          (84, 'O', 1), (90, 'O', 0), (120, 'A', 1), (124, 'A', 0), (140, 'P', 1), (143, 'P', 0), (180, 'O', 1), (186, 'O', 0)]   # (in pictures)
def scripted(tap, src, alone, pictures=230):
    g = Game2(tap, src); S = g.sym
    g.to_grid(key='1')
    grid = g.mem(S['cars'], 5 * S['c_size'])
    g.go(alone=False); g.key('Q', False)
    two = g.two() if 'two_p' in S else 0
    def picture(): g.rpc('run', until_pc=S['dt_ok'], max_frames=40); g.rpc('set', a=5)
    picture()
    g.poke(S['cars'], grid)
    if alone:
        for i in range(1, 5): g.rpc('write', addr=S['cars'] + i * S['c_size'] + 19, value=0)
    g.poke(S['yg_vf'], [0] * (S['yg_tang'] + 1 - S['yg_vf']))
    for v in ('ticks', 'renders', 'race_time', 'seed'): g.poke(S[v], [1, 0])
    path = []; other = []
    for n in range(pictures):
        for (at, k, down) in SCRIPT:
            if at == n: g.key(k, bool(down))
        picture(); path.append(g.car(0)); other.append(g.car(1))
    g.close(); return two, path, other
for alone in (True, False):
    two, pa, oa = scripted(TAP2, SRC2, alone); _, pb, ob = scripted(TAP1, SRC1, alone)
    same = sum(1 for a, b in zip(pa, pb) if a == b)
    first = next((i for i, (a, b) in enumerate(zip(pa, pb)) if a != b), None)
    far = max(math.hypot(a[0] - b[0], a[1] - b[1]) for a, b in zip(pa, pb))
    check(two == 0 and same == len(pa), "one player, %s: a scripted drive's car is where it is on the tape without the switch, all %d pictures%s" %
          ('alone' if alone else 'with the computer cars', len(pa), '' if same == len(pa) else ' - NOT SO: %d the same, first different at frame %s, furthest apart %.1f px' % (same, first, far)))
    if not alone:
        check(oa[-1] != oa[0] and oa == ob, "... and the second car is the computer's, where it is on that tape too%s" % ('' if oa == ob else ' - NOT SO (first different at frame %s)' % next(i for i, (a, b) in enumerate(zip(oa, ob)) if a != b)))
print('%d pass, %d fail' % (PASS, FAIL))
sys.exit(1 if FAIL else 0)
