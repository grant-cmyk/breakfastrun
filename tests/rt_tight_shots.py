"""The tighter-track trial's pictures (17 Nov 2026), into docs/design/racetrack/tight/:
  <name>_track.png    the whole track as the game colours it, 3 pixels to one (tools/make_world.py draws it at build time)
  <name>_corner.png   the screen, 3x, with your car half-way round the first big corner, in the pack
  <name>_lap.mp4      (only with "clip") the screen at real speed: one picture for every TV frame, 50 a second, 2x, 10 s
                      from one second after the green light - the first corner, the right-hand straight, the second corner
Your car is driven by tests/rt_ace.py's corner-cutting autopilot (LOOK 72: a tidy line, not the quickest).
Usage: python3 tests/rt_tight_shots.py <name> [clip]      name as in build/racer_tight_<name>.tap"""
import os, sys, shutil, subprocess, tempfile
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rt_lib import Game, ROOT
import rt_ace
name = sys.argv[1]; clip = 'clip' in sys.argv
OUT = os.path.join(ROOT, 'docs', 'design', 'racetrack', 'tight'); os.makedirs(OUT, exist_ok=True)
src = os.path.join(ROOT, 'build', 'tight_' + name, 'src')
shutil.copy(os.path.join(src, 'rt_track_preview.png'), os.path.join(OUT, name + '_track.png'))
tmp = tempfile.mkdtemp()
def grab(g, path):
    g.rpc('screenshot', path=path)
    im = Image.open(path).convert('RGB')
    bx, by = (im.width - 256) // 2, (im.height - 192) // 2
    return im.crop((bx, by, bx + 256, by + 192))
g = Game('racer_tight_' + name, src); g.to_grid(); g.go()
steer = rt_ace.ace(g, 72); done = False; n = 0
for f in range(560 if clip else 400):
    steer(); g.run(1)
    if not done and g.car()[1] < g.sym['starty'] - 20:        # it has climbed 20 px from the start straight: half-way round the first corner
        im = grab(g, os.path.join(tmp, 'c.png')); im.resize((768, 576), Image.NEAREST).save(os.path.join(OUT, name + '_corner.png')); done = True
    if clip and f >= 50 and n < 500:
        grab(g, os.path.join(tmp, 'c.png')).resize((512, 384), Image.NEAREST).save(os.path.join(tmp, 'f%04d.png' % n)); n += 1
g.close()
if clip:
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '50', '-i', os.path.join(tmp, 'f%04d.png'), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '14', os.path.join(OUT, name + '_lap.mp4')], check=True)
shutil.rmtree(tmp)
print(name, 'track and corner pictures' + (', and a %d-frame clip' % n if clip else ''), '->', OUT)
