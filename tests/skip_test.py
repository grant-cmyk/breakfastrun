"""A key skips the start jingle (Grant, 16 Nov 2026: "key should skip a jingle"): with no key the lights
come after the jingle's ~6 s; a key tapped during it brings them within a step or two. (zxdev; RESULT line.)"""
import json, os, subprocess
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); N = os.environ.get('TRACK', '1')
NAME = 'racer' if N == '1' else 'racer_track' + N
SYM = {}
for l in open(os.path.join(ROOT, 'build', NAME + '.sym')):
    p = l.split()
    if len(p) >= 3 and p[1] == 'EQU': SYM[p[0].lower()] = int(p[2].rstrip('H'), 16)
def run(tap):
    z = subprocess.Popen(['/home/user/zx-emulator/zxdev', 'serve', '--stdio'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    def rpc(m, **p):
        z.stdin.write(json.dumps({'id': 1, 'method': m, 'params': p}) + '\n'); z.stdin.flush(); r = json.loads(z.stdout.readline()); return r.get('result', r)
    rd = lambda n: bytes.fromhex(rpc('read', addr=SYM[n], len=1)['hex'])[0]
    rpc('load', path=os.path.join(ROOT, 'build', NAME + '.tap')); rpc('run', frames=300)
    rpc('key_down', keys='1'); rpc('run', frames=10); rpc('key_up', keys='1'); t = 0
    while rd('start_go') == 0 and t < 900:
        rpc('run', frames=2); t += 2
        if tap and t == 60: rpc('key_down', keys='M')
        if tap and t == 70: rpc('key_up', keys='M')
    z.kill(); return t / 50
fails = 0
def ok(c, m):
    global fails
    print('PASS' if c else 'FAIL', m); fails += 0 if c else 1
a = run(False); ok(5.3 < a < 6.6, 'no key: the start jingle plays through, the lights %.1f s after 1 was let go' % a)
b = run(True); ok(1.2 <= b < 2.0, 'a key tapped 1.2 s in: the jingle stops and the lights come at %.1f s' % b)
print('RESULT: PASS' if not fails else 'RESULT: %d FAIL' % fails)
