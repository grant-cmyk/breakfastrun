"""When each car crosses the start line in a 60-second race in the pack (your car by autopilot): how long the computer
cars' laps are on a tape. Usage: python3 tests/rt_laps.py <tape name in build/> <its src folder>
SECS=150 for a longer race (tracks 2 and 3 are longer); ALONE=1: the computer cars stay on the grid - your laps alone."""
import sys, os
from rt_lib import *
name = sys.argv[1]; src = sys.argv[2]
ALONE = os.environ.get('ALONE') == '1'; SECS = int(os.environ.get('SECS', '60'))
g = Game(name, src); g.to_grid(); g.go(alone=ALONE)
S = g.sym; last = [1] * 5; t = [[] for _ in range(5)]
for f in range(SECS * 50):
    g.steer(); g.run(1)
    if f % 5 == 0:
        for i in range(5):
            l = g.mem(S['cars'] + i * S['c_size'] + 25, 1)[0]
            if l != last[i]: t[i].append(f / 50); last[i] = l
print(name, 'alone,' if ALONE else 'in the pack,', 'line crossings, seconds after the green light (you first, then the four computer cars):', t, '- pictures:', g.w16(S['renders']))
g.close()
