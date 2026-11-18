#!/usr/bin/env python3
"""THE DRIVER CARDS -> THE GAME'S NUMBERS (17 Nov 2026). Reads tools/driver_cards.txt (Grant's ratings out of 10 for each
car's acceleration, speed and grip) and writes src/cards.asm, which the CARDS=1 build uses (tools/build_cards.sh).
To change a car: change its rating in tools/driver_cards.txt and build again. Nothing else need be touched.
To change what a rating is WORTH (every car at once): THE SCALE just below.
  python3 tools/make_cards.py           writes src/cards.asm and prints the scale and each car's numbers
  python3 tools/make_cards.py table     only prints them (nothing is written)

THE SCALE. A rating of 5 for speed and acceleration is the car as it has always been (1.75 px a TV frame, push 64).
  SPEED  SPEED_K[s]: so many 64ths of the plain push more or less at speed, and the top speed is 7 pushes:
         448 + 7 x SPEED_K[s] in 256ths of a pixel a TV frame. (Why 7: every TV frame a car gains its push and then loses
         an eighth.) A point above 5 is worth 3.1% of the top speed; a point below it only 1.6% (a little more for the
         last), so that a slow car is not left a lap behind - Grant gave two of them speed 2.
  ACCEL  each point is ACCEL_STEP 64ths of the plain push more or less, while the car is under four fifths of its top speed
  GRIP   TYRES[g]: what the tyres of YOUR car will hold, in 256ths of a pixel a frame of sideways speed - gripping, while
         you hold Q, while it is sliding, and both (16, 8, 8, 5 was the car as it was: about a rating of 7 to 8 now).
         SLIDE_AT[g]: for a COMPUTER car, the speed (256 = 1 px a frame) above which it slides when it steers, and which
         its driver brakes down to for a corner (plus the driver's own margin - AI_x_SLIP in src/ai_tune.asm).
  ARMOUR (only the ARMOUR=1 build uses it - src/armour.asm, tools/build_armour.sh; a card without "armour N" gets 5)
         every car has six pieces of armour. ARMOUR_PIECE[r]: the points of damage ONE PIECE takes before it is lost. A
         bump does both cars the same damage - by how fast they were closing: a FIRM BUMP (closing at a pixel a TV
         frame, the usual knock in the pack) is 10 points, a RAM at two pixels a frame 18, a rub 3 or 4; the tank's
         shell is 16 and the clown's wheel 12 (those numbers: src/armour_tune.asm). The scale is flatter at the bottom
         than at the top, as the speed scale is: at 14 a piece for a rating of 2 the dragster limped within 20 seconds
         of every race (five-race reports, tests/rt_armour.py); at 26 she limps late in about half of them.
"""
import os, re, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
# ---- THE SCALE (the only numbers to tune; the ratings are Grant's) ----
#        rating:  1   2   3   4   5   6   7   8   9  10
SPEED_K  = [None, -6, -4, -3, -2,  0,  2,  4,  6,  8, 10]   # the SPEED push, 64ths more or less than the plain push: each 1 is 1.6% of the top speed
ACCEL_STEP = 5          # 64ths of the push a point of acceleration: 5 is 7.8% a point
#        what YOUR car's tyres hold at each rating: gripping, while you hold Q, while sliding, both (16, 8, 8, 5 was the car as it was)
TYRES    = [None, (6, 3, 3, 2), (7, 4, 3, 2), (9, 4, 4, 3), (10, 5, 5, 3), (12, 6, 5, 4), (13, 7, 6, 4), (15, 7, 7, 5), (17, 9, 8, 5), (19, 10, 9, 6), (21, 11, 10, 7)]
SLIDE_AT = [None, 210, 240, 270, 300, 330, 360, 390, 420, 450, 480]
#        ARMOUR: the damage one of a car's six pieces takes (a firm bump is 10 - FIRM_BUMP, for the table only)
ARMOUR_PIECE = [None, 22, 26, 30, 34, 38, 46, 55, 65, 77, 92]
FIRM_BUMP = 10
# ---- GAME_SPEED (Grant, 18 Nov 2026: "the game plays too fast, I want it slower and smoother"): ONE number for the whole
#      game's speed, in percent of today's (GAME_SPEED=60 bash tools/build_armour.sh ...; 100, the default, is the game as
#      it was, byte for byte). Every car's top speed and push (so its acceleration), your car's tyres (so it slides the
#      same way, only slower), and the computer cars' corner speeds (where they slide and what they brake down to, the
#      driver's margin included) are all multiplied by it - so each car keeps its place against the others. The rest
#      that goes with speed (the computer cars' slide steps, the bounce in a bump, the skid's hiss, the engine's note)
#      is GAME_SPEED in src/options.asm, written by build.sh. Grass, NOS and the limp are shares of the push already.
GAME_SPEED = int(os.environ.get('GAME_SPEED', '100'))
def gs(v): return (v * GAME_SPEED + 50) // 100           # a speed at GAME_SPEED, rounded
# ---- who drives what in the race today (the others are on the choose screen only) ----
PLAYER = 'MAX'
CPU = [('FRANK', 'C', 'CYAN'), ('SPIKE', 'G', 'GREEN'), ('BRUNO', 'P', 'PINK'), ('JANE', 'W', 'WHITE')]

