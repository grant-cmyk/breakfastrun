"""Your laps when you go off the track a fair bit and come back on further round (Grant, 18 Nov 2026: "I also went off
track for a bit, and I seemed to lose a lap - need to check how lap tracking works if you go off the track a fair bit").
On the tight track (the armour tape by default), alone, your car is driven round by an autopilot and, at chosen places,
off the road onto the grass along a path of points, then back onto the road further round. After each excursion the test
reads your lap and your next waypoint: rejoining the road further round must cost nothing; a short cut across the
infield (half the track) must not gain anything. Then a whole 3-lap race with excursions must finish on the right lap.
  python3 tests/lap_offtrack_test.py [tape name]        (default racer_armour_grip1; its src folder is build/<name>/src)
Prints PASS/FAIL lines and RESULT."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rt_lib import *
NAME = sys.argv[1] if len(sys.argv) > 1 else 'racer_armour_grip1'
fails = 0
def ok(c, m):
    global fails
    print('PASS' if c else 'FAIL', m); fails += 0 if c else 1

class Drive:
    def __init__(self):
        self.g = g = Game(NAME, os.path.join(ROOT, 'build', NAME, 'src'))
        g.to_grid(); g.go(alone=True)
        S = g.sym; self.S = S; self.N = len(g.wps); self.ws = S['ws']
        self.surf = g.mem(S['surface_map'], 9 * S['maph'])
    def me(self):
        c = self.g.mem(self.S['cars'], 26)
        return c[25], c[13]                              # (lap, the next waypoint the game has you heading for)
    def grass(self):
        x, y, a = self.g.car(); tx, ty = (x + 8) >> 3, (y + 8) >> 3
        return not (0 <= ty < self.S['maph'] and 0 <= tx < 72) or bool(self.surf[ty * 9 + (tx >> 3)] & (0x80 >> (tx & 7)))
    def aim(self, tx, ty, gas=True):
        g = self.g; x, y, ang = g.car(); x += 8; y += 8
        diff = (math.degrees(math.atan2(tx - x, -(ty - y))) % 360 - ang * 360 / 64 + 540) % 360 - 180
        g.key('Q', gas and abs(diff) < 70); g.key('O', diff < -8); g.key('P', diff > 8)
        return math.hypot(tx - x, ty - y)
    def road_to(self, wp):
        """the autopilot along the road until it next aims at waypoint wp (round the lap if it aims at it now)"""
        if self.g.wp == wp % self.N: self.g.drive(frames=40)
        self.g.drive(until_wp=wp % self.N)
    def path(self, pts, reach=14):
        """drive through each point in turn (on the grass, mostly); counts the TV frames spent on the grass"""
        on = 0
        for (tx, ty) in pts:
            f = 0
            while self.aim(tx, ty) > reach and f < 1500:
                self.g.run(1); f += 1; on += self.grass()
        return on
    def rejoin(self, wp):
        """back onto the road at waypoint wp, then the autopilot carries on from the one after"""
        self.path([self.g.wps[wp % self.N]], 20)
        self.g.wp = (wp + 1) % self.N
        self.g.drive(frames=60)
    def close(self): self.g.close()

def ahead(a, b, n):  # how many waypoints b is ahead of a, round the lap
    return (b - a) % n
def check_back(d, lap0, at, what):
    lap, wp = d.me()
    ok(lap == lap0 and 0 <= ahead(at, wp, d.N) <= 4, '%s: lap %d as before, the game has you heading for waypoint %d (back on at %d)' % (what, lap, wp, at))
def check_line(d, lap0, n=1):
    d.road_to(d.ws + 3)
    lap, wp = d.me()
    ok(lap == lap0 + n, '  ... then over the line: lap %d (it was %d)' % (lap, lap0))
def off_along(d):    # excursion 1's path: into the infield at waypoint 2, then 90 px from the middle of the road up to 9
    W = d.g.wps
    return d.path([(W[2][0] - 60, W[2][1] - 10), (W[3][0] - 90, W[3][1]), (W[9][0] - 90, W[9][1])])

# 1. RUNNING ALONG THE GRASS: the right-hand straight (going up) - off into the infield at waypoint 2, along the grass
#    90 px from the middle of the road past eight waypoints, back on at waypoint 11 round the top corner
d = Drive(); N = d.N; W = d.g.wps
d.road_to(2)
lap0, wp0 = d.me()
on = off_along(d)
stuck = d.me()[1]
d.rejoin(11)
check_back(d, lap0, 11, 'along the infield grass past eight waypoints (%d TV frames on the grass; heading for %d while off), back on at 11' % (on, stuck))
check_line(d, lap0)

# 2. A SPIN INTO THE INFIELD: off at waypoint 26 into the infield, stopped there 3 seconds, back on at waypoint 33
d.road_to(26)
lap0, wp0 = d.me()
d.path([(W[27][0] + 70, W[27][1]), (W[30][0] + 80, W[30][1])])
for k in ('Q', 'O', 'P'): d.g.key(k, False)
d.g.run(150)
d.rejoin(33)
check_back(d, lap0, 33, 'into the infield at 26, stopped there 3 s, back on at 33')
check_line(d, lap0)
d.close()

# 3. CORNER CUTS: across the bottom-left corner's grass (30 to 37) and across the little grass island at the top (15 to
#    21) - both slower than the road (the grass costs more than the corner saves); counted as if driven
d = Drive(); W = d.g.wps
d.road_to(30)
lap0, wp0 = d.me()
d.path([(W[30][0] + 60, W[30][1] + 40), (W[37][0], W[37][1] - 50)])
d.rejoin(37)
check_back(d, lap0, 37, 'across the bottom-left corner\'s grass, 30 to 37')
check_line(d, lap0)
lap0 += 1
d.road_to(15)
d.path([((W[16][0] + W[20][0]) // 2, W[15][1])])
d.rejoin(21)
check_back(d, lap0, 21, 'across the grass island at the top, 15 to 21')
check_line(d, lap0)
d.close()

# 4. A SHORT CUT: from the top straight (waypoint 15) straight down across the infield and over the start line (28
#    waypoints - more than half the track - missed): no lap for it, and the game still has you heading for the waypoint
#    where you left; the next time round, over the line, one lap
d = Drive(); W = d.g.wps
d.road_to(15)
lap0, wp0 = d.me()
d.path([(W[15][0], W[15][1] + 60), (W[43][0], W[43][1] - 40)])
d.rejoin(43)
lap1, wp1 = d.me()
ok(lap1 == lap0 and ahead(wp0, wp1, N) <= 5, 'a short cut across the infield and over the line, 15 to 43: no lap for it (lap %d, it was %d), the game still has you heading for %d, near where you left the road (%d)' % (lap1, lap0, wp1, wp0))
for k in ('Q', 'O', 'P'): d.g.key(k, False)
d.g.run(600)
lap1, wp1 = d.me()
ok(lap1 == lap0 and ahead(wp0, wp1, N) <= 5, '  ... and still not after 12 seconds stood there: lap %d, heading for %d (never more than half the track at once)' % (lap1, wp1))
check_line(d, lap0)
d.close()

# 5. A SHORT CUT QUICKER THAN THE ROAD: the car lifted from waypoint 2 and set down on the road at waypoint 14 at once
#    (12 waypoints round, no time taken): not counted at once, but once you have stood there as long as the road would have
#    taken you (about 2 pixels a TV frame), it is - no time gained, no lap lost
d = Drive(); W = d.g.wps
d.road_to(2)
lap0, wp0 = d.me()
for k in ('Q', 'O', 'P'): d.g.key(k, False)
d.g.put(W[14][0] - 8, W[14][1] - 8, 48)
d.g.run(25)
lap1, wp1 = d.me()
ok(lap1 == lap0 and ahead(wp0, wp1, N) <= 4, 'set down 12 waypoints round at once: not counted at once (heading for %d; was %d)' % (wp1, wp0))
d.g.run(275)
lap2, wp2 = d.me()
ok(lap2 == lap0 and ahead(14, wp2, N) <= 2, '  ... counted after 6 seconds there (heading for %d), lap %d as before' % (wp2, lap2))
d.close()

# 6. a whole race of 3 laps, with excursion 1 on every lap: it finishes, on the right lap
d = Drive(); S = d.S
laps_seen = []
for lap in range(S['laps']):
    d.road_to(2)
    off_along(d)
    d.rejoin(11)
    d.road_to(d.ws + 3)
    laps_seen.append(d.me()[0])
d.g.run(100)
done = d.g.mem(S['you_done'], 1)[0]
ok(laps_seen == list(range(2, S['laps'] + 2)) and done == 1,
   'a 3-lap race, off along the grass past eight waypoints on every lap: laps after each crossing %s, finished %s' % (laps_seen, 'yes' if done else 'NO'))
d.close()
print('RESULT:', 'PASS' if fails == 0 else '%d FAIL' % fails)

