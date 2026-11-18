"""Build the faces editor page (tools/faces_page.template.html) from the game's faces: tools/face_art.txt (everyday) and
tools/face_moods.txt (eyes, happy, sad, and Grant's trial expressions idea1 and idea2 once he has pasted some - until
then they start as copies of the everyday face). Seven drivers. Usage: python3 tools/make_faces_page.py <out.html>
Paste the page's text back with: python3 tools/import_faces.py pasted.txt"""
import os, re, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
art = {m.group(1): m.group(2).split() for m in re.finditer(r'== (\w+) face ==\n((?:[X.]{16}\n){16})', open(os.path.join(HERE, 'face_art.txt')).read())}
moods = {(m.group(1), m.group(2)): m.group(3).split() for m in re.finditer(r'== (\w+) (\w+) ==\n((?:[X.]{16}\n){16})', open(os.path.join(HERE, 'face_moods.txt')).read())}
KEYS = ['YOU', 'CYAN', 'GREEN', 'PINK', 'WHITE', 'SPECS', 'DOT']
NAMES = ['MAX (you)', 'FRANK', 'SPIKE', 'BRUNO', 'JANE', 'SPECS', 'DOT']
COLS = ['#ff0000', '#00ffff', '#00ff00', '#ff00ff', '#ffffff', '#ffff00', '#d7d7d7']
h = lambda rows: [r.replace('X', '#') for r in rows]
faces = [[h(art[k])] + [h(moods.get((k, m), art[k])) for m in ('eyes', 'happy', 'sad', 'idea1', 'idea2')] for k in KEYS]
data = {'keys': KEYS, 'names': NAMES, 'colours': COLS, 'faces': faces}
page = open(os.path.join(HERE, 'faces_page.template.html')).read().replace('/*DATA*/{}', json.dumps(data))
open(sys.argv[1], 'w').write(page)
print('wrote', sys.argv[1])
