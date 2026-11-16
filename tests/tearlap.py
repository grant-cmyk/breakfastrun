"""An autopilot lap in zxdev with the TEAR REPORT on: how many TV frames each picture took, how long the
screen copy took (from copy_to_screen to copy_done, in T-states, with the screen memory's contention), and
which cells of the window were shown torn or late (zxdev: tear on=true, tear_report).
Usage: python3 tests/tearlap.py [tape] [sym] [src dir]     ALONE=1: the computer cars stay on the grid
       HEAT=file.png: the tear heat map      LAPS=n"""
import os, sys, json, math, subprocess
from collections import Counter
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
TAP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'build', 'racer.tap')
SYMF = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'build', 'racer.sym')
SRC = sys.argv[3] if len(sys.argv) > 3 else os.path.join(ROOT, 'src')
ZXDEV = os.environ.get('ZXDEV', os.path.join(ROOT, '..', 'zx-emulator', 'zxdev'))
if not os.path.exists(ZXDEV): ZXDEV = '/home/user/zx-emulator/zxdev'
SYM = {}
for line in open(SYMF):
    p = line.split()
    if len(p) >= 3 and p[1] == 'EQU': SYM[p[0].lower()] = int(p[2].rstrip('H'), 16)
wps = [tuple(int(v) for v in l.split('dw')[1].split(',')) for l in open(os.path.join(SRC, 'waypoints.asm')).read().split('waypoints:')[1].splitlines() if 'dw' in l]
z = subprocess.Popen([ZXDEV, 'serve', '--stdio'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
def rpc(method, **params):
    z.stdin.write(json.dumps({'id': 1, 'method': method, 'params': params}) + '\n'); z.stdin.flush()
    r = json.loads(z.stdout.readline())
    if 'error' in r: raise SystemExit('%s: %s' % (method, r['error']))
    return r['result']
def mem(addr, n):
    r = rpc('read', addr=addr, len=n)
    return bytes.fromhex(r['hex']) if 'hex' in r else bytes(r['bytes'])
w16 = lambda a: int.from_bytes(mem(a, 2), 'little')
held = set()
def key(k, down):
    if down and k not in held: rpc('key_down', keys=k); held.add(k)
    if not down and k in held: rpc('key_up', keys=k); held.discard(k)
rpc('load', path=TAP); rpc('random', pin=True)
n = 0
while mem(0x5800 + 8 * 32 + 10, 1)[0] != 0x7A and n < 400: rpc('run', frames=5); n += 1
rpc('run', frames=25)
if 'jin_on' in SYM: rpc('write', addr=SYM['jin_on'], value=0xFF)
rpc('press', keys=os.environ.get('TKEY', '1'), frames=10, after=5)
while w16(SYM['renders']) == 0: rpc('run', frames=5)
key('Q', True)
while mem(SYM['race_on'], 1)[0] == 0: rpc('run', frames=1)
if os.environ.get('ALONE'):
    for i in range(1, 5): rpc('write', addr=SYM['cars'] + i * SYM['c_size'] + 19, value=0)
CARS = SYM['cars']
x0 = w16(CARS + 1); wp = SYM.get('ws', 0) if os.environ.get('WS') else 0
c = mem(CARS, 14); wp = c[13]                    # the waypoint the game says your car is heading for
start_wp, laps, fr = wp, 0, 0
# the copy's own time: T-states between two breakpoints, a few pictures
ct = []
try:
    for _ in range(6):
        rpc('run', until_pc=SYM['copy_to_screen'], max_frames=30); t0 = rpc('state')
        rpc('run', until_pc=SYM['copy_done'], max_frames=30); t1 = rpc('state')
        ct.append('%d (from %d T after the interrupt)' % (t1['t'] - t0['t'], t0['frame_t']))
        key('Q', True)
except SystemExit as e:
    ct = ['n/a: %s' % e]
rpc('access', on=True); rpc('tear', on=True, reset=True)
r_last = w16(SYM['renders']); f_last = 0; frames = Counter(); LAPS = int(os.environ.get('LAPS', '1'))
while laps < LAPS and fr < 1800 * LAPS:
    c = mem(CARS, 14)
    x, y, ang = c[1] + 256 * c[2] + 8, c[4] + 256 * c[5] + 8, c[10]
    tx, ty = wps[wp]
    if math.hypot(tx - x, ty - y) < 28:
        wp = (wp + 1) % len(wps); laps += wp == start_wp
    diff = (math.degrees(math.atan2(tx - x, -(ty - y))) % 360 - ang * 360 / 64 + 540) % 360 - 180
    key('Q', abs(diff) < 70); key('O', diff < -8); key('P', diff > 8)
    rpc('run', frames=1); fr += 1
    r = w16(SYM['renders'])
    if r != r_last:
        if f_last: frames[fr - f_last] += 1
        r_last, f_last = r, fr
args = dict(top=12)
if os.environ.get('HEAT'): args['path'] = os.environ['HEAT']
rep = rpc('tear_report', **args)
z.kill()
pics = sum(frames.values()) or 1
avg = (sum(k * v for k, v in frames.items()) / pics) or 1
print('lap%s: %d TV frames, %d pictures; TV frames a picture %s; average %.2f = %.1f pictures a second' % (' ALONE' if os.environ.get('ALONE') else '', fr, pics, dict(sorted(frames.items())), avg, 50 / avg))
print('screen copy, T-states a picture:', ct)
keep = {k: v for k, v in rep.items() if k not in ('worst', 'routines', 'worst_frames')}
print('tear report:', json.dumps(keep)[:600])
rows = Counter();
for w in rep.get('worst', []):
    print('  cell col %2d row %2d: torn %d late %d clean %d seam %d  by %s' % (w.get('col'), w.get('row'), w.get('torn', 0), w.get('late', 0), w.get('clean', 0), w.get('seam', 0), w.get('last_written_by')))
print('  torn cell-frames by routine:', json.dumps(rep.get('routines'))[:400])
