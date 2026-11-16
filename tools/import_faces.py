"""Take in faces copied from the Breakfast Run Faces page ("Copy all faces as text"): the everyday
ones into tools/face_art.txt, happy and sad into tools/face_moods.txt. Then run make_faces.py.
Usage: python3 tools/import_faces.py pasted.txt   (blocks: NAME now|happy|sad, then 16 rows of # and .)"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
KEY = {'YOU': 'YOU', 'CYAN': 'CYAN', 'SLIM': 'WHITE', 'PINK': 'PINK', 'GREEN': 'GREEN', 'SPECS': 'SPECS', 'DOT': 'DOT'}
d = {}
for m in re.finditer(r'(\w+) (now|eyes|happy|sad)\n((?:[#.]{16}\n?){16})', open(sys.argv[1]).read()):
    rows = m.group(3).split(); assert len(rows) == 16, m.group(0)[:20]
    d[(KEY[m.group(1)], m.group(2))] = [r.replace('#', 'X') for r in rows]
p = os.path.join(HERE, 'face_art.txt'); s = open(p).read(); n = 0
for (k, mood), rows in d.items():
    if mood != 'now': continue
    pat = re.compile(r'== %s face ==\n(?:[X.]{16}\n){16}' % k); new = '== %s face ==\n%s\n' % (k, '\n'.join(rows))
    n += pat.search(s).group(0) != new; s = pat.sub(new, s)
open(p, 'w').write(s)
p = os.path.join(HERE, 'face_moods.txt'); s = open(p).read()
for (k, mood), rows in d.items():
    if mood == 'now': continue
    pat = re.compile(r'== %s %s ==\n(?:[X.]{16}\n){16}' % (k, mood)); new = '== %s %s ==\n%s\n' % (k, mood, '\n'.join(rows))
    if not pat.search(s): s = s.rstrip('\n') + '\n\n' + new; n += 1; continue      # (a frame the file has not had before: eyes)
    n += pat.search(s).group(0) != new; s = pat.sub(new, s)
open(p, 'w').write(s)
print('%d faces read, %d changed' % (len(d), n))
