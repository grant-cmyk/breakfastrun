"""RACE OR COMBAT (RACEMODE=1; Grant, 18 Nov 2026: "Now I need a game option - combat or race") - the test, in the emulator,
on the real tape. Usage: python3 tests/race_mode_test.py [tape name in build/, default racer_race70]
(build it: bash tools/build_race.sh; racer_race70_elastic too)
  1 THE TITLE: row 12 reads "M  MODE: RACE" to start with; M makes it COMBAT, M again RACE; the choice is the game played
    (rmode) - and it is REMEMBERED: a COMBAT race run to the flag, back to the title, the title still says COMBAT and the
    next race is COMBAT again
  2 RACE, THE CARS: all five cars drawn side by side at the same heading make the SAME picture, pixel for pixel, at each of
    the 16 headings (in COMBAT the same test finds five different cars - the test can tell); the race order's car pictures
    the same too
  3 RACE, A WHOLE RACE (the good-driver autopilot, every TV frame): no shell, no wheels out, nobody's armour ever less than
    whole, no car spun by a weapon - though the cars bump (the count goes up); the computer drivers do not steer at
    other cars (card_near returns at once)
  4 RACE, THE RACE ORDER: right of each car (columns 29-31) the GAP TO THE CAR AHEAD where COMBAT has its health blocks:
    those squares are in the row's own colour (not the blocks' black), the gap shown for each place is the gap to the car
    ahead worked out from the game's checkpoint times (as it was at most a few pictures before), there is writing in the
    squares when there is a gap and none in the leader's row
  6 RACE, EACH DRIVER ITS OWN (Grant, 19 Nov 2026: "the racers race too similarly ... maybe cars are slightly
    different"): once the lights are green each computer car's driving numbers (its style row: reach, line, ease, fuss;
    and its PACE, REACT, ERR) and its car's row (grip, ACCEL and SPEED pushes) are the ones ai_tune.asm gives that colour
    (the tape's own numbers, from its symbols), no two drivers and no two cars alike - and the cars only SLIGHTLY
    different: each push within 2 64ths of MAX's card on the straight (KS; about 4.6% of the top speed at 70%) and 6 on
    the way up (KA), the grip within 64-112 64ths of the card's (on the elastic tape the rubber band, kept in the row's
    eighth byte, taken off first)
  5 COMBAT: the health blocks are there (green on black, whole armour) and the code is as assembled (card_near, arm_bump,
    arm_tick, the cars' own pictures). The rest of COMBAT is tests/armour_test.py's (RT_MODE=combat on this tape)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rt_lib import *
import rt_ace
TAPE = sys.argv[1] if len(sys.argv) > 1 else 'racer_race70'
SRC = os.path.join(ROOT, 'build', TAPE, 'src')
TOWER_Y = 6
passed = failed = 0
def check(ok, msg):
    global passed, failed
    print(('PASS  ' if ok else 'FAIL  ') + msg)
    if ok: passed += 1
    else: failed += 1
def text(g, row, col, n):
    """the ROM letters on the screen at a character row: what they read"""
    font = g.mem(0x3D00, 768); scr = g.mem(0x4000, 6144); out = ''
    for c in range(col, col + n):
        cell = bytes(scr[((row & 0x18) << 8) | (l << 8) | ((row & 7) << 5) | c] for l in range(8))
        out += next((chr(32 + i) for i in range(96) if font[i * 8:i * 8 + 8] == cell), '?')
    return out
def to_title(g):
    n = 0
    while g.mem(0x5800 + 8 * 32 + 10, 1)[0] != 0x7A and n < 400: g.run(5); n += 1
    g.run(25)
def bits(g, x, y):
    """the 16 x 16 pixels (set or not) of the screen at a car's place in the world"""
    cx, cy = g.cam(); scr = g.mem(0x4000, 6144); out = []
    for r in range(16):
        yy = y - cy + 8 + r; row = 0
        for c in range(16):
            xx = x - cx + 8 + c
            b = scr[((yy & 0xC0) << 5) | ((yy & 7) << 8) | ((yy & 0x38) << 2) | (xx >> 3)]
            row = row * 2 + (1 if b & (0x80 >> (xx & 7)) else 0)
        out.append(row)
    return tuple(out)
