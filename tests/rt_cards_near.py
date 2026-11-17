"""The driver cards: DO BRUNO AND SPIKE GO LOOKING FOR THE OTHER CARS? (17 Nov 2026). Races in the pack (your car by the
corner-cutting autopilot), run twice from the same luck: as built, and with the two drivers' NEAR numbers set to 0 (they
mind their own business). Prints, for each: the bumps counted in a race (the game's own count: every picture two cars
touch), and for GREEN (Spike) and PINK (Bruno) the share of the race in which their line was pulled towards another car
(their aim moved further off the middle of the road than their own wandering ever puts it), and how often Spike was
seen in a lunge (looked at every 4th TV frame).
Usage: python3 tests/rt_cards_near.py <tape name in build/> <its src folder> [races, default 5] [ace=LOOK,LIFT]"""
import sys
from rt_lib import *
import rt_ace
def races(name, src, n, off, look, lift):
    bumps = []; pulled = [0, 0]; total = 0; lunges = 0
    for race in range(n):
        g = Game(name, src); g.to_grid(); S = g.sym; CS = S['c_size']
        g.poke(S['seed'], [(0x34 + 37 * race) & 255, 0x12 + race])
        if off: g.poke(S['cd_near'], [0] * 8)
        st = g.mem(S['ai_styles'], 20)
        g.go(); steer = rt_ace.ace(g, look, lift)
        for f in range(80 * 50):
            steer(); g.run(1)
            if f % 4 == 0:
                c = g.mem(S['cars'], CS * 5); total += 1
                lunges += c[2 * CS + 16] > 0 and c[2 * CS + 17] >= 4
                for j, k in enumerate((2, 3)):
                    half = st[5 * (k - 1) + 2]; ox, oy = (c[k * CS + 14] + 128) % 256 - 128, (c[k * CS + 15] + 128) % 256 - 128
                    pulled[j] += max(abs(ox), abs(oy)) > half
                if all(c[i * CS + 25] > S['laps'] for i in range(5)): break
        bumps.append(g.w16(S['bumps'])); g.close()
    return bumps, [100.0 * p / total for p in pulled], lunges / n
if __name__ == '__main__':
    name, src = sys.argv[1], sys.argv[2]; a = sys.argv[3:]
    n = ([int(v) for v in a if v.isdigit()] or [5])[0]
    look, lift = ([[int(x) for x in v[4:].split(',')] for v in a if v.startswith('ace=')] or [[104, 30]])[0]
    for off in (False, True):
        b, p, l = races(name, src, n, off, look, lift)
        print('%s, %s: bumps a race %s (mean %.0f); line pulled towards another car - GREEN %.0f%% of the race, PINK %.0f%%; GREEN lunging at a car in %.0f of a race\'s pictures' % (name, 'NEAR set to 0' if off else 'as built', b, sum(b) / len(b), p[0], p[1], l))
