"""Pictures of RACE mode (18 Nov 2026) for docs/design/racetrack/race_mode/: the title with the mode row, the grid in RACE,
mid-race in RACE (3x stills), and a real-speed clip of a close finish (every TV frame, 50 a second, 2x) - the good-driver
autopilot (rt_ace.py) from the back of the grid, the race run with a given run of luck (tests/race_measure.py's race N).
Usage: python3 tests/race_shots.py [tape, default racer_race70] [race, default 3] [seconds of clip, default 12]"""
import sys, os, shutil, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rt_lib import *
import rt_ace
TAPE = sys.argv[1] if len(sys.argv) > 1 else 'racer_race70'
RACE = int(sys.argv[2]) if len(sys.argv) > 2 else 3
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