INK = [2, 5, 6, 3, 7]                   # the cars' colours on the track: you red, then cyan, yellow, magenta, white
def same_pictures(g):
    """each car in turn set down at the same place on the start straight (300, 400), heading the same way, the others parked
    out of the way (the computer cars told not to steer), at each of the 16 headings: at how many headings the five cars
    make the same picture - the pixels of the car's own colour around that place, from their top-left"""
    S = g.sym; CS = S['c_size']; same = 0; tx, ty = 300, 400
    for h in range(16):
        pics = []
        for k in range(5):
            for j in range(5):
                if j != k: g.put(*((tx, ty - 34) if j == 0 else (40 + 30 * j, ty)), 16, i=j)
                if j: g.poke(S['cars'] + j * CS + 16, [0]); g.poke(S['cars'] + j * CS + 18, [255]); g.poke(S['cars'] + j * CS + 23, [0])
            g.put(tx, ty, h * 4, i=k)
            g.key('Q', False)
            r0 = g.w16(S['renders'])                  # (held at that heading, every TV frame: a computer car left alone
            while g.w16(S['renders']) < r0 + 4:       # turns for its waypoint) for four pictures
                g.poke(S['cars'] + k * CS + 10, [h * 4]); g.poke(S['cars'] + k * CS + 6, [0, 0, 0, 0]); g.run(1)
            px, at = g.window(); cx, cy = g.cam(); x, y = tx - cx, ty - cy
            pts = [(r, c) for r in range(max(0, y - 1), min(152, y + 17)) for c in range(max(0, x - 1), min(192, x + 17)) if px[r, c] == INK[k]]
            if not pts:
                if os.environ.get('WHERE'): print('   car %d not seen: at %s, view %s' % (k, g.car(k), (cx, cy)))
                pics.append(None); continue
            r0 = min(r for r, c in pts); c0 = min(c for r, c in pts)
            pics.append(frozenset((r - r0, c - c0) for r, c in pts))
        same += pics[0] is not None and all(p == pics[0] for p in pics)
        if os.environ.get('WHERE'): print('   heading %d: %s' % (h * 4, ['-' if p is None else (len(p), p == pics[0]) for p in pics]))
    return same
def race(g, each):
    """the good driver, a whole race, each(frame) every TV frame"""
    S = g.sym; steer = rt_ace.ace(g, 104, 30)
    for f in range(160 * 50):
        steer(); g.run(1); each(f)
        if g.mem(S['race_over'], 1)[0]: break
    return f

# ---- 1 the title ----
g = Game(TAPE, SRC); S = g.sym
to_title(g)
check(text(g, 12, 6, 15) == 'M  MODE: RACE  ' and g.mem(S['rmode'], 1)[0] == 1, 'the title: row 12 reads "%s" (RACE to start with), rmode %d' % (text(g, 12, 6, 15), g.mem(S['rmode'], 1)[0]))
g.rpc('press', keys='M', frames=6, after=10)
check(text(g, 12, 6, 15) == 'M  MODE: COMBAT' and g.mem(S['rmode'], 1)[0] == 0, 'M: "%s", rmode %d' % (text(g, 12, 6, 15), g.mem(S['rmode'], 1)[0]))
g.rpc('press', keys='M', frames=6, after=10)
check(text(g, 12, 6, 15) == 'M  MODE: RACE  ' and g.mem(S['rmode'], 1)[0] == 1, 'M again: "%s"' % text(g, 12, 6, 15))
g.rpc('press', keys='M', frames=6, after=10)          # COMBAT, and a race in it
g.to_grid(); g.go()
def combat_code(g):
    S = g.sym
    return (g.mem(S['card_near'], 1)[0], g.mem(S['arm_bump'], 1)[0], g.mem(S['arm_tick'], 1)[0], g.mem(S['dc_kmask'] + 1, 1)[0], g.mem(S['tw_kmask'] + 1, 1)[0])
