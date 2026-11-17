"""The driver cards: A REAL-SPEED CLIP of the race from the green light (17 Nov 2026) - one screenshot every TV frame, played
at 50 a second, twice the size: what the tape shows, at the speed it shows it. Your car is driven by the corner-cutting
autopilot (rt_ace.py), so that it stays with the pack; the white car is Jane's dragster.
Usage: python3 tests/rt_cards_shots.py [tape name in build/, default racer_cards] [its build folder] [seconds, default 12]
       ACE=88,60 (the autopilot's LOOK and LIFT)  SEED=0 (another run of luck)  FROM=0 (seconds after the green light to start at)
       ONLY=4 (just you and the white car: the other three are taken off the road)
       LATE=1.5 (you sit on the grid that many seconds after the green light, so that the others lead you away)
Writes docs/design/racetrack/cards/<tape>_race.mp4 and prints, second by second, each car's speed and how far the white
car is from yours (so that what the clip shows can be checked against the numbers).   (needs ffmpeg)"""
import sys, os, math, subprocess, tempfile, shutil
from rt_lib import *
import rt_ace
name = sys.argv[1] if len(sys.argv) > 1 else 'racer_cards'
folder = sys.argv[2] if len(sys.argv) > 2 else name
secs = float(sys.argv[3]) if len(sys.argv) > 3 else 12
look, lift = [int(v) for v in os.environ.get('ACE', '88,60').split(',')]
seed = int(os.environ.get('SEED', '0')); start = float(os.environ.get('FROM', '0')); late = float(os.environ.get('LATE', '0'))
OUT = os.path.join(ROOT, 'docs', 'design', 'racetrack', 'cards'); os.makedirs(OUT, exist_ok=True)
g = Game(name, os.path.join(ROOT, 'build', folder, 'src')); g.to_grid(); S = g.sym; CS = S['c_size']
g.poke(S['seed'], [(0x34 + 37 * seed) & 255, 0x12 + seed])
g.go(); steer = rt_ace.ace(g, look, lift)
only = int(os.environ.get('ONLY', '0'))
if only:                                 # ONLY=4: just you and that computer car (4 is the white one) - the rest are put on the
    for i in range(1, 5):                # grass in the middle with no throttle, so that the two can be watched side by side
        if i != only: g.put(240 + 24 * i, 300, i=i); g.rpc('write', addr=S['cars'] + i * CS + 19, value=0)
for f in range(int(start * 50)):
    if f < late * 50: g.key('Q', False)
    else: steer()
    g.run(1)
tmp = tempfile.mkdtemp()
s16 = lambda lo, hi: (lo + 256 * hi + 32768) % 65536 - 32768
who = ['YOU', 'CYAN', 'GREEN', 'PINK', 'WHITE']
for f in range(int(secs * 50)):
    if start * 50 + f < late * 50: g.key('Q', False); g.key('O', False); g.key('P', False)   # (LATE=: you sit on the grid that long)
    else: steer()
    g.run(1)
    g.rpc('screenshot', path=os.path.join(tmp, 'f%04d.png' % f))
    if f % 50 == 49:
        c = g.mem(S['cars'], CS * 5); line = []
        pos = [(c[i * CS + 1] + 256 * c[i * CS + 2], c[i * CS + 4] + 256 * c[i * CS + 5]) for i in range(5)]
        for i in range(5):
            r = c[i * CS:(i + 1) * CS]
            line.append('%s %.2f' % (who[i], math.hypot(s16(r[6], r[7]), s16(r[8], r[9])) / 256))
        print('%4.1f s: speeds (px a TV frame) %s; the white car is %d px from yours' % (start + (f + 1) / 50, ', '.join(line), math.hypot(pos[4][0] - pos[0][0], pos[4][1] - pos[0][1])))
g.close()
mp4 = os.path.join(OUT, name + ('_you_and_car%d' % only if only else '_race') + '.mp4')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '50', '-i', os.path.join(tmp, 'f%04d.png'), '-vf', 'scale=iw*2:ih*2:flags=neighbor',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '16', mp4], check=True)
shutil.rmtree(tmp)
print('wrote', os.path.relpath(mp4, ROOT))
