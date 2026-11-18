"""Shared by the race-track trial's tests and picture tools (racetrack_test.py, racetrack_shots.py): start zxdev on a
tape, get to the race, drive by autopilot, read the screen as colours."""
import os, sys, json, math, subprocess
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
ZXDEV = '/home/user/zx-emulator/zxdev'
RGB = [(0, 0, 0), (0, 0, 215), (215, 0, 0), (215, 0, 215), (0, 215, 0), (0, 215, 215), (215, 215, 0), (215, 215, 215)]
class Game:
    def __init__(self, name='racer_racetrack', src=None):
        self.tap = os.path.join(ROOT, 'build', name + '.tap')
        self.sym = {}
        for line in open(os.path.join(ROOT, 'build', name + '.sym')):
            p = line.split()
            if len(p) >= 3 and p[1] == 'EQU': self.sym[p[0].lower()] = int(p[2].rstrip('H'), 16)
        src = src or os.path.join(ROOT, 'build', 'racetrack', 'src')
        self.wps = [tuple(int(v) for v in l.split('dw')[1].split(',')) for l in open(os.path.join(src, 'waypoints.asm')).read().split('waypoints:')[1].splitlines() if 'dw' in l]
        self.z = subprocess.Popen([ZXDEV, 'serve', '--stdio'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        self.held = set()
        self.rpc('load', path=self.tap); self.rpc('random', pin=True)
    def rpc(self, method, **params):
        self.z.stdin.write(json.dumps({'id': 1, 'method': method, 'params': params}) + '\n'); self.z.stdin.flush()
        r = json.loads(self.z.stdout.readline())
        if 'error' in r: raise SystemExit('%s: %s' % (method, r['error']))
        return r['result']
    def mem(self, addr, n):
        r = self.rpc('read', addr=addr, len=n)
        return bytes.fromhex(r['hex']) if 'hex' in r else bytes(r['bytes'])
    def w16(self, a): return int.from_bytes(self.mem(a, 2), 'little')
    def poke(self, addr, data): self.rpc('write', addr=addr, hex=bytes(data).hex())
    def key(self, k, down):
        if down and k not in self.held: self.rpc('key_down', keys=k); self.held.add(k)
        if not down and k in self.held: self.rpc('key_up', keys=k); self.held.discard(k)
    def run(self, frames=1): self.rpc('run', frames=frames)
    def to_grid(self, key='1'):
        """through the title to the first picture of the race (the lights not yet started); key='2': two players"""
        n = 0
        while self.mem(0x5800 + 8 * 32 + 10, 1)[0] != 0x7A and n < 400: self.run(5); n += 1
        self.run(25)
        if 'jin_on' in self.sym: self.rpc('write', addr=self.sym['jin_on'], value=0xFF)
        # (RACE or COMBAT tapes, tools/build_race.sh: RT_MODE=combat or race chooses the game, as the title's M would - the
        #  tests written for the armour tape run on these in COMBAT. Unset: the game the tape starts with, RACE.)
        if os.environ.get('RT_MODE') and 'rmode' in self.sym: self.poke(self.sym['rmode'], [int(os.environ['RT_MODE'] == 'race')])
        self.rpc('press', keys=key, frames=10, after=5)
        n = 0
        while self.w16(self.sym['renders']) == 0 and n < 200: self.run(5); n += 1
        assert n < 200, 'the race never started'
        self.run(10)
    def go(self, alone=False):
        """Q until the lights are green; alone: the computer cars stay on the grid"""
        self.key('Q', True)
        n = 0
        while self.mem(self.sym['race_on'], 1)[0] == 0 and n < 600: self.run(1); n += 1
        assert n < 600, 'the lights never went green'
        if alone:
            for i in range(1, 5): self.rpc('write', addr=self.sym['cars'] + i * self.sym['c_size'] + 19, value=0)
        self.wp = self.mem(self.sym['cars'], 14)[13]
    def car(self, i=0):
        # (The emulator stops wherever the processor is when the TV frame ends. If that is inside the game's own move of a
        # car - between writing the low and the high byte of where it is - the place read here is half old, half new, and
        # 256 pixels out: seen once, 17 Nov 2026, as a car "at x 763" on a 576-pixel world. So the move is let finish first.)
        S = self.sym
        if 'ph_yok' in S and S['physics'] <= self.rpc('regs')['pc'] < S['ph_yok']: self.rpc('run', until_pc=S['ph_yok'], max_frames=2)
        c = self.mem(self.sym['cars'] + i * self.sym['c_size'], 14)
        return c[1] + 256 * c[2], c[4] + 256 * c[5], c[10]
    def put(self, x, y, ang=None, i=0, stop=True):
        """a car set down at (x, y) (its 16 x 16 box's top-left), standing still"""
        a = self.sym['cars'] + i * self.sym['c_size']
        self.poke(a, [0, x & 255, x >> 8, 0, y & 255, y >> 8] + ([0, 0, 0, 0] if stop else list(self.mem(a + 6, 4))))
        if ang is not None: self.poke(a + 10, [ang])
    def steer(self):
        x, y, ang = self.car(); x += 8; y += 8
        tx, ty = self.wps[self.wp]
        if math.hypot(tx - x, ty - y) < 28: self.wp = (self.wp + 1) % len(self.wps)
        diff = (math.degrees(math.atan2(tx - x, -(ty - y))) % 360 - ang * 360 / 64 + 540) % 360 - 180
        self.key('Q', abs(diff) < 70); self.key('O', diff < -8); self.key('P', diff > 8)
    def drive(self, frames=None, until_wp=None, each=None):
        f = 0
        while (frames is None or f < frames) and (until_wp is None or self.wp != until_wp) and f < 4000:
            self.steer(); self.run(1); f += 1
            if each: each(f)
    def next_picture(self):
        """run to just after the next picture has gone to the screen (colours and all)"""
        r = self.w16(self.sym['renders'])
        n = 0
        while self.w16(self.sym['renders']) == r and n < 50: self.run(1); n += 1
    def cam(self): return self.w16(self.sym['camx']), self.w16(self.sym['camy'])
    def window(self):
        """the play window as the TV shows it: 152 rows of 192 colour numbers (0-7), and the squares' attributes"""
        import numpy as np
        px = np.zeros((152, 192), np.uint8); at = np.zeros((19, 24), np.uint8)
        scr = self.mem(0x4000, 6912)
        for r in range(19):
            for c in range(24):
                a = scr[6144 + (r + 1) * 32 + c + 1]; at[r, c] = a
                for l in range(8):
                    y = 8 + r * 8 + l
                    b = scr[((y & 0xC0) << 5) | ((y & 7) << 8) | ((y & 0x38) << 2) | (c + 1)]
                    for i in range(8): px[r * 8 + l, c * 8 + i] = (a & 7) if b & (0x80 >> i) else ((a >> 3) & 7)
        return px, at
    def shot(self, path, scale=3):
        from PIL import Image
        tmp = path + '.tmp.png'
        self.rpc('screenshot', path=tmp)
        im = Image.open(tmp).convert('RGB'); os.remove(tmp)
        im.resize((im.width * scale, im.height * scale), Image.NEAREST).save(path)
    def weapon_dots(self):
        """ARMOUR tapes: where the tank's shell and the clown's wheels are drawn this picture - a list of (x, y, colour), each
        the top-left pixel in the world of a dot 3 x 3 before the game holds it inside one colour square (the sums are
        arm_draw's and arm_dot's own, src/armour.asm). Any other tape: nothing."""
        S = self.sym
        if 'sh_life' not in S: return []
        out = []; v = self.mem(S['sh_rec'], 11)
        if v[10]: out.append((v[1] + 256 * v[2] + 7, v[4] + 256 * v[5] + 7, 7))
        if self.mem(S['wh_out'], 1)[0]:
            k = S.get('arm_clown', 2); c = self.mem(S['cars'] + k * S['c_size'], 11); x, y = c[1] + 256 * c[2], c[4] + 256 * c[5]
            t = self.mem(S['thrust_tab'] + 4 * (c[10] >> 2), 4); s8 = lambda b: b - 256 if b > 127 else b
            sc = lambda a: (((a >> 1) * 3) >> 3); q = lambda a: a - (a >> 2)
            d, e = -sc(s8(t[2])), sc(s8(t[0]))
            for dx, dy in ((d, e), (-d, -e), (q(-d), q(-e)), (-q(-d), -q(-e))): out.append((x + dx + 7, y + dy + 7, 6))
        return out
    def close(self): self.z.kill()
