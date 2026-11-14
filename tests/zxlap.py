"""An autopilot lap in zxdev (Grant's own emulator, the retro plugin's zx-toolkit skill), profiled
instruction by instruction: where every T-state of a lap goes, by routine (the nearest label at or
below each instruction - cars_init, data and tables excluded by name), and how many TV frames each
picture took. More detail than profile_ticks.py (which splits a picture into its stages).
Usage: python3 tests/zxlap.py [tape] [sym]      ZXDEV=path to zxdev (default: ../zx-emulator/zxdev)
       add LIST=routine to list that routine's instructions, heaviest first"""
import os, sys, json, math, subprocess, re
from collections import defaultdict, Counter
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
TAP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'build', 'racer.tap')
SYMF = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'build', 'racer.sym')
ZXDEV = os.environ.get('ZXDEV', os.path.join(ROOT, '..', 'zx-emulator', 'zxdev'))
SYM = {}
for line in open(SYMF):
    p = line.split()
    if len(p) >= 3 and p[1] == 'EQU': SYM[p[0].lower()] = int(p[2].rstrip('H'), 16)
wps = [tuple(int(v) for v in l.split('dw')[1].split(',')) for l in open(os.path.join(ROOT, 'src', 'waypoints.asm')).read().split('waypoints:')[1].splitlines() if 'dw' in l]
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
while w16(SYM['renders']) == 0: rpc('run', frames=5)
key('Q', True)
while mem(SYM['race_on'], 1)[0] == 0: rpc('run', frames=1)
rpc('profile', on=True)
# the tables kept in the back buffer's bottom rows must come through a lap untouched (the taller
# window once drew map tiles over them: "the road shape has broken", Grant, 14 Nov 2026)
BUF = 0xC000; TABLES = {'messages (BUFA)': 0x1080, 'constants (BUFD)': 0x1380, 'messages (BUFE)': 0x1480,
                        'letters (BUFF)': 0x1580, 'messages (BUFG)': 0x1680, 'messages (BUFH)': 0x1780}
tables0 = {n: mem(BUF + a, 122) for n, a in TABLES.items()}   # (122 of 128: each strip's last 6 bytes take the interrupt's pushes)
CARS = SYM['cars']
x0 = w16(CARS + 1); wp = 0
while wps[wp][0] < x0 + 30: wp += 1
start_wp, laps, fr = wp, 0, 0
r_last = w16(SYM['renders']); f_last = 0; frames = Counter(); slow = Counter()
while laps < 1 and fr < 1500:
    c = mem(CARS, 11)
    x, y, ang = c[1] + 256 * c[2] + 8, c[4] + 256 * c[5] + 8, c[10]
    tx, ty = wps[wp]
    if math.hypot(tx - x, ty - y) < 28:
        wp = (wp + 1) % len(wps); laps += wp == start_wp
    diff = (math.degrees(math.atan2(tx - x, -(ty - y))) % 360 - ang * 360 / 64 + 540) % 360 - 180
    key('Q', abs(diff) < 70); key('O', diff < -8); key('P', diff > 8)
    rpc('run', frames=1); fr += 1
    r = w16(SYM['renders'])
    if r != r_last:
        if f_last:
            frames[fr - f_last] += 1
            cs = mem(CARS, SYM['c_size'] * 5); cx, cy = w16(SYM['camx']), w16(SYM['camy'])
            vis = sum(1 for i in range(5) if -16 < cs[i * SYM['c_size'] + 1] + 256 * cs[i * SYM['c_size'] + 2] - cx < 176 and -16 < cs[i * SYM['c_size'] + 4] + 256 * cs[i * SYM['c_size'] + 5] - cy < 120)
            slow[(fr - f_last, vis, (r - 1) & 3)] += 1
        r_last, f_last = r, fr
broken = [n for n, a in TABLES.items() if mem(BUF + a, 122) != tables0[n]]
rep = rpc('profile_report', top=20000)
rpc('quit') if False else z.kill()
labels = sorted((a, n) for n, a in SYM.items() if 0x5F00 <= a < 0xFFF0)
import bisect
addrs = [a for a, _ in labels]
def owner(a):
    if a < 0x4000: return 'ROM'
    if 0xE800 <= a < SYM.get('topmem', 0xFAD0): return 'copier (generated)'
    i = bisect.bisect_right(addrs, a) - 1
    return labels[i][1] if i >= 0 else '?'