check(combat_code(g) == (0xDD, 0xDD, 0xCD, 0xFF, 0xFF), 'COMBAT chosen on the title: the code as assembled (card_near %02X, arm_bump %02X, arm_tick %02X, picture masks %02X %02X)' % combat_code(g))
g.run(150)                                            # (the race order's rows drawn for the race)
blocks = [g.mem(0x5800 + (TOWER_Y + 2 * p) * 32 + 29, 3) for p in range(5)]
check(all(b[0] & 0x38 == 0 and b[0] & 7 == 4 for b in blocks), 'COMBAT: the health blocks - columns 29-31 black, green ink, in every row (%s)' % ' '.join(b.hex() for b in blocks))
f = race(g, lambda f: None)
check(g.mem(S['race_over'], 1)[0] != 0, 'COMBAT: the race run to the flag (%.0f s)' % (f / 50))
g.key('Q', False); g.key('O', False); g.key('P', False); g.run(100)
g.rpc('press', keys='X', frames=6, after=10)
to_title(g)
check(text(g, 12, 6, 15) == 'M  MODE: COMBAT' and g.mem(S['rmode'], 1)[0] == 0, 'back at the title after the race: still "%s"' % text(g, 12, 6, 15))
g.rpc('press', keys='1', frames=10, after=5)
n = 0
while g.mem(S['race_on'], 1)[0] == 0 and n < 2000: g.key('Q', True); g.run(1); n += 1
check(combat_code(g) == (0xDD, 0xDD, 0xCD, 0xFF, 0xFF), 'the next race: COMBAT again (card_near %02X, arm_bump %02X, arm_tick %02X, masks %02X %02X)' % combat_code(g))
g.close()

