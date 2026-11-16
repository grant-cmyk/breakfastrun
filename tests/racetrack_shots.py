"""The race-track trial's pictures, from the real tape (build/racer_racetrack.tap) in the emulator, into
docs/design/racetrack/built/: 3x stills (start grid, a bend, your car on the limit line, across the grass's edge, on the
grass) and two 2x GIFs at real speed (the slide off the first bend into the grass and back; the first bend in the pack).
Usage: python3 tests/racetrack_shots.py"""
import os, sys, re
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rt_lib import Game, ROOT
OUT = os.path.join(ROOT, 'docs', 'design', 'racetrack', 'built'); os.makedirs(OUT, exist_ok=True)
src = open(os.path.join(ROOT, 'build', 'racetrack', 'src', 'world.asm')).read()
SY = int(re.search(r'TRACK_SY\s+equ\s+(\d+)', src).group(1)); LX = 288
wsrc = open(os.path.join(ROOT, 'tools', 'make_world.py')).read()
wns = {'__file__': os.path.join(ROOT, 'tools', 'make_world.py')}
exec(wsrc[:wsrc.index('road = road_mask(ROAD)')], wns)
GRASS = ~np.array(wns['road_mask'](wns['ROAD'] + 20), dtype=bool)
def grab(g):
    """the play window and its frame, as the TV shows it"""
    tmp = os.path.join(OUT, '_tmp.png'); g.rpc('screenshot', path=tmp)
    im = Image.open(tmp).convert('RGB'); os.remove(tmp)
    bx, by = (im.width - 256) // 2, (im.height - 192) // 2
    return im.crop((bx, by, bx + 208, by + 168))
def still(g, name):
    im = grab(g); im.resize((im.width * 3, im.height * 3), Image.NEAREST).save(os.path.join(OUT, name)); print(name)
def gif(frames, name):
    fr = [f.resize((f.width * 2, f.height * 2), Image.NEAREST) for f in frames]
    pal = fr[len(fr) // 2].convert('P', palette=Image.ADAPTIVE, colors=16)
    fr = [f.quantize(palette=pal, dither=Image.NONE) for f in fr]
    fr[0].save(os.path.join(OUT, name), save_all=True, append_images=fr[1:] + [fr[-1]] * 12, duration=40, loop=0); print(name, len(fr), 'frames')

g = Game(); g.to_grid(); still(g, 'start_grid.png')
g.go(); fr = []
def each(f):
    if f % 2 == 0 and 40 <= f < 300: fr.append(grab(g))
    if f == 150: still(g, 'bend_in_the_pack.png')
g.drive(frames=300, each=each); gif(fr, 'bend_in_the_pack.gif')
g.drive(frames=260); still(g, 'bend.png'); g.close()

g = Game(); g.to_grid(); g.go(alone=True); g.key('Q', False); g.run(260)      # (the lights and the chief's GOOD LUCK have gone)
for name, y in (('car_on_the_line.png', SY - 44), ('car_in_a_mixed_square.png', SY - 56), ('car_on_the_grass.png', SY - 84)):
    g.put(LX + 60, y, 16); g.run(14); still(g, name)
g.close()

g = Game(); g.to_grid(); g.go(alone=True); fr = []; phase = deep = back = n = 0
while n < 1500:
    x, y, ang = g.car(); on = GRASS[y + 8, x + 8]
    if phase == 0:
        g.key('Q', True); g.key('O', False); g.key('P', False); deep += on
        if deep > 60: phase = 1
    else:
        g.steer(); back = 0 if on else back + 1
        if back > 60: break
    g.run(1); n += 1
    if n % 2 == 0 and n > 60: fr.append(grab(g))
g.close(); gif(fr, 'slide_into_the_grass.gif')
