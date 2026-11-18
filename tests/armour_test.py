"""ARMOUR AND WEAPONS (ARMOUR=1; Grant, 17 Nov 2026) - the test, in the emulator, on the real tape.
Usage: python3 tests/armour_test.py [tape name in build/, default racer_armour_grip1]     (build it: bash tools/build_armour.sh)
  1 a bump takes armour from BOTH cars - the same damage, so pieces go in proportion to their ratings; a harder ram
    does more; the grass does none
  2 the bar on the screen is each car's armour, row by row, as the race order changes; a piece just lost flashes, then
    stays a dot
  3 the tank's shell: fired at a car in line it hits, spins it where it is and costs it armour; fired at nothing it ends
    at its range; fired across the road it ends on the grass
  4 the clown's wheels: they come out for a car alongside, hit it, and do not hit a car out of reach
  5 a car with no armour limps - half its top speed - and still finishes the race
  6 with ARMOUR off the driver cards' tapes are byte for byte the tapes they were (their md5s, as recorded here on
    17 Nov 2026 - if a rating in tools/driver_cards.txt is changed on purpose they change too: record the new ones)
The cars are set down by hand on the long straight on the right (x 509, running up the screen) and held still (no
throttle, no steering) so that each thing happens alone."""
import sys, os, math, hashlib
from rt_lib import *
TAPE = sys.argv[1] if len(sys.argv) > 1 else 'racer_armour_grip1'
SRC = os.path.join(ROOT, 'build', TAPE, 'src')
CARDS_MD5 = {'racer_cards': '40d10f129d10d6ccee8a946af540e2c7', 'racer_cards_grip1': 'ed5512fe7fbc6afc5db7d3839b0ec70b'}   # (18 Nov 2026, later: the grid's [ boxes moved into the square behind each car - every race-track tape's map changed; re-recorded. Were 4e5e8094..., 8d2a8659...) (18 Nov 2026: the corner arrow's option C, your car's grass slowdown halved, you last on the grid and MAX's speed 4 changed every race-track tape; re-recorded then. Was 2c244abf..., e18993a3...)
YOU, FRANK, SPIKE, BRUNO, JANE = range(5)
passed = failed = 0
def check(ok, msg):
    global passed, failed
    print(('PASS  ' if ok else 'FAIL  ') + msg)
    if ok: passed += 1
    else: failed += 1
class Scene:
    """a race just begun, every car held still and out of the way (in a row on the grass in the middle) until it is wanted"""
    def __init__(self):
        g = self.g = Game(TAPE, SRC); g.to_grid(); g.go(alone=True); g.key('Q', False); g.run(2)
        self.S = g.sym; self.CS = self.S['c_size']
        for i in range(5): self.hold(i, 200 + 30 * i, 250, 0)
        self.quiet()
    def hold(self, i, x, y, ang, vx=0, vy=0):
        g, a = self.g, self.S['cars'] + i * self.CS
        g.put(x, y, ang, i); g.poke(a + 6, [vx & 255, (vx >> 8) & 255, vy & 255, (vy >> 8) & 255])
        if i: g.poke(a + 11, [0]); g.poke(a + 16, [255, 1]); g.poke(a + 19, [0]); g.poke(a + 23, [0])   # a "late turn-in" that never ends: no steering; no throttle
    def quiet(self, shells=True, wheels=True):
        """the weapons' cool-downs: 0 (ready) or a long time (kept out of this part of the test)"""
        self.g.poke(self.S['sh_cool'], [0 if shells else 250]); self.g.poke(self.S['wh_cool'], [0 if wheels else 250])
    def row(self, i): return list(self.g.mem(self.S['arm_tab'] + 8 * i, 8))      # what a piece takes, pieces, damage in the piece, flash, spin, safe, wheel-safe, spins
    def damage(self, i): r = self.row(i); return (6 - r[1]) * r[0] + r[2]
    def picture(self, n=1):
        for _ in range(n):
            self.g.next_picture(); self.g.rpc('run', until_pc=self.S['snd_picture'], max_frames=40)
            for i in range(1, 5): self.g.poke(self.S['cars'] + i * self.CS + 16, [255])
    def bars(self):
        """the bars as the screen has them: for each place, the six pieces from the foot up - 'X' there, '.' a dot, '?' anything else"""
        scr = self.g.mem(0x4000, 6144); out = []
        for p in range(5):
            y0 = (self.S['tower_y'] + 2 * p) * 8; s = ''
            for k in range(6):
                v = [scr[((y & 0xC0) << 5) | ((y & 7) << 8) | ((y & 0x38) << 2) | 31] & 0x0E for y in (y0 + 12 - 2 * k, y0 + 13 - 2 * k)]
                s += 'X' if v == [0x0E, 0x0E] else '.' if v == [0, 0x04] else '?'
            out.append(s)
        return out
    def want_bar(self, i):
        r = self.row(i); n = r[1] + (1 if r[3] & 2 else 0)
        return 'X' * n + '.' * (6 - n)
    def close(self): self.g.close()
