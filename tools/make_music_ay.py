"""The race tune for the AY sound chip (Grant, 15 Nov 2026: "go ahead on ay-version"): src/music_ay.asm
from a driving tune in tools/make_ditties.py. The beeper could not carry a tune under the game
("no suggestion of music, just background beeping"); the AY plays by itself once its registers
are set, so the interrupt only has to set them - about 250 T a frame.
Usage: python3 tools/make_music_ay.py [ditty key, default ditty13 = Kettle's On, driving]
  mu_tune: a byte a step (MU_STEP frames): the note's place in mu_ptab (2 x its number), 254 a
           rest, 255 the end (it starts again)
  mu_ptab: 2 bytes a pitch: the AY's tone period (fine, coarse)
The bass (channel B) is a pedal on the tune's key note, low then an octave up, a step each; the
hat (channel C, noise) ticks on the off-beat. LOW: semitones the melody is under the music box."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_ditties as md
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
key = sys.argv[1] if len(sys.argv) > 1 else 'ditty13'
d = next(x for x in md.DITTIES + md.RACERS if x['key'] == key)
AY_HZ = 1773400                                   # the 128K's AY clock
LOW = int(os.environ.get('LOW', 24))             # two octaves: 495-1,108 Hz, a singing register (12 was shrill on paper: 990-2,217 Hz)
BASS = int(os.environ.get('BASS', 47))            # MIDI B2: the pedal (Kettle's On is in B)
period = lambda midi: round(AY_HZ / 16 / md.freq_of(midi))
STEP = d.get('step'); assert STEP
steps = [midi for t, midi, length in md.notes_of(d)]
kinds = []
for m in steps:
    if m is not None and m not in kinds: kinds.append(m)
with open(os.path.join(ROOT, 'src', 'music_ay.asm'), 'w') as f:
    f.write('; made by tools/make_music_ay.py from tools/make_ditties.py: "%s", %d steps of %d TV frames, for the AY chip\n' % (d['name'], len(steps), STEP))
    f.write('MU_STEP equ %d\nAY_BASS_LO equ %d                ; the bass pedal\'s tone periods: MIDI %d, and an octave up\nAY_BASS_HI equ %d\n' % (STEP, period(BASS), BASS, period(BASS + 12)))
    f.write('; a byte a step: the note\'s place in mu_ptab, 254 a rest, 255 the end\nmu_tune_src:\n')
    for q in range(0, len(steps), 12):
        f.write('        db ' + ','.join('254' if m is None else '%d' % (kinds.index(m) * 2) for m in steps[q:q + 12]) + '\n')
    f.write('        db 255\n; a word a pitch: the AY tone period\nmu_ptab_src:\n')
    for k in kinds:
        f.write('        dw %d    ; note %d, %.0f Hz\n' % (period(k - LOW), k - LOW, AY_HZ / 16 / period(k - LOW)))
# ---- the jingle (start, and chequered flag): any tune, on the ordinary speaker, by jin_start's two-voice engine
# (src/plateco.asm). JKEY picks it: a ditty of make_ditties.py, or one written for this sound (JINGLES below).
from math import gcd
from functools import reduce
ARP = [95, 102, 98, 102, 95, 102, 98, 102, 95, 103, 98, 103, 95, 103, 98, 103,      # "Full English": a minor arpeggio
       93, 100, 97, 100, 93, 100, 97, 100, 93, 102, 98, 102, 93, 102, 98, 102,       # over the bass, the way trance
       95, 102, 98, 102, 95, 107, 102, 107, 98, 102, 107, 110, 107, 102, 98, 95]     # leads go (written 15 Nov 2026)
JINGLES = {'arp': ('Full English', 6, ARP)}
# Two jingles (Grant, 15 Nov 2026, from the Jingle Lab: "Spilt Milk is a good start jingle, then second helpings
# for chequered flag"): JKEYS = start,flag - each a key and its bass's note (MIDI: 43 G, 47 B). JKEY=one plays one at both.
JSECS = float(os.environ.get('JSECS', 5.8))
JKEYS = os.environ.get('JKEYS', 'ditty3:43,ditty12:47')
if os.environ.get('JKEY'): JKEYS = '%s:%s,%s:%s' % (os.environ['JKEY'], os.environ.get('BASS', 47), os.environ['JKEY'], os.environ.get('BASS', 47))
LOOP_T = 91                                       # T a turn of the engine's loop (measured from a recording)
bper = lambda hz: round(3500000 / (LOOP_T * 2 * hz))   # a voice flips every `period` turns
KICK_T = 6 * 7 / 2 * 2500                          # the kick's six flips take 52,500 T of a beat's first step
with open(os.path.join(ROOT, 'src', 'jingle.asm'), 'w') as f:
    f.write('; made by tools/make_music_ay.py (JKEYS=%s): the jingles, for jin_start / jin_flag (plateco.asm)\n' % JKEYS)
    f.write('; Two voices on the one speaker: the tune, and under it a bass on the key note - low, high, low, high, four steps to\n; a beat - with a kick on each beat and a tick of noise half way. Kept in the table block at TD (racer.asm: jc_a, jc_b).\n')
    for tag, spec in zip('ab', JKEYS.split(',')):
        jkey, jbass = spec.split(':'); jbass = int(jbass)
        if jkey in JINGLES: jname, jstep, jsteps = JINGLES[jkey]
        else:
            jd = next(x for x in md.DITTIES + md.RACERS if x['key'] == jkey); jn = md.notes_of(jd); jname = jd['name']
            jstep = reduce(gcd, [l for _, _, l in jn]); jsteps = []
            for t, m, l in jn: jsteps += [m] * (l // jstep)      # (a long note is the same pitch on each of its steps; None a rest)
        JN = min(len(jsteps), round(JSECS / (jstep * 0.02))); JN -= JN % 4; jsteps = jsteps[:JN]
        jkinds = sorted(set(m for m in jsteps if m is not None)); STEP_T = jstep * 0.02 * 3500000
        f.write('; %s: "%s", %d steps, %.1f s\n' % ('the start' if tag == 'a' else 'the chequered flag', jname, JN, JN * jstep * 0.02))
        f.write('jc_%s_src:                       ; what jin_go copies to jc: the tune, the periods, a step\'s turns, a beat\'s, the bass low and high\n' % tag)
        f.write('        dw TD + jb_tune_%s - td_src, TD + jb_per_%s - td_src, %d, %d\n        db %d, %d\n' % (tag, tag, round(STEP_T / LOOP_T), round((STEP_T - KICK_T) / LOOP_T), bper(md.freq_of(jbass)), bper(md.freq_of(jbass + 12))))
        f.write('jb_per_%s:                       ; each pitch\'s period\n' % tag)
        for k in jkinds:
            hz = md.freq_of(k - LOW); f.write('        db %d    ; %.0f Hz (wanted %.0f)\n' % (bper(hz), (3500000 / LOOP_T / 2) / bper(hz), hz))
        f.write('jb_tune_%s:                      ; a pitch a step; 254 a rest; 255 ends\n        db ' % tag + ','.join('254' if m is None else '%d' % jkinds.index(m) for m in jsteps) + ',255\n')
print('music_ay.asm: %s, %d steps, %d pitches, %d bytes' % (d['name'], len(steps), len(kinds), len(steps) + 1 + 2 * len(kinds)))

# (the file in two parts: racer.asm includes it with JIN_PART 0 for the start's jingle and title3.asm with
#  JIN_PART 1 for the flag's - the table block has room in two places, not one: 15 Nov 2026)
_p = os.path.join(ROOT, 'src', 'jingle.asm'); _s = open(_p).read()
if 'JIN_PART' not in _s:
    _i = _s.index('jc_a_src:'); _i = _s.rindex('\n', 0, _s.rindex('\n', 0, _i)) + 1 if _s[:_i].rstrip().endswith('s') else _i
    _a = _s.index('; the start:') if '; the start:' in _s else _s.index('jc_a_src:'); _b = _s.rindex('\n', 0, _s.index('jc_b_src:') - 1) + 1
    _s = _s[:_a] + '        if 1 - JIN_PART\n' + _s[_a:_b] + '        endif\n        if JIN_PART\n' + _s[_b:].rstrip('\n') + '\n        endif\n'
    open(_p, 'w').write(_s)
