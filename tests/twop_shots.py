"""Two players (src/twoplayer.asm): the pictures in docs/design/racetrack/two_player/ -
  two_player_both.png    a 3x still, both players' cars in the view
  two_player_leash.png   a 3x still just after the leash has put a car back (it is flashing: caught on a picture that shows it)
  two_player_clip.mp4    12 seconds at real speed (one screenshot each TV frame, 50 a second, 2x): both racing from the
                         lights, player 2 (cyan) easing off and dropping back, the leash putting it back, and on
Usage: python3 tests/twop_shots.py [tape name in build/, default racer_2p] [its build folder under build/]   (needs ffmpeg)"""
import os, sys, subprocess, shutil, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from twop_lib import Game2
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
TAP = sys.argv[1] if len(sys.argv) > 1 else 'racer_2p'
SRC = os.path.join(ROOT, 'build', sys.argv[2] if len(sys.argv) > 2 else TAP, 'src')
OUT = os.path.join(ROOT, 'docs', 'design', 'racetrack', 'two_player'); os.makedirs(OUT, exist_ok=True)
g = Game2(TAP, SRC); g.start(2); S = g.sym
tmp = tempfile.mkdtemp()
EASE_FROM, FRAMES = 150, 600                              # player 2 eases off 3 s in; the clip is 12 s
leashed = None; still = False
for f in range(FRAMES):
    if f == EASE_FROM: g.lift[1] = 0.45
    if leashed is not None and f == leashed + 40: g.lift[1] = 1.0
    g.step()
    g.rpc('screenshot', path=os.path.join(tmp, 'f%04d.png' % f))
    if f == 120: g.shot(os.path.join(OUT, 'two_player_both.png'), 3)
    t = g.mem(S['lsh_t'], 2)
    if t[0] and leashed is None: leashed = f; print('the leash goes at frame %d (%.1f s): car %d put back' % (f, f / 50, t[1]))
    if leashed is not None and not still and f > leashed + 2 and (g.w16(S['renders']) & 1) == 1 and t[0]:
        g.shot(os.path.join(OUT, 'two_player_leash.png'), 3); still = True
g.close()
clip = os.path.join(OUT, 'two_player_clip.mp4')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '50', '-i', os.path.join(tmp, 'f%04d.png'), '-vf', 'scale=iw*2:ih*2:flags=neighbor',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '14', clip], check=True)
shutil.rmtree(tmp)
print('wrote', clip, os.path.getsize(clip), 'bytes; leash at', leashed)