X = 501                                                   # a car's x on the right-hand straight (its middle 509)

def bumps():
    sc = Scene(); g, S = sc.g, sc.S; sc.quiet(False, False)
    per = [sc.row(i)[0] for i in range(5)]
    def ram(a, b, speed):
        """car a driven up the straight into the back of car b at so many 256ths of a pixel a TV frame; the damage each took"""
        g.poke(S['arm_tab'] + 8 * a + 5, [0]); g.poke(S['arm_tab'] + 8 * b + 5, [0])
        d0 = sc.damage(a), sc.damage(b)
        sc.hold(b, X, 250, 0); sc.hold(a, X, 250 + 18, 0, vy=-speed); sc.picture(2)
        return sc.damage(a) - d0[0], sc.damage(b) - d0[1]
    soft = ram(BRUNO, JANE, 300); hard = ram(BRUNO, JANE, 600)
    check(soft[0] == soft[1] > 0 and hard[0] == hard[1] > soft[0], 'a bump costs both cars the same damage, and a harder ram costs more (the tank into the dragster at 1.2 px a frame: %d each; at 2.3: %d each)' % (soft[0], hard[0]))
    n = 0
    while sc.row(BRUNO)[1] == 6 and n < 40: ram(BRUNO, JANE, 600); n += 1
    dj, db = sc.damage(JANE), sc.damage(BRUNO); lj, lb = 6 - sc.row(JANE)[1], 6 - sc.row(BRUNO)[1]
    check(dj == db or lj == 6, 'after %d more rams the tank and the dragster have taken the same damage (%d and %d)' % (n, db, dj))
    check(lb == 1 and lj == min(6, db // per[JANE]) and lj > lb, 'in proportion to their ratings: the dragster (a piece takes %d) has lost %d pieces when the tank (a piece takes %d) loses its first' % (per[JANE], lj, per[BRUNO]))
    sc.hold(BRUNO, 200 + 30 * BRUNO, 250, 0); sc.hold(JANE, 200 + 30 * JANE, 250, 0)    # (the tank and the dragster back to their places first: left on the
    d = ram(YOU, FRANK, 500)                    #  straight, your car could meet them too - 18 Nov 2026, seen when the grid's [ boxes moved)
    check(d[0] == d[1] > 0 and sc.row(YOU)[0] == per[FRANK], 'your car too: you ram Frank, whose rating is yours, and each takes %d' % d[0])
    for i in range(5): sc.hold(i, 200 + 30 * i, 250, 0)
    g.poke(S['arm_tab'] + 1, [3, 0]); sc.picture(2)
    mug = g.mem(S['dmg'], 1)[0]
    check(mug == g.mem(S['arm_mug'] + 3, 1)[0] and 0 < mug < 8, 'the mug is your armour: with 3 pieces of 6 it stands at %d of 8 (the game\'s own table)' % mug)
    before = sc.row(YOU)[:3]; g.put(300, 300, 16, 0); g.key('Q', True)
    for _ in range(150): g.run(1)
    g.key('Q', False)
    check(sc.row(YOU)[:3] == before and g.w16(S['bumps']) > 0, 'driving over the grass costs no armour (150 TV frames of it: %s before and after)' % before[1:3])
    sc.close()

def bar():
    sc = Scene(); g, S = sc.g, sc.S; sc.quiet(False, False)
    n = 0
    while [v & 7 for v in g.mem(S['shown_order'], 5)] != list(g.mem(S['order'], 5)) and n < 100: sc.picture(); n += 1    # (the rows are drawn for the race one at a time after the lights)
    for i, n in enumerate([6, 5, 3, 1, 0]): g.poke(S['arm_tab'] + 8 * i + 1, [n, 0, 1])       # (flash 1: the bar is drawn afresh)
    sc.picture(3)
    order = list(g.mem(S['order'], 5)); got = sc.bars(); want = [sc.want_bar(c) for c in order]
    check(got == want and '?' not in ''.join(got), 'the bars on the screen are the cars\' armour, 6 5 3 1 0 pieces set by hand: %s for the cars in the order %s' % (' '.join(got), order))
    scr = g.mem(0x4000, 6144); gap = True
    for p in range(5):                                    # (nothing but the bar in the row's last 5 pixels, and a clear pixel left of the bar)
        for y in range((S['tower_y'] + 2 * p) * 8, (S['tower_y'] + 2 * p) * 8 + 16):
            if scr[((y & 0xC0) << 5) | ((y & 7) << 8) | ((y & 0x38) << 2) | 31] & 0x11: gap = False
    check(gap, 'the bar is 3 pixels wide with a clear pixel either side of it, in all five rows')
    # a piece is lost: it flashes, then it is a dot
    p = order.index(JANE); g.poke(S['arm_tab'] + 8 * JANE + 1, [4, sc.row(JANE)[0] - 1, 1]); sc.picture(2)
    g.poke(S['arm_tab'] + 8 * JANE + 5, [0])
    sc.hold(JANE, X, 250, 0); sc.hold(BRUNO, X, 268, 0, vy=-600)
    seen = []; n = 0
    while n < 40:
        sc.picture(); n += 1; r = sc.row(JANE)
        p = list(g.mem(S['order'], 5)).index(JANE)      # (her row now: holding the two cars can change the order - 18 Nov 2026,
                                                          # with you last on the grid it does)
        if r[1] == 3: seen.append((r[3], sc.bars()[p][3]))
        if r[1] == 3 and r[3] == 0 and len([s for s in seen if s[0] == 0]) >= 4: break
    fl = [s[1] for s in seen if s[0] > 0]; after = [s[1] for s in seen if s[0] == 0]
    check(len(fl) >= 10 and 'X' in fl and '.' in fl and '?' not in fl, 'the dragster loses a piece in a ram: on the bar it FLASHES for %d pictures (%s)' % (len(fl), ''.join(fl)))
    check(len(after) >= 4 and set(after) == {'.'} and sc.bars()[p] == 'XXX...', '... then it stops, and the piece is a single dot (%s)' % sc.bars()[p])
    sc.close()
    # in a race: the rows follow the order
    g = Game(TAPE, SRC); g.to_grid(); g.go(); S = g.sym; import rt_ace
    steer = rt_ace.ace(g, 104, 30); sc = Scene.__new__(Scene); sc.g, sc.S, sc.CS = g, S, S['c_size']
    for f in range(100): steer(); g.run(1)
    for i, n in enumerate([6, 5, 4, 3, 2]): g.poke(S['arm_tab'] + 8 * i + 1, [n, 0, 1])
    orders = set(); bad = looked = 0
    for f in range(40 * 50):
        if f < 200: g.key('Q', False)                     # (you hang back at first, so that places change)
        else: steer()
        g.run(1)
        if f % 6 == 0 and f >= 30:                        # (not before the pieces set by hand above have been drawn)
            g.rpc('run', until_pc=S['snd_picture'], max_frames=40)
            order = list(g.mem(S['order'], 5)); shown = [v & 7 for v in g.mem(S['shown_order'], 5)]; got = sc.bars()
            if shown == order:
                orders.add(tuple(order)); looked += 1
                if got != [sc.want_bar(c) for c in order]:
                    bad += 1
                    if os.environ.get('WHERE'): print('   wrong at TV frame %d: order %s, bars %s, wanted %s, rows %s' % (f, order, got, [sc.want_bar(c) for c in order], [sc.row(c)[1:4] for c in order]))
    check(bad == 0 and len(orders) >= 3 and looked > 100, 'in a race the bars follow the cars as the rows swap: %d pictures looked at, %d different orders, %d wrong' % (looked, len(orders), bad))
    g.close()

def shell():
    sc = Scene(); g, S = sc.g, sc.S; sc.quiet(True, False)
    sc.hold(BRUNO, X, 340, 0); sc.hold(FRANK, X, 280, 0); sc.hold(YOU, X - 70, 310, 0)      # (your car beside the road: the view is on it)
    d0 = sc.damage(FRANK); fired = shown = pics = 0; spun = []; n = 0
    while n < 40:
        sc.picture(); n += 1
        k = list(g.mem(S['sh_fired'], 2))
        if k[0] and not fired: fired = n
        if g.mem(S['sh_life'], 1)[0]:
            pics += 1; cx, cy = g.cam(); px, at = g.window()
            for wx, wy, _ in g.weapon_dots():
                wx -= cx; wy -= cy; wx = (wx & ~7) + min(wx & 7, 5); wy = (wy & ~7) + min(wy & 7, 5)
                if 0 <= wx < 190 and 0 <= wy < 150 and (px[wy:wy + 3, wx:wx + 3] != 0).all(): shown += 1
            if n > 1: g.shot(os.path.join(ROOT, 'build', 'armour_test_shell.png'))
        if k[1]: break
    check(0 < fired <= 5 and k == [1, 1], 'the tank fires at a car 60 pixels ahead in line within %d pictures of being free to, and the shell hits it (fired %d, hit %d)' % (fired, k[0], k[1]))
    check(pics >= 1 and shown == pics, 'the shell is on the screen, a dot 3 x 3, in every picture it flies (%d of %d)' % (shown, pics))
    r = sc.row(FRANK)
    check(sc.damage(FRANK) - d0 == S['shell_dmg'] and r[4] > 0 and r[7] == 1, 'the car it hits loses armour (%d damage) and begins to spin' % (sc.damage(FRANK) - d0))
    a0 = g.car(FRANK); angs = []; still = True; frames = r[4] and 0
    for f in range(60):
        g.run(1); c = g.mem(S['cars'] + FRANK * sc.CS, 11)
        if sc.row(FRANK)[4]: frames = f + 1
        angs.append(c[10]); still &= (c[1] + 256 * c[2], c[4] + 256 * c[5]) == a0[:2] and not any(c[6:10])
    check(still and len(set(angs)) >= 6 and angs[-1] == a0[2] and frames <= S['spin_t'], 'it spins WHERE IT IS: no speed, the same place, its heading through %d different values, and it ends facing as it began (%d TV frames)' % (len(set(angs)), frames))
    # your car too: no control while it spins
    sc.quiet(True, False); sc.hold(FRANK, 230, 250, 0); sc.hold(YOU, X, 280, 0); g.key('Q', True); g.key('P', True)
    g.poke(S['cars'] + 16, [0]); hit = 0; n = 0; moved = 0
    while n < 300 and not hit:
        g.put(X, 280, 0, 0); g.run(1); n += 1; hit = sc.row(YOU)[4]
    p0 = g.car(YOU)[:2]
    while sc.row(YOU)[4] > 1: g.run(1); moved = max(moved, math.hypot(g.car(YOU)[0] - p0[0], g.car(YOU)[1] - p0[1]))
    g.key('Q', False); g.key('P', False)
    check(hit > 0 and moved == 0, 'your car too: hit while you hold accelerate and steer, it spins and does not move until the spin is over')
    # at nothing: the range
    sc.quiet(True, False); sc.hold(YOU, 200, 250, 0); sc.hold(BRUNO, X, 340, 0); sc.hold(FRANK, X, 280, 0)
    k0 = list(g.mem(S['sh_fired'], 2)); n = 0
    while list(g.mem(S['sh_fired'], 1))[0] == k0[0] and n < 300: g.run(1); n += 1
    sc.hold(FRANK, 230, 250, 0); y0 = 340; ymin = y0
    while g.mem(S['sh_life'], 1)[0] and n < 600: g.run(1); n += 1; v = g.mem(S['sh_rec'], 6); ymin = min(ymin, v[4] + 256 * v[5])
    k = list(g.mem(S['sh_fired'], 2)); want = S['shell_life'] << (S['shell_shift'] - 2)
    check(k == [k0[0] + 1, k0[1]] and want - 8 <= y0 - ymin <= want, 'a shell fired at nothing (its target taken away) hits nobody and ends at its range: %d pixels (%d asked)' % (y0 - ymin, want))
    # across the road: the grass
    sc.quiet(True, False); sc.hold(BRUNO, X - 10, 300, 16); sc.hold(FRANK, X + 14, 300, 16)
    n = 0
    while list(g.mem(S['sh_fired'], 1))[0] == k[0] and n < 300: g.run(1); n += 1
    sc.hold(FRANK, 230, 250, 0); x0 = X - 10; xmax = x0
    while g.mem(S['sh_life'], 1)[0] and n < 600: g.run(1); n += 1; v = g.mem(S['sh_rec'], 6); xmax = max(xmax, v[1] + 256 * v[2])
    surf = g.mem(S['surface_map'], 9 * S['maph']); tx, ty = (xmax + 8) >> 3, (300 + 8) >> 3
    check(list(g.mem(S['sh_fired'], 2)) == [k[0] + 1, k[1]] and xmax - x0 < want - 16 and surf[ty * 9 + (tx >> 3)] & (0x80 >> (tx & 7)), 'a shell fired across the road ends on the grass, short of its range (after %d pixels)' % (xmax - x0))
    sc.close()

def wheels():
    sc = Scene(); g, S = sc.g, sc.S; sc.quiet(False, True)
    sc.hold(SPIKE, X, 300, 0); sc.hold(FRANK, X + 22, 300, 0); sc.hold(JANE, X - 40, 300, 0); sc.hold(BRUNO, X, 264, 0); sc.hold(YOU, X - 60, 345, 0)
    d0 = sc.damage(FRANK); out = shown = pics = 0; n = 0
    while n < 30:
        sc.picture(); n += 1
        if g.mem(S['wh_out'], 1)[0]:
            if not out: out = n
            pics += 1; cx, cy = g.cam(); px, at = g.window(); ok = 0
            for wx, wy, _ in g.weapon_dots():
                wx -= cx; wy -= cy; wx = (wx & ~7) + min(wx & 7, 5); wy = (wy & ~7) + min(wy & 7, 5)
                ok += 0 <= wx < 190 and 0 <= wy < 150 and bool((px[wy:wy + 3, wx:wx + 3] != 0).all())
            shown += ok == 4
        elif out: break
    k = list(g.mem(S['sh_fired'], 4))
    check(0 < out <= 5 and k[2] == 1 and pics >= S['wh_time'] - 1, 'the clown\'s wheels come out for a car 22 pixels to his side within %d pictures, and stay out %d pictures' % (out, pics))
    check(shown == pics, 'they are on the screen - two dots out to each side of him - in every one of those pictures (%d of %d)' % (shown, pics))
    r = sc.row(FRANK)
    check(k[3] == 1 and sc.damage(FRANK) - d0 == S['wheel_dmg'] and r[7] == 1, 'the car alongside is hit once: it spins and loses armour (%d damage)' % (sc.damage(FRANK) - d0))
    check(sc.row(JANE)[7] == 0 and sc.row(BRUNO)[7] == 0 and sc.damage(JANE) == 0 and sc.damage(BRUNO) == 0, 'a car 40 pixels to his other side, and one 36 pixels ahead of him, are not touched')
    sc.quiet(False, True); sc.hold(FRANK, X + 36, 300, 0); sc.picture(8)
    check(list(g.mem(S['sh_fired'], 4))[2] == 1, 'and for a car 36 pixels to his side - out of reach - the wheels do not come out')
    sc.close()

def limp():
    import rt_ace
    g = Game(TAPE, SRC); g.to_grid(); g.go(); S = g.sym; CS = S['c_size']; steer = rt_ace.ace(g, 104, 30)
    s16 = lambda lo, hi: (lo + 256 * hi + 32768) % 65536 - 32768
    speed = lambda i: (lambda c: math.hypot(s16(c[6], c[7]), s16(c[8], c[9])) / 256)(g.mem(S['cars'] + i * CS, 10))
    full = [0.0] * 5
    for f in range(400):
        steer(); g.run(1)
        for i in (YOU, JANE): full[i] = max(full[i], speed(i))
    g.poke(S['arm_tab'] + 1, [0, 0, 1]); g.poke(S['arm_tab'] + 8 * JANE + 1, [0, 0, 1])
    for f in range(100): steer(); g.run(1)
    top = [[] for _ in range(5)]; f = 0; jwp = set()
    while g.mem(S['cars'] + 25, 1)[0] <= S['laps'] and f < 200 * 50:
        steer(); g.run(1); f += 1
        if g.mem(S['arm_tab'] + 1, 1)[0]: g.poke(S['arm_tab'] + 1, [0, 0])      # (the oil can would mend it)
        for i in (YOU, JANE): top[i].append(speed(i))
        jwp.add(g.mem(S['cars'] + JANE * CS + 13, 1)[0])
    done = g.mem(S['cars'] + 25, 1)[0] > S['laps']
    top = [sorted(t)[len(t) * 9 // 10] if t else 0 for t in top]       # (the speed it is under nine tenths of the time: a knock from a car behind can shove it faster for a moment)
    check(0.4 * full[YOU] < top[YOU] <= 0.56 * full[YOU], 'with no armour your car limps: nine tenths of the time it is under %.2f px a TV frame, where it did %.2f (half is asked)' % (top[YOU], full[YOU]))
    check(0.4 * full[JANE] < top[JANE] <= 0.60 * full[JANE] and len(jwp) > 10, 'and a computer car: the dragster under %.2f, where it did %.2f - and it keeps going round (%d waypoints passed)' % (top[JANE], full[JANE], len(jwp)))
    check(done, 'limping all the way from 10 seconds in, your car still finishes the race (%.0f seconds)' % ((f + 500) / 50))
    g.close()

def same_tapes():
    for name, md5 in CARDS_MD5.items():
        p = os.path.join(ROOT, 'build', name + '.tap')
        got = hashlib.md5(open(p, 'rb').read()).hexdigest() if os.path.exists(p) else 'not built'
        check(got == md5, 'with ARMOUR off, build/%s.tap is byte for byte the tape it was (md5 %s)' % (name, got))

if __name__ == '__main__':
    bumps(); bar(); shell(); wheels(); limp(); same_tapes()
    print('%d passed, %d failed' % (passed, failed))
    sys.exit(1 if failed else 0)