# ---- 2 the cars' pictures, RACE and COMBAT ----
os.environ['RT_MODE'] = 'combat'
g = Game(TAPE, SRC); g.to_grid(); g.go(alone=True)
nc = same_pictures(g); g.close()
os.environ['RT_MODE'] = 'race'
g = Game(TAPE, SRC); g.to_grid(); g.go(alone=True); S = g.sym
nr = same_pictures(g)
check(nr == 16 and nc < 4, 'the five cars at each of 16 headings: the same picture at %d of 16 in RACE (in COMBAT: %d - the test tells cars apart)' % (nr, nc))
rows = []
for p in range(5):
    r = TOWER_Y + 2 * p; scr = g.mem(0x4000, 6144)
    rows.append(tuple(scr[(((r + k // 8) & 0x18) << 8) | ((k & 7) << 8) | (((r + k // 8) & 7) << 5) | c] for k in range(16) for c in (27, 28)))
check(all(x == rows[0] for x in rows) and any(rows[0]), 'RACE: the race order\'s five car pictures (columns 27-28) the same')
g.close()

# ---- 3, 4 a whole RACE ----
g = Game(TAPE, SRC); g.to_grid(); g.go(); S = g.sym; CS = S['c_size']
check(combat_code(g)[:3] == (0xC9, 0xC9, 0xC9) and combat_code(g)[3:] == (0, 0), 'RACE: no line pulls, no armour lost, no weapons (card_near, arm_bump, arm_tick return at once), every car the racer (masks 0)')
Y = S
def sgn(v): return v - 256 if v > 127 else v
want_d = [[Y['ai_r%s_%s' % (c, k)] for k in ('reach', 'lmask', 'lhalf', 'ease', 'fuss')] + [Y['ai_r%s_pace' % c], Y['ai_r%s_react' % c] + Y['opt_react1'], Y['ai_r%s_err' % c]] for c in 'cymw']
have_d = [list(g.mem(S['ai_race'] + 5 * k, 5)) + list(g.mem(S['cars'] + (k + 1) * CS + S['c_pace'], 3)) for k in range(4)]
check(have_d == want_d and len(set(map(tuple, have_d))) == 4, 'RACE: each computer driver its own numbers, as ai_tune.asm gives them (reach, line, half, ease, fuss, pace, react, err): %s' % ' / '.join(','.join(map(str, d)) for d in have_d))
rows = [g.mem(S['cd_race'] + 8 * k, 8) for k in range(4)]
ks16 = lambda v: v - 65536 if v > 32767 else v
cdk = lambda n: ks16(S[n]) if S[n] > 32767 else S[n]
have_c = [(r[0] + 256 * r[1], sgn((r[4] - r[7]) & 255), sgn((r[5] - r[7]) & 255)) for r in rows]
want_c = [(S['cd_r_slide'] * S['ai_r%s_grip' % c] // 64, sgn((cdk('cd_r_ka') + ks16(S['ai_r%s_ka' % c])) & 255), sgn((cdk('cd_r_ks') + ks16(S['ai_r%s_ks' % c])) & 255)) for c in 'cymw']
small = all(abs(ks - sgn(cdk('cd_r_ks') & 255)) <= 2 and abs(ka - sgn(cdk('cd_r_ka') & 255)) <= 6 and 64 * S['cd_r_slide'] // 64 <= gr <= 112 * S['cd_r_slide'] // 64 for gr, ka, ks in have_c)
check(have_c == want_c and len(set(have_c)) == 4 and small, 'RACE: each computer car slightly different, as ai_tune.asm gives them (grip, ACCEL push, SPEED push; MAX\'s card %d, %d, %d): %s' % (S['cd_r_slide'], sgn(cdk('cd_r_ka') & 255), sgn(cdk('cd_r_ks') & 255), ' / '.join('%d,%d,%d' % c for c in have_c)))
bad = []; gapbad = []; inkbad = []; colbad = []; hist = []; seen_gap = [0]; last_r = [None]; wrongs = [set()]
def each(f):
    if g.mem(S['race_on'], 1)[0] and not g.mem(S['fin_count'], 1)[0]:     # the gap each place should show, every TV frame
        order = list(g.mem(S['order'], 5)); gaps = [g.w16(S['gaps'] + 2 * k) for k in range(5)]
        hist.append([0] + [max(0, gaps[order[p]] - gaps[order[p - 1]]) for p in range(1, 5)]); del hist[:-100]
    if f % 2: return
    sh = g.mem(S['sh_rec'], 11)[10]; wh = g.mem(S['wh_out'], 1)[0]; arm = g.mem(S['arm_tab'], 40)
    if sh or wh or any(arm[k * 8 + 1] != 6 for k in range(5)) or g.weapon_dots(): bad.append((f, sh, wh, [arm[k * 8 + 1] for k in range(5)]))
    r = g.w16(S['renders'])
    if r == last_r[0] or not g.mem(S['race_on'], 1)[0] or g.mem(S['fin_count'], 1)[0]: return
    last_r[0] = r
    if f < 600: return                                # (the first few seconds: the rows are still being drawn for the race)
    shown = [g.w16(S['shgap'] + 2 * p) for p in range(5)]; scr = g.mem(0x4000, 6912)
    prevwrong = set(wrongs[0]); nowwrong = wrongs[0] = set()
    for p in range(5):
        if all(h[p] != shown[p] for h in hist): gapbad.append((f, p, shown[p], sorted(set(h[p] for h in hist))))
        r0 = TOWER_Y + 2 * p
        ink = sum(scr[(((r0 + k // 8) & 0x18) << 8) | ((k & 7) << 8) | (((r0 + k // 8) & 7) << 5) | c] != 0 for k in range(16) for c in (29, 30, 31))
        if shown[p]: seen_gap[0] += 1
        wrong = (shown[p] != 0) != (ink != 0)
        if wrong and (p, shown[p]) in prevwrong: inkbad.append((f, p, shown[p], ink))     # (wrong at two pictures running: not one caught half drawn)
        if wrong: nowwrong.add((p, shown[p]))
        at = [scr[6144 + (r0 + k) * 32 + c] for k in (0, 1) for c in (26, 29, 30, 31)]
        if any(a != at[0] for a in at): colbad.append((f, p, at))
bumps0 = g.w16(S['bumps'])
f = race(g, each)
check(not bad, 'RACE, a whole race (%.0f s, every other TV frame): no shell, no wheels, every car\'s armour whole, nothing drawn for a weapon%s' % (f / 50, '' if not bad else ' - %d frames wrong, first %s' % (len(bad), bad[0])))
check(g.w16(S['bumps']) - bumps0 > 0, 'RACE: the cars did bump (%d bumps) - and lost nothing' % (g.w16(S['bumps']) - bumps0))
check(not gapbad and seen_gap[0] > 50, 'RACE: each place\'s gap shown is its gap to the car ahead (as at some TV frame in the last 100, about 16 pictures - each place\'s gap is brought up to date one picture in five, and not while rows of the order are being drawn again; gaps seen %d times)%s' % (seen_gap[0], '' if not gapbad else ' - %d wrong, first %s' % (len(gapbad), gapbad[0])))
check(not inkbad, 'RACE: writing in columns 29-31 when there is a gap, none when not (the leader)%s' % ('' if not inkbad else ' - %d wrong, first %s' % (len(inkbad), inkbad[0])))
check(not colbad, 'RACE: columns 29-31 in the row\'s own colour, as the place and the car (no health blocks)%s' % ('' if not colbad else ' - %d wrong, first %s' % (len(colbad), colbad[0])))
g.close()
print('%d passed, %d failed (%s)' % (passed, failed, TAPE))
sys.exit(1 if failed else 0)