# group the small labels under the routine they belong to: a label counts as a routine's
# start if it is in GROUPS; everything else goes to the nearest group start below it
GROUPS = ['main', 'tick', 'read_keys', 'physics', 'ai_drive', 'bump_all', 'bump', 'o_check', 'oc_quick', 'oc_try', 'race_progress',
          'hud_update', 'camera', 'cloth_fill', 'draw_tiles', 'draw_car', 'snd_picture', 'snd_wait', 'isr', 'you_grip',
          'tower_update', 'map_update', 'strip_tick', 'strip_triggers', 'bar_tick', 'print_big', 'print_at', 'gap_draw', 'st_text',
          'surface', 'rnd', 'abs_hl', 'scr_addr', 'buf_addr', 'cf_init', 'mul8s', 'sq_mul', 'lap_and_inc', 'tower_row', 'bubble',
          'glyph', 'wave_tick', 'nos_take', 'time_fmt', 'set_attrs', 'clear_cells', 'fin_key', 'map_dot', 'map_off', 'cp_hook',
          'flash', 'start_lights', 'inv_draw'] + [n for n in SYM if re.match(r'(tile_|td_|cf_l|cf_s|cf_m|cfw_|bp_pair|gt_|dt_)', n)]
gstarts = sorted((SYM[n], n) for n in set(GROUPS) if n in SYM)
gaddr = [a for a, _ in gstarts]
def group(a):
    if a < 0x4000: return 'ROM'
    if 0xE800 <= a < SYM.get('topmem', 0xFAD0): return 'copier (generated)'
    i = bisect.bisect_right(gaddr, a) - 1
    return gstarts[i][1] if i >= 0 else '?'
tot = defaultdict(int); fine = defaultdict(int)
for e in rep['top']:
    tot[group(e['addr'])] += e['t_states']; fine[owner(e['addr'])] += e['t_states']
pics = sum(frames.values()) or 1
total = rep['total_t_states']
print('zxdev lap: %d TV frames, %d pictures, %.0f T a picture all told (3 frames = 209,664)' % (fr, pics, total / pics))
print('TV frames per picture:', dict(sorted(frames.items())))
print('PASS the tables in the buffer\'s bottom rows are untouched after the lap' if not broken else 'FAIL tables overwritten during the lap: %s' % ', '.join(broken))
if os.environ.get('SLOW'):
    print('pictures by (cars in view, HUD slot): at 3 frames / at 4 or more')
    for vis in range(6):
        print('  %d cars: ' % vis + '   '.join('slot %d: %3d / %2d' % (sl, slow[(3, vis, sl)], sum(v for (f, v_, s_), v in slow.items() if f > 3 and v_ == vis and s_ == sl)) for sl in range(4)))
big = defaultdict(int)
for n, v in tot.items(): big[re.sub(r'^(tile_|td_|gt_|dt_).*', 'draw_tiles (generated)', re.sub(r'^(cf_|cfw_).*', 'cloth_fill (parts)', n))] += v
for n, v in sorted(big.items(), key=lambda kv: -kv[1])[:32]:
    print('%-28s %7d T a picture  %4.1f%%' % (n, v // pics, 100 * v / total))
if os.environ.get('FINE'):
    for n, v in sorted(fine.items(), key=lambda kv: -kv[1])[:int(os.environ['FINE'])]: print('  %-24s %04X %7d T a picture' % (n, SYM.get(n, 0), v // pics))
L = os.environ.get('LIST')
if L:
    print('--- %s, by label' % L)
    for n, v in sorted(fine.items(), key=lambda kv: -kv[1]):
        if group(SYM[n]) == L if n in SYM else False: print('  %-24s %7d T a picture' % (n, v // pics))
    print('--- %s, heaviest instructions' % L)
    k = 0
    for e in rep['top']:
        if group(e['addr']) == L:
            print('  %04X %-18s %6d T a picture, %5.1f times' % (e['addr'], owner(e['addr']), e['t_states'] // pics, e['count'] / pics)); k += 1
            if k > 40: break
