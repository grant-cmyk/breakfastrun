"""Armour and weapons: THE PICTURES (17 Nov 2026) - a still of the race-order panel with its armour bars, and REAL-SPEED
CLIPS (one screenshot every TV frame, played at 50 a second, twice the size) of three moments from a real race on the
tape: the tank shooting and hitting, the clown's wheels hitting, and a bump that costs the dragster a piece of armour
(its bar flashing). Nothing is staged: your car is driven by the corner-cutting autopilot, starting LATE seconds after
the lights so that it races in the pack; the race is run once to find the moments (each must happen in view), then
again - it plays out the same - recording a few seconds round each.
Usage: python3 tests/rt_armour_shots.py [tape name in build/, default racer_armour_grip1]      (needs ffmpeg)
       SEED=0 (the first run of luck tried; it goes on to the next until all three moments are found)  LATE=2
Writes docs/design/racetrack/armour/: armour_panel.png (the whole screen, 3x), armour_panel_close.png (the panel, 6x),
armour_tank.mp4, armour_wheels.mp4, armour_ram.mp4 - and says what each shows and when."""
import sys, os, subprocess, tempfile, shutil
from rt_lib import *
import rt_ace
from PIL import Image
name = sys.argv[1] if len(sys.argv) > 1 else 'racer_armour_grip1'
late = float(os.environ.get('LATE', '2'))
OUT = os.path.join(ROOT, 'docs', 'design', 'racetrack', 'armour'); os.makedirs(OUT, exist_ok=True)
WHO = ['YOU', 'FRANK', 'SPIKE', 'BRUNO', 'JANE']
def race(seed, record=None, still=None):
    """one race; record: {clip name: (first TV frame, last)} - screenshots of those; else returns the moments found"""
    g = Game(name, os.path.join(ROOT, 'build', name, 'src')); g.to_grid(); S = g.sym; CS = S['c_size']
    g.poke(S['seed'], [(0x34 + 37 * seed) & 255, 0x12 + seed]); g.go(); steer = rt_ace.ace(g, 104, 30)
    found = {}; prev = None; tmp = {k: tempfile.mkdtemp() for k in (record or {})}; fired_at = None
    def seen(i, cx, cy, c):
        x, y = c[i * CS + 1] + 256 * c[i * CS + 2] - cx, c[i * CS + 4] + 256 * c[i * CS + 5] - cy
        return 8 <= x <= 168 and 8 <= y <= 128
    for f in range(75 * 50):
        if f < late * 50: g.key('Q', False); g.key('O', False); g.key('P', False)
        else: steer()
        g.run(1)
        if record is not None:
            for k, (a, b) in record.items():
                if a <= f <= b: g.rpc('screenshot', path=os.path.join(tmp[k], 'f%04d.png' % (f - a)))
            if still is not None and f == still:
                g.shot(os.path.join(OUT, 'armour_panel.png'), 3)
                Image.open(os.path.join(OUT, 'armour_panel.png')).crop(((48 + 200) * 3, (48 + 36) * 3, (48 + 256) * 3, (48 + 132) * 3)).resize((56 * 6, 96 * 6), Image.NEAREST).save(os.path.join(OUT, 'armour_panel_close.png'))
            if f > max([b for a, b in record.values()] + [still or 0]): break
            continue
        c = g.mem(S['cars'], CS * 5); a = g.mem(S['arm_tab'], 40); k = list(g.mem(S['sh_fired'], 4)); cx, cy = g.cam()
        now = dict(k=k, pcs=[a[i * 8 + 1] for i in range(5)], safe=[a[i * 8 + 5] for i in range(5)], spins=[a[i * 8 + 7] for i in range(5)])
        if prev:
            if k[0] > prev['k'][0]: fired_at = f if seen(3, cx, cy, c) else None
            if k[1] > prev['k'][1] and fired_at is not None and 'tank' not in found:
                v = [i for i in range(5) if now['spins'][i] > prev['spins'][i]]
                if v and seen(v[0], cx, cy, c): found['tank'] = (fired_at, 'the tank fires at %.1f s and hits %s at %.1f s' % (fired_at / 50, WHO[v[0]], f / 50))
            if k[3] > prev['k'][3] and 'wheels' not in found and seen(2, cx, cy, c):
                v = [i for i in range(5) if now['spins'][i] > prev['spins'][i]]
                if v and seen(v[0], cx, cy, c): found['wheels'] = (f, 'the clown\'s wheels hit %s at %.1f s' % (WHO[v[0]], f / 50))
            if now['pcs'][4] < prev['pcs'][4] and now['safe'][4] > prev['safe'][4] and seen(4, cx, cy, c) and f > 250:
                you = now['safe'][0] > prev['safe'][0]
                if 'ram' not in found or (you and not found['ram'][2]):
                    found['ram'] = (f, 'the dragster is bumped%s at %.1f s and loses a piece: %d of 6 left' % (' by YOUR car' if you else '', f / 50, now['pcs'][4]), you)
            if now['pcs'] != prev['pcs'] and 'still' not in found and f > 20 * 50 and len(set(now['pcs'])) >= 4: found['still'] = (f + 30, 'armour %s' % now['pcs'])
        prev = now
    g.close()
    if record is None: return found
    for k in record:
        mp4 = os.path.join(OUT, 'armour_%s.mp4' % k)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '50', '-i', os.path.join(tmp[k], 'f%04d.png'), '-vf', 'scale=iw*2:ih*2:flags=neighbor',
                        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '16', mp4], check=True)
        shutil.rmtree(tmp[k]); print('wrote', os.path.relpath(mp4, ROOT))
seed = int(os.environ.get('SEED', '0'))
while True:
    found = race(seed)
    print('run of luck %d:' % seed, '; '.join('%s - %s' % (k, v[1]) for k, v in found.items()))
    if all(k in found for k in ('tank', 'wheels', 'ram', 'still')) or seed > int(os.environ.get('SEED', '0')) + 12: break
    seed += 1
rec = {k: (max(found[k][0] - 75, 0), found[k][0] + 150) for k in ('tank', 'wheels', 'ram') if k in found}
race(seed, rec, found.get('still', (1500,))[0])
print('the clips are from run of luck %d (you start %.0f s late); each begins 1.5 s before its moment and runs 4.5 s' % (seed, late))
