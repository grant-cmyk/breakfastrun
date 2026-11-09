"""Drive your car round a full lap on the real ROM with a simple autopilot
(it presses O / P / Q like a player), the two computer cars racing too.
Reports pictures per second along the lap (the slowest stretch matters) and
writes build/stage3_lap.gif and a contact sheet build/stage3_sheet.png."""
import os, re, math
import numpy as np
from PIL import Image
from zx._spectrum import Spectrum
import zx._spectrum as zs
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SYM = {}
for line in open(os.path.join(ROOT, 'build', 'racer.sym')):
    p = line.split()
    if len(p) >= 3 and p[1] == 'EQU': SYM[p[0].lower()] = int(p[2].rstrip('H'), 16)
src = open(os.path.join(ROOT, 'src', 'world.asm')).read()
wps = [tuple(int(v) for v in l.split('dw')[1].split(',')) for l in open(os.path.join(ROOT, 'src', 'waypoints.asm')).read().split('waypoints:')[1].splitlines() if 'dw' in l]
CARS, CS = SYM['cars'], SYM['c_size']
held = set()
def key(sp, k, down):
    if down and k not in held: sp.devices.notify(zs.KeyStroke(zs.KEYS[k].ID, pressed=True)); held.add(k)
    if not down and k in held: sp.devices.notify(zs.KeyStroke(zs.KEYS[k].ID, pressed=False)); held.discard(k)
frames = []
def grab(sp):
    sp.render_screen()
    px = np.array(sp.get_frame_pixels(), dtype=np.uint8).reshape(-1, 352, 4)[:, :, [2, 1, 0]]
    frames.append(Image.fromarray(px[24:24 + 192, 48:48 + 256]))      # the whole screen
with Spectrum(headless=True) as sp:
    sp.load_tape(os.path.join(ROOT, 'build', 'racer.tap'))
    while sp.read16(SYM['renders']) == 0: sp.run(duration=0.1, fast_forward=True)
    wp, t, laps = 0, 0.0, 0
    x0 = sp.read16(CARS + 1)
    while wps[wp][0] < x0 + 30: wp += 1
    start_wp = wp
    seg = []; r_last = sp.read16(SYM['renders']); t_last = 0.0
    while laps < 1 and t < 40:
        x, y, ang = sp.read16(CARS + 1) + 8, sp.read16(CARS + 4) + 8, sp.read8(CARS + 10)
        tx, ty = wps[wp]
        if math.hypot(tx - x, ty - y) < 28:
            wp = (wp + 1) % len(wps)
            if wp == start_wp: laps += 1
            r = sp.read16(SYM['renders']); seg.append(((r - r_last) / (t - t_last + 1e-9), wp)); r_last, t_last = r, t
        want = math.degrees(math.atan2(tx - x, -(ty - y))) % 360
        diff = (want - ang * 360 / 64 + 540) % 360 - 180
        key(sp, 'Q', abs(diff) < 70)
        key(sp, 'O', diff < -8); key(sp, 'P', diff > 8)
        sp.run(duration=0.02, fast_forward=True); t += 0.02
        grab(sp)
    for k in list(held): key(sp, k, False)
print('lap time %.1f s' % t)
fps = [f for f, _ in seg if f > 0]
print('pictures per second between waypoints: min %.1f  max %.1f  mean %.1f' % (min(fps), max(fps), sum(fps) / len(fps)))
print('per stretch:', ' '.join('%.1f' % f for f in fps))
out = os.path.join(ROOT, 'build', 'stage3_lap.gif')
small = [f.resize((f.width * 2, f.height * 2), Image.NEAREST) for f in frames[::1]]
small[0].save(out, save_all=True, append_images=small[1:], duration=20, loop=0)
pick = frames[30::len(frames) // 9][:8]
sheet = Image.new('RGB', (pick[0].width * 4 * 2, pick[0].height * 2 * 2), 'white')
for i, f in enumerate(pick):
    sheet.paste(f.resize((f.width * 2, f.height * 2), Image.NEAREST), ((i % 4) * f.width * 2, (i // 4) * f.height * 2))
sheet.save(os.path.join(ROOT, 'build', 'stage3_sheet.png'))
print('wrote', out)
