"""Build docs/tools/skid_lab.html: the Skid Lab - a car alone in an open area, outside the
game, to try and tune how it slides (Grant, 10 Nov 2026: "lets create a test outside of the
game of a car in an open area and test the skid/slide").

Two models, switchable:
  GAME NOW   - the slide as it is in the game today (racer.asm: skid, friction).
  GRIP LIMIT - a tyre-grip model from the research: the tyres can cancel only so much
               sideways speed a frame (their grip); turn harder or faster than that and the
               car slides, and sliding grip is lower than static grip, so a slide eases off
               gradually; throttle uses part of the same grip (the friction circle).
Units are the game's: pixels and TV frames (50 a second); the car is your big car, drawn
with the game's 16 headings. Writes the page with the art embedded."""
import os, re, json
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
t = open(os.path.join(HERE, 'big_car_art.txt')).read()
art = {(m.group(1), m.group(2)): m.group(3).split() for m in re.finditer(r'== (\w+) big heading ([\d.]+) ==\n((?:[Xo.]{20}\n){20})', t)}
you = [art[('YOU', h)] for h in ('0', '22.5', '45')]
page = open(os.path.join(ROOT, 'docs', 'tools', 'skid_lab.template.html')).read().replace('__CAR__', json.dumps(you))
open(os.path.join(ROOT, 'docs', 'tools', 'skid_lab.html'), 'w').write(page)
print('ok')
