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
  GRIP   HOLD[g]: what the tyres of YOUR car will hold, in 256ths of a pixel a frame of sideways speed (16 was the car as
         it was). While you hold Q, and while it is sliding, they hold half of that; both together, five sixteenths.
         SLIDE_AT[g]: for a COMPUTER car, the speed (256 = 1 px a frame) above which it slides when it steers, and which
         its driver brakes down to for a corner (plus the driver's own margin - AI_x_SLIP in src/ai_tune.asm).
"""
import os, re, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
# ---- THE SCALE (the only numbers to tune; the ratings are Grant's) ----
#        rating:  1   2   3   4   5   6   7   8   9  10
SPEED_K  = [None, -6, -4, -3, -2,  0,  2,  4,  6,  8, 10]   # the SPEED push, 64ths more or less than the plain push: each 1 is 1.6% of the top speed
ACCEL_STEP = 5          # 64ths of the push a point of acceleration: 5 is 7.8% a point
HOLD     = [None, 7,  8,  9, 10, 12, 13, 15, 17, 19, 21]
SLIDE_AT = [None, 210, 240, 270, 300, 330, 360, 390, 420, 450, 480]
# ---- who drives what in the race today (the others are on the choose screen only) ----
PLAYER = 'MAX'
CPU = [('FRANK', 'C', 'CYAN'), ('SPIKE', 'G', 'GREEN'), ('BRUNO', 'P', 'PINK'), ('JANE', 'W', 'WHITE')]

def read_cards(path=None):
    cards = []; name = None
    for line in open(path or os.path.join(ROOT, 'tools', 'driver_cards.txt')):
        m = re.match(r'==\s*(\w+)\s*/\s*(.+?)\s*==', line)
        if m: name = m.group(1).upper(); car = m.group(2); continue
        m = re.match(r'acceleration\s+(\d+),\s*speed\s+(\d+),\s*grip\s+(\d+)', line)
        if m and name:
            a, s, g = (int(v) for v in m.groups())
            for what, v in (('acceleration', a), ('speed', s), ('grip', g)):
                if not 1 <= v <= 10: raise SystemExit('driver_cards.txt: %s has %s %d - ratings are 1 to 10' % (name, what, v))
            cards.append(dict(name=name, car=car, a=a, s=s, g=g)); name = None
    return cards
def top(s): return 448 + 7 * SPEED_K[s]
def k_speed(s): return SPEED_K[s]
def k_accel(a): return ACCEL_STEP * (a - 5)
def tyres(g):
    g = max(1, min(10, g)); h = HOLD[g]
    return h, (h + 1) // 2, (h + 1) // 2, (h * 5 + 8) // 16
def numbers(c):
    """one car's game numbers from its card"""
    n = dict(c); n['top'] = top(c['s']); n['ks'] = k_speed(c['s']); n['ka'] = k_accel(c['a']); n['slide'] = SLIDE_AT[c['g']]
    # YOUR car's sums have one push and a top speed that holds it: the push must at least be what that top speed needs
    n['push'] = max(64 + n['ka'], -(-n['top'] // 7))
    n['tyres'] = tyres(c['g'])
    return n
def table(cards):
    out = ['THE SCALE (tools/make_cards.py): what a rating is worth',
           'rating   top speed, px a TV frame   push while getting up to speed   your tyres hold   a computer car slides above',
           '                                    (64 = the car as it was)         (16 = as it was)  (px a TV frame, when it steers)']
    for r in range(1, 11):
        out.append('  %2d           %.2f                        %3d                          %2d                %.2f' % (r, top(r) / 256, 64 + k_accel(r), HOLD[r], SLIDE_AT[r] / 256))
    out.append('THE CARS')
    for c in cards:
        n = numbers(c)
        out.append('  %-6s %-10s acceleration %d, speed %d, grip %d -> top speed %.2f px a frame (%d), push %d (your car: %d), tyres %s, slides above %.2f' % (
            c['name'], c['car'], c['a'], c['s'], c['g'], n['top'] / 256, n['top'], 64 + n['ka'], n['push'], ','.join(str(v) for v in n['tyres']), n['slide'] / 256))
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
    L += ['; ---- your car (%s): its top speed, its push, and its tyres at each level of grip you buy (a level = a point of grip) ----' % PLAYER,
          'CD_TOP  equ %d' % p['top'], 'CD_PUSH equ %d' % p['push']]
    for lv in range(1, 6):
        t = tyres(p['g'] + lv - 1)
        L += ['CD_L%d_%s equ %d' % (lv, k, v) for k, v in zip('GQSB', t)]
    L += ['; ---- every driver\'s card, as numbers (for the choose screen to come: nothing is stored for these) ----']
    for c in cards:
        n = numbers(c)
        L += ['CD_%s_A equ %d' % (c['name'], c['a']), 'CD_%s_S equ %d' % (c['name'], c['s']), 'CD_%s_G equ %d' % (c['name'], c['g'])]
    L += ['; ---- the computer cars, in the order of their kinds: where it slides (a word), where it brakes to for a corner,',
          ';      four fifths of its top speed (both / 4), its ACCEL push and its SPEED push (64ths more or less than the plain 64),',
          ';      1 while it is braking (the game writes it), and a byte to make the row 8 ----',
          'cd_tab:']
    for who, letter, colour in CPU:
        n = by[who]
        for what, k in (('acceleration', n['ka']), ('speed', n['ks'])):
            if not -60 <= k <= 60: raise SystemExit('%s: the scale gives a %s push the game cannot multiply (%d: keep it within 60 of the plain push)' % (who, what, k))
        L.append('        dw %d' % n['slide'])
        L.append('        db %d+AI_%s_SLIP, %d, %d, %d, 0, 0      ; %s: %s (%s) - acceleration %d, speed %d, grip %d' % (
            n['slide'] // 4, letter, n['top'] * 4 // 5 // 4, n['ka'] & 255, n['ks'] & 255, colour, who, n['car'], n['a'], n['s'], n['g']))
    return '\n'.join(L) + '\n'
if __name__ == '__main__':
    cards = read_cards()
    print(table(cards))
    if 'table' not in sys.argv[1:]:
        out = os.path.join(os.environ.get('CARDS_OUT', os.path.join(ROOT, 'src')), 'cards.asm')
        open(out, 'w').write(asm(cards))
        print('wrote', os.path.relpath(out, ROOT))
