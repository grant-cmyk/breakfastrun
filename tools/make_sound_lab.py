"""The Sound Lab page (a Claude artifact): play the four ditties in their three styles, and try the
options for each event sound, as the Spectrum's one-bit speaker would make them. The ditties are
the recordings in docs/sound/ (tools/make_ditties.py), squeezed to MP3 with ffmpeg and put inside
the page; the event sounds are made in the page from lists of speaker flips.
Usage: python3 tools/make_sound_lab.py out.html"""
import os, sys, base64, subprocess, tempfile, json
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = sys.argv[1]
tmp = tempfile.mkdtemp()
audio = {}
for d in range(1, 9):
    for st in ('pips', 'plink', 'buzz'):
        audio['ditty%d_%s' % (d, st)] = None
audio['demo_in_game'] = None
for n in audio:
    mp3 = os.path.join(tmp, n + '.mp3')
    subprocess.check_call(['ffmpeg', '-loglevel', 'error', '-y', '-i', os.path.join(ROOT, 'docs', 'sound', n + '.wav'), '-ac', '1', '-b:a', '64k', mp3])
    audio[n] = base64.b64encode(open(mp3, 'rb').read()).decode()
page = open(os.path.join(ROOT, 'tools', 'sound_lab.template.html')).read()
open(OUT, 'w').write(page.replace('/*AUDIO*/{}', json.dumps(audio)))
print('wrote %s: %.1f MB' % (OUT, os.path.getsize(OUT) / 1e6))
