"""When each car crosses the start line in a 60-second race in the pack (your car by autopilot): how long the computer
cars' laps are on a tape. Usage: python3 tests/rt_laps.py <tape name in build/> <its src folder>"""
import sys
from rt_lib import *
name = sys.argv[1]; src = sys.argv[2]
g = Game(name, src); g.to_grid(); g.go()
S = g.sym; last = [1] * 5; t = [[] for _ in range(5)]
for f in range(3000):
    g.steer(); g.run(1)
    if f % 5 == 0:
        for i in range(5):
            l = g.mem(S['cars'] + i * S['c_size'] + 25, 1)[0]
            if l != last[i]: t[i].append(f / 50); last[i] = l
print(name, 'line crossings, seconds after the green light (you first, then the four computer cars):', t, '- pictures:', g.w16(S['renders']))
g.close()
