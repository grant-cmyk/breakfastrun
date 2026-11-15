"""The Jingle Lab page (a Claude artifact): each candidate tune as the game's own two-voice "trance"
jingle engine plays it - recorded from the built game in zxdev, one build a tune (JKEY=... python3
tools/make_music_ay.py; bash build.sh) - so Grant can pick by ear. The recordings are
docs/sound/jingles/*.mp3. Usage: python3 tools/make_jingle_lab.py out.html"""
import os, sys, base64, json
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
TUNES = [('ditty13', "Kettle's On, driving", 'in the game now', 'B'),
         ('arp', 'Full English', 'NEW: a minor arpeggio written for this sound, the way trance leads go', 'B'),
         ('ditty5', "Kettle's On", 'the original skipping jig', 'B'),
         ('ditty11', 'Chequered Flag', 'a galloping fanfare', 'B'),
         ('ditty9', 'Green Light', 'driving and bright', 'B'),
         ('ditty12', 'Second Helpings', 'bouncy, off the beat', 'B'),
         ('ditty10', 'Flat Out', 'a rock and roll boogie riff', 'G'),
         ('ditty3', 'Spilt Milk', 'cheeky, stop-start, tiptoe', 'G'),
         ('ditty8', 'Butter Fingers', "clumsy slips and stumbles (Spilt Milk's cousin)", 'G'),
         ('ditty6', 'Crumbs!', 'a galloping chase, minor key', 'G'),
         ('ditty1', 'Toast Rack March', 'a jaunty little march', 'B'),
         ('ditty2', 'Marmalade Swing', 'bouncy, lazy swing', 'B'),
         ('ditty7', 'Pop-Up Toaster', 'boingy leaps and pauses', 'B'),
         ('ditty4', 'Sunny Side Up', 'a calm morning waltz', 'G')]
data = [{'key': k, 'name': n, 'note': t, 'bass': b, 'mp3': base64.b64encode(open(os.path.join(ROOT, 'docs', 'sound', 'jingles', k + '.mp3'), 'rb').read()).decode()} for k, n, t, b in TUNES]
page = open(os.path.join(ROOT, 'tools', 'jingle_lab.template.html')).read()
open(sys.argv[1], 'w').write(page.replace('/*DATA*/[]', json.dumps(data)))
print('wrote %s: %.1f MB' % (sys.argv[1], os.path.getsize(sys.argv[1]) / 1e6))
