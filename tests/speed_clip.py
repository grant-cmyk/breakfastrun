"""THE SLOWER GAME, SIDE BY SIDE (18 Nov 2026): a real-speed clip of several race-track tapes from the green light, your car
by the corner-cutting autopilot (ace 104,30) in the pack - one picture of the TV for every TV frame (50 a second), so the
clip plays at the game's own speed. Each tape's screen (the border left off) at twice size, in a grid, its name above it.
Usage: python3 tests/speed_clip.py <out.mp4> <tape:label> [<tape:label> ...]     SECS=8 (how long), COLS=2 (tapes a row)
Needs ffmpeg. Each tape is run in its own emulator, one after another."""
import sys, os, subprocess, tempfile, shutil
from rt_lib import *
import rt_ace
from PIL import Image, ImageDraw
SECS = float(os.environ.get('SECS', '8')); COLS = int(os.environ.get('COLS', '2'))
out = sys.argv[1]; tapes = [a.split(':', 1) for a in sys.argv[2:]]
tmp = tempfile.mkdtemp()
def record(i, name):
    g = Game(name, os.path.join(ROOT, 'build', name, 'src')); g.to_grid(); g.go(); steer = rt_ace.ace(g, 104, 30)
    for f in range(int(SECS * 50)):
        steer(); g.run(1); g.rpc('screenshot', path=os.path.join(tmp, '%d_%04d.png' % (i, f)))
    g.close()
for i, (name, label) in enumerate(tapes): record(i, name)
W, H, TOP = 512, 384, 24                   # (the screen less its border, 256 x 192, at twice size; a strip for the name)
rows = -(-len(tapes) // COLS)
for f in range(int(SECS * 50)):
    sheet = Image.new('RGB', (COLS * W, rows * (H + TOP)), (0, 0, 0)); d = ImageDraw.Draw(sheet)
    for i, (name, label) in enumerate(tapes):
        im = Image.open(os.path.join(tmp, '%d_%04d.png' % (i, f))).convert('RGB')
        bx, by = (im.width - 256) // 2, (im.height - 192) // 2
        im = im.crop((bx, by, bx + 256, by + 192)).resize((W, H), Image.NEAREST)
        x, y = (i % COLS) * W, (i // COLS) * (H + TOP)
        sheet.paste(im, (x, y + TOP)); d.text((x + 8, y + 6), label, fill=(255, 255, 255))
    sheet.save(os.path.join(tmp, 'sheet_%04d.png' % f))
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '50', '-i', os.path.join(tmp, 'sheet_%04d.png'),
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', out], check=True)
shutil.copy(os.path.join(tmp, 'sheet_%04d.png' % int(SECS * 25)), os.path.splitext(out)[0] + '_still.png')
shutil.rmtree(tmp)
print('wrote', out)
