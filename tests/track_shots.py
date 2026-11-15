"""Pictures of a track's own build, for looking at (not a test): docs/design/tracks/built/
    trackN_grid.png        the start grid, before the lights
    trackN_lap_1..4.png    four places round the lap, your car driven by script among the computer cars
    trackN_minimap.png     the panel's mini-map, large
    trackN_lines.png       the whole table with the lines the four computer cars took over 3 laps (and the script's)
Run:  TRACK=2 python3 tests/track_shots.py   (after TRACK=2 bash build.sh)"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.environ.get('TRACK', '2')
src = open(os.path.join(HERE, 'track2_test.py')).read()
src = src[:src.index('# ---------------------------------------------------------------- the data the tape')] + src[src.index('def autopilot('):src.index('sp = boot(); go_green(sp); press(sp, \'Q\', False)\ncross, trace')]
exec(src.replace("os.path.dirname(os.path.abspath(__file__))", repr(HERE)))
from PIL import ImageDraw
DEST = os.path.join(ROOT_, 'docs', 'design', 'tracks', 'built'); os.makedirs(DEST, exist_ok=True)
OUT = DEST                                              # (shot() saves there)
T = 'track%s_' % TRACK
sp = boot(); sp.run(duration=1.0, fast_forward=True); shot(sp, T + 'grid.png')
sb = screen_bits(sp)[118:160, 8:56]                  # (the map is in the window's bottom left corner since 15 Nov 2026)
Image.fromarray(((1 - sb) * 255).astype(np.uint8)).resize((48 * 8, 42 * 8), Image.NEAREST).save(os.path.join(DEST, T + 'minimap.png'))
go_green(sp); press(sp, 'Q', False)
# drive with the keys; a picture when your next waypoint reaches each of four places on the first lap
marks = {WS + NWP // 8: 1, WS + 3 * NWP // 8: 2, WS + 5 * NWP // 8: 3, WS + 7 * NWP // 8: 4}; marks = {k % NWP: v for k, v in marks.items()}
lines = [[] for _ in range(N)]; keys = set(); t = 0.0; done = set()
def setk(want):
    for k in list(keys - want): press(sp, k, False); keys.discard(k)
    for k in want - keys: press(sp, k, True); keys.add(k)
while t < 240 and min(laps_of(sp, n) for n in range(N)) < LAPS + 1 and sp.read8(SYM['race_over']) == 0:
    c = car(sp, 0); wx, wy = WPS[(c['wp'] + 1) % NWP]
    e = (heading(c['x'] + 8, c['y'] + 8, wx, wy) - c['ang'] + 32) % 64 - 32
    k = set()
    if e > 1: k.add('P')
    if e < -1: k.add('O')
    if abs(e) < 12 or math.hypot(c['vx'], c['vy']) < 0.9: k.add('Q')
    if laps_of(sp, 0) > LAPS: k = set()
    setk(k); sp.run(duration=0.06, fast_forward=True); t += 0.06
    for n in range(N):
        cc = car(sp, n); lines[n].append((cc['x'] + 8, cc['y'] + 8))
    if c['wp'] in marks and c['wp'] not in done and laps_of(sp, 0) == 1:
        done.add(c['wp']); shot(sp, T + 'lap_%d.png' % marks[c['wp']]); print('lap_%d: waypoint %d, car at %d, %d, %.1f s' % (marks[c['wp']], c['wp'], c['x'], c['y'], t))
setk(set())
sp.__exit__(None, None, None)
S = 2
im = Image.fromarray(((1 - world) * 255).astype(np.uint8)).convert('RGB').resize((MAPW * 8 * S, MAPH * 8 * S), Image.NEAREST)
d = ImageDraw.Draw(im)
COL = [(215, 0, 0), (0, 160, 160), (0, 170, 0), (215, 0, 215), (120, 120, 120)]
for n in range(N - 1, -1, -1):
    d.line([(x * S, y * S) for x, y in lines[n]], fill=COL[n], width=1)
for i, (x, y) in enumerate(WPS):
    d.ellipse([x * S - 3, y * S - 3, x * S + 3, y * S + 3], outline=(0, 0, 215));
    if i % 5 == 0: d.text((x * S + 5, y * S - 5), str(i), fill=(0, 0, 215))
im.save(os.path.join(DEST, T + 'lines.png'))
print('saved in', DEST)
