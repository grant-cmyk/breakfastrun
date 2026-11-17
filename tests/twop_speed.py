"""Pictures a second, one player and two (src/twoplayer.asm), the way tests/stage_profile.py measures them: three
8-second autopilot drives -
  start  alone (the computer cars stay on the grid), from the lights
  mid    alone, mid-lap (from the 12th waypoint on)
  pack   with the computer cars, from 1 second after the lights
With two players both cars are driven (player 2's autopilot lifts a little, so they are near but not on top of each other).
Usage: python3 tests/twop_speed.py <tape name in build/> <its build folder under build/> [players: 1, 2 or both]"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from twop_lib import Game2
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
TAP = sys.argv[1]; SRC = os.path.join(ROOT, 'build', sys.argv[2], 'src')
WHO = sys.argv[3] if len(sys.argv) > 3 else 'both'
SECS = 8
def measure(players, scen):
    g = Game2(TAP, SRC)
    if players == 2 and 'two_p' not in g.sym: g.close(); return None
    g.start(players, alone=(scen != 'pack'))
    g.lift[1] = 0.95
    two = players == 2
    if scen == 'mid':
        w = (g.wpn[0] + 12) % len(g.wps)
        while g.wpn[0] != w: g.step(p2=two)
    if scen == 'pack':
        for _ in range(50): g.step(p2=two)
    r0 = g.w16(g.sym['renders'])
    for _ in range(SECS * 50): g.step(p2=two)
    n = g.w16(g.sym['renders']) - r0
    g.close(); return n / SECS
free = None
for line in open(os.path.join(ROOT, 'build', TAP + '.sym')):
    p = line.split()
    if len(p) >= 3 and p[0].lower() == 'code_end': free = 0xC000 - int(p[2].rstrip('H'), 16)
for players in ((1, 2) if WHO == 'both' else (int(WHO),)):
    res = [measure(players, s) for s in ('start', 'mid', 'pack')]
    if res[0] is None: continue
    print('%-34s %d player%s  start %5.2f  mid-lap %5.2f  pack %5.2f  pictures a second   (%d bytes free in the program)' %
          (TAP, players, ' ' if players == 1 else 's', res[0], res[1], res[2], free))
