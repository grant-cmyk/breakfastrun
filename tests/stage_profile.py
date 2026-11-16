"""Where the time goes, a picture: an autopilot drive in zxdev with its profiler on (T-states by instruction
address), added up by routine from the tape's .sym. Three drives:
  SCEN=start  alone (the computer cars stay on the grid), the first seconds down the start straight
  SCEN=mid    alone, mid-lap (from the 12th waypoint on)
  SCEN=pack   with the computer cars, from the lights
Prints T-states a picture (everything but the waiting), pictures a second, and the routines that cost most.
Usage: python3 tests/stage_profile.py [tape] [sym] [src dir]      SECS=8 (how long is timed)"""
import os, sys, json, math, subprocess, bisect
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
TAP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'build', 'racer.tap')
SYMF = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'build', 'racer.sym')
SRC = sys.argv[3] if len(sys.argv) > 3 else os.path.join(ROOT, 'src')
SCEN = os.environ.get('SCEN', 'pack'); SECS = float(os.environ.get('SECS', '8'))
ZXDEV = '/home/user/zx-emulator/zxdev'
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
rpc('press', keys='1', frames=10, after=5)
while w16(SYM['renders']) == 0: rpc('run', frames=5)
key('Q', True)
while mem(SYM['race_on'], 1)[0] == 0: rpc('run', frames=1)
if SCEN != 'pack':
    for i in range(1, 5): rpc('write', addr=SYM['cars'] + i * SYM['c_size'] + 19, value=0)
CARS = SYM['cars']; wp = mem(CARS, 14)[13]
def drive(frames=None, until_wp=None):
    global wp
    f = 0
    while (frames is None or f < frames) and (until_wp is None or wp != until_wp) and f < 3000:
        c = mem(CARS, 14)
        x, y, ang = c[1] + 256 * c[2] + 8, c[4] + 256 * c[5] + 8, c[10]
        tx, ty = wps[wp]
        if math.hypot(tx - x, ty - y) < 28: wp = (wp + 1) % len(wps)
        diff = (math.degrees(math.atan2(tx - x, -(ty - y))) % 360 - ang * 360 / 64 + 540) % 360 - 180
        key('Q', abs(diff) < 70); key('O', diff < -8); key('P', diff > 8)
        rpc('run', frames=1); f += 1
if SCEN == 'mid': drive(until_wp=(wp + 12) % len(wps))
if SCEN == 'pack': drive(frames=50)                      # (the pack is under way)
r0 = w16(SYM['renders']); rpc('profile', on=True)
N = int(SECS * 50); drive(frames=N)
r1 = w16(SYM['renders']); rep = rpc('profile_report', top=100000)
z.kill()
pics = r1 - r0
names = sorted((a, n) for n, a in SYM.items() if a >= 0x5B00)
addrs = [a for a, _ in names]
WAIT = ('snd_wait', 'main', 'main_go', 'have_dt', 'wait_show')      # waiting for the TV frame, and the engine note played meanwhile
tot = {}
for e in rep['top']:
    a = e['addr']
    if a < 0x4000: n = '(ROM: the interrupt)'
    else:
        i = bisect.bisect_right(addrs, a) - 1; n = names[i][1] if i >= 0 else '?'
    tot[n] = tot.get(n, 0) + e['t_states']
GROUPS = [('cloth_fill', 'cloth'), ('cloth_pats', 'cloth'), ('cf_', 'cloth'), ('tdraw', 'tiles'), ('t1_', 'tiles'), ('td_', 'tiles'), ('dt_', 'tiles'), ('draw_tiles', 'tiles'),
          ('dc_', 'cars drawn'), ('draw_car', 'cars drawn'), ('copy_', 'screen copy'), ('cp_', 'screen copy'), ('copier', 'screen copy'),
          ('rt_', 'racetrack'), ('gr_', 'racetrack')]
grp = {}
all_t = rep['total_t_states']
for n, t in tot.items():
    g = next((gname for pre, gname in GROUPS if n.startswith(pre)), None)
    if 0xE800 <= SYM.get(n, 0) < 0xFFC3 and 'copier' not in n: g = g or 'screen copy'
    if g: grp[g] = grp.get(g, 0) + t
wait = sum(t for n, t in tot.items() if n in WAIT or n.startswith('snd_w') or n.startswith('sw_'))
print('%s %s: %d TV frames, %d pictures = %.2f pictures a second (%.2f TV frames a picture)' % (os.path.basename(TAP), SCEN, N, pics, pics * 50.0 / N, N / max(pics, 1)))
print('  T-states a picture: %d in all; %d of it waiting for the TV (with the engine note); so %d of work' % (all_t // pics, wait // pics, (all_t - wait) // pics))
print('  by part:', ', '.join('%s %d' % (g, t // pics) for g, t in sorted(grp.items(), key=lambda kv: -kv[1])))
if os.environ.get('DUMP'):                                # DUMP=file: every label's T a picture, in address order
    with open(os.environ['DUMP'], 'w') as f:
        for a, n in names:
            if tot.get(n): f.write('%04X %-16s %7d\n' % (a, n, tot[n] // pics))
        f.write('     %-16s %7d\n' % ('(ROM: the interrupt)', tot.get('(ROM: the interrupt)', 0) // pics))
print('  by routine:', ', '.join('%s %d' % (n, t // pics) for n, t in sorted(tot.items(), key=lambda kv: -kv[1])[:int(os.environ.get('TOP', '22'))]))
