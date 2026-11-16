"""How long TRK_SET takes to put a track on its working places (the tape with several tracks, tools/make_multi.py),
and that going to a track and back leaves the first track's memory exactly as loaded.
Usage: python3 tests/unpack_time.py [tape] [sym]"""
import os, sys, json, subprocess
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
TAP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'build', 'racer_2tracks.tap')
SYMF = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'build', 'racer_2tracks.sym')
ZXDEV = os.environ.get('ZXDEV', '/home/user/zx-emulator/zxdev')
SYM = {}
for line in open(SYMF):
    p = line.split()
    if len(p) >= 3 and p[1] == 'EQU': SYM[p[0].lower()] = int(p[2].rstrip('H'), 16)
z = subprocess.Popen([ZXDEV, 'serve', '--stdio'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
def rpc(method, **params):
    z.stdin.write(json.dumps({'id': 1, 'method': method, 'params': params}) + '\n'); z.stdin.flush()
    r = json.loads(z.stdout.readline())
    if 'error' in r: raise SystemExit('%s: %s' % (method, r['error']))
    return r['result']
def mem(addr, n):
    out = b''
    while n:
        k = min(n, 4096); r = rpc('read', addr=addr, len=k)
        out += bytes.fromhex(r['hex']) if 'hex' in r else bytes(r['bytes']); addr += k; n -= k
    return out
rpc('load', path=TAP); n = 0
while mem(0x5800 + 8 * 32 + 10, 1)[0] != 0x7A and n < 400: rpc('run', frames=5); n += 1
rpc('run', frames=50)
HP = SYM['hp']; ntrk = None
info = json.load(open(os.path.join(ROOT, 'build', 'multi', 'multi.json')))
areas = [(lo, hi) for lo, hi in info['packed'] + info['raw']]
snap = lambda: b''.join(mem(lo, hi - lo) for lo, hi in areas)
live = snap()
rpc('call', addr=HP + 4, a=0, iff1=0, max_t=3000000)      # (the first track unpacked over itself: only bytes past the end of its shorter tables may change)
first = snap(); ok = True
print('unpacking the first track over itself as loaded changes %d bytes (the mini-map strip past its last line: start-up leftovers)' % sum(a != b for a, b in zip(live, first)))
for t in range(len(info['tracks'])):
    r = rpc('call', addr=HP + 4, a=t, iff1=0, max_t=3000000)
    print('track %d (the tape\'s track %d): unpacked in %d T-states = %.2f s (%.1f TV frames); returned %s' % (t + 1, info['tracks'][t], r['t_states'], r['t_states'] / 3500000, r['t_states'] / 69888, r.get('returned')))
r = rpc('call', addr=HP + 4, a=0, iff1=0, max_t=3000000)
back = snap()
print('%s the first track\'s %d bytes are exactly as loaded after going round the tracks and back' % ('PASS' if back == first else 'FAIL', len(first)))
if back != first:
    import bisect
    lab = sorted((v, k) for k, v in SYM.items() if 0x5B00 <= v <= 0xFFFF)
    addrs = [a for lo, hi in areas for a in range(lo, hi)]
    d = [addrs[i] for i in range(len(first)) if first[i] != back[i]]
    def near(a):
        i = bisect.bisect_right(lab, (a, '~')) - 1
        return '%s+%d' % (lab[i][1], a - lab[i][0])
    print('  %d bytes differ: %s' % (len(d), ', '.join('%04X %s' % (a, near(a)) for a in d[:30])))
z.kill()
