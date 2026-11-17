"""Two players (src/twoplayer.asm), shared by tests/two_player_test.py, twop_speed.py and twop_shots.py: a Game with an
autopilot for each player's car - player 1 on O P Q, player 2 on 6 7 0."""
import math
from rt_lib import Game
KEYS = [('O', 'P', 'Q'), ('6', '7', '0')]          # left, right, accelerate
WIN_W, WIN_H = 192, 152                            # the play window, in pixels
class Game2(Game):
    def start(self, players=2, alone=False):
        """to the grid by the title's 1 or 2, then the lights (Q), to green"""
        self.to_grid(key=str(players))
        self.go(alone=False)
        self.key('Q', False)
        if alone:                                  # the computer cars stay on the grid (their throttle is shut)
            for i in range(players, 5): self.rpc('write', addr=self.sym['cars'] + i * self.sym['c_size'] + 19, value=0)
        self.wpn = [self.rec(0)[13], self.rec(1)[13]]
        self.lift = [1.0, 1.0]                     # how much of the time each autopilot accelerates (1: always)
        self.f = 0
    def rec(self, i): return self.mem(self.sym['cars'] + i * self.sym['c_size'], self.sym['c_size'])
    def laps(self, i): return self.rec(i)[25]
    def two(self): return self.mem(self.sym['two_p'], 1)[0]
    def pilot(self, i, on=True):
        """the careful autopilot (rt_lib's) for car i on that player's keys; on=False: hands off"""
        l, r, go = KEYS[i]
        if not on:
            for k in (l, r, go): self.key(k, False)
            return
        x, y, ang = self.car(i); x += 8; y += 8
        if self.rec(i)[13] != self.wpn[i] and math.hypot(self.wps[self.wpn[i]][0] - x, self.wps[self.wpn[i]][1] - y) > 60:
            self.wpn[i] = self.rec(i)[13]          # (the leash moved the car: aim at what the game now aims it at)
        tx, ty = self.wps[self.wpn[i]]
        if math.hypot(tx - x, ty - y) < 28: self.wpn[i] = (self.wpn[i] + 1) % len(self.wps)
        diff = (math.degrees(math.atan2(tx - x, -(ty - y))) % 360 - ang * 360 / 64 + 540) % 360 - 180
        self.key(go, abs(diff) < 70 and (self.f * self.lift[i]) % 1 + self.lift[i] >= 1)
        self.key(l, diff < -8); self.key(r, diff > 8)
    def step(self, p1=True, p2=True):
        self.pilot(0, p1); self.pilot(1, p2); self.run(1); self.f += 1
    def in_window(self, i):
        """car i's 16 x 16 box wholly inside the play window?  (and where it is in it)"""
        x, y, _ = self.car(i); cx, cy = self.cam()
        return 0 <= x - cx <= WIN_W - 16 and 0 <= y - cy <= WIN_H - 16, (x - cx, y - cy)
