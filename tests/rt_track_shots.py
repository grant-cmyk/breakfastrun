"""The green-line race track on any track (17 Nov 2026): pictures of a tape for docs/design/racetrack/built/ -
  green_<tag>_grid.png   the grid before the lights, 3x
  green_<tag>_bend.png   a bend in the pack, 3x
  green_<tag>_bend.mp4   that bend at real speed, 2x: one screenshot for EVERY TV frame, played at 50 a second, so the clip
                         shows the game's own picture rate and nothing smoother (ffmpeg makes it from the frames)
Usage: python3 tests/rt_track_shots.py <tag> <tape name in build/> [first frame of the clip] [how many frames] [the still's frame]
   e.g. python3 tests/rt_track_shots.py track2 racer_track_green_track2 60 300 200"""
import os, sys, subprocess, tempfile, shutil
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rt_lib import Game, ROOT
OUT = os.path.join(ROOT, 'docs', 'design', 'racetrack', 'built')
tag, tape = sys.argv[1], sys.argv[2]
F0 = int(sys.argv[3]) if len(sys.argv) > 3 else 60; N = int(sys.argv[4]) if len(sys.argv) > 4 else 300
STILL = int(sys.argv[5]) if len(sys.argv) > 5 else F0 + N // 2
tmp = tempfile.mkdtemp()
def grab(g, path):
    """the Spectrum's 256 x 192 picture, without the emulator's border"""
    g.rpc('screenshot', path=path)
    im = Image.open(path).convert('RGB')
    bx, by = (im.width - 256) // 2, (im.height - 192) // 2
    im = im.crop((bx, by, bx + 256, by + 192)); im.save(path); return im
g = Game(tape, os.path.join(ROOT, 'build', tape.replace('racer_', ''), 'src')); g.to_grid()
im = grab(g, os.path.join(tmp, 'grid.png')); im.resize((768, 576), Image.NEAREST).save(os.path.join(OUT, 'green_%s_grid.png' % tag))
g.go()
def each(f):
    if F0 <= f < F0 + N: grab(g, os.path.join(tmp, 'f%04d.png' % (f - F0)))
    if f == STILL: im = grab(g, os.path.join(tmp, 'still.png')); im.resize((768, 576), Image.NEAREST).save(os.path.join(OUT, 'green_%s_bend.png' % tag))
g.drive(frames=F0 + N + 1, each=each); g.close()
mp4 = os.path.join(OUT, 'green_%s_bend.mp4' % tag)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '50', '-i', os.path.join(tmp, 'f%04d.png'), '-vf', 'scale=512:384:flags=neighbor',
                '-c:v', 'libx264', '-crf', '14', '-pix_fmt', 'yuv420p', mp4], check=True)
shutil.rmtree(tmp)
print('green_%s_grid.png, green_%s_bend.png, green_%s_bend.mp4 (%d TV frames, %.1f s)' % (tag, tag, tag, N, N / 50))
