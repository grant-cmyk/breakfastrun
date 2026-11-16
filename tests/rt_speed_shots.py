"""The race-track trial's speed pass (16 Nov 2026): for each tape of the menu, the first bend in the pack as a 3x still and
as a 2x GIF at real speed (a frame of the GIF for every second TV frame, about 5 s), into docs/design/racetrack/built/.
Usage: python3 tests/rt_speed_shots.py [name ...]      names: full sparse noline pin pindash pin1 grip1 rows16 (default: all)"""
import os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rt_lib import Game, ROOT
OUT = os.path.join(ROOT, 'docs', 'design', 'racetrack', 'built')
TAPES = {'rows16': ('racer_racetrack_noline_rows16', 'racetrack_noline_rows16'), 'grip1': ('racer_racetrack_noline_grip1', 'racetrack_noline_grip1'), 'pin1': ('racer_racetrack_noline_pin1', 'racetrack_noline_pin1'), 'pin': ('racer_racetrack_noline_pin', 'racetrack_noline_pin'), 'pindash': ('racer_racetrack_noline_pindash', 'racetrack_noline_pindash'), 'full': ('racer_racetrack', 'racetrack'), 'sparse': ('racer_racetrack_sparse', 'racetrack_sparse'), 'noline': ('racer_racetrack_noline', 'racetrack_noline')}
def grab(g):
    tmp = os.path.join(OUT, '_tmp_%s.png' % g.tag); g.rpc('screenshot', path=tmp)
    im = Image.open(tmp).convert('RGB'); os.remove(tmp)
    bx, by = (im.width - 256) // 2, (im.height - 192) // 2
    return im.crop((bx, by, bx + 208, by + 168))
for tag in (sys.argv[1:] or list(TAPES)):
    tape, folder = TAPES[tag]
    g = Game(tape, os.path.join(ROOT, 'build', folder, 'src')); g.tag = tag; g.to_grid(); g.go(); fr = []
    def each(f):
        if f % 2 == 0 and 40 <= f < 300: fr.append(grab(g))
        if f == 150:
            im = grab(g); im.resize((im.width * 3, im.height * 3), Image.NEAREST).save(os.path.join(OUT, 'speed_%s_bend.png' % tag))
    g.drive(frames=300, each=each); g.close()
    fr = [f.resize((f.width * 2, f.height * 2), Image.NEAREST) for f in fr]
    pal = fr[len(fr) // 2].convert('P', palette=Image.ADAPTIVE, colors=16)
    fr = [f.quantize(palette=pal, dither=Image.NONE) for f in fr]
    fr[0].save(os.path.join(OUT, 'speed_%s_bend.gif' % tag), save_all=True, append_images=fr[1:] + [fr[-1]] * 12, duration=40, loop=0)
    print('speed_%s_bend.png and .gif (%d frames)' % (tag, len(fr)))
