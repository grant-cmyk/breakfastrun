"""The Jingle Lab page (a Claude artifact): each candidate tune as the game's own two-voice "trance"
jingle engine plays it - recorded from the built game in zxdev, one build a tune (JKEY=... python3
tools/make_music_ay.py; bash build.sh) - so Grant can pick by ear. The recordings are
docs/sound/jingles/*.mp3. Usage: python3 tools/make_jingle_lab.py out.html"""
import os, sys, base64, json
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
TUNES = [('t_sunrise', 'Sunrise Special', 'NEW 15 Nov: a rising anthem with gaps in it', 'B'),
         ('t_offbeat', 'Off The Beat', 'NEW 15 Nov: stabs on the off-beat only, the bass carries it', 'G'),
         ('t_drip', 'Coffee Drip', 'NEW 15 Nov: three falling notes going round against the beat', 'B'),
         ('t_pulse', 'Pulse Check', 'NEW 15 Nov: an octave bounce, the top note walking down', 'B'),
         ('t_answer', 'Order Up', 'NEW 15 Nov: a call, then its answer higher up (bass on E)', 'E'),
         ('t_hands', 'Hands Up', 'NEW 15 Nov: long notes with a pick-up, a little faster', 'B'),
         ('ditty13', "Kettle's On, driving", 'the first one tried', 'B'),
         ('arp', 'Full English', 'NEW: a minor arpeggio written for this sound, the way trance leads go', 'B'),
         ('ditty5', "Kettle's On", 'the original skipping jig', 'B'),
         ('ditty11', 'Chequered Flag', 'a galloping fanfare', 'B'),
         ('ditty9', 'Green Light', 'driving and bright', 'B'),
         ('ditty12', 'Second Helpings', 'IN THE GAME: the start (since 15 Nov) - bouncy, off the beat', 'B'),
         ('ditty10', 'Flat Out', 'a rock and roll boogie riff', 'G'),
         ('ditty3', 'Spilt Milk', 'IN THE GAME: the chequered flag (since 15 Nov) - cheeky, stop-start, tiptoe', 'G'),
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