def read_cards(path=None):
    cards = []; name = None
    for line in open(path or os.path.join(ROOT, 'tools', 'driver_cards.txt')):
        m = re.match(r'==\s*(\w+)\s*/\s*(.+?)\s*==', line)
        if m: name = m.group(1).upper(); car = m.group(2); continue
        m = re.match(r'acceleration\s+(\d+),\s*speed\s+(\d+),\s*grip\s+(\d+)(?:,\s*armour\s+(\d+))?', line)
        if m and name:
            a, s, g = (int(v) for v in m.groups()[:3]); r = int(m.group(4) or 5)       # (a card with no armour rating: 5)
            for what, v in (('acceleration', a), ('speed', s), ('grip', g), ('armour', r)):
                if not 1 <= v <= 10: raise SystemExit('driver_cards.txt: %s has %s %d - ratings are 1 to 10' % (name, what, v))
            cards.append(dict(name=name, car=car, a=a, s=s, g=g, r=r, weapon='None yet.')); name = None; continue
        m = re.match(r'weapon:\s*(.*\S)', line)        # (the line after the ratings, as the driver cards page exports it; a card without one: "None yet.")
        if m and cards: cards[-1]['weapon'] = m.group(1)
    return cards
def top(s): return 448 + 7 * SPEED_K[s]
def k_speed(s): return SPEED_K[s]
def k_accel(a): return ACCEL_STEP * (a - 5)
def tyres(g): return TYRES[max(1, min(10, g))]
def numbers(c):
    """one car's game numbers from its card"""
    n = dict(c); n['top'] = gs(top(c['s'])); n['ks'] = gs(64 + k_speed(c['s'])) - 64; n['ka'] = gs(64 + k_accel(c['a'])) - 64; n['slide'] = gs(SLIDE_AT[c['g']])
    # a computer car has the ACCEL push up to four fifths of its top speed - or, if that push alone would never get it
    # there (7 pushes is all a push can hold), up to 85% of what it can hold; from there the SPEED push takes over
    n['vsw'] = min(n['top'] * 4 // 5, 7 * (64 + n['ka']) * 85 // 100)
    # YOUR car's sums have one push and a top speed that holds it: the push must at least be what that top speed needs
    n['push'] = max(64 + n['ka'], -(-n['top'] // 7))
    n['tyres'] = gs_tyres(c['g'])
    return n
def gs_tyres(g): return tuple(max(1, gs(v)) for v in tyres(g))   # your tyres at GAME_SPEED (never less than 1)
def frames_to_speed(a, s=5, want=358):
    """TV frames from rest to 1.4 px a frame (four fifths of the old top speed), by the game's own sums"""
    ka, t = k_accel(a), top(s); vsw = min(t * 4 // 5, 7 * (64 + ka) * 85 // 100); v = 0; n = 0
    while v < want and n < 200:
        v = (v + (64 + ka if v < vsw else 64 + k_speed(s))) * 7 / 8; n += 1
    return n
def table(cards):
    out = ['THE SCALE (tools/make_cards.py): what a rating is worth. A TV frame is a fiftieth of a second; 5 for speed and',
           'acceleration is the car as it always was; "tyres hold" 16 and "slides above" 1.00 were the cars as they were.',
           'rating   SPEED: top speed    ACCELERATION: push, and TV frames    GRIP, your car:   GRIP, a computer car: it slides (and',
           '         px a TV frame       from rest to 1.4 px a frame          the tyres hold    brakes for a corner) above ... px a frame']
    for r in range(1, 11):
        out.append('  %2d         %.2f                 %3d      %2d                         %2d                 %.2f' % (r, top(r) / 256, 64 + k_accel(r), frames_to_speed(r), TYRES[r][0], SLIDE_AT[r] / 256))
    out.append('ARMOUR (the ARMOUR=1 build): every car has 6 pieces; what ONE piece takes, and so how many knocks the car takes in all')
    out.append('rating   a piece takes   firm bumps a piece   firm bumps for all six   rams (twice as fast)   shells   wheel hits')
    for r in range(1, 11):
        p = ARMOUR_PIECE[r]
        out.append('  %2d         %2d               %4.1f                 %3d                  %3d              %2d        %2d' % (
            r, p, p / FIRM_BUMP, -(-6 * p // FIRM_BUMP), -(-6 * p // 18), -(-6 * p // 16), -(-6 * p // 12)))
    out.append('THE CARS')
    for c in cards:
        n = numbers(c)
        out.append('  %-6s %-10s acceleration %d, speed %d, grip %d, armour %d -> top speed %.2f px a frame, push %d, tyres %s, slides above %.2f, a piece of armour takes %d' % (
            c['name'], c['car'], c['a'], c['s'], c['g'], c['r'], n['top'] / 256, 64 + n['ka'], ','.join(str(v) for v in n['tyres']), n['slide'] / 256, ARMOUR_PIECE[c['r']]) + ('' if c['weapon'].lower().startswith('none') else '; weapon: ' + c['weapon']))
    return '\n'.join(out)
def asm(cards):
    by = {c['name']: numbers(c) for c in cards}
    for who in [PLAYER] + [c[0] for c in CPU]:
        if who not in by: raise SystemExit('driver_cards.txt has no card for ' + who)
    L = ['; GENERATED by tools/make_cards.py from tools/driver_cards.txt - do not edit by hand',
         '; THE DRIVER CARDS as the game\'s numbers (CARDS=1). To change a car, change its rating in tools/driver_cards.txt and',
         '; build again; to change what a rating is worth, the scale at the top of tools/make_cards.py.']
    L += ['; ' + l for l in table(cards).splitlines()]
    p = by[PLAYER]
    if GAME_SPEED != 100:
        L += ['; GAME_SPEED %d: every speed below is %d%% of the scale above (top speeds, pushes, your tyres, the corner speeds)' % (GAME_SPEED, GAME_SPEED)]
    L += ['; ---- your car (%s): its top speed, its push, and its tyres at each level of grip you buy (a level = a point of grip) ----' % PLAYER,
          'CD_TOP  equ %d' % p['top'], 'CD_PUSH equ %d' % p['push']]
    for lv in range(1, 6):
        t = gs_tyres(p['g'] + lv - 1)
        L += ['CD_L%d_%s equ %d' % (lv, k, v) for k, v in zip('GQSB', t)]
    L += ['; ---- every driver\'s card, as numbers (for the choose screen to come: nothing is stored for these) ----']
    for c in cards:
        n = numbers(c)
        L += ['CD_%s_A equ %d' % (c['name'], c['a']), 'CD_%s_S equ %d' % (c['name'], c['s']), 'CD_%s_G equ %d' % (c['name'], c['g']), 'CD_%s_R equ %d' % (c['name'], c['r'])]
    L += ['; ---- ARMOUR (the ARMOUR=1 build, src/armour.asm): the damage one piece of armour takes - your car, then the computer cars in the order of their kinds ----']
    L += ['CD_ARM_%d equ %d      ; %s, armour %d' % (i, ARMOUR_PIECE[by[who]['r']], who, by[who]['r']) for i, who in enumerate([PLAYER] + [c[0] for c in CPU])]
    L += ['; ---- the computer cars, in the order of their kinds: where it slides (a word), where it brakes to for a corner,',
          ';      where its ACCEL push gives way to its SPEED push (both / 4), its ACCEL push and its SPEED push (64ths more or less than the plain 64),',
          ';      1 while it is braking (the game writes it), and a byte to make the row 8 ----',
          'cd_tab:']
    for who, letter, colour in CPU:
        n = by[who]
        for what, k in (('acceleration', n['ka']), ('speed', n['ks'])):
            if not -60 <= k <= 60: raise SystemExit('%s: the scale gives a %s push the game cannot multiply (%d: keep it within 60 of the plain push)' % (who, what, k))
        L.append('        dw %d' % n['slide'])
        brake = '%d+AI_%s_SLIP' % (n['slide'] // 4, letter) if GAME_SPEED == 100 else '((%d+AI_%s_SLIP)*%d+50)/100' % (SLIDE_AT[by[who]['g']] // 4, letter, GAME_SPEED)
        L.append('        db %s, %d, %d, %d, 0, 0      ; %s: %s (%s) - acceleration %d, speed %d, grip %d' % (
            brake, n['vsw'] // 4, n['ka'] & 255, n['ks'] & 255, colour, who, n['car'], n['a'], n['s'], n['g']))
    return '\n'.join(L) + '\n'
if __name__ == '__main__':
    cards = read_cards()
    print(table(cards))
    if 'table' not in sys.argv[1:]:
        out = os.path.join(os.environ.get('CARDS_OUT', os.path.join(ROOT, 'src')), 'cards.asm')
        open(out, 'w').write(asm(cards))
        print('wrote', os.path.relpath(out, ROOT))
