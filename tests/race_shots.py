"""Pictures of RACE mode (18 Nov 2026) for docs/design/racetrack/race_mode/: the title with the mode row, the grid in RACE,
mid-race in RACE (3x stills), and a real-speed clip of a close finish (every TV frame, 50 a second, 2x) - the good-driver
autopilot (rt_ace.py) from the back of the grid, the race run with a given run of luck (tests/race_measure.py's race N).
Usage: python3 tests/race_shots.py [tape, default racer_race70] [race, default 3] [seconds of clip, default 12]
       python3 tests/race_shots.py racer_race75 mix [races to look through, default 8] [seconds, default 12]
         (19 Nov 2026, each computer driver its own style: race_mix_<tape>.mp4 - the SECS seconds, from those races, in which
         the computer cars change places with each other most often while near your car (in the picture); real speed,
         every TV frame, 2x. Prints which race and when.)"""
import sys, os, shutil, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rt_lib import *
import rt_ace
TAPE = sys.argv[1] if len(sys.argv) > 1 else 'racer_race70'
RACE = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 3
SECS = float(sys.argv[3]) if len(sys.argv) > 3 else 12
OUT = os.path.join(ROOT, 'docs', 'design', 'racetrack', 'race_mode'); os.makedirs(OUT, exist_ok=True)
SRC = os.path.join(ROOT, 'build', TAPE, 'src')
def start(stills):
    g = Game(TAPE, SRC); S = g.sym
    n = 0
    while g.mem(0x5800 + 8 * 32 + 10, 1)[0] != 0x7A and n < 400: g.run(5); n += 1
    g.run(40)
    if stills: g.shot(os.path.join(OUT, 'race_title.png'))
    g.to_grid()
    g.poke(S['seed'], [(0x34 + 37 * (RACE - 1)) & 255, 0x12 + RACE - 1])
    g.run(30)
    if stills: g.shot(os.path.join(OUT, 'race_grid.png'))
    g.go()
    return g
def clip(g, first, last, name):
    tmp = os.path.join(OUT, 'clip_tmp'); shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    steer = rt_ace.ace(g, 104, 30); k = 0
    for f in range(last):
        steer(); g.run(1)
        if f >= first: g.rpc('screenshot', path=os.path.join(tmp, '%05d.png' % k)); k += 1
    g.close()
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '50', '-i', os.path.join(tmp, '%05d.png'), '-vf', 'scale=iw*2:ih*2:flags=neighbor',
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', os.path.join(OUT, name)], check=True)
    shutil.rmtree(tmp)
    return k
if len(sys.argv) > 2 and sys.argv[2] == 'mix':
    RACES = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    SECS = float(sys.argv[4]) if len(sys.argv) > 4 else 12
    best = None
    for RACE in range(1, RACES + 1):
        g = start(False); S = g.sym; CS = S['c_size']; steer = rt_ace.ace(g, 104, 30); ev = []; prev = None
        for f in range(160 * 50):
            steer(); g.run(1)
            o = list(g.mem(S['order'], 5)); c = g.mem(S['cars'], CS * 5)
            pos = [(c[i * CS + 1] + 256 * c[i * CS + 2], c[i * CS + 4] + 256 * c[i * CS + 5]) for i in range(5)]
            if prev and o != prev and sorted(o) == sorted(prev) == list(range(5)):
                a, b = [v for v in prev if v], [v for v in o if v]
                for p in range(4):
                    for q in range(p + 1, 4):        # two computer cars changed places, both within 80 px of yours
                        if b.index(a[p]) > b.index(a[q]) and all(abs(pos[v][0] - pos[0][0]) < 80 and abs(pos[v][1] - pos[0][1]) < 80 for v in (a[p], a[q])):
                            ev.append(f)
            prev = o
            if g.mem(S['race_over'], 1)[0]: break
        g.close()
        n = int(SECS * 50)
        for e in ev:
            k = sum(1 for x in ev if e - 50 <= x < e - 50 + n)
            if best is None or k > best[0]: best = (k, RACE, max(0, e - 50))
        print('race %d: computer cars changing places with each other near you %d times' % (RACE, len(ev)))
    k, RACE, first = best
    g = start(False)
    name = 'race_mix_%s.mp4' % TAPE.replace('racer_', '')
    frames = clip(g, first, first + int(SECS * 50), name)
    print('%s: race %d, from %.1f s after the lights, %d TV frames - %d changes of place between computer cars near you' % (name, RACE, first / 50, frames, k))
    sys.exit(0)
# 1: the stills, and where the race ends
g = start(True); S = g.sym; steer = rt_ace.ace(g, 104, 30); end = None
for f in range(160 * 50):
    steer(); g.run(1)
    if f == 25 * 50: g.shot(os.path.join(OUT, 'race_mid.png'))
    if g.mem(S['race_over'], 1)[0]: end = f; break
g.close()
print('the race ends at TV frame %s after the lights' % end)
# 2: the clip - the same race again (the same luck, the same driving: the emulator repeats itself), the last SECS seconds
tmp = os.path.join(OUT, 'clip_tmp'); shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
g = start(False); steer = rt_ace.ace(g, 104, 30); first = max(0, end - int(SECS * 50) + 50); k = 0
for f in range(end + 50):
    steer(); g.run(1)
    if f >= first: g.rpc('screenshot', path=os.path.join(tmp, '%05d.png' % k)); k += 1
g.close()
clip = os.path.join(OUT, 'race_close_finish.mp4')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '50', '-i', os.path.join(tmp, '%05d.png'), '-vf', 'scale=iw*2:ih*2:flags=neighbor',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', clip], check=True)
shutil.rmtree(tmp)
print('stills: race_title.png, race_grid.png, race_mid.png; clip: race_close_finish.mp4 (%d TV frames)' % k)
