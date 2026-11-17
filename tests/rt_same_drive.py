"""Do two tapes play the SAME GAME? For changes that are meant to be exact (quicker, nothing else): the same scripted drive
on both, and after every picture all five cars' whole records (place, speed, heading, waypoint, lap, buttons...) and your
car's grip sums must be the same, byte for byte.
How (as tests/two_player_test.py's last check): the game moves the cars in a burst at the start of each picture - as many
TV frames' worth as the last picture took - so two tapes of different speed would not get the same bursts. Both are
stopped at the same instruction every picture (dt_ok, where the burst's length is set) and given the same length there:
3, 4, 5, 6, 8, 4, 1, 5 ... in turn, so that every length is tried. The keys change at set pictures.
RANDOM NUMBERS: the crash noise takes random numbers for as long as it waits for the TV, so how many it takes depends on
how quick the picture was - and the computer cars' lines and mistakes come from the same run of numbers. That is not a
difference in the rules, so the run of numbers is started afresh, the same on both tapes, before every picture's moving.
Usage: python3 tests/rt_same_drive.py <tape A> <its build folder> <tape B> <its build folder>   (names in build/)
       PICTURES=300 (how long); the drive is run twice: alone, and with the computer cars."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from twop_lib import Game2
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A, AD, B, BD = sys.argv[1:5]
PICTURES = int(os.environ.get('PICTURES', '300'))
BURSTS = (3, 4, 5, 6, 8, 4, 1, 5, 4, 2, 7, 4)
# (picture, key, down): accelerate, steer both ways, brake, the NOS, onto the grass and back
SCRIPT = [(0, 'Q', 1), (14, 'P', 1), (20, 'P', 0), (30, 'O', 1), (38, 'O', 0), (50, 'P', 1), (58, 'P', 0), (70, 'SPACE', 1), (72, 'SPACE', 0),
          (90, 'O', 1), (110, 'O', 0), (120, 'Q', 0), (124, 'A', 1), (132, 'A', 0), (132, 'Q', 1), (150, 'P', 1), (175, 'P', 0),
          (200, 'O', 1), (206, 'O', 0), (230, 'P', 1), (236, 'P', 0), (250, 'Q', 0), (262, 'Q', 1), (270, 'O', 1), (290, 'O', 0)]
def scripted(tap, folder, alone):
    g = Game2(tap, os.path.join(ROOT, 'build', folder, 'src')); S = g.sym
    g.to_grid(key='1')
    grid = g.mem(S['cars'], 5 * S['c_size'])
    g.go(alone=False); g.key('Q', False)
    n = [0]
    def picture():
        g.rpc('run', until_pc=S['dt_ok'], max_frames=40); g.rpc('set', a=BURSTS[n[0] % len(BURSTS)]); n[0] += 1
    picture()
    g.poke(S['cars'], grid)
    if alone:
        for i in range(1, 5): g.rpc('write', addr=S['cars'] + i * S['c_size'] + 19, value=0)
    g.poke(S['yg_vf'], [0] * (S['yg_tang'] + 1 - S['yg_vf']))
    for v in ('ticks', 'renders', 'race_time', 'seed'): g.poke(S[v], [1, 0])
    out = []
    for p in range(PICTURES):
        for (at, k, down) in SCRIPT:
            if at == p: g.key(k, bool(down))
        picture()
        g.poke(S['seed'], [(p * 157 + 1) & 255, (p * 31 + 7) & 255])   # (see RANDOM NUMBERS above)
        out.append(g.mem(S['cars'], 5 * S['c_size']) + g.mem(S['yg_vf'], S['yg_tang'] + 1 - S['yg_vf']))
    g.close(); return out
bad = 0
for alone in (True, False):
    a = scripted(A, AD, alone); b = scripted(B, BD, alone)
    same = sum(1 for x, y in zip(a, b) if x == y)
    first = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), None)
    ok = same == len(a) and a[-1] != a[0]
    bad += not ok
    print('%s  %s: all five cars and the grip sums the same on %s and %s at %d of %d pictures%s' % ('PASS' if ok else 'FAIL', 'alone' if alone else 'with the computer cars', A, B, same, len(a),
          '' if first is None else ' - first different at picture %d, byte %d' % (first, next(i for i, (x, y) in enumerate(zip(a[first], b[first])) if x != y))))
sys.exit(1 if bad else 0)
