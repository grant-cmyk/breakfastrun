"""Build docs/tools/car_editor.html: the car pixel editor, loaded with the game's
current car art (the three drawn headings of each car, from make_data.py).
X = ink, o = paper (the car's white body), . = empty."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'make_data.py')).read()
ns = {'__file__': os.path.join(HERE, 'make_data.py')}
exec(src[:src.index('KINDS = [')], ns)
INK, NONE, DITH = ns['INK'], ns['NONE'], ns['DITH']
def rows(g):
    return [''.join('X' if v == INK or (v == DITH and (x + y) % 2 == 0) else '.' if v == NONE else 'o'
                    for x, v in enumerate(r)) for y, r in enumerate(g)]
art = [[rows(g) for g in ns['frames_for'](k)[:3]] for k in range(5)]
docs = os.path.join(HERE, '..', 'docs', 'tools')
page = open(os.path.join(docs, 'car_editor.template.html')).read().replace('__ART__', json.dumps(art, separators=(',', ':')))
open(os.path.join(docs, 'car_editor.html'), 'w').write(page); print('ok')
