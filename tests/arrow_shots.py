"""Pictures of the layout of 15 Nov 2026 and the corner arrows, from the game itself (real 48K ROM, zx package),
into docs/design/arrows/: for the track built (TRACK=1, 2 or 3; default 1)
  v2_tN_grid.png  _gentle.png  _sharp.png  _straight.png     the whole screen, 2 x
  v2_tN_strip.png       the window's bottom strip, 4 x: the map, a message, three spoons, the mug at full damage
  v2_tN_map_road.png  v2_tN_map_cloth.png    the mini-map close up, 6 x, over road and over busy cloth
  v2_tN_corner.gif      driven by script from the line through the first corner, the arrow flashing
  v2_t1_arrow_above_centre.png  v2_t1_arrow_dead_centre.png   (track 1) the arrow's spot as built, and at the window's
                        exact middle: your car standing (left) and flat out (right)
(the pictures without v2_ are the first version's: a yellow map box, the arrow ahead of the car)
Usage: python3 tests/arrow_shots.py      (TRACK=n bash build.sh first for tracks 2 and 3)"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.environ.get('TRACK', '1')
ROOT_ = os.path.join(HERE, '..')
TSRC = os.path.join(ROOT_, 'src') if TRACK == '1' else os.path.join(ROOT_, 'build', 'track' + TRACK, 'src')
if TRACK != '1':
    os.environ.setdefault('ZTAP', os.path.join(ROOT_, 'build', 'racer_track%s.tap' % TRACK))
    os.environ.setdefault('ZSYM', os.path.join(ROOT_, 'build', 'racer_track%s.sym' % TRACK))
src = open(os.path.join(HERE, 'drive_test.py')).read()
src = src[:src.index('with Racer(headless=True)')].replace("os.path.dirname(os.path.abspath(__file__))", repr(HERE))
src = src.replace("os.path.join(ROOT, 'src',", "os.path.join(%r," % TSRC)
exec(src)
DEST = os.path.join(ROOT_, 'docs', 'design', 'arrows'); os.makedirs(DEST, exist_ok=True)
rd = lambda n: open(os.path.join(TSRC, n)).read()
WPS = [tuple(int(v) for v in l.split('dw')[1].split(',')) for l in rd('waypoints.asm').split('waypoints:')[1].splitlines() if 'dw' in l]
ATAB = [int(l.split('defb')[1].split(';')[0]) for l in rd('arrowtab.asm').splitlines() if 'defb' in l]
PLACES = {'1': dict(gentle=14, sharp=0, straight=37), '2': dict(gentle=40, sharp=12, straight=18), '3': dict(gentle=10, sharp=36, straight=41)}[TRACK]
C_WP = 13
def frame(sp):
    sp.render_screen()
    px = np.array(sp.get_frame_pixels(), dtype=np.uint8).reshape(-1, 352, 4)[:, :, [2, 1, 0]]
    return Image.fromarray(px)
def save(sp, name, box=None, zoom=2):
    im = frame(sp)
    if box: im = im.crop(box)
    im.resize((im.width * zoom, im.height * zoom), Image.NEAREST).save(os.path.join(DEST, 'v2_t%s_%s.png' % (TRACK, name)))
def boot():
    sp = Racer(headless=True); sp.__enter__(); sp.load_tape(TAP); t = 0
    while g(sp, 'renders') == 0 and t < 60: sp.run(duration=0.1, fast_forward=True); t += 0.1
    return sp
def arrow_on(sp):
    for _ in range(6):
        at_copy_done(sp)
        if arrow_state(sp): return True
        sp.run(duration=0.02, fast_forward=True)
    return False
sp = boot(); sp.run(duration=0.6, fast_forward=True); at_copy_done(sp)
save(sp, 'grid')
_f = frame(sp); OX = (_f.width - 256) // 2; OY = (_f.height - 192) // 2      # the screen inside the border
go_green(sp); press(sp, 'Q', False)
sp.write(SYM['inv'], bytes([1, 1, 1])); sp.write(SYM['dmg'], bytes([SYM['dmg_max']]))
sp.run(duration=0.5, fast_forward=True); at_copy_done(sp)
save(sp, 'strip', (OX, OY + 104, OX + 208, OY + 168), 4)
sp.write(SYM['inv'], bytes([1, 0, 0])); sp.write(SYM['dmg'], bytes([2]))
sp.run(duration=3.5, fast_forward=True)
def stand(k, others=True):                                          # your car stood where it would be while heading for waypoint k
    (x0, y0), (x1, y1) = WPS[(k - 2) % NWP], WPS[(k - 1) % NWP]; d = math.dist((x0, y0), (x1, y1)); ux, uy = (x1 - x0) / d, (y1 - y0) / d
    h = round(math.atan2(ux, -uy) / (2 * math.pi) * 64) % 64
    put(sp, 0, int(x1 - 20 * ux) - 8, int(y1 - 20 * uy) - 8, h); sp.write(CARS + C_WP, bytes([k]))
    for i in CPUS:
        back = 26 + 22 * i; side = 12 if i % 2 else -12
        if others: put(sp, i, int(x1 - back * ux - side * uy) - 8, int(y1 - back * uy + side * ux) - 8, h)
        else: put(sp, i, 4 + 40 * i, SY + 58)
        sp.write(CARS + i * CS + 19, bytes([0]))
    sp.run(duration=0.6, fast_forward=True); sp.write(CARS + C_WP, bytes([k]))
for name, k in PLACES.items():
    stand(k); print(name, 'waypoint', k, ARROW_KINDS[ATAB[k] >> 3], 'arrow on:', arrow_on(sp)); save(sp, name)
# the map close up, 6 x: where the most road lies under it, and where the busiest cloth does
def under(k):
    (x0, y0), (x1, y1) = WPS[(k - 2) % NWP], WPS[(k - 1) % NWP]; d = math.dist((x0, y0), (x1, y1))
    cx, cy = int(x1 - 20 * (x1 - x0) / d) - 8 - (WW // 2 - 8), int(y1 - 20 * (y1 - y0) / d) - 8 - (WH // 2 - 8)
    ys, xs = slice(cy + MM_TOP, cy + MM_TOP + MM_H), slice(cx, cx + 24)
    road_ = np.mean([[surf[(y // 8) * MAPW + x // 8] == 0 for x in range(xs.start, xs.stop)] for y in range(ys.start, ys.stop)]) if cx >= 0 and cy >= 0 and ys.stop < MAPH * 8 else -1
    return road_, int(world[ys, xs].sum())
sc = {k: under(k) for k in range(NWP)}
for name, k in (('map_road', max(sc, key=lambda k: sc[k][0])), ('map_cloth', max(sc, key=lambda k: sc[k][1] - 1000 * (sc[k][0] > 0.2)))):
    stand(k, others=False); at_copy_done(sp); print(name, 'waypoint', k, 'road under it %.0f%%, map ink under it %d' % (100 * sc[k][0], sc[k][1]))
    save(sp, name, (OX + 4, OY + 8 + MM_TOP - 12, OX + 4 + 64, OY + 8 + WH + 4), 6)
if TRACK == '1':                                                    # the arrow's spot against the window's exact middle: your car standing, then at speed
    for spot, y in (('spot', SYM['arrow_y']), ('centre', WH // 2)):
        sp.write(SYM['ad_y'] + 1, bytes([y - 5 + SYM['buf_top']]))
        stand(0, others=False); arrow_on(sp); im1 = frame(sp).crop((OX, OY, OX + 208, OY + 168))
        put(sp, 0, WPS[41][0] - 8, WPS[41][1] - 8, 16); sp.write(CARS + C_WP, bytes([42])); press(sp, 'Q', True); r = None
        for _ in range(150):                                        # flat out along the start straight until the corner's arrow is up
            sp.run(duration=0.04, fast_forward=True); at_copy_done(sp)
            if car(sp, 0)['vx'] > 1.5 and sp.read8(SYM['arrow_tab'] + car(sp, 0)['wp']) and g(sp, 'renders') & 2: break
        press(sp, 'Q', False); im2 = frame(sp).crop((OX, OY, OX + 208, OY + 168))
        both = Image.new('RGB', (424, 168), (255, 255, 255)); both.paste(im1, (0, 0)); both.paste(im2, (216, 0))
        both.resize((848, 336), Image.NEAREST).save(os.path.join(DEST, 'v2_t1_%s.png' % ('arrow_above_centre' if spot == 'spot' else 'arrow_dead_centre')))
        sp.run(duration=1.0, fast_forward=True)
    sp.write(SYM['ad_y'] + 1, bytes([SYM['arrow_y'] - 5 + SYM['buf_top']]))
sp.__exit__(None, None, None)

# the GIF: from the line, round the first corner, steering at the waypoints with the keys
sp = boot(); go_green(sp)
frames = []; r_last = -1; keys = set()
def want(k, down):
    if down != (k in keys): press(sp, k, down); (keys.add if down else keys.discard)(k)
t = 0.0
while t < 14.0 and len(frames) < 120:
    sp.run(duration=0.04, fast_forward=True); t += 0.04
    c = car(sp, 0); wx, wy = WPS[c['wp']]
    aim = round(math.atan2(wx - c['x'] - 8, -(wy - c['y'] - 8)) / (2 * math.pi) * 64) % 64
    d = (aim - c['ang'] + 32) % 64 - 32
    want('P', d > 1); want('O', d < -1); want('Q', abs(d) < 12)
    r = g(sp, 'renders')
    if r != r_last and t > 0.8:
        r_last = r; at_copy_done(sp)
        frames.append(frame(sp).crop((OX, OY, OX + 208, OY + 168)).resize((416, 336), Image.NEAREST).convert('P', palette=Image.ADAPTIVE, colors=16))
for k in list(keys): press(sp, k, False)
frames[0].save(os.path.join(DEST, 'v2_t%s_corner.gif' % TRACK), save_all=True, append_images=frames[1:], duration=80, loop=0)
print('gif:', len(frames), 'pictures; your car ended heading for waypoint', car(sp, 0)['wp'])
sp.__exit__(None, None, None)
